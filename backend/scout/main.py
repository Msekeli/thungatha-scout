from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from scout.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)


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
