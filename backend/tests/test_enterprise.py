from unittest.mock import MagicMock, patch

from app.enterprise.llm_budget import (
    LLMBudgetExceeded,
    check_budget,
    estimate_tokens_from_response,
    get_tenant_budget,
    get_monthly_usage,
)
from app.enterprise.sla import record_sla_event, get_sla_summary
from app.auth.config import DEFAULT_TENANT_ID


def test_estimate_tokens_from_usage_object():
    response = MagicMock()
    response.usage.prompt_tokens = 100
    response.usage.completion_tokens = 50
    assert estimate_tokens_from_response(response) == (100, 50)


def test_estimate_tokens_fallback():
    response = MagicMock()
    response.usage = None
    response.choices = [MagicMock(message=MagicMock(content="hello world"))]
    prompt, completion = estimate_tokens_from_response(response)
    assert prompt == 512
    assert completion >= 1


@patch("app.enterprise.llm_budget.get_monthly_usage", return_value=999_000)
@patch("app.enterprise.llm_budget.get_tenant_budget", return_value=1_000_000)
def test_check_budget_ok(mock_budget, mock_usage):
    check_budget(DEFAULT_TENANT_ID, estimated_tokens=100)


@patch("app.enterprise.llm_budget.get_monthly_usage", return_value=999_000)
@patch("app.enterprise.llm_budget.get_tenant_budget", return_value=1_000_000)
def test_check_budget_exceeded(mock_budget, mock_usage):
    try:
        check_budget(DEFAULT_TENANT_ID, estimated_tokens=2000)
        assert False, "Should have raised"
    except LLMBudgetExceeded:
        pass


def test_sla_summary_empty_structure():
    with patch("app.enterprise.sla.get_connection") as mock_conn:
        cur = MagicMock()
        mock_conn.return_value.cursor.return_value = cur
        cur.fetchone.side_effect = [(0, 0, None, None)]
        cur.fetchall.return_value = []
        result = get_sla_summary(DEFAULT_TENANT_ID, days=7)
        assert result["compliance_rate"] == 1.0
        assert result["breaches"] == 0
