import pytest


def balance(client, acc):
    return client.get(f"/accounts/{acc}").json()["balance"]


def test_successful_transfer_moves_funds(client, transfer):
    r = transfer("100.00")
    assert r.status_code == 201
    assert r.json()["status"] == "completed"
    assert balance(client, "ACC-001") == "900.00"
    assert balance(client, "ACC-002") == "150.00"


def test_insufficient_funds_rejected_and_balances_unchanged(client, transfer):
    r = transfer("5000.00")
    assert r.status_code == 402
    assert balance(client, "ACC-001") == "1000.00"


def test_unknown_account_returns_404(client, transfer):
    assert transfer(destination="ACC-999").status_code == 404


def test_same_account_transfer_rejected(client, transfer):
    assert transfer(destination="ACC-001").status_code == 422


def test_unsupported_currency(client, transfer):
    assert transfer(currency="XYZ").status_code == 422


@pytest.mark.parametrize("amount", ["0", "-10.00", "10.555", "abc"])
def test_invalid_amounts_rejected(transfer, amount):
    assert transfer(amount).status_code == 422


def test_missing_idempotency_key_rejected(client):
    r = client.post("/transfers", json={"source": "ACC-001", "destination": "ACC-002",
                                         "amount": "1.00", "currency": "USD"})
    assert r.status_code == 422
