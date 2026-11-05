import asyncio

import jwt
import pytest
from jwt.exceptions import InvalidTokenError

from scout.supabase_jwt import verify_supabase_access_token


def test_legacy_hs256_token_uses_auth_user_endpoint(monkeypatch) -> None:
    token = jwt.encode(
        {"sub": "user"},
        "test-secret-that-is-long-enough-for-hmac-signing-keys",
        algorithm="HS256",
    )

    async def verify_legacy(received_token, supabase_url, publishable_key):
        assert received_token == token
        assert supabase_url == "https://scout.supabase.co"
        assert publishable_key == "publishable-key"
        return {"sub": "user"}

    monkeypatch.setattr("scout.supabase_jwt.verify_legacy_access_token", verify_legacy)
    claims = asyncio.run(
        verify_supabase_access_token(
            token, "https://scout.supabase.co", "publishable-key"
        )
    )
    assert claims == {"sub": "user"}


def test_unsupported_jwt_algorithm_is_rejected() -> None:
    token = jwt.encode(
        {"sub": "user"},
        "test-secret-that-is-long-enough-for-hmac-signing-keys",
        algorithm="HS384",
    )
    with pytest.raises(InvalidTokenError, match="Unsupported"):
        asyncio.run(
            verify_supabase_access_token(
                token, "https://scout.supabase.co", "publishable-key"
            )
        )
