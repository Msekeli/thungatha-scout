from scout.settings import Settings

from admin_authentication_test_client import create_test_client


def test_admin_endpoint_rejects_missing_bearer_token() -> None:
    settings = Settings(
        scout_supabase_url="https://scout.supabase.co",
        scout_supabase_publishable_key="public-key",
        scout_admin_email="admin@example.com",
    )
    assert create_test_client(settings).get("/protected").status_code == 401


def test_admin_endpoint_fails_closed_when_auth_is_not_configured() -> None:
    client = create_test_client(Settings())
    response = client.get("/protected", headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 503


def test_admin_endpoint_rejects_non_bearer_authorization_header() -> None:
    settings = Settings(
        scout_supabase_url="https://scout.supabase.co",
        scout_supabase_publishable_key="public-key",
        scout_admin_email="admin@example.com",
    )
    response = create_test_client(settings).get(
        "/protected", headers={"Authorization": "Basic invalid"}
    )
    assert response.status_code == 401


def test_admin_endpoint_rejects_non_user_tokens(monkeypatch) -> None:
    async def verified_claims(*args):
        return {"sub": "service-role-id", "email": "admin@example.com"}

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token", verified_claims
    )
    settings = Settings(
        scout_supabase_url="https://scout.supabase.co",
        scout_supabase_publishable_key="public-key",
        scout_admin_email="admin@example.com",
    )
    response = create_test_client(settings).get(
        "/protected", headers={"Authorization": "Bearer service-token"}
    )
    assert response.status_code == 401
