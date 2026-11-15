class FakeSourcePreviewService:
    async def preview_source(self, source_id):
        return {
            "outcome": "success",
            "complete": True,
            "detail": None,
            "discovery_preview": {
                "total_vacancies": 7,
                "jobs": [{"id": "job-1", "title": "Software Engineer"}],
            },
        }
