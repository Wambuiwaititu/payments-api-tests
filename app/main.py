"""A tiny in-memory mock payments API used as a test target (demo only)."""
from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Mock Payments API")

ACCOUNTS: dict[str, Decimal] = {}
TRANSFERS: dict[str, dict] = {}
IDEMPOTENCY: dict[str, tuple[dict, dict]] = {}
SUPPORTED_CURRENCIES = {"USD", "KES", "EUR"}


def reset_state():
    ACCOUNTS.clear(); TRANSFERS.clear(); IDEMPOTENCY.clear()
    ACCOUNTS.update({"ACC-001": Decimal("1000.00"), "ACC-002": Decimal("50.00")})


reset_state()


class TransferIn(BaseModel):
    source: str
    destination: str
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)


class RefundIn(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)


@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    if account_id not in ACCOUNTS:
        raise HTTPException(404, "account not found")
    return {"id": account_id, "balance": str(ACCOUNTS[account_id])}


@app.post("/transfers", status_code=201)
def create_transfer(body: TransferIn, idempotency_key: str = Header(...)):
    payload = body.model_dump(mode="json")
    if idempotency_key in IDEMPOTENCY:
        old_payload, old_result = IDEMPOTENCY[idempotency_key]
        if old_payload != payload:
            raise HTTPException(409, "idempotency key reused with different payload")
        return old_result
    if body.currency.upper() not in SUPPORTED_CURRENCIES:
        raise HTTPException(422, "unsupported currency")
    for acc in (body.source, body.destination):
        if acc not in ACCOUNTS:
            raise HTTPException(404, f"account {acc} not found")
    if body.source == body.destination:
        raise HTTPException(422, "source and destination must differ")
    if ACCOUNTS[body.source] < body.amount:
        raise HTTPException(402, "insufficient funds")
    ACCOUNTS[body.source] -= body.amount
    ACCOUNTS[body.destination] += body.amount
    tid = f"TRF-{uuid4().hex[:8]}"
    transfer = {"id": tid, **payload, "currency": body.currency.upper(),
                "status": "completed", "refunded": "0.00"}
    TRANSFERS[tid] = transfer
    IDEMPOTENCY[idempotency_key] = (payload, transfer)
    return transfer


@app.post("/transfers/{transfer_id}/refunds", status_code=201)
def refund(transfer_id: str, body: RefundIn):
    t = TRANSFERS.get(transfer_id)
    if not t:
        raise HTTPException(404, "transfer not found")
    remaining = Decimal(t["amount"]) - Decimal(t["refunded"])
    amount = body.amount if body.amount is not None else remaining
    if amount > remaining:
        raise HTTPException(422, "refund exceeds remaining amount")
    if ACCOUNTS[t["destination"]] < amount:
        raise HTTPException(402, "destination has insufficient funds for refund")
    ACCOUNTS[t["destination"]] -= amount
    ACCOUNTS[t["source"]] += amount
    t["refunded"] = str(Decimal(t["refunded"]) + amount)
    t["status"] = "refunded" if Decimal(t["refunded"]) == Decimal(t["amount"]) else "partially_refunded"
    return {"transfer_id": transfer_id, "amount": str(amount), "status": t["status"]}
