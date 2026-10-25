def test_same_key_same_payload_returns_same_transfer_once(client, transfer):
    first = transfer("100.00", k="key-1")
    second = transfer("100.00", k="key-1")
    assert first.json()["id"] == second.json()["id"]
    # money moved only once
    assert client.get("/accounts/ACC-001").json()["balance"] == "900.00"


def test_same_key_different_payload_conflicts(transfer):
    transfer("100.00", k="key-2")
    assert transfer("200.00", k="key-2").status_code == 409


def test_failed_request_does_not_consume_key(transfer):
    assert transfer("5000.00", k="key-3").status_code == 402
    assert transfer("10.00", k="key-3").status_code == 201
