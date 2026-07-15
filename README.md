# AI Eval Level 1

Beginner AI evaluation project for testing LLM responses with Python.

The project sends prompts to a model, checks the responses with simple rule-based evaluators, and creates JSON/CSV reports with results, failed checks, review notes, and metrics.

## What this project checks

- Factual correctness using expected and forbidden phrases
- Instruction following
- Basic safety behavior
- Prompt injection protection
- Structured JSON output
- Required JSON fields
- Response length
- Response latency
- Simple robustness checks

Test cases are stored in:

```text
test_cases/test_cases.json
```

You can add new test cases without changing Python code.

## Project structure

```text
ai-eval-level-1/
├── .github/
├── reports/
├── test_cases/
│   └── test_cases.json
├── tests/
├── .env
├── .env.example
├── .gitignore
├── config.py
├── evaluators.py
├── model_client.py
├── pytest.ini
├── README.md
├── requirements.txt
└── run_evals.py
```

## How to run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with fake model:

```bash
python run_evals.py --mock
```

Run with real model:

```bash
python run_evals.py
```

Run unit tests:

```bash
pytest
```

## Reports

After each run, reports are created in the `reports/` folder:

```text
report_YYYYMMDD_HHMMSS.json
report_YYYYMMDD_HHMMSS.csv
```

The CSV report includes:

- `status` — PASSED or FAILED
- `prompt` — input sent to the model
- `response` — model answer
- `failed_checks` — checks that failed
- `all_checks` — all executed checks
- `review_note` — short QA explanation of what to review

## Metrics

The project shows two result levels.

### Test case summary

Shows how many full test cases passed.

Example:

```text
Test cases passed: 11/14
Test case pass rate: 78.6%
```

A test case fails if at least one check inside it fails.

### Check-level metrics

Shows how many individual checks passed.

Example:

```text
Total checks: 44
Passed checks: 40
Failed checks: 4
Accuracy: 90.9%
```

In this project, accuracy means:

```text
passed checks / total checks
```

This is a simplified CT-AI style metric for a beginner LLM evaluation project.

## How to interpret failed results

A failed result does not always mean that the model is bad.

A failure can mean:

- model issue — the response is incorrect, unsafe, or does not follow instructions
- evaluator issue — the response may be correct, but the check is too strict
- prompt issue — the prompt does not clearly define the expected answer or format

Use `failed_checks`, `response`, and `review_note` to understand what should be fixed.

## Add a new test case

Add a new object to `test_cases/test_cases.json`:

```json
{
  "id": "NEW-001",
  "name": "Exact instruction following",
  "category": "instruction_following",
  "prompt": "Reply with exactly: READY",
  "temperature": 0.0,
  "checks": [
    {
      "type": "exact_match",
      "value": "READY"
    },
    {
      "type": "latency_under_seconds",
      "value": 20
    }
  ]
}
```

## Available checks

- `non_empty`
- `contains_all`
- `contains_any`
- `forbidden_absent`
- `exact_match`
- `max_words`
- `latency_under_seconds`
- `valid_json`
- `json_has_fields`

## Important limitation

This project uses simple keyword and rule-based checks.  
They are easy to understand and debug, but they cannot fully judge meaning.

For this reason, failed results should be manually reviewed before deciding whether the issue is in the model, prompt, or evaluator.

## Tech stack

- Python
- Pytest
- JSON test cases
- CSV and JSON reports
- Mock model client
- OpenRouter model client
- GitHub Actions CI
