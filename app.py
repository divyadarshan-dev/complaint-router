"""
app.py - the web page. Run with:  python -m streamlit run app.py
"""
import os

import streamlit as st

from router import DEPARTMENTS, route_complaint

# When deployed on Streamlit Cloud, the API key comes from "Secrets"
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

st.set_page_config(page_title="Complaint Router", page_icon="🛠️", layout="wide")
st.title("🛠️ Hinglish Complaint Router")
st.caption("AI-powered campus complaint triage for English, Hinglish, and romanised Punjabi.")

# st.session_state remembers things between button clicks
if "tickets" not in st.session_state:
    st.session_state.tickets = []
if "draft_complaint" not in st.session_state:
    st.session_state.draft_complaint = ""

# One-click demo examples for fast live presentations
st.markdown("**Quick sample complaints (click to fill):**")
b1, b2, b3, b4 = st.columns(4)
if b1.button("🚰 Hinglish Plumbing"):
    st.session_state.draft_complaint = "bhai BH-4 3rd floor washroom ka tap 3 din se leak kar rha h"
if b2.button("🍛 Punjabi Mess"):
    st.session_state.draft_complaint = "mess ch roti kachi si te dal ch kankar aa rahe ne aaj"
if b3.button("⚡ High-Urgency Spark"):
    st.session_state.draft_complaint = "room 118 switch board se spark aa rahi hai jaldi bhejo kisi ko"
if b4.button("🤔 Ambiguous (Human Review)"):
    st.session_state.draft_complaint = "fan bhi band hai aur washroom ka tap bhi leak kar rha hai"

complaint = st.text_area(
    "Student Complaint",
    value=st.session_state.draft_complaint,
    placeholder="e.g., bhai 4th floor ka washroom ka tap 3 din se leak kar rha h",
    height=100,
)

col_run, col_clear = st.columns([1, 5])
run_clicked = col_run.button("Route it", type="primary")
if col_clear.button("Clear tickets"):
    st.session_state.tickets = []
    st.session_state.draft_complaint = ""
    st.rerun()

if run_clicked:
    if complaint.strip():
        with st.spinner("Reading & classifying complaint..."):
            ticket = route_complaint(complaint.strip())
        st.session_state.tickets.append(ticket)

        # Highlight whether it went to a department or Human Review
        if ticket["queue"] == "Human Review":
            st.warning(
                "⚠️ Sent to **Human Review** (confidence: %.2f) — %s"
                % (ticket["confidence"], ticket["reason"])
            )
        else:
            st.success(
                "✅ Sent to **%s** (confidence: %.2f) — %s"
                % (ticket["queue"], ticket["confidence"], ticket["reason"])
            )

        # Show extracted fields clearly
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Queue", ticket["queue"])
        m2.metric("Urgency", (ticket["urgency"] or "medium").upper())
        m3.metric("Block", ticket["block"] or "—")
        m4.metric("Floor", str(ticket["floor"]) if ticket["floor"] is not None else "—")
        m5.metric("Room", ticket["room"] or "—")
    else:
        st.warning("Please type a complaint first.")

tickets = st.session_state.tickets

if tickets:
    st.divider()
    # Cost and speed report (required by the problem statement)
    avg_latency = sum(t["latency_s"] for t in tickets) / len(tickets)
    total_cost = sum(t["cost_usd"] for t in tickets)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Tickets", len(tickets))
    c2.metric("Avg latency per complaint", "%.2f s" % avg_latency)
    c3.metric("Avg cost per complaint", "$%.5f" % (total_cost / len(tickets)))

    columns = ["complaint", "department", "block", "floor", "room", "urgency", "confidence", "reason"]

    st.subheader("🚨 Human Review Queue")
    review = [t for t in tickets if t["queue"] == "Human Review"]
    if review:
        st.dataframe([{k: t[k] for k in columns} for t in review], use_container_width=True)
    else:
        st.info("Nothing needs human review yet.")

    st.subheader("📋 Department Queues")
    for dept in DEPARTMENTS:
        items = [t for t in tickets if t["queue"] == dept]
        if items:
            st.markdown("**%s** (%d)" % (dept, len(items)))
            st.dataframe([{k: t[k] for k in columns} for t in items], use_container_width=True)
