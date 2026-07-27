"""
document_loader.py
-------------------
Loads all documents (PDF and TXT) from the data/ subfolders and returns
them as a single list of LangChain Document objects, each tagged with
its source file path and category (research_papers / nutrition_guidelines /
fitness_articles) in its metadata.
"""

import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

CATEGORIES = ["research_papers", "nutrition_guidelines", "fitness_articles"]


def load_documents(data_dir: str = DATA_DIR):
    """
    Walk through data/research_papers, data/nutrition_guidelines, and
    data/fitness_articles, load every .pdf and .txt file found, and return
    a flat list of LangChain Document objects with metadata attached.
    """
    all_docs = []

    for category in CATEGORIES:
        folder = os.path.join(data_dir, category)
        if not os.path.isdir(folder):
            continue

        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)

            if filename.lower().endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            elif filename.lower().endswith(".txt"):
                loader = TextLoader(filepath, encoding="utf-8")
            else:
                continue  # skip unsupported file types

            docs = loader.load()

            # Tag each chunk with useful metadata for later citation
            for doc in docs:
                doc.metadata["source_file"] = filename
                doc.metadata["category"] = category

            all_docs.extend(docs)

    return all_docs


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} document(s) total.")
    for d in docs:
        print(f" - {d.metadata['category']}/{d.metadata['source_file']}")
