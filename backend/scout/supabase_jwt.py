from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    InvalidTokenError,
    PyJWKClientConnectionError,
    PyJWKClientError,
)
from starlette.concurrency import run_in_threadpool

from scout.application.supabase_legacy_auth import (
    AuthenticationServiceUnavailable,
    verify_legacy_access_token,
)


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)


def verify_asymmetric_access_token(
    token: str,
    supabase_url: str,
) -> dict[str, Any]:
    issuer = f"{supabase_url.rstrip('/')}/auth/v1"
    jwks_url = f"{issuer}/.well-known/jwks.json"
    try:
        signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
    except PyJWKClientConnectionError as error:
        raise AuthenticationServiceUnavailable from error
    except PyJWKClientError as error:
        raise InvalidTokenError("No trusted signing key matches this token.") from error

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256"],
        audience="authenticated",
        issuer=issuer,
        options={"require": ["exp", "iat", "sub"]},
    )


async def verify_supabase_access_token(
    token: str,
    supabase_url: str,
    publishable_key: str,
) -> dict[str, Any]:
    algorithm = jwt.get_unverified_header(token).get("alg")
    if algorithm == "HS256":
        return await verify_legacy_access_token(
            token, supabase_url, publishable_key
        )
    if algorithm not in {"ES256", "RS256"}:
        raise InvalidTokenError("Unsupported access token algorithm.")
    return await run_in_threadpool(
        verify_asymmetric_access_token, token, supabase_url
    )
