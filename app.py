"""
app.py
------
FitEvidence AI - Streamlit front-end.

Run with:
    streamlit run app.py
"""

import os
import sys
import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from retriever import retrieve_relevant_chunks  # noqa: E402
from llm import generate_answer  # noqa: E402

st.set_page_config(page_title="FitEvidence AI", page_icon="🏋️", layout="centered")

st.title("🏋️ FitEvidence AI")
st.caption("An evidence-based fitness assistant powered by Retrieval-Augmented Generation (RAG)")

st.markdown(
    "Ask a question about training, nutrition, or recovery. "
    "Answers are grounded in the documents inside the `data/` folder — not general internet opinion."
)

example_questions = [
    "What is progressive overload?",
    "How much protein is needed for muscle growth?",
    "Does creatine improve strength?",
    "How does sleep affect muscle growth?",
]

with st.sidebar:
    st.header("Example questions")
    for q in example_questions:
        if st.button(q):
            st.session_state["question"] = q

question = st.text_input(
    "Your question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. Is training to failure necessary?",
)

if st.button("Get Answer", type="primary") and question.strip():
    with st.spinner("Retrieving relevant research..."):
        try:
            chunks = retrieve_relevant_chunks(question)
        except FileNotFoundError as e:
            st.error(str(e))
            st.stop()

    if not chunks:
        st.warning("No relevant information found in the knowledge base for this question.")
    else:
        with st.spinner("Generating evidence-based answer..."):
            try:
                result = generate_answer(question, chunks)
            except ValueError as e:
                st.error(str(e))
                st.stop()

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Sources")
        for source in result["sources"]:
            st.markdown(f"- `{source}`")

        with st.expander("Show retrieved context (debug view)"):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i} — {chunk.metadata.get('source_file')}**")
                st.text(chunk.page_content)
