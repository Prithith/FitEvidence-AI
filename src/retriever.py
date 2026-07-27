"""
retriever.py
------------
Loads the saved FAISS vector store and provides a function to retrieve
the most relevant chunks for a given user question.
"""

import os
from langchain_community.vectorstores import FAISS

from embedding import get_embedding_model

VECTOR_STORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "embeddings", "vector_store"
)

TOP_K = 4  # number of chunks to retrieve per query


def load_vector_store():
    """Loads the FAISS index from disk. Raises a clear error if it doesn't exist yet."""
    if not os.path.exists(VECTOR_STORE_DIR):
        raise FileNotFoundError(
            "No vector store found. Run `python src/build_index.py` first."
        )

    embedding_model = get_embedding_model()
    # allow_dangerous_deserialization is safe here since we created this index ourselves
    return FAISS.load_local(
        VECTOR_STORE_DIR, embedding_model, allow_dangerous_deserialization=True
    )


def retrieve_relevant_chunks(query: str, k: int = TOP_K):
    """
    Given a user question, returns the top-k most relevant document chunks,
    each with its source metadata attached.
    """
    vector_store = load_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results


if __name__ == "__main__":
    question = "Does creatine improve strength?"
    chunks = retrieve_relevant_chunks(question)
    print(f"Top {len(chunks)} chunks for: '{question}'\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}] Source: {chunk.metadata.get('source_file')}")
        print(chunk.page_content[:200], "...\n")
