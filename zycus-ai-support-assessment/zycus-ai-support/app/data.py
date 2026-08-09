import json
from datetime import datetime, timedelta, timezone
from app.config import DATA_DIR


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tickets():
    return load_json(DATA_DIR / "tickets.json")


def load_accounts():
    return load_json(DATA_DIR / "accounts.json")


def get_account(account_id):
    return next((x for x in load_accounts() if x.get("account_id") == account_id), None)


def get_account_tickets(account_id, days=90):
    all_tickets = load_tickets()
    dates = []
    for item in all_tickets:
        try:
            dates.append(datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")))
        except (KeyError, ValueError):
            pass
    reference = max(dates) if dates else datetime.now(timezone.utc)
    cutoff = reference - timedelta(days=days)
    result = []
    for ticket in all_tickets:
        if ticket.get("account_id") != account_id:
            continue
        try:
            created = datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        if created >= cutoff:
            result.append(ticket)
    return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)
