# 🚀 Enterprise AI Knowledge Agent (Local RAG)

A secure, enterprise-grade Retrieval-Augmented Generation (RAG) agent designed to interact with local MS SQL Databases and document stores using private LLMs.

---

## 📋 1. Overview
This project demonstrates a local-first AI agent that can query both structured SQL data and unstructured files (PDF/Docx). By leveraging **Ollama**, all data processing remains on-premise, ensuring complete data privacy and enterprise compliance without relying on external cloud APIs.

---

## 🛠️ 2. Tech Stack
- **Framework:** FastAPI (Python 3.12)
- **Orchestration:** LangChain & LangGraph
- **LLM & Embeddings:** Ollama (Llama 3.1 & nomic-embed-text)
- **Vector Store:** ChromaDB
- **Database:** Microsoft SQL Server
- **Infrastructure:** Docker & Docker Compose

---

## 🏗️ 3. Architecture
1. **Ingestion:** Documents are chunked and embedded into a local ChromaDB instance.
2. **Retrieval:** Semantic search identifies relevant context for user queries.
3. **Tool Use:** The agent dynamically generates and executes SQL queries to fetch structured data from MS SQL Server.
4. **Generation:** Ollama synthesizes a final response based on the combined retrieved context and SQL results.

---

## 🚦 4. Getting Started

### Prerequisites
- [Docker Desktop](https://docker.com)
- [Ollama](https://ollama.com) (Running on Windows Host)

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd rag_agent_docker
