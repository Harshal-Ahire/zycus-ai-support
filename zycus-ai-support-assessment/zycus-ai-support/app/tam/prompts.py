PROMPT_VERSION = "tam-v1"


def build_prompt(account, tickets, risks):
    account_text = "\n".join(f"{k}: {v}" for k, v in account.items())
    ticket_text = "\n\n".join(
        f"Ticket {t.get('ticket_id')}: {t.get('subject')}\nProduct: {t.get('product')} | Category: {t.get('category')} | Urgency: {t.get('urgency')} | Status: {t.get('status')}\nBody: {t.get('body')}"
        for t in tickets
    ) or "No tickets found."
    return f"""You are a Technical Account Manager assistant.
Use only the supplied account and ticket data.
Return JSON only with executive_summary, open_risks, talking_points.
The executive summary must be 3 to 5 sentences.
Every ticket-based risk must include a direct quote copied from the ticket body. Do not invent quotes.

Account:
{account_text}

Last 90 days tickets:
{ticket_text}

Deterministic risk signals:
{risks}
"""
