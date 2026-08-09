from app.llm import llm, normalize_category, normalize_urgency
from app.rag import get_kb
from app.schemas import TriageResult, KBMatch

KNOWN_CODES = [
    "AUTH_TOKEN_EXPIRED", "SAML_ASSERTION_EXPIRED", "AUDIENCE_MISMATCH", "GROUP_NOT_MAPPED",
    "SESSION_INVALID", "SSO_GROUP_NOT_FOUND", "ERR_CONNECTION_TIMEOUT", "PIPELINE_STALLED",
    "RATE_LIMIT_EXCEEDED", "QUOTA_EXCEEDED", "DEPENDENCY_UNAVAILABLE", "CHECKSUM_MISMATCH",
    "INVALID_CONFIGURATION",
]


def fallback(ticket, matches):
    text = f"{ticket.get('subject','')} {ticket.get('body','')}".lower()
    if any(x in text for x in ["billing", "invoice", "price", "pricing", "upgrade"]):
        category = "Billing"
    elif any(x in text for x in ["how do i", "how to", "configure", "setup", "set up"]):
        category = "How-To"
    elif any(x in text for x in ["slow", "latency", "timeout", "timing out", "performance"]):
        category = "Performance"
    elif any(x in text for x in ["integrat", "oauth", "webhook", "snowflake", "salesforce", "bigquery"]):
        category = "Integration"
    elif any(x in text for x in ["lost", "missing", "discrepancy", "data loss"]):
        category = "Data Loss"
    elif any(x in text for x in ["new user", "new joiner", "onboarding"]):
        category = "Onboarding"
    elif any(x in text for x in ["request", "would like", "need bulk", "feature"]):
        category = "Feature Request"
    else:
        category = "Bug"

    if any(x in text for x in ["outage", "data loss", "everyone", "all users", "critical"]):
        urgency = "P1"
    elif any(x in text for x in ["blocked", "cannot", "can't", "failed", "not working", "unavailable"]):
        urgency = "P2"
    elif category in {"How-To", "Feature Request"}:
        urgency = "P4"
    else:
        urgency = "P3"

    team = "Technical Support"
    if category == "Billing": team = "Billing Support"
    if category == "Integration": team = "Integrations Support"
    if category == "Onboarding": team = "Customer Success / Onboarding"
    if category == "Data Loss": team = "Technical Support - Incident Response"

    known = bool(matches) or any(code.lower() in text for code in KNOWN_CODES)
    return TriageResult(
        product_area=ticket.get("product_area") or ticket.get("product") or "Unknown",
        category=category, urgency=urgency,
        reasoning="Fallback classification based on ticket wording and knowledge-base retrieval.",
        known_issue=known,
        knowledge_base_matches=[KBMatch(**x) for x in matches],
        recommended_team=team,
        draft_response="Thanks for contacting support. We have reviewed the reported issue and the available documentation. We will investigate it and follow up with the next troubleshooting steps.",
    )


def triage_ticket(ticket):
    matches = get_kb().search(f"{ticket.get('subject','')}\n{ticket.get('body','')}")
    if not llm.available:
        return fallback(ticket, matches)
    try:
        raw = llm.json(__import__('app.triage.prompts', fromlist=['build_prompt']).build_prompt(ticket, matches))
        return TriageResult(
            product_area=str(raw.get("product_area") or ticket.get("product_area") or ticket.get("product") or "Unknown"),
            category=normalize_category(raw.get("category")), urgency=normalize_urgency(raw.get("urgency")),
            reasoning=str(raw.get("reasoning", "")), known_issue=bool(raw.get("known_issue", bool(matches))),
            knowledge_base_matches=[KBMatch(**x) for x in matches],
            recommended_team=str(raw.get("recommended_team", "Technical Support")),
            draft_response=str(raw.get("draft_response", "Thanks for contacting support. We are reviewing the issue and will follow up with next steps.")),
        )
    except Exception:
        return fallback(ticket, matches)
