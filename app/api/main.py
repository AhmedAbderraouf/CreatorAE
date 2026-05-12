"""
CreatorAE FastAPI backend.

Endpoints:
  GET  /       — health check
  POST /query  — submit a compliance question
"""

import os
import sys
from pathlib import Path

# Ensure the project root is on the path when running with uvicorn from subdirs
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.rag.chain import query as rag_query


app = FastAPI(
    title="CreatorAE — UAE Creator Compliance Assistant",
    description=(
        "Bilingual RAG-based assistant that helps UAE creators, influencers, "
        "and agencies understand which media and advertising regulations may apply "
        "to their content. Not legal advice."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        json_schema_extra={"example": "Do I need a permit to film sponsored content inside Dubai Mall?"},
    )


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/", summary="Health check")
def health_check():
    return {"status": "CreatorAE API running"}


@app.post("/query", response_model=QueryResponse, summary="Ask a compliance question")
def query_endpoint(request: QueryRequest):
    try:
        result = rag_query(request.question)
        return QueryResponse(answer=result["answer"], sources=result["sources"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
