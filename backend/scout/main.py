from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from scout.api.employers import router as employers_router
from scout.api.greenhouse_routes import router as greenhouse_router
from scout.api.lever_routes import router as lever_router
from scout.api.source_discovery_routes import router as source_discovery_router
from scout.api.vacancies import router as vacancies_router
from scout.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(employers_router, prefix=settings.api_prefix)
app.include_router(greenhouse_router, prefix=settings.api_prefix)
app.include_router(lever_router, prefix=settings.api_prefix)
app.include_router(source_discovery_router, prefix=settings.api_prefix)
app.include_router(vacancies_router, prefix=settings.api_prefix)


def _problem_response(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    extensions: dict | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    problem = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
    }
    if extensions:
        problem.update(extensions)

    return JSONResponse(
        status_code=status_code,
        content=problem,
        media_type="application/problem+json",
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exception: HTTPException,
) -> JSONResponse:
    return _problem_response(
        request=request,
        status_code=exception.status_code,
        title="Request failed",
        detail=str(exception.detail),
        headers=exception.headers,
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    return _problem_response(
        request=request,
        status_code=422,
        title="Request validation failed",
        detail="One or more request fields are invalid.",
        extensions={"errors": exception.errors()},
    )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "thungatha-scout-api"}
