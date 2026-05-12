# CreatorAE — UAE Creator Compliance Assistant

A bilingual RAG assistant that helps creators, influencers, agencies, and startups figure out which UAE media and advertising regulations might apply to their content. Answers are pulled directly from official documents — no hallucinated laws.

---

## The Problem

UAE regulatory documents are dense, scattered, and written in legal language most creators never read. Questions like:

- Do I need a permit to film a sponsored reel inside a mall?
- What disclosure rules apply to paid brand deals on social media?
- What are the actual penalties for posting unlicensed advertising content?

These aren't easy to answer, and legal consultation is expensive. This project makes the documents queryable in plain English or Arabic.

---

## Architecture

```
User Query (English or Arabic)
         ↓
 LangChain Retrieval (similarity search)
         ↓
  Chroma Vector DB (local persistence)
         ↓
Retrieved UAE Regulatory Context (top-25 chunks)
         ↓
   OpenAI LLM (gpt-4o-mini, temperature=0)
         ↓
  FastAPI Response / Streamlit UI
```

---

## Document Corpus

10 official UAE regulatory documents organised into topic subfolders.

| Folder | Document | Notes |
|---|---|---|
| `advertising/` | Advertiser-Guide.pdf | UAE Media Council advertiser guidance |
| `advertising/` | Media Services Fees.txt | Cabinet Resolution 41/2025 fee schedule |
| `filming_permits/` | How To Film In Dubai.txt | DFTC filming permit criteria |
| `general/` | Media Services Guide.pdf | Comprehensive media services reference |
| `media_law/` | Federal Decree by Law No. (55) of 2023 Regulating Media.pdf | Primary media regulation law |
| `media_law/` | Executive Regulations of the Media Regulation Law.pdf | Executive regulation (Cabinet Res. 68/2024) |
| `media_law/` | Cabinet-Resolution-Media-Violations-and-Penalties.pdf | Administrative fines and penalties |
| `media_law/` | Decree-Law on the Establishment and Regulation of the National Media Authority.txt | NMA establishment decree (Arabic) |
| `media_law/` | Media Contents Standards.pdf | Content classification and standards |
| `privacy/` | Law on Combating Rumors and Cybercrimes.txt | Federal Decree-Law 34/2021 |

To add new documents, drop them into the right subfolder and re-run ingestion.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ (tested on 3.13) |
| Web API | FastAPI + Uvicorn |
| UI | Streamlit |
| RAG Framework | LangChain (LCEL) |
| Vector Store | ChromaDB (local persistence) |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-4o-mini` |
| Containerisation | Docker / Docker Compose |
| Deployment Target | AWS EC2 |

---

## Project Structure

```
CreatorAE/
│
├── app/
│   ├── api/
│   │   └── main.py              # FastAPI endpoints
│   │
│   ├── rag/
│   │   ├── retriever.py         # ChromaDB retriever setup
│   │   ├── chain.py             # LangChain RAG pipeline
│   │   └── prompts.py           # System prompt + guardrails
│   │
│   ├── ingestion/
│   │   ├── ingest.py            # Main ingestion runner
│   │   ├── loaders.py           # PDF + TXT document loaders (recursive)
│   │   ├── chunking.py          # RecursiveCharacterTextSplitter
│   │   └── embedding.py         # OpenAI embeddings setup
│   │
│   └── ui/
│       └── streamlit_app.py     # Streamlit chat interface
│
├── docs/                        # UAE regulatory documents — topic subfolders
│   ├── advertising/
│   ├── filming_permits/
│   ├── general/
│   ├── media_law/
│   └── privacy/
│
├── chroma_db/                   # Vector store (gitignored, rebuilt by ingest)
├── tests/
│   └── test_api.py
│
├── query.py                     # Quick terminal test interface
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Setup

### Requirements

- Python 3.11+
- OpenAI API key — [platform.openai.com](https://platform.openai.com)

### Install

```bash
git clone https://github.com/your-username/CreatorAE.git
cd CreatorAE
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# add your OPENAI_API_KEY to .env
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `CHROMA_DB_DIR` | No | `./chroma_db` | ChromaDB persistence path |
| `DOCS_DIR` | No | `./docs` | Path to regulatory documents |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model for generation |

---

## Running Ingestion

Run this once before querying. Re-run it whenever you add documents.

```bash
python -m app.ingestion.ingest
```

The pipeline recursively scans all subfolders of `docs/`, chunks the text, embeds it, and stores it in ChromaDB. Source filename, relative path, and topic folder are all kept in metadata.

```
[1/4] Loading documents from: ./docs
  Loading: advertising\Advertiser-Guide.pdf
    -> 14 page(s) loaded
  ...

[2/4] Chunking documents...
Total chunks after splitting: 266

[3/4] Initialising OpenAI embeddings (text-embedding-3-small)...

[4/4] Storing vectors in ChromaDB at: ./chroma_db
Ingestion complete. 266 chunks stored in 'creator_ae_regulations'.
```

Re-running clears and rebuilds the collection from scratch.

---

## Running the API

```bash
python -m uvicorn app.api.main:app --reload
```

API at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### Endpoints

`GET /` — health check
```json
{ "status": "CreatorAE API running" }
```

`POST /query`
```json
// request
{ "question": "Do I need a permit to film sponsored content inside a mall?" }

// response
{
  "answer": "According to the retrieved documents...",
  "sources": ["Advertiser-Guide.pdf", "Federal Decree by Law No. (55) of 2023 Regulating Media.pdf"]
}
```

---

## Running the UI

```bash
python -m streamlit run app/ui/streamlit_app.py
```

Open `http://localhost:8501`.

---

## Terminal Interface

```bash
python query.py
```

Type questions directly in the terminal. Useful for quick testing without running the servers.

---

## Tests

```bash
pytest tests/ -v
```

---

## Example Queries

| Query | What it retrieves |
|---|---|
| Do I need a permit to film sponsored content inside a mall? | Filming permit criteria, NOC requirements |
| What disclosure rules apply to paid brand deals? | Advertiser guidance on sponsorship disclosure |
| What are the penalties for violating UAE media regulations? | Fines and penalties from the Cabinet Resolution |
| هل يحتاج المؤثر إلى ترخيص لنشر محتوى إعلاني ممول؟ | Responds in Arabic from retrieved context |
| Is filming someone without consent illegal in UAE? | Article 44 of the Cybercrime Law on privacy invasion |

---

## Docker

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- UI: `http://localhost:8501`

Run ingestion inside Docker:
```bash
docker compose run --rm api python -m app.ingestion.ingest
```

---

## AWS EC2 Deployment

Instance: `t3.medium` (2 vCPU / 4 GB RAM), Ubuntu 22.04

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
git clone https://github.com/your-username/CreatorAE.git
cd CreatorAE
cp .env.example .env && nano .env
docker compose run --rm api python -m app.ingestion.ingest
docker compose up -d
```

Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
    }

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

ChromaDB persists to `./chroma_db` on the host. Mount it to an EBS volume for production. Future migration path: ECR + ECS Fargate + EFS for the vector store.

---

## Roadmap

- [ ] More UAE regulatory documents (TDRA, Dubai Culture, Abu Dhabi DoE)
- [ ] Streaming responses
- [ ] Confidence scoring per retrieved chunk
- [ ] Document version tracking
- [ ] Rate limiting + API key auth for production

---

## Disclaimer

This is not legal advice. Answers are generated from retrieved regulatory documents for informational purposes only. Always consult a qualified UAE legal professional before making compliance decisions.
