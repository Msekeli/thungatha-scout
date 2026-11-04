from fastapi import FastAPI
from fastapi.testclient import TestClient

from scout.authentication import require_admin
from scout.settings import Settings, get_settings


def create_test_client(settings: Settings) -> TestClient:
    test_app = FastAPI()
    test_app.dependency_overrides[get_settings] = lambda: settings
    test_app.add_api_route(
        "/protected",
        lambda claims=__import__(
            "fastapi"
        ).Depends(require_admin): {"subject": claims["sub"]},
    )
    return TestClient(test_app)


def test_admin_endpoint_rejects_missing_bearer_token() -> None:
    client = create_test_client(
        Settings(
            scout_supabase_url="https://scout.supabase.co",
            scout_supabase_publishable_key="public-key",
            scout_admin_email="admin@example.com",
        )
    )

    response = client.get("/protected")

    assert response.status_code == 401


def test_admin_endpoint_fails_closed_when_auth_is_not_configured() -> None:
    client = create_test_client(Settings())

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 503


def test_admin_endpoint_accepts_configured_administrator(monkeypatch) -> None:
    async def verified_claims(*args):
        return {
            "sub": "user-123",
            "email": "ADMIN@example.com",
            "role": "authenticated",
        }

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token",
        verified_claims,
    )
    client = create_test_client(
        Settings(
            scout_supabase_url="https://scout.supabase.co",
            scout_supabase_publishable_key="public-key",
            scout_admin_email="admin@example.com",
        )
    )

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"subject": "user-123"}


def test_admin_endpoint_rejects_other_authenticated_users(monkeypatch) -> None:
    async def verified_claims(*args):
        return {
            "sub": "user-456",
            "email": "someone@example.com",
            "role": "authenticated",
        }

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token",
        verified_claims,
    )
    client = create_test_client(
        Settings(
            scout_supabase_url="https://scout.supabase.co",
            scout_supabase_publishable_key="public-key",
            scout_admin_email="admin@example.com",
        )
    )

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 403


def test_admin_endpoint_rejects_non_user_tokens(monkeypatch) -> None:
    async def verified_claims(*args):
        return {"sub": "service-role-id", "email": "admin@example.com"}

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token",
        verified_claims,
    )
    client = create_test_client(
        Settings(
            scout_supabase_url="https://scout.supabase.co",
            scout_supabase_publishable_key="public-key",
            scout_admin_email="admin@example.com",
        )
    )

    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer service-token"},
    )

    assert response.status_code == 401
