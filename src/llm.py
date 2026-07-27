"""
llm.py
------
Takes the user's question plus the retrieved context chunks, and asks
Gemini to generate an evidence-based answer grounded in that context,
along with a list of the sources used.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

# You can swap this for any current Gemini chat model name -
# check https://ai.google.dev/gemini-api/docs/models for the latest options.
CHAT_MODEL = "gemini-3.5-flash-lite"
PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    """You are FitEvidence AI, an evidence-based fitness and nutrition assistant.

Answer the user's question using ONLY the context provided below. If the
context does not contain enough information to answer confidently, say so
clearly instead of guessing or relying on outside knowledge.

Keep the tone clear, practical, and non-alarmist. Avoid absolute claims;
reflect the nuance in the source material (e.g. "most research suggests"
rather than "science proves").

Context:
{context}

Question: {question}

Answer:"""
)


def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Copy .env.example to .env and add your key."
        )
    return ChatGoogleGenerativeAI(model=CHAT_MODEL, google_api_key=api_key, temperature=0.3)


def generate_answer(question: str, chunks):
    """
    chunks: list of LangChain Document objects (from retriever.py)
    Returns a dict with the answer text and a deduplicated list of sources.
    """
    context_text = "\n\n---\n\n".join(chunk.page_content for chunk in chunks)

    llm = get_llm()
    chain = PROMPT_TEMPLATE | llm
    response = chain.invoke({"context": context_text, "question": question})

    # Gemini 3.x models can return content as a list of structured blocks
    # instead of a plain string. Extract just the human-readable text.
    raw_content = response.content
    if isinstance(raw_content, str):
        answer_text = raw_content
    else:
        answer_text = "".join(
            block.get("text", "")
            for block in raw_content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()

    sources = sorted({
        f"{chunk.metadata.get('category')}/{chunk.metadata.get('source_file')}"
        for chunk in chunks
    })
    return {
        "answer": answer_text,
        "sources": sources,
    }


if __name__ == "__main__":
    from retriever import retrieve_relevant_chunks

    question = "How much protein do I need for muscle growth?"
    chunks = retrieve_relevant_chunks(question)
    result = generate_answer(question, chunks)

    print("Answer:\n", result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(" -", s)
