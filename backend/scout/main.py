from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from scout.api.router_registration import register_application_routes
from scout.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
register_application_routes(app, settings.api_prefix)


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
    errors = exception.errors()
    fields = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in errors
    )
    return _problem_response(
        request=request,
        status_code=422,
        title="Request validation failed",
        detail=f"Request validation failed: {fields}",
        extensions={"errors": errors},
    )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "thungatha-scout-api"}
