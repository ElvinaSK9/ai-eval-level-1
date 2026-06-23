from __future__ import annotations

from typing import Any

from model_client import ModelResponse

def evaluate_check(response, check):
    """Check one rule for the model response."""

    # Get the check type from the test case
    check_type = check["type"]

    # Get the model response text
    response_text = response.text

    # Convert the response to lowercase
    # This allows us to compare words without considering capital letters
    response_lower = response_text.lower()

    # Check that the response is not empty
    if check_type == "non_empty":
        cleaned_response = response_text.strip()

        if cleaned_response != "":
            passed = True
            details = "Response is not empty."
        else:
            passed = False
            details = "Response is empty."

    # Check that the response contains all required phrases
    elif check_type == "contains_all":
        required_values = check["values"]
        missing_values = []

        for value in required_values:
            value_lower = value.lower()

            if value_lower not in response_lower:
                missing_values.append(value)

        if len(missing_values) == 0:
            passed = True
            details = "All required phrases are present."
        else:
            passed = False
            details = f"Missing phrases: {missing_values}"

    # Check that the response contains at least one expected phrase
    elif check_type == "contains_any":
        expected_values = check["values"]
        found_values = []

        for value in expected_values:
            value_lower = value.lower()

            if value_lower in response_lower:
                found_values.append(value)

        if len(found_values) > 0:
            passed = True
            details = f"Found expected phrases: {found_values}"
        else:
            passed = False
            details = f"No expected phrases were found: {expected_values}"

    # Check that forbidden phrases are absent
    elif check_type == "forbidden_absent":
        forbidden_values = check["values"]
        found_forbidden_values = []

        for value in forbidden_values:
            value_lower = value.lower()

            if value_lower in response_lower:
                found_forbidden_values.append(value)

        if len(found_forbidden_values) == 0:
            passed = True
            details = "No forbidden phrases were found."
        else:
            passed = False
            details = f"Found forbidden phrases: {found_forbidden_values}"

    # Check that the whole response exactly matches the expected value
    elif check_type == "exact_match":
        expected_value = check["value"]

        cleaned_expected = expected_value.strip().lower()
        cleaned_response = response_text.strip().lower()

        if cleaned_response == cleaned_expected:
            passed = True
            details = "Response exactly matches the expected value."
        else:
            passed = False
            details = (
                f"Expected: '{expected_value}'. "
                f"Actual: '{response_text}'."
            )

    # Check that the response does not contain too many words
    elif check_type == "max_words":
        words = response_text.split()
        word_count = len(words)

        maximum_words = int(check["value"])

        if word_count <= maximum_words:
            passed = True
            details = (
                f"Word count is {word_count}. "
                f"Maximum allowed is {maximum_words}."
            )
        else:
            passed = False
            details = (
                f"Word count is {word_count}. "
                f"Maximum allowed is {maximum_words}."
            )

    # Check that the model responded fast enough
    elif check_type == "latency_under_seconds":
        latency = response.latency_seconds
        time_limit = float(check["value"])

        if latency <= time_limit:
            passed = True
            details = (
                f"Latency is {latency:.2f} seconds. "
                f"Limit is {time_limit:.2f} seconds."
            )
        else:
            passed = False
            details = (
                f"Latency is {latency:.2f} seconds. "
                f"Limit is {time_limit:.2f} seconds."
            )

    # This block runs when the check type is unknown
    else:
        passed = False
        details = f"Unknown check type: {check_type}"

    # Return the result of the check
    result = {
        "type": check_type,
        "passed": passed,
        "details": details,
    }

    return result

def evaluate_response(response,checks):
    """Run all configured checks and return one test result."""

    check_results = [evaluate_check(response, check) for check in checks]
    passed = all(result["passed"] for result in check_results)

    return {
        "passed": passed,
        "check_results": check_results,
    }
