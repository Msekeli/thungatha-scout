import asyncio

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult


class FailingAdapter:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.closed = False

    async def retrieve(self, source_config):
        raise self.error

    async def close(self) -> None:
        self.closed = True


def test_invalid_adapter_configuration_is_recorded_as_malformed() -> None:
    adapter = FailingAdapter(ValueError("missing slug"))
    result = asyncio.run(retrieve_adapter_result(adapter, {}))

    assert result.outcome == "malformed"
    assert result.complete is False
    assert "missing slug" in result.detail
    assert adapter.closed is True


def test_unexpected_adapter_exception_is_recorded_as_transient_failure() -> None:
    adapter = FailingAdapter(RuntimeError("connection dropped"))
    result = asyncio.run(retrieve_adapter_result(adapter, {}))

    assert result.outcome == "transient_failure"
    assert result.vacancies == []
    assert result.complete is False
    assert "connection dropped" in result.detail
    assert adapter.closed is True


def test_successful_empty_result_is_preserved() -> None:
    class EmptyAdapter:
        async def retrieve(self, source_config):
            return ATSAdapterResult("empty", [], 1, True, total_vacancies=0)

        async def close(self) -> None:
            return None

    result = asyncio.run(retrieve_adapter_result(EmptyAdapter(), {}))
    assert result.outcome == "empty"
    assert result.complete is True
