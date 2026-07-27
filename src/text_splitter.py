"""
text_splitter.py
-----------------
Splits loaded documents into smaller overlapping chunks so that retrieval
can return focused, relevant passages instead of entire documents.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

# chunk_size and chunk_overlap can be tuned:
# - Smaller chunks -> more precise retrieval, but less surrounding context
# - Larger chunks -> more context per chunk, but retrieval can be less precise
CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def split_documents(documents, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
    """
    Split a list of LangChain Document objects into smaller chunks.
    Metadata (source_file, category) is preserved on every chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    return chunks


if __name__ == "__main__":
    from document_loader import load_documents

    docs = load_documents()
    chunks = split_documents(docs)
    print(f"Split {len(docs)} document(s) into {len(chunks)} chunk(s).")
    if chunks:
        print("\nExample chunk:\n")
        print(chunks[0].page_content[:300])
