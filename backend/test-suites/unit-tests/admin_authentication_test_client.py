from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from scout.authentication import require_admin
from scout.settings import Settings, get_settings


def create_test_client(settings: Settings) -> TestClient:
    app = FastAPI()
    app.dependency_overrides[get_settings] = lambda: settings

    def protected(claims: dict = Depends(require_admin)) -> dict[str, str]:
        return {"subject": claims["sub"]}

    app.add_api_route("/protected", protected)
    return TestClient(app)
