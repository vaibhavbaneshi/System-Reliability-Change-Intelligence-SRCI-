from app.git.service_mapper import infer_services_from_commit_message, map_files_to_services


def test_map_files_to_services_by_path():
    services = ["auth-service", "billing-service", "notification-service"]
    files = ["auth-service/src/main.py", "docs/readme.md"]
    assert map_files_to_services(files, services) == ["auth-service"]


def test_map_files_nested_path():
    services = ["payment-service"]
    assert map_files_to_services(["apps/payment-service/handler.go"], services) == ["payment-service"]


def test_infer_from_commit_message():
    services = ["auth-service", "billing-service"]
    msg = "fix(auth-service): token validation"
    assert "auth-service" in infer_services_from_commit_message(msg, services)


def test_merge_recommendation_helper():
    from app.git.sync import _merge_recommendation

    assert _merge_recommendation("high") == "review_required"
    assert _merge_recommendation("low") == "approve"
