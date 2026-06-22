from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from config import REPORTS_DIRECTORY, TEST_CASES_FILE
from evaluators import evaluate_response
from model_client import FakeModelClient, OpenRouterClient


def load_test_cases(json_file_path):
    with open(json_file_path, "r") as file:
        test_cases = json.load(file)
    return test_cases

def save_reports(results):
    reports_directory = Path(REPORTS_DIRECTORY)
    reports_directory.mkdir(exist_ok=True)
    current_time = datetime.now()
    # convert the date and time to the text
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")

    # Create file names
    json_file_name = "report_" + timestamp + ".json"
    csv_file_name = "report_" + timestamp + ".csv"

    json_path = reports_directory / json_file_name
    csv_path = reports_directory / csv_file_name

    # Convert Python results to JSON text
    json_text = json.dumps(
        results,
        ensure_ascii=False,
        indent=2
    )

    with open(json_path,"w") as json_file:
        json_file.write(json_text)

    with open(csv_path,"w", newline="") as csv_file:
        columns = ["id", "category", "passed", "latency_seconds", "model"]

        writer = csv.DictWriter(csv_file, fieldnames=columns)
        for result in results:
            csv_row={
                "id": result["id"],
                "category": result["category"],
                "passed": result["passed"],
                "latency_seconds": result["latency_seconds"],
                "model": result["model"]
            }

            writer.writerow(csv_row)

    return json_path, csv_path


def run(mock: bool = False) -> int:
    """Execute all JSON test cases and return a process exit code."""

    client = FakeModelClient() if mock else OpenRouterClient()
    test_cases = load_test_cases(TEST_CASES_FILE)
    results: list[dict[str, Any]] = []

    print(f"Running {len(test_cases)} AI evaluation tests...")

    for test_case in test_cases:
        print(f"\n{test_case['id']} - {test_case['name']}")
        response = client.ask(
            prompt=test_case["prompt"],
            temperature=float(test_case.get("temperature", 0.0)),
        )
        evaluation = evaluate_response(response, test_case["checks"])

        result = {
            "id": test_case["id"],
            "name": test_case["name"],
            "category": test_case["category"],
            "prompt": test_case["prompt"],
            "response": response.text,
            "model": response.model,
            "latency_seconds": round(response.latency_seconds, 3),
            **evaluation,
        }
        results.append(result)

        status = "PASSED" if result["passed"] else "FAILED"
        print(f"Result: {status}")
        print(f"Response: {response.text}")

    passed_count = sum(result["passed"] for result in results)
    pass_rate = passed_count / len(results) * 100 if results else 0
    json_path, csv_path = save_reports(results)

    print("\n=== Summary ===")
    print(f"Passed: {passed_count}/{len(results)}")
    print(f"Pass rate: {pass_rate:.1f}%")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")

    return 0 if passed_count == len(results) else 1


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run beginner AI evaluation tests.")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run without an API key by using predictable fake responses.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_arguments()
    raise SystemExit(run(mock=arguments.mock))
