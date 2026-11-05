from contextlib import contextmanager
from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancies import get_extraction_service
from scout.main import app


class FakeExtractionService:
    async def extract_source(self, source_id):
        return {
            "id": str(uuid4()),
            "source_id": str(source_id),
            "outcome": "success",
            "jobs_received": 2,
            "jobs_inserted": 2,
            "jobs_updated": 0,
            "complete": True,
        }

    def list_vacancies(self, employer_id=None, limit=200, offset=0):
        return [{"employer_id": str(employer_id), "title": "Software Engineer"}]

    def list_vacancy_page(
        self,
        employer_id=None,
        review_status=None,
        location_scope="cape_town",
        limit=50,
        offset=0,
    ):
        return {
            "items": [
                {
                    "employer_id": str(employer_id) if employer_id else None,
                    "title": "Software Engineer",
                }
            ],
            "total": 201,
            "limit": limit,
            "offset": offset,
            "has_more": offset + 1 < 201,
        }

    def get_vacancy(self, vacancy_id):
        return {
            "id": str(vacancy_id),
            "title": "Software Engineer",
            "description": "<p>Build software.</p>",
            "review_status": "needs_verification",
        }

    def update_vacancy_review(self, vacancy_id, review_status, review_reason):
        return {
            "id": str(vacancy_id),
            "review_status": review_status,
            "review_reason": review_reason,
        }

    def archive_vacancy(self, vacancy_id, reason):
        return {"id": str(vacancy_id), "archived_reason": reason}

    def restore_vacancy(self, vacancy_id):
        return {"id": str(vacancy_id), "archived_at": None}

    def list_archived_vacancies(self, limit=200, offset=0):
        return [{"id": str(uuid4()), "title": "Archived vacancy"}]

    def list_extraction_runs(self, source_id):
        return [
            {
                "id": str(uuid4()),
                "source_id": str(source_id),
                "outcome": "not_found",
                "jobs_received": 0,
                "jobs_inserted": 0,
                "jobs_updated": 0,
                "complete": False,
                "detail": "Greenhouse returned HTTP 404.",
            }
        ]

    def list_all_extraction_runs(self):
        return [{"source_id": "source-1", "outcome": "success"}]


@contextmanager
def vacancy_client():
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
