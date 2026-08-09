from app.data import load_tickets
from app.triage.pipeline import triage_ticket


def ticket(tid):
    return next(x for x in load_tickets() if x["ticket_id"] == tid)


def test_triage_required_fields():
    r = triage_ticket(ticket("TKT-10008"))
    assert r.product_area
    assert r.category in {"Bug","Feature Request","How-To","Performance","Billing","Integration","Onboarding","Data Loss"}
    assert r.urgency in {"P1","P2","P3","P4"}
    assert r.draft_response


def test_triage_retrieves_kb():
    r = triage_ticket(ticket("TKT-10175"))
    assert r.knowledge_base_matches


def test_triage_adversarial():
    r = triage_ticket({"subject":"Something is wrong","body":"It is not working and I need help."})
    assert r.category and r.urgency and r.draft_response
