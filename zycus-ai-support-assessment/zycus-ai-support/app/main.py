from fastapi import FastAPI
from app.schemas import TicketInput, TriageResult, AccountHealthRequest, AccountHealthResult
from app.triage.pipeline import triage_ticket
from app.tam.pipeline import generate_account_health

app = FastAPI(title="AI Support and TAM Assistant", version="1.0.0")

@app.get("/")
def root():
    return {"service": "AI Support and TAM Assistant", "status": "ok"}

@app.post("/triage", response_model=TriageResult)
def triage(request: TicketInput):
    return triage_ticket(request.model_dump())

@app.post("/account-health", response_model=AccountHealthResult)
def account_health(request: AccountHealthRequest):
    return generate_account_health(request.account_id)
