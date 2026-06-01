# ResearchOps AI - Enterprise Agentic RAG for Live AI Paper Intelligence

ResearchOps AI ingests recent AI research papers from arXiv, stores embeddings and paper metadata in Qdrant Cloud, and provides a FastAPI + React application for search and streaming RAG chat with source citations.

## Stack

- Backend: Python 3.12, FastAPI, LangGraph, OpenAI, Qdrant Client
- Frontend: React, TypeScript, Vite
- Vector database: Qdrant Cloud
- Deployment: Docker Compose

## Requirements

- OpenAI API key
- Qdrant Cloud cluster URL and API key
- Python 3.12+
- Node.js 22+
- Docker, for containerized runs

## Environment

Create a local `.env` from the example:

```bash
cp .env.example .env
```

Set at least:

```env
OPENAI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

Keep these aligned unless you intentionally change embedding models:

```env
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_VECTOR_SIZE=1536
QDRANT_COLLECTION_NAME=research_papers
```

## Local Development

Install backend dependencies:

```bash
uv sync
```

Run the backend:

```bash
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173/
```

## Docker

Run the full app:

```bash
docker compose up --build
```

Open:

```text
http://localhost:3000/
```

Stop the app:

```bash
docker compose down
```

## Demo Flow

1. Open the frontend.
2. Click `Ingest` to fetch and embed 100 recent papers.
3. Search papers by keyword or category.
4. Ask a question in chat, for example:

```text
What are the latest papers about agentic RAG?
```

The assistant streams a Markdown-formatted answer and returns source citations from the retrieved papers.

## API

Health:

```bash
curl http://127.0.0.1:8000/health
```

Ingest:

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"limit":100,"categories":["cs.AI","cs.CL","cs.LG","cs.IR"]}'
```

Search:

```bash
curl "http://127.0.0.1:8000/papers?keyword=rag&category=cs.AI"
```

Chat:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the latest papers about agentic RAG?"}'
```

Streaming chat:

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"What are the latest papers about agentic RAG?"}'
```

## Notes

- The Qdrant collection is created automatically during ingestion.
- `.env` is ignored and must not be committed.
- `.env.example` contains placeholders only.
- The app intentionally excludes authentication, billing, RBAC, and admin features to keep the portfolio demo focused.
