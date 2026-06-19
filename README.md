# AI Eval Project — version 1

A small API-based AI evaluation project for a manual QA engineer who is starting Python automation.

## What this version checks

- Factuality using required and forbidden phrases
- Instruction following
- Basic safety behavior
- Empty responses
- Response length
- Response latency
- Overall pass rate

Test cases are stored in `test_cases/test_cases.json`. You can add a new test without changing Python code.

## Project structure

```text
ai-eval-level-1/
├── config.py
├── evaluators.py
├── model_client.py
├── run_evals.py
├── test_cases/test_cases.json
├── tests/test_evaluators.py
├── reports/
├── .env.example
└── requirements.txt
```

## Run in PyCharm

1. Open the project folder in PyCharm.
2. Create a virtual environment with Python 3.11 or newer.
3. Open the PyCharm terminal and run:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. Add your OpenRouter API key to `.env`.
6. Run without API costs first:

```bash
python run_evals.py --mock
```

7. Run against the configured OpenRouter model:

```bash
python run_evals.py
```

8. Run unit tests:

```bash
pytest -v
```

## Add a new test

Add another object to `test_cases/test_cases.json`:

```json
{
  "id": "NEW-001",
  "name": "My new test",
  "category": "instruction_following",
  "prompt": "Reply with exactly: READY",
  "temperature": 0.0,
  "checks": [
    {"type": "exact_match", "value": "READY"},
    {"type": "latency_under_seconds", "value": 20}
  ]
}
```

Available checks:

- `non_empty`
- `contains_all`
- `contains_any`
- `forbidden_absent`
- `exact_match`
- `max_words`
- `latency_under_seconds`

## Important limitation

Keyword checks are transparent and easy to debug, but they cannot reliably judge meaning. 