"""
Document loaders for PDF, TXT, and HTML files.
Recursively scans all subfolders of the docs/ directory.
Source metadata includes both filename and relative path from docs root.
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredHTMLLoader
from langchain_core.documents import Document


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".html", ".htm"}


def load_documents(docs_dir: str) -> List[Document]:
    """
    Recursively scan docs_dir and load all supported files.
    Returns a flat list of LangChain Document objects.
    Each document carries:
      - metadata["source"]        — filename only (e.g. "Advertiser-Guide.pdf")
      - metadata["source_path"]   — relative path from docs root (e.g. "advertising/Advertiser-Guide.pdf")
      - metadata["topic_folder"]  — immediate parent folder name (e.g. "advertising")
      - metadata["file_type"]     — extension without dot (e.g. "pdf")
    """
    docs_path = Path(docs_dir).resolve()
    if not docs_path.exists():
        raise FileNotFoundError(f"docs directory not found: {docs_dir}")

    all_documents: List[Document] = []

    # rglob("*") walks all subdirectories
    for file_path in sorted(docs_path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative = file_path.relative_to(docs_path)
        print(f"  Loading: {relative}")

        documents = _load_single_file(file_path)

        for doc in documents:
            doc.metadata["source"]       = file_path.name
            doc.metadata["source_path"]  = str(relative).replace("\\", "/")
            doc.metadata["topic_folder"] = relative.parts[0] if len(relative.parts) > 1 else "root"
            doc.metadata["file_type"]    = file_path.suffix.lower().lstrip(".")

        all_documents.extend(documents)
        print(f"    -> {len(documents)} page(s) loaded")

    print(f"\nTotal pages loaded across all files: {len(all_documents)}")
    return all_documents


def _load_single_file(file_path: Path) -> List[Document]:
    """Load a single file based on its extension."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return PyPDFLoader(str(file_path)).load()

    if suffix in {".txt"}:
        return TextLoader(str(file_path), encoding="utf-8").load()

    if suffix in {".html", ".htm"}:
        return UnstructuredHTMLLoader(str(file_path)).load()

    raise ValueError(f"Unsupported file type: {suffix}")
