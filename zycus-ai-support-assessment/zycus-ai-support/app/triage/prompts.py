PROMPT_VERSION = "triage-v1"


def build_prompt(ticket, matches):
    context = "\n\n".join(
        f"Document: {x['document']}\nSection: {x['section']}\n{x['excerpt']}" for x in matches
    )
    return f"""You are a technical support triage assistant.
Use only the supplied ticket and knowledge-base context.

Allowed categories: Bug, Feature Request, How-To, Performance, Billing, Integration, Onboarding, Data Loss.
Urgency: P1 critical business impact/outage/data loss; P2 high impact; P3 normal support issue; P4 low impact or informational.

Return JSON only with: product_area, category, urgency, reasoning, known_issue, recommended_team, draft_response.
The draft response must not claim an action has already been performed.

Subject: {ticket.get('subject','')}
Body: {ticket.get('body','')}
Product from input: {ticket.get('product','')}

Knowledge base:
{context}
"""
