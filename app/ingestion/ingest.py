"""
Main ingestion pipeline: load -> chunk -> embed -> store in ChromaDB.

Run:
    python -m app.ingestion.ingest
or:
    python app/ingestion/ingest.py
"""

import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()

import chromadb
from langchain_chroma import Chroma

from app.ingestion.loaders import load_documents
from app.ingestion.chunking import chunk_documents
from app.ingestion.embedding import get_embeddings


DOCS_DIR = os.getenv("DOCS_DIR", "./docs")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
COLLECTION_NAME = "creator_ae_regulations"


def run_ingestion():
    print("=" * 50)
    print("CreatorAE — Document Ingestion Pipeline")
    print("=" * 50)

    # 1. Load raw documents
    print("\n[1/4] Loading documents from:", DOCS_DIR)
    documents = load_documents(DOCS_DIR)

    if not documents:
        print("No documents found. Exiting.")
        return

    # 2. Chunk documents
    print("\n[2/4] Chunking documents...")
    chunks = chunk_documents(documents)

    # 3. Set up embeddings
    print("\n[3/4] Initialising OpenAI embeddings (text-embedding-3-small)...")
    embeddings = get_embeddings()

    # 4. Store in ChromaDB
    print(f"\n[4/4] Storing vectors in ChromaDB at: {CHROMA_DB_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    # Drop existing collection so re-running ingestion is idempotent
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"  Existing collection '{COLLECTION_NAME}' cleared.")
    except Exception:
        pass

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=COLLECTION_NAME,
    )

    print(f"\nIngestion complete. {len(chunks)} chunks stored in '{COLLECTION_NAME}'.")
    print("=" * 50)


if __name__ == "__main__":
    run_ingestion()
