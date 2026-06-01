# PRD.md

# ResearchOps AI - Agentic RAG for AI Research Papers

## Overview

ResearchOps AI is a simple enterprise-style RAG assistant that ingests live AI research papers from public APIs, stores them in Qdrant Cloud, and allows users to chat with an AI assistant to search, summarize, and compare research papers.

The goal is to demonstrate production-style AI engineering skills including:

* API Integration
* Data Ingestion Pipelines
* Vector Databases (Qdrant)
* Agentic RAG
* FastAPI Backend
* React Frontend
* Docker Deployment

---

# Objectives

Build a portfolio-ready AI application that demonstrates:

1. Live data ingestion from external APIs
2. Vector search with Qdrant Cloud
3. Agentic RAG workflow
4. Modern React frontend
5. Containerized deployment

---

# Target User

AI Engineer Recruiters

Hiring Managers

Developers interested in AI research

---

# Data Source

Primary Source:

* arXiv API

Categories:

* cs.AI
* cs.CL
* cs.LG
* cs.IR

Data to ingest:

* Title
* Authors
* Abstract
* Published Date
* PDF URL
* Category

---

# Functional Requirements

## 1. Data Ingestion Service

Endpoint:

POST /ingest

Responsibilities:

* Fetch latest papers from arXiv
* Generate embeddings
* Store vectors in Qdrant Cloud
* Store metadata in Qdrant payload

Success Criteria:

* At least 100 papers ingested successfully

---

## 2. Agentic RAG Chat API

Endpoint:

POST /chat

User sends:

{
"message": "What are the latest papers about agentic RAG?"
}

System should:

1. Analyze user question
2. Search Qdrant
3. Retrieve relevant papers
4. Generate answer
5. Return sources

Response:

{
"answer": "...",
"sources": [
{
"title": "...",
"url": "..."
}
]
}

---

## 3. Search API

Endpoint:

GET /papers

Query Params:

* keyword
* category

Returns paper metadata.

---

## 4. Health Check

Endpoint:

GET /health

Response:

{
"status": "ok"
}

---

# Non Functional Requirements

* Response time under 5 seconds
* Dockerized services
* Environment variables for secrets
* Clear project structure
* Logging enabled

---

# Tech Stack

## Backend

* Python 3.12
* FastAPI
* LangGraph
* Qdrant Client
* OpenAI Embeddings

## Frontend

* React
* TypeScript
* Vite
* TailwindCSS
* shadcn/ui

## Infrastructure

* Docker
* Docker Compose

## Vector Database

* Qdrant Cloud

---

# Agent Workflow

User Question

↓

Agent

↓

Retriever Tool

↓

Qdrant Search

↓

Relevant Context

↓

LLM

↓

Final Answer + Sources

---

# Frontend Requirements

## Chat Interface

Features:

* Chat input
* Chat history
* Streaming responses
* Source citations

Style:

* Apple-inspired
* Minimal
* White background
* Rounded cards
* Soft shadows

---

## Papers Page

Display:

* Title
* Authors
* Published Date
* Link to Paper

Search box included.

---

# Project Structure

researchops-ai/

├── backend/

│ ├── api/

│ ├── agents/

│ ├── services/

│ ├── ingestion/

│ └── Dockerfile

│

├── frontend/

│ ├── src/

│ ├── components/

│ ├── pages/

│ └── Dockerfile

│

├── docker-compose.yml

│

└── README.md

---

# Environment Variables

Backend:

OPENAI_API_KEY=

QDRANT_URL=

QDRANT_API_KEY=

ARXIV_BASE_URL=

---

# Docker Requirements

Backend Container

* FastAPI Application

Frontend Container

* React Application

Docker Compose

* Run frontend and backend together

Commands:

docker compose up --build

docker compose down

---

# Out of Scope

Do NOT build:

* Authentication
* Multi-user support
* RBAC
* Billing
* Admin dashboard
* Kubernetes
* CI/CD
* Complex multi-agent systems

Keep the project focused and portfolio-friendly.

---

# Success Criteria

A recruiter should be able to:

1. Run docker compose up
2. Ingest research papers
3. Ask questions in chat
4. Receive RAG-based answers
5. View paper sources

The entire setup should be understandable within 10 minutes of reviewing the repository.
