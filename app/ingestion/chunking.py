"""
Text chunking using RecursiveCharacterTextSplitter.
Chunk size and overlap are tuned for regulatory document retrieval.
"""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split loaded documents into overlapping chunks suitable for embedding.
    Source metadata is preserved on every chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(documents)
    print(f"Total chunks after splitting: {len(chunks)}")
    return chunks
