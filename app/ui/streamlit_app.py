"""
CreatorAE — Streamlit UI
Minimal bilingual interface for querying UAE creator compliance regulations.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from app.rag.chain import query as rag_query


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CreatorAE — UAE Compliance Assistant",
    page_icon="🇦🇪",
    layout="centered",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🇦🇪 CreatorAE")
st.subheader("UAE Creator Compliance Assistant")
st.markdown(
    """
    Ask about UAE media law, advertising regulations, filming permits, and content compliance.
    Answers are grounded in official UAE regulatory documents.
    **This is not legal advice.**
    """
)
st.divider()

# ── Query input ───────────────────────────────────────────────────────────────
question = st.text_area(
    "Your question (English or Arabic):",
    placeholder="e.g. Do I need a permit to film sponsored content inside a mall in Dubai?",
    height=100,
)

submit = st.button("Ask CreatorAE", type="primary")

# ── Response ──────────────────────────────────────────────────────────────────
if submit:
    if not question.strip():
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving relevant regulations..."):
            try:
                result = rag_query(question)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        st.markdown("### Answer")
        st.markdown(result["answer"])

        if result["sources"]:
            st.divider()
            st.markdown("**Sources retrieved:**")
            for src in result["sources"]:
                st.markdown(f"- `{src}`")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "CreatorAE is an AI assistant and does not provide legal advice. "
    "Always consult a qualified UAE legal professional for binding guidance."
)
