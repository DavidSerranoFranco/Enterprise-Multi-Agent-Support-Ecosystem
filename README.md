# Enterprise Multi-Agent Support Ecosystem (RAG-Powered)

## Summary

This project is a production-grade backend infrastructure designed to automate complex customer support workflows using Generative AI. It implements a sophisticated Multi-Agent Orchestration architecture that dynamically classifies user intent and routes queries to specialized agents. By leveraging Retrieval-Augmented Generation (RAG), the system ensures all AI responses are grounded in verified corporate documentation, effectively eliminating hallucinations.

## Technical Architecture

The system is built on a decoupled, asynchronous microservices architecture:

* **API Layer:** High-performance asynchronous endpoints developed with FastAPI.
* **Intelligent Orchestrator:** A semantic routing engine that directs queries to Support, Sales, Technical, or General agents based on intent analysis.
* **RAG Engine:** A document processing pipeline using ChromaDB and HuggingFace/OpenAI embeddings for real-time semantic search across PDF, DOCX, and TXT files.
* **Persistence Layer:** PostgreSQL managed via SQLAlchemy for conversation history, auditing, and system observability.

## Key Features

* **Agentic Specialization:** Distinct LLM profiles for technical troubleshooting, sales conversion, and general corporate information.
* **Performance Optimization:** Inference calls optimized for sub-second latency using Groq LPU hardware acceleration and Gemini 1.5/2.0 models.
* **Context Management:** Advanced conversational memory handling to maintain state across multi-turn interactions.
* **Observability:** Integrated tracking of token consumption, response latency, and document relevance scores.

## Technology Stack

* **Core:** Python 3.10+, FastAPI, LangChain.
* **LLMs:** Google Gemini, Meta Llama 3.3 (via Groq).
* **Vector Database:** ChromaDB.
* **Relational Database:** PostgreSQL.
* **DevOps:** Docker, Celery, Redis.

## Compliance and Security

The architecture follows ISO 27001 principles for information security, ensuring data integrity and confidentiality. It includes input sanitization to prevent prompt injection and implements structured metadata filtering for secure document retrieval.

## Quick Start (Docker)

To deploy the entire ecosystem including PostgreSQL, ChromaDB, and the FastAPI backend:

```bash
docker-compose up --build
```

---
**Developed by David Serrano Franco**
Data Engineer | AI Engineer & AI/MLOps Architect
