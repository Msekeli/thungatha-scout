import pytest

from scout.authentication import require_admin
from scout.main import app


@pytest.fixture(autouse=True)
def allow_admin_in_api_tests():
    app.dependency_overrides[require_admin] = lambda: {
        "sub": "test-administrator",
        "email": "admin@example.com",
    }
    yield
    app.dependency_overrides.pop(require_admin, None)
