from datetime import UTC, datetime
from uuid import uuid4


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

    def export_vacancies(self, limit=50, offset=0, location_scope="south_africa"):
        return {
            "items": [
                {
                    "scout_vacancy_id": uuid4(),
                    "employer_name": "Example Employer",
                    "logo_url": None,
                    "title": "Software Engineer",
                    "description": "Build software.",
                    "location_text": "Cape Town, South Africa",
                    "application_url": "https://jobs.example.com/apply/123",
                    "published_at": datetime(2026, 11, 1, tzinfo=UTC),
                    "source_updated_at": None,
                    "first_seen_at": datetime(2026, 11, 2, tzinfo=UTC),
                }
            ],
            "total": 81,
            "limit": limit,
            "offset": offset,
            "has_more": offset + 1 < 81,
            "location_scope": location_scope,
        }

    def get_vacancy(self, vacancy_id):
        return {
            "id": str(vacancy_id),
            "title": "Software Engineer",
            "description": "<p>Build software.</p>",
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

