import asyncio

import httpx
import pytest

from scout.ats_adapters.greenhouse_adapter.greenhouse_career_site_parser import (
    CareersLinks,
    find_greenhouse_board_candidates,
)
from scout.employer_name_matching import board_name_matches, company_aliases
from scout.ats_adapters.greenhouse_adapter.greenhouse_board_resolver import (
    candidate_tokens,
    resolve_greenhouse_board,
)


def test_parser_collects_board_link_and_inline_api_candidates() -> None:
    parser = CareersLinks()
    parser.feed(
        '<a href="https://job-boards.greenhouse.io/northwind/jobs/123">Role</a>'
        "<script>fetch('https://boards-api.greenhouse.io/v1/boards/other-team/jobs')</script>"
    )
    assert find_greenhouse_board_candidates(
        parser, httpx.URL("https://northwind.example/jobs")
    ) == ["northwind", "other-team"]


def test_parser_reads_greenhouse_embed_for_parameter() -> None:
    parser = CareersLinks()
    parser.feed(
        '<iframe src="https://boards.greenhouse.io/embed/job_board?for=northwind"></iframe>'
    )
    assert find_greenhouse_board_candidates(
        parser, httpx.URL("https://northwind.example")
    ) == ["northwind"]


def test_parser_reads_greenhouse_api_script_source() -> None:
    parser = CareersLinks()
    parser.feed(
        '<script src="https://boards-api.greenhouse.io/v1/boards/northwind/jobs"></script>'
    )
    assert find_greenhouse_board_candidates(
        parser, httpx.URL("https://northwind.example")
    ) == ["northwind"]


def test_job_identifier_is_not_mistaken_for_board_token() -> None:
    parser = CareersLinks()
    page_url = httpx.URL("https://careers.northwind.co.za/jobs?gh_jid=8857266002")
    assert candidate_tokens(parser, page_url, "") == ["northwind"]


def test_company_aliases_match_board_metadata_without_employer_constants() -> None:
    aliases = company_aliases("Northwind", "Northwind Careers", "careers.northwind.com")
    assert board_name_matches("Northwind Group", aliases)
    assert not board_name_matches("Another Employer", aliases)


def test_resolver_validates_candidate_against_greenhouse_metadata() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/missing"):
            return httpx.Response(404)
        return httpx.Response(200, json={"name": "Northwind Group"})

    async def run() -> tuple[str, str]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await resolve_greenhouse_board(
                client, ["missing", "northwind"], ["northwind"]
            )

    assert asyncio.run(run()) == ("northwind", "Northwind Group")


def test_resolver_rejects_a_board_with_unrelated_metadata() -> None:
    async def run() -> None:
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"name": "Different Employer"})
        )
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(ValueError, match="could not be confirmed"):
                await resolve_greenhouse_board(client, ["northwind"], ["northwind"])

    asyncio.run(run())
