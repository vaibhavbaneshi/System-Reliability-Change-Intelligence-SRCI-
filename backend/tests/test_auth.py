import hashlib

from app.auth.config import AuthContext, DEFAULT_TENANT_ID
from app.auth.keys import hash_api_key, key_prefix


def test_hash_api_key_deterministic():
    h1 = hash_api_key("srci_demo_key")
    h2 = hash_api_key("srci_demo_key")
    assert h1 == h2
    assert len(h1) == 64


def test_key_prefix():
    assert key_prefix("srci_demo_key") == "srci_demo_ke"


def test_auth_context_admin():
    ctx = AuthContext(tenant_id=DEFAULT_TENANT_ID, role="admin")
    assert ctx.is_admin is True


def test_auth_context_analyst_not_admin():
    ctx = AuthContext(tenant_id=DEFAULT_TENANT_ID, role="analyst")
    assert ctx.is_admin is False


def test_demo_key_hash_matches_migration():
    expected = hashlib.sha256(b"srci_demo_key").hexdigest()
    assert hash_api_key("srci_demo_key") == expected
