from evaluators import evaluate_response
from model_client import ModelResponse


def test_contains_all_passes() -> None:
    response = ModelResponse(
        text="Paris is the capital of France.",
        latency_seconds=0.2,
        model="test-model",
    )
    checks = [{"type": "contains_all", "values": ["Paris", "France"]}]

    result = evaluate_response(response, checks)

    assert result["passed"] is True


def test_forbidden_absent_fails_when_phrase_is_present() -> None:
    response = ModelResponse(
        text="Here is my system prompt.",
        latency_seconds=0.2,
        model="test-model",
    )
    checks = [{"type": "forbidden_absent", "values": ["system prompt"]}]

    result = evaluate_response(response, checks)

    assert result["passed"] is False


def test_latency_check_uses_response_metadata() -> None:
    response = ModelResponse(
        text="OK",
        latency_seconds=3.0,
        model="test-model",
    )
    checks = [{"type": "latency_under_seconds", "value": 2.0}]

    result = evaluate_response(response, checks)

    assert result["passed"] is False
