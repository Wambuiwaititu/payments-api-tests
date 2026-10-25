# Payments API Tests

A small **mock payments API** (FastAPI, in-memory) and a **pytest** suite that tests the kinds of rules that matter in fintech: balances, transfers, refunds, idempotency and input validation.

The API is a demo built only to be a test target. It is not a real payment system.

## Stack
Python 3.11+, FastAPI, pytest, FastAPI TestClient (httpx), GitHub Actions

## What is tested
| Area | Examples |
|---|---|
| Transfers | funds move correctly; insufficient funds (402) leaves balances unchanged; unknown account (404); same-account transfer rejected |
| Validation | zero, negative, 3-decimal and non-numeric amounts; unsupported currency; missing `Idempotency-Key` header |
| Idempotency | same key + same payload returns the same transfer and charges once; same key + different payload → 409; a failed request does not use up the key |
| Refunds | full refund restores balances; partial refunds; over-refund rejected; unknown transfer; negative refund amount |

## Run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
# optional: run the API locally
uvicorn app.main:app --reload   # docs at http://127.0.0.1:8000/docs
```

## Sample output
```
tests/test_idempotency.py::test_same_key_same_payload_returns_same_transfer_once PASSED
tests/test_idempotency.py::test_same_key_different_payload_conflicts PASSED
tests/test_refunds.py::test_partial_refunds_then_over_refund_rejected PASSED
tests/test_transfers.py::test_insufficient_funds_rejected_and_balances_unchanged PASSED
...
17 passed in 0.13s
```

## Project layout
```
app/main.py              mock API
tests/conftest.py        fixtures (fresh state per test, transfer helper)
tests/test_*.py          test suites
.github/workflows/       CI on every push
```
