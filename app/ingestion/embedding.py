"""
OpenAI embedding setup.
Uses text-embedding-3-small for cost-effective, high-quality retrieval.
"""

import os

from langchain_openai import OpenAIEmbeddings


def get_embeddings() -> OpenAIEmbeddings:
    """Return an OpenAI embeddings instance using text-embedding-3-small."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
    )
