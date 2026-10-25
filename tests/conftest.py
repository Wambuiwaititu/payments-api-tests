import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app, reset_state


@pytest.fixture
def client():
    reset_state()
    return TestClient(app)


@pytest.fixture
def key():
    return str(uuid.uuid4())


@pytest.fixture
def transfer(client, key):
    def _make(amount="100.00", source="ACC-001", destination="ACC-002", currency="USD", k=None):
        return client.post("/transfers", headers={"Idempotency-Key": k or str(uuid.uuid4())},
                           json={"source": source, "destination": destination,
                                 "amount": amount, "currency": currency})
    return _make
