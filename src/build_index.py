"""
build_index.py
--------------
Runs the full ingestion pipeline:
    documents -> chunks -> embeddings -> FAISS vector store (saved to disk)
Run this once after adding/changing files in data/, e.g.:
    python src/build_index.py
"""
import os
import time
from langchain_community.vectorstores import FAISS
from document_loader import load_documents
from text_splitter import split_documents
from embedding import get_embedding_model

VECTOR_STORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "embeddings", "vector_store"
)

# Tune these to stay under the free-tier ~100 requests/minute limit
BATCH_SIZE = 20      # chunks embedded per API call
BATCH_DELAY = 15     # seconds to wait between batches


def build_faiss_in_batches(chunks, embedding_model):
    """
    Embeds chunks in small batches with a delay between them,
    merging results into a single FAISS index, to avoid hitting
    the Gemini free-tier rate limit (429 RESOURCE_EXHAUSTED).
    """
    vector_store = None
    total = len(chunks)

    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        batch_store = FAISS.from_documents(batch, embedding_model)

        if vector_store is None:
            vector_store = batch_store
        else:
            vector_store.merge_from(batch_store)

        if i + BATCH_SIZE < total:
            time.sleep(BATCH_DELAY)

    return vector_store


def build_index():
    print("Step 1/4: Loading documents...")
    docs = load_documents()
    if not docs:
        print("No documents found in data/. Add some .pdf or .txt files first.")
        return
    print(f"  Loaded {len(docs)} document(s).")

    print("Step 2/4: Splitting into chunks...")
    chunks = split_documents(docs)
    print(f"  Created {len(chunks)} chunk(s).")

    print("Step 3/4: Generating embeddings and building FAISS index...")
    embedding_model = get_embedding_model()
    vector_store = build_faiss_in_batches(chunks, embedding_model)

    print("Step 4/4: Saving index to disk...")
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    vector_store.save_local(VECTOR_STORE_DIR)
    print(f"\nDone. Vector store saved to: {VECTOR_STORE_DIR}")


if __name__ == "__main__":
    build_index()