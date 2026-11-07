from secrets import compare_digest

from fastapi import Depends, Header, HTTPException, status
from pydantic import SecretStr

from scout.settings import Settings, get_settings


def require_vacancy_export_access(
    export_key: str | None = Header(default=None, alias="X-Scout-Export-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    configured_key: SecretStr | None = settings.scout_export_api_key

    if configured_key is None:
        if settings.app_env.casefold() not in {"development", "test"}:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vacancy export authentication is not configured.",
            )
        return

    expected_key = configured_key.get_secret_value()
    if not export_key or not compare_digest(export_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid Scout export key is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
