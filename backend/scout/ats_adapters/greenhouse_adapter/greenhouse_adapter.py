from typing import Any

import httpx

from .greenhouse_contracts import (
    API_ROOT,
    GreenhouseResult,
    GreenhouseUrlError,
    parse_board_token,
)
from .greenhouse_response_mapper import GreenhouseResponseMapper


class GreenhouseAdapter:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=False,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def retrieve(self, board_token: str) -> GreenhouseResult:
        board_url = f"{API_ROOT}/{board_token}"
        try:
            board_response = await self._client.get(board_url)
            failure = GreenhouseResponseMapper.failure(board_response, board_token)
            if failure:
                return failure
            board = board_response.json()
            if not isinstance(board, dict) or not isinstance(board.get("name"), str):
                return GreenhouseResponseMapper.malformed(
                    board_token, "Board metadata is malformed."
                )
            response = await self._client.get(f"{board_url}/jobs?content=true")
            failure = GreenhouseResponseMapper.failure(
                response, board_token, board["name"]
            )
            if failure:
                return failure
            payload = response.json()
            jobs = payload.get("jobs") if isinstance(payload, dict) else None
            meta = payload.get("meta") if isinstance(payload, dict) else None
            total = meta.get("total") if isinstance(meta, dict) else None
            if (
                not isinstance(jobs, list)
                or not isinstance(total, int)
                or total < 0
                or not all(GreenhouseResponseMapper.valid_job(job) for job in jobs)
            ):
                return GreenhouseResponseMapper.malformed(
                    board_token,
                    "Job response must contain valid jobs and meta.total.",
                )
            complete = len(jobs) == total
            outcome = "partial" if not complete else "success" if jobs else "empty"
            return GreenhouseResult(
                outcome=outcome,
                board_token=board_token,
                board_name=board["name"],
                jobs=jobs,
                pages_fetched=1,
                complete=complete,
                detail=(
                    None
                    if complete
                    else f"API reported {total} jobs but returned {len(jobs)}."
                ),
                total_jobs=total,
            )
        except (httpx.TimeoutException, httpx.TransportError):
            return GreenhouseResult(
                "transient_failure",
                board_token,
                None,
                [],
                0,
                False,
                "Greenhouse request failed or timed out.",
            )
        except (ValueError, TypeError):
            return GreenhouseResponseMapper.malformed(
                board_token, "Greenhouse returned invalid JSON."
            )
