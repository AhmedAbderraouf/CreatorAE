"""
Quick terminal test script for the CreatorAE RAG pipeline.

Usage:
    python query.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

from app.rag.chain import query


def main():
    print("=" * 60)
    print("CreatorAE — Terminal Query Interface")
    print("=" * 60)
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    while True:
        question = input("Question: ").strip()

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        print("\nRetrieving relevant regulations...\n")

        try:
            result = query(question)
        except Exception as e:
            print(f"Error: {e}\n")
            continue

        print("-" * 60)
        print("Answer:\n")
        print(result["answer"])
        print()

        if result["sources"]:
            print("Sources:")
            for src in result["sources"]:
                print(f"  - {src}")

        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
