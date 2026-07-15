from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIRECTORY, TEST_CASES_FILE
from evaluators import evaluate_response
from model_client import FakeModelClient, OpenRouterClient


def load_test_cases(json_file_path):
    with open(json_file_path, "r") as file:
        test_cases = json.load(file)
    return test_cases

def prepare_checks_text(check_results):
    # Prepare failed checks and all checks as readable text

    failed_checks = []
    all_checks = []

    for check in check_results:
        check_type = check["type"]
        check_passed = check["passed"]
        check_details = check["details"]

        if check_passed:
            check_status = "PASSED"
        else:
            check_status = "FAILED"

        check_text = check_status + ": " + check_type + " - " + check_details
        all_checks.append(check_text)

        if not check_passed:
            failed_checks.append(check_text)

    return failed_checks, all_checks


def create_review_note(passed, failed_checks):
    """Create a simple QA note to explain what to do with the result."""

    if passed:
        return "Passed. No action needed."

    failed_checks_text = " ".join(failed_checks).lower()

    if "expected phrases" in failed_checks_text:
        return "Possible evaluator issue. Response may be correct, but expected phrases should be reviewed."

    if "forbidden" in failed_checks_text:
        return "Possible model issue. Response may contain forbidden content."

    if "json" in failed_checks_text:
        return "Possible format issue. Check JSON format and required fields."

    if "latency" in failed_checks_text:
        return "Performance issue. Response time is higher than expected."

    return "Failed. Manual review needed: check prompt, response, and failed checks."

def calculate_metrics(results):
    # calculate simplified style metrics for check results

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    for result in results:
        for check in result["check_results"]:
            total_checks += 1

            if check["passed"]:
                passed_checks += 1
            else:
                failed_checks += 1

    if total_checks > 0:
        accuracy = passed_checks / total_checks
    else:
        accuracy = 0

    metrics = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "accuracy": round(accuracy, 3),
        "accuracy_percent": round(accuracy * 100, 1),
    }

    return metrics

def save_reports(results):
    reports_directory = Path(REPORTS_DIRECTORY)
    reports_directory.mkdir(exist_ok=True)

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")

    json_file_name = "report_" + timestamp + ".json"
    csv_file_name = "report_" + timestamp + ".csv"

    json_path = reports_directory / json_file_name
    csv_path = reports_directory / csv_file_name

    # Save full technical report to JSON
    with open(json_path, "w") as json_file:
        json_text = json.dumps(results, indent=2, ensure_ascii=False)
        json_file.write(json_text)

    # Save readable report to CSV
    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "id",
            "name",
            "category",
            "status",
            "model",
            "latency_seconds",
            "prompt",
            "response",
            "failed_checks",
            "all_checks",
            "review_note"
        ])

        for result in results:
            if result["passed"]:
                status = "PASSED"
            else:
                status = "FAILED"

            failed_checks, all_checks = prepare_checks_text(result["check_results"])

            review_note = create_review_note(
                result["passed"],
                failed_checks
            )

            writer.writerow([
                result["id"],
                result["name"],
                result["category"],
                status,
                result["model"],
                result["latency_seconds"],
                result["prompt"],
                result["response"],
                " | ".join(failed_checks),
                " | ".join(all_checks),
                review_note
            ])

    return json_path, csv_path

def run(mock=False):
    # Run all AI evaluation tests and return an exit code.

    # Choose which model client to use
    if mock:
        client = FakeModelClient()
    else:
        client = OpenRouterClient()

    # Load test cases from the JSON file
    test_cases = load_test_cases(TEST_CASES_FILE)

    # This list will contain the results of all tests
    results = []

    number_of_tests = len(test_cases)

    print(f"Running {number_of_tests} AI evaluation tests...")

    # Run every test case
    for test_case in test_cases:
        test_id = test_case["id"]
        test_name = test_case["name"]
        prompt = test_case["prompt"]
        checks = test_case["checks"]

        # Get temperature from the test case.
        # If temperature is missing, use 0.0.
        temperature = test_case.get("temperature", 0.0)
        temperature = float(temperature)

        print(f"\n{test_id} - {test_name}")

        # Send the prompt to the model
        response = client.ask(
            prompt=prompt,
            temperature=temperature,
        )

        # Check whether the model response meets the test requirements
        evaluation = evaluate_response(
            response,
            checks,
        )

        # Create a dictionary with information about the test result
        result = {
            "id": test_id,
            "name": test_name,
            "category": test_case["category"],
            "prompt": prompt,
            "response": response.text,
            "model": response.model,
            "latency_seconds": round(response.latency_seconds, 3),
            "passed": evaluation["passed"],
            "check_results": evaluation["check_results"],
        }

        # Add the current result to the list of all results
        results.append(result)

        if result["passed"]:
            status = "PASSED"
        else:
            status = "FAILED"

        print(f"Result: {status}")
        print(f"Response: {response.text}")

    # Count passed tests
    passed_count = 0

    for result in results:
        if result["passed"]:
            passed_count += 1

    # Calculate the percentage of passed tests
    if len(results) > 0:
        pass_rate = passed_count / len(results) * 100
    else:
        pass_rate = 0

    # Save test results to JSON and CSV files
    json_path, csv_path = save_reports(results)

    # Print the final summary
    print("\n=== Summary ===")
    print(f"Test cases passed: {passed_count}/{len(results)}")
    print(f"Test case pass rate: {pass_rate:.1f}%")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")

    metrics = calculate_metrics(results)
    print("\n=== Metrics ===")
    print(f"Total checks: {metrics['total_checks']}")
    print(f"Passed checks: {metrics['passed_checks']}")
    print(f"Failed checks: {metrics['failed_checks']}")
    print(f"Accuracy: {metrics['accuracy_percent']}%")

    # Return 0 if all tests passed.
    # Return 1 if at least one test failed.
    if passed_count == len(results):
        return 0
    else:
        return 1

def parse_arguments():
    """Read arguments entered in the terminal."""

    # Create an object that reads terminal arguments
    parser = argparse.ArgumentParser(
        description="Run beginner AI evaluation tests."
    )

    # Add the optional --mock argument
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use fake model responses instead of the real API.",
    )

    # Read the arguments entered by the user
    arguments = parser.parse_args()

    return arguments


# Run this code only when this file is started directly
if __name__ == "__main__":

    # Read terminal arguments
    arguments = parse_arguments()

    # Run tests
    exit_code = run(mock=arguments.mock)

    # Finish the program with exit code 0 or 1
    raise SystemExit(exit_code)