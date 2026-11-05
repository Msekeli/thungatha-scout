from scout.settings import Settings

from admin_authentication_test_client import create_test_client


def test_admin_endpoint_accepts_configured_administrator(monkeypatch) -> None:
    async def verified_claims(*args):
        return {
            "sub": "user-123", "email": "ADMIN@example.com",
            "role": "authenticated",
        }

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token", verified_claims
    )
    settings = Settings(
        scout_supabase_url="https://scout.supabase.co",
        scout_supabase_publishable_key="public-key",
        scout_admin_email="admin@example.com",
    )
    response = create_test_client(settings).get(
        "/protected", headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 200
    assert response.json() == {"subject": "user-123"}


def test_admin_endpoint_rejects_other_authenticated_users(monkeypatch) -> None:
    async def verified_claims(*args):
        return {
            "sub": "user-456", "email": "someone@example.com",
            "role": "authenticated",
        }

    monkeypatch.setattr(
        "scout.authentication.verify_supabase_access_token", verified_claims
    )
    settings = Settings(
        scout_supabase_url="https://scout.supabase.co",
        scout_supabase_publishable_key="public-key",
        scout_admin_email="admin@example.com",
    )
    response = create_test_client(settings).get(
        "/protected", headers={"Authorization": "Bearer valid-token"}
    )
    assert response.status_code == 403
