from fastapi import Depends, FastAPI

from scout.api.career_page_routes import router as career_page_router
from scout.api.employers import router as employers_router
from scout.api.greenhouse_routes import router as greenhouse_router
from scout.api.lever_routes import router as lever_router
from scout.api.teamtailor_routes import router as teamtailor_router
from scout.api.vacancies import router as vacancies_router
from scout.api.vacancy_export_routes import router as vacancy_export_router
from scout.api.workable_routes import router as workable_router
from scout.api.workday_routes import router as workday_router
from scout.authentication import require_admin


def register_application_routes(app: FastAPI, api_prefix: str) -> None:
    protected = [Depends(require_admin)]
    routers = (
        employers_router,
        career_page_router,
        greenhouse_router,
        lever_router,
        teamtailor_router,
        workable_router,
        workday_router,
    )
    for router in routers:
        app.include_router(router, prefix=api_prefix, dependencies=protected)

    # Keep the server-to-server export key independent of administrator sessions.
    app.include_router(vacancy_export_router, prefix=api_prefix)
    app.include_router(vacancies_router, prefix=api_prefix, dependencies=protected)
