from app.auth.rbac import role_allows, Role


def test_viewer_can_read():
    assert role_allows(Role.VIEWER, "GET", "/incidents")
    assert not role_allows(Role.VIEWER, "POST", "/incidents/ingest")


def test_analyst_can_ingest():
    assert role_allows(Role.ANALYST, "POST", "/incidents/ingest")
    assert role_allows(Role.ANALYST, "POST", "/incidents/abc/run-rca")


def test_admin_can_everything():
    assert role_allows(Role.ADMIN, "POST", "/autonomy/start")
    assert role_allows(Role.ADMIN, "DELETE", "/anything")


def test_viewer_cannot_train():
    assert not role_allows(Role.VIEWER, "POST", "/train")
