import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st
from app.data import load_accounts
from app.triage.pipeline import triage_ticket
from app.tam.pipeline import generate_account_health

st.set_page_config(page_title="AI Support Assistant", layout="wide")
st.title("AI Technical Support Assistant")

triage_tab, tam_tab = st.tabs(["Ticket Triage", "TAM Account Health"])

with triage_tab:
    subject = st.text_input("Ticket subject")
    body = st.text_area("Ticket body", height=220)
    if st.button("Analyze ticket"):
        if not body.strip():
            st.error("Enter a ticket body.")
        else:
            r = triage_ticket({"subject": subject, "body": body})
            st.write("Product area:", r.product_area)
            st.write("Category:", r.category)
            st.write("Urgency:", r.urgency)
            st.write("Reasoning:", r.reasoning)
            st.write("Known issue:", r.known_issue)
            st.write("Recommended team:", r.recommended_team)
            st.subheader("Knowledge base matches")
            for m in r.knowledge_base_matches:
                st.write(f"{m.document} — {m.section} ({m.relevance})")
                st.caption(m.excerpt)
            st.subheader("Draft first response")
            st.write(r.draft_response)

with tam_tab:
    account_ids = [a["account_id"] for a in load_accounts()]
    account_id = st.selectbox("Account", account_ids)
    if st.button("Generate account brief"):
        r = generate_account_health(account_id)
        st.subheader("Executive summary")
        st.write(r.executive_summary)
        st.subheader("Open risks and flagged issues")
        if not r.open_risks:
            st.write("No risks found.")
        for risk in r.open_risks:
            st.write(f"{risk.severity.upper()}: {risk.reason}")
            if risk.ticket_id:
                st.write(f"Ticket: {risk.ticket_id}")
            if risk.quote:
                st.write(f"Quote: {risk.quote}")
        st.subheader("Recommended talking points")
        for point in r.talking_points:
            st.write(f"- {point}")
