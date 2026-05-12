"""
LangChain RAG chain: retrieve relevant chunks → build prompt → call OpenAI LLM.
Returns the answer and the list of source document names cited.
"""

import os
from typing import Dict, List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.rag.retriever import get_retriever
from app.rag.prompts import SYSTEM_PROMPT


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = 0.0  # Deterministic — regulatory context demands consistency


def _format_docs(docs: List[Document]) -> str:
    """Combine retrieved chunks into a single context string with source labels."""
    sections = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        sections.append(f"[Source {i}: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(sections)


def _extract_sources(docs: List[Document]) -> List[str]:
    """Return unique source document names from retrieved chunks."""
    seen: set = set()
    sources: List[str] = []
    for doc in docs:
        name = doc.metadata.get("source", "Unknown")
        if name not in seen:
            seen.add(name)
            sources.append(name)
    return sources


def query(question: str) -> Dict:
    """
    Run a question through the RAG pipeline.
    Returns {"answer": str, "sources": list[str]}.
    """
    retriever = get_retriever()
    llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)

    # Retrieve relevant chunks
    retrieved_docs = retriever.invoke(question)
    context = _format_docs(retrieved_docs)
    sources = _extract_sources(retrieved_docs)

    # Build the prompt with retrieved context injected into the system message
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({"context": context, "question": question})

    return {
        "answer": answer,
        "sources": sources,
    }
