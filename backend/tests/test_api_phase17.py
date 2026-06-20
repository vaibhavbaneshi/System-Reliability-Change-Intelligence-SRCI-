from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.auth.config import AuthContext, DEFAULT_TENANT_ID
from app.tenant.context import set_auth_context


def test_health_no_auth():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200


def test_auth_me_default():
    set_auth_context(
        AuthContext(tenant_id=DEFAULT_TENANT_ID, role="admin", email="test@local")
    )
    client = TestClient(app)
    res = client.get("/auth/me")
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"
    assert "tenant_id" in data


def test_login_info():
    client = TestClient(app)
    res = client.get("/auth/login")
    assert res.status_code == 200
    assert "api_key" in res.json()["methods"]


@patch("app.api.enterprise_routes.get_usage_summary")
def test_llm_usage_endpoint(mock_summary):
    mock_summary.return_value = {
        "budget_tokens": 100000,
        "used_tokens": 0,
        "remaining_tokens": 100000,
        "utilization_pct": 0,
        "by_endpoint": [],
    }
    set_auth_context(
        AuthContext(tenant_id=DEFAULT_TENANT_ID, role="viewer")
    )
    client = TestClient(app)
    res = client.get("/enterprise/llm-usage")
    assert res.status_code == 200
    assert res.json()["budget_tokens"] == 100000
