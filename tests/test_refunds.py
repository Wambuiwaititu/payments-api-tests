def test_full_refund_restores_balances(client, transfer):
    tid = transfer("40.00").json()["id"]
    r = client.post(f"/transfers/{tid}/refunds", json={})
    assert r.status_code == 201 and r.json()["status"] == "refunded"
    assert client.get("/accounts/ACC-001").json()["balance"] == "1000.00"


def test_partial_refunds_then_over_refund_rejected(client, transfer):
    tid = transfer("40.00").json()["id"]
    assert client.post(f"/transfers/{tid}/refunds", json={"amount": "15.00"}).json()["status"] == "partially_refunded"
    assert client.post(f"/transfers/{tid}/refunds", json={"amount": "30.00"}).status_code == 422
    assert client.post(f"/transfers/{tid}/refunds", json={"amount": "25.00"}).json()["status"] == "refunded"


def test_refund_unknown_transfer(client):
    assert client.post("/transfers/TRF-nope/refunds", json={}).status_code == 404


def test_refund_negative_amount_rejected(client, transfer):
    tid = transfer("10.00").json()["id"]
    assert client.post(f"/transfers/{tid}/refunds", json={"amount": "-1"}).status_code == 422
