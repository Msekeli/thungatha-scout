from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.ats_adapters.ats_adapter_contracts import ATSAdapter
from scout.ats_adapters.greenhouse_adapter.greenhouse_source_adapter import (
    GreenhouseSourceAdapter,
)
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository


class SourcePreviewService:
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
        adapter_factories: dict[str, Callable[[], ATSAdapter]] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection
        self._adapter_factories = adapter_factories or {
            "greenhouse": GreenhouseSourceAdapter,
            "lever": LeverSourceAdapter,
        }

    async def preview_source(self, source_id: UUID) -> dict[str, Any]:
        with self._connection_factory() as connection:
            source = EmployerSourceRepository(connection).get_by_id(source_id)
        if source is None:
            raise LookupError("Employer source not found.")
        adapter_factory = self._adapter_factories.get(source["adapter_key"])
        if adapter_factory is None:
            raise ValueError("No adapter is registered for this source.")
        result = await retrieve_adapter_result(
            adapter_factory(), source["adapter_config"]
        )
        jobs = [
            {
                "id": vacancy.external_job_id,
                "title": vacancy.title,
                "absolute_url": vacancy.raw_payload.get("hostedUrl")
                or vacancy.application_url,
                "location": {"name": vacancy.location_text},
                "content": vacancy.description,
            }
            for vacancy in result.vacancies[:5]
        ]
        total_vacancies = (
            result.total_vacancies
            if result.total_vacancies is not None
            else len(result.vacancies)
        )
        preview = {"total_vacancies": total_vacancies, "jobs": jobs}
        if result.complete and result.outcome in {"success", "empty"}:
            with self._connection_factory() as connection, connection.transaction():
                EmployerSourceRepository(connection).update_discovery_preview(
                    source_id, preview
                )
        return {
            "outcome": result.outcome,
            "complete": result.complete,
            "detail": result.detail,
            "discovery_preview": preview,
        }
