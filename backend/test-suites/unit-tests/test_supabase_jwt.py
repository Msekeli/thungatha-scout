import asyncio
from datetime import UTC

import jwt
import pytest
from jwt.exceptions import InvalidTokenError

from scout.supabase_jwt import verify_supabase_access_token


def test_legacy_hs256_token_uses_auth_user_endpoint(monkeypatch) -> None:
    token = jwt.encode({"sub": "user"}, "test-secret", algorithm="HS256")

    async def verify_legacy(received_token, supabase_url, publishable_key):
        assert received_token == token
        assert supabase_url == "https://scout.supabase.co"
        assert publishable_key == "publishable-key"
        return {"sub": "user"}

    monkeypatch.setattr(
        "scout.supabase_jwt.verify_legacy_access_token",
        verify_legacy,
    )

    claims = asyncio.run(
        verify_supabase_access_token(
            token,
            "https://scout.supabase.co",
            "publishable-key",
        )
    )

    assert claims == {"sub": "user"}


def test_asymmetric_token_is_verified_against_project_claims(monkeypatch) -> None:
    from datetime import UTC, datetime, timedelta
    from types import SimpleNamespace

    from cryptography.hazmat.primitives.asymmetric import ec

    from scout.supabase_jwt import verify_asymmetric_access_token

    private_key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "user-123",
            "email": "admin@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://scout.supabase.co/auth/v1",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="ES256",
    )

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, received_token):
            assert received_token == token
            return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setattr(
        "scout.supabase_jwt._jwks_client",
        lambda url: FakeJwksClient(),
    )

    claims = verify_asymmetric_access_token(
        token,
        "https://scout.supabase.co",
    )

    assert claims["sub"] == "user-123"
    assert claims["email"] == "admin@example.com"


def test_asymmetric_token_rejects_wrong_issuer(monkeypatch) -> None:
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    from cryptography.hazmat.primitives.asymmetric import ec
    from jwt.exceptions import InvalidIssuerError

    from scout.supabase_jwt import verify_asymmetric_access_token

    private_key = ec.generate_private_key(ec.SECP256R1())
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "user-123",
            "aud": "authenticated",
            "iss": "https://wrong-project.supabase.co/auth/v1",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="ES256",
    )

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, received_token):
            return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setattr(
        "scout.supabase_jwt._jwks_client",
        lambda url: FakeJwksClient(),
    )

    with pytest.raises(InvalidIssuerError):
        verify_asymmetric_access_token(token, "https://scout.supabase.co")


def test_unsupported_jwt_algorithm_is_rejected() -> None:
    token = jwt.encode(
        {"sub": "user"},
        "test-secret",
        algorithm="HS384",
    )

    with pytest.raises(InvalidTokenError, match="Unsupported"):
        asyncio.run(
            verify_supabase_access_token(
                token,
                "https://scout.supabase.co",
                "publishable-key",
            )
        )
