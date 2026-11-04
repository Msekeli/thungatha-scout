from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from scout.settings import Settings, get_settings
from scout.supabase_jwt import (
    AuthenticationServiceUnavailable,
    verify_supabase_access_token,
)

bearer_scheme = HTTPBearer(auto_error=False)


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid bearer access token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not all(
        [
            settings.scout_supabase_url,
            settings.scout_supabase_publishable_key,
            settings.scout_admin_email,
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrator authentication is not configured.",
        )

    try:
        claims = await verify_supabase_access_token(
            credentials.credentials,
            settings.scout_supabase_url,
            settings.scout_supabase_publishable_key.get_secret_value(),
        )
    except AuthenticationServiceUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable.",
        ) from error
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The access token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    if claims.get("role") != "authenticated" or not claims.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The access token is not a valid user session.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_email = str(claims.get("email") or "").strip().casefold()
    admin_email = settings.scout_admin_email.strip().casefold()
    if not token_email or token_email != admin_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not authorised to use Scout.",
        )

    return claims
