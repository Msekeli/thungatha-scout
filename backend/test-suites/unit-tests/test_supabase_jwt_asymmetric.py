from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.exceptions import InvalidIssuerError

from scout.supabase_jwt import verify_asymmetric_access_token


def signed_token(private_key, issuer: str) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": "user-123",
            "email": "admin@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "iss": issuer,
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        private_key,
        algorithm="ES256",
    )


def install_fake_jwks(monkeypatch, private_key, token: str) -> None:
    class FakeJwksClient:
        def get_signing_key_from_jwt(self, received_token):
            assert received_token == token
            return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setattr("scout.supabase_jwt._jwks_client", lambda url: FakeJwksClient())


def test_asymmetric_token_validates_signature_and_project_claims(monkeypatch) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    token = signed_token(private_key, "https://scout.supabase.co/auth/v1")
    install_fake_jwks(monkeypatch, private_key, token)

    claims = verify_asymmetric_access_token(token, "https://scout.supabase.co")

    assert claims["sub"] == "user-123"
    assert claims["email"] == "admin@example.com"
    assert claims["role"] == "authenticated"


def test_asymmetric_token_rejects_wrong_issuer(monkeypatch) -> None:
    private_key = ec.generate_private_key(ec.SECP256R1())
    token = signed_token(private_key, "https://wrong-project.supabase.co/auth/v1")
    install_fake_jwks(monkeypatch, private_key, token)

    with pytest.raises(InvalidIssuerError):
        verify_asymmetric_access_token(token, "https://scout.supabase.co")
