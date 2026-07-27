"""
embedding.py
------------
Provides a single function to get the Gemini embedding model used to turn
text chunks (and user queries) into numerical vectors for similarity search.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from langchain_google_genai._common import GoogleGenerativeAIError

load_dotenv()

EMBEDDING_MODEL = "models/gemini-embedding-001"


def get_embedding_model():
    """
    Returns a configured Gemini embeddings client.
    Requires GOOGLE_API_KEY to be set in the environment (.env file).
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found. Copy .env.example to .env and add your key."
        )
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key,
    )


@retry(
    retry=retry_if_exception_type(GoogleGenerativeAIError),
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(6),
)
def embed_documents_safely(embeddings, texts, batch_size=20, delay=13):
    """
    Embeds a list of texts in batches, respecting the free-tier
    ~100 requests/minute limit, with automatic retry on 429s.
    """
    import time

    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        vectors = embeddings.embed_documents(batch)
        all_vectors.extend(vectors)
        if i + batch_size < len(texts):  # don't sleep after the last batch
            time.sleep(delay)
    return all_vectors