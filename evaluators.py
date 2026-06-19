from __future__ import annotations

from typing import Any

from model_client import ModelResponse


def evaluate_check(response: ModelResponse, check: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one rule from a JSON test case."""

    check_type = check["type"]
    response_lower = response.text.lower()

    if check_type == "non_empty":
        passed = bool(response.text.strip())
        details = "Response is not empty."

    elif check_type == "contains_all":
        values = [value.lower() for value in check["values"]]
        missing = [value for value in values if value not in response_lower]
        passed = not missing
        details = "All required phrases are present." if passed else f"Missing: {missing}"

    elif check_type == "contains_any":
        values = [value.lower() for value in check["values"]]
        passed = any(value in response_lower for value in values)
        details = "At least one expected phrase is present."

    elif check_type == "forbidden_absent":
        values = [value.lower() for value in check["values"]]
        found = [value for value in values if value in response_lower]
        passed = not found
        details = "No forbidden phrases were found." if passed else f"Found: {found}"

    elif check_type == "exact_match":
        expected = check["value"].strip().lower()
        passed = response.text.strip().lower() == expected
        details = f"Expected exact value: {check['value']}"

    elif check_type == "max_words":
        word_count = len(response.text.split())
        passed = word_count <= int(check["value"])
        details = f"Word count: {word_count}"

    elif check_type == "latency_under_seconds":
        limit = float(check["value"])
        passed = response.latency_seconds <= limit
        details = f"Latency: {response.latency_seconds:.2f}s; limit: {limit:.2f}s"

    else:
        passed = False
        details = f"Unknown check type: {check_type}"

    return {
        "type": check_type,
        "passed": passed,
        "details": details,
    }


def evaluate_response(
    response: ModelResponse,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run all configured checks and return one test result."""

    check_results = [evaluate_check(response, check) for check in checks]
    passed = all(result["passed"] for result in check_results)

    return {
        "passed": passed,
        "checks": check_results,
    }
