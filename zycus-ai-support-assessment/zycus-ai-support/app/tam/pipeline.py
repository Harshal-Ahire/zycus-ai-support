from app.data import get_account, get_account_tickets
from app.llm import llm
from app.schemas import AccountHealthResult, RiskFlag
from app.tam.prompts import build_prompt


def detect_risks(account, tickets):
    risks = []
    health = account.get("health_status")
    if health in {"At Risk", "Churning"}:
        risks.append({"severity": "high" if health == "Churning" else "medium", "reason": f"Account health is {health}."})
    if account.get("usage_trend") in {"Declining", "Inactive"}:
        risks.append({"severity": "medium", "reason": f"Usage trend is {account.get('usage_trend')}."})
    if account.get("p1_tickets_last_30d", 0) > 0:
        risks.append({"severity": "high", "reason": f"There are {account['p1_tickets_last_30d']} P1 ticket(s) in the last 30 days."})
    for note in account.get("escalation_notes", []) or []:
        if any(x in note.lower() for x in ["competing vendor", "negative sentiment", "churn", "escalat"]):
            risks.append({"severity": "high", "reason": note})

    words = ["considering alternatives", "competing vendor", "unacceptable", "cancel", "churn", "executive escalation", "board presentation", "critical", "blocked"]
    for ticket in tickets:
        body = ticket.get("body", "")
        if any(x in body.lower() for x in words):
            lines = [x.strip() for x in body.splitlines() if x.strip()]
            risks.append({
                "severity": "high" if ticket.get("urgency") == "P1" else "medium",
                "reason": "The ticket contains an escalation or business-impact signal.",
                "ticket_id": ticket.get("ticket_id"), "quote": (lines[0] if lines else body[:300])[:400]
            })
    return risks[:10]


def fallback(account, tickets, risks):
    summary = (
        f"{account['company']} is on the {account.get('plan_tier')} plan with {account.get('seats_active')} active seats. "
        f"The account is currently {account.get('health_status')} with a {account.get('usage_trend')} usage trend. "
        f"There are {len(tickets)} tickets from the last 90 days."
    )
    points = [
        f"Review account health: {account.get('health_status')}.",
        f"Review support activity from the last 90 days: {len(tickets)} ticket(s).",
        f"Discuss renewal date: {account.get('renewal_date')}.",
    ]
    return AccountHealthResult(account_id=account["account_id"], company=account["company"], executive_summary=summary,
        open_risks=[RiskFlag(**x) for x in risks], talking_points=points,
        ticket_count_last_90_days=len(tickets), account_found=True)


def generate_account_health(account_id):
    account = get_account(account_id)
    if not account:
        return AccountHealthResult(account_id=account_id, company="Unknown",
            executive_summary="The account ID was not found in accounts.json.",
            open_risks=[RiskFlag(severity="low", reason="No matching account record was found.")],
            talking_points=["Confirm the account ID before the QBR."], ticket_count_last_90_days=0, account_found=False)

    tickets = get_account_tickets(account_id, 90)
    risks = detect_risks(account, tickets)
    if not llm.available:
        return fallback(account, tickets, risks)
    try:
        raw = llm.json(build_prompt(account, tickets, risks))
        return AccountHealthResult(account_id=account_id, company=account["company"],
            executive_summary=str(raw.get("executive_summary", "")),
            open_risks=[RiskFlag(**x) for x in raw.get("open_risks", [])],
            talking_points=[str(x) for x in raw.get("talking_points", [])],
            ticket_count_last_90_days=len(tickets), account_found=True)
    except Exception:
        return fallback(account, tickets, risks)
