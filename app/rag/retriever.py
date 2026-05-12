"""
ChromaDB vector store retriever.
Returns the top-k most relevant regulatory chunks for a given query.
"""

import os

import chromadb
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from app.ingestion.embedding import get_embeddings


CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")
COLLECTION_NAME = "creator_ae_regulations"
DEFAULT_TOP_K = 25


def get_retriever(top_k: int = DEFAULT_TOP_K) -> VectorStoreRetriever:
    """Load the persisted ChromaDB collection and return a LangChain retriever."""
    embeddings = get_embeddings()

    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    vector_store = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )
