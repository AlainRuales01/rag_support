# Technical Support RAG

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C)](https://www.langchain.com/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-000000)](https://www.pinecone.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash_Lite-4285F4)](https://ai.google.dev/)

A **Proof of Concept (PoC)** developed to evaluate the feasibility of a domain-filtered **Retrieval-Augmented Generation (RAG)** pipeline for multi-vendor technical support documentation (hardware manuals, network devices, and VPN setups). 

The goal of this prototype is to validate whether metadata-conditioned vector search paired with strict prompt guardrails can eliminate hallucinations and provide reliable, step-by-step troubleshooting answers with exact page citations before committing to a full-scale deployment.

This PoC was developed using free-tier resources provided by Google AI Studio. Consequently, key technical decisions—such as batch ingestion sizing, rate-limiting intervals with exponential backoff, embedding dimension truncation, and client instance caching—were specifically engineered to operate reliably without exceeding free quota limits.

---

## Problem & Scope

Technical support teams lose significant time searching through multi-brand documentation (e.g., HP, Cisco, Epson, TP-Link). Standard LLM solutions often cross-contaminate procedures between vendors or hallucinate giving mix information or no context data.

This project validates four core requirements:
- **Domain Isolation:** Restricting search to specific product tags (`category`, `brand`, `model`) to eliminate cross-vendor confusion.
- **Hallucination Suppression:** Using strict similarity score thresholds to trigger an explicit refusal path when answers are absent.
- **Procedural Step Retention:** Chunking documents without splitting numbered troubleshooting workflows.
- **API Ingestion Resilience:** Implementing exponential backoff and jitter to survive embedding rate limits (`429`).

---

## Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Document Ingestion Pipeline"]
        direction LR
        Docs["📄 Technical Manuals (PDF)"] --> Split["✂️ Text Splitter (2400 chars)"] --> Embed["🔢 Gemini Embeddings"] --> VectorDB[("🗄️ Pinecone Index")]
    end

    subgraph Inference ["2. Query & Generation Pipeline"]
        direction LR
        User["👤 User Query + Filters"] --> API["⚡ Flask API"] --> Search["🔍 Filtered Search (Score ≥ 0.65)"] --> LLM["🤖 Gemini 3.5 Flash-Lite"] --> Out["✅ Answer + Citations"]
    end

    VectorDB -.-> Search
```

---

## Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.11 | High performance, native typing, and broad library compatibility. |
| **API Framework** | Flask | Minimalist REST API using Blueprints for modular route separation. |
| **RAG Orchestration** | LangChain (LCEL) | Clean, declarative pipeline chaining (`retriever \| prompt \| llm \| parser`). |
| **Vector Database** | Pinecone | Managed serverless vector index with native metadata filtering. |
| **Embedding Model** | Google `gemini-embedding-001` | Semantic representations truncated to 768 dimensions for optimal balance of index size and retrieval precision. |
| **LLM Engine** | Google Gemini `gemini-3.5-flash-lite` | High token speed, low latency, and deterministic output at low temperature (`0.1`). |
| **Document Loader** | PyMuPDF (`PyMuPDFLoader`) | C-based PDF text extraction with fast page parsing and metadata tracking. |

---

## Key Technical Decisions

### 1. Hard Metadata Pre-filtering over Flat Vector Search
* **Context:** Hardware manuals share identical keywords (*"power indicator"*, *"factory reset"*, *"gateway IP"*).
* **Decision:** Enforce mandatory metadata filters (`category`, `brand`, `model`) directly in Pinecone's vector search stage.
* **Result:** Guarantees absolute search isolation within the target equipment without retrieving unrelated vendor guides.

### 2. Similarity Score Cutoff (`score_threshold = 0.65`) vs. Pure Top-$K$
* **Context:** Pure top-$k$ retrieval always returns $k$ documents, even when completely irrelevant, tempting the LLM to invent an answer.
* **Decision:** Configured retrieval with `search_type="similarity_score_threshold"` ($k=5$, threshold $= 0.65$).
* **Result:** Irrelevant chunks are discarded before reaching the prompt. If no relevant chunks exist, an empty context cleanly triggers the refusal response.

### 3. Balanced Chunking Window (2400 Characters / ~600 Tokens)
* **Context:** Oversized chunks pack multiple unrelated topics and instructions into a single embedding vector, diluting semantic precision and causing specific ideas to get lost. In other hand, overly aggressive fragmentation fails to capture relevant context.
* **Decision:** Configured `RecursiveCharacterTextSplitter` with `chunk_size = 2400` characters (~600 tokens) and `chunk_overlap = 400` characters (~100 tokens).
* **Result:** Strikes an optimal balance that captures comprehensive technical explanations without overflowing into multiple contexts, preserving semantic focus during retrieval.

### 4. Resilient Ingestion with Exponential Backoff and Jitter
* **Context:** Batch indexing triggers cloud embedding quota exhaustion (`429 ResourceExhausted`).
* **Decision:** Batched documents into sets of 20 with an exponential backoff formula:
  $$\text{wait} = \min(120, 30 \times 2^{\text{attempt}-1}) + \text{Uniform}(0, 5)$$
* **Result:** Eliminates failed ingestion runs and prevents wasting cloud quotas.

### 5. Deterministic Responses via Strict Prompt Guardrails
* **Context:** Generic conversational prompts produce unsubstantiated technical advice.
* **Decision:** System prompt mandates strict adherence to retrieved text, an exact refusal phrase (*"No dispongo de información suficiente..."*), and source attribution (`[Document, Page X]`).
* **Result:** Output is audit-ready and verifiable against original vendor manuals.

### 6. Client Singleton Caching via `@lru_cache`
* **Context:** Re-creating embedding and LLM client instances on every HTTP request introduces connection and authentication overhead.
* **Decision:** Cached client instances using Python's `@lru_cache`.
* **Result:** Reuses established connection pools and reduces request latency.

### 7. Matryoshka Embedding Truncation (768 Dimensions)
* **Context:** Full-dimensional vector representations consume significant memory and compute in Pinecone, rapidly exhausting free-tier vector limits.
* **Decision:** Using Matryoshka Representation Learning (MRL) native to Google Gemini embeddings to truncate output vectors to 768 dimensions (`output_dimensionality=768`).
* **Result:** Drastically reduces vector database memory waste and retrieval latency while retaining near-full semantic fidelity without losing critical technical information.

---

## Project Structure

```text
├── app.py                     # Flask application entry point
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation & technical decisions
├── data/
│   └── raw/                   # Raw vendor documentation
│       ├── impresora/         # Printer manuals (Epson, HP, etc.)
│       └── vpn/               # Network/VPN documentation (Cisco, TP-Link, etc.)
└── src/
    ├── api/
    │   └── routes.py          # REST endpoints and query validation
    ├── core/
    │   └── config.py          # Environment credentials and config
    ├── generation/
    │   ├── chain.py           # LCEL RAG chain assembly and document formatting
    │   ├── llm.py             # LLM client with LRU caching
    │   └── prompt.py          # Guarded prompt template with source formatting
    ├── ingestion/
    │   ├── loader.py          # PyMuPDF document loader and metadata filter
    │   ├── pipeline.py        # Ingestion pipeline with exponential retry logic
    │   └── splitters.py       # Recursive text splitter configuration
    └── retrieval/
        ├── embeddings.py      # Embedding model loader with dimension tuning
        └── vectorstore.py     # Pinecone vector store connector
```

---

## Getting Started

### 1. Environment Setup

- **Python Version:** 3.11

```powershell
# Create and activate virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt
```

### 2. Environment Variables

Configure your API credentials in  using `config.template` file:
You should copy this file template and rename it to `config.py` in the same directory, then fill in your actual API keys.
```ini
GOOGLE_API_KEY="your_google_gemini_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
```

### 3. Ingestion Pipeline

Place source manuals in `data/raw/<category>/` adhering to the naming convention:

```text
BRAND-MODEL-FILECATEGORYTYPE.ext
```

*Examples:*
- `HP-LASERJET-M404-USERMANUAL.pdf`
- `CISCO-ANYCONNECT-VPNCONFIGURATION.pdf`
- `EPSON-L355-USERMANUAL.pdf`

Run the ingestion script to process and index documents into Pinecone:

```powershell
python -m src.ingestion.pipeline
```

### 4. Running the API

Start the local Flask server:

```powershell
python app.py
```

The service runs at `http://127.0.0.1:5000`.

---

## API Reference

### `GET /query`

Queries the RAG chain for technical troubleshooting guidance.

**Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `question` | string | **Yes** | Technical question or issue to solve. |
| `category` | string | Conditional* | Equipment category (e.g., `impresora`, `vpn`). |
| `brand` | string | Conditional* | Manufacturer (e.g., `EPSON`, `HP`, `CISCO`). |
| `model` | string | Conditional* | Specific model number (e.g., `L355`, `M404`). |

*\*At least one filter (`category`, `brand`, or `model`) must be supplied.*

#### Example 1: Valid Grounded Query

**Request:**
```text
GET /query?category=impresora&brand=EPSON&model=L355&question=%C2%BFC%C3%B3mo%20puedo%20saber%20si%20el%20nivel%20de%20tinta%20es%20bajo%3F
```

**Response (200 OK):**
```json
{
  "response": "Para resolver la consulta \"¿Cómo puedo saber si el nivel de tinta es bajo?\", sigue los siguientes pasos:\n1. Observe visualmente las ventanas transparentes de los tanques de tinta ubicados en el lateral del equipo.\n2. Verifique si el nivel de tinta se encuentra por debajo de la línea límite inferior marcada en el tanque.\n3. Si la luz indicadora de tinta parpadea en el panel de control, indica que el nivel está próximo a agotarse.\n\nFuente(s) de información:\n[EPSON-L355-USERMANUAL.pdf, Página 28]"
}
```

#### Example 2: Out-of-Scope Query (Refusal)

**Request:**
```text
GET /query?category=impresora&brand=EPSON&model=L355&question=%C2%BFC%C3%B3mo%20configurar%20un%20servidor%20DNS%20en%20esta%20impresora%3F
```

**Response (200 OK):**
```json
{
  "response": "No dispongo de información suficiente en los documentos para responder a esa pregunta."
}
```

---

## Production Roadmap

To scale this prototype into a production service:

1. **Hybrid Search (Dense + Sparse):** Combine Pinecone dense vector retrieval with BM25 / SPLADE keyword search to improve accuracy on exact hexadecimal error codes.
2. **Asynchronous Ingestion Queue:** Move ingestion to background workers (Celery / Redis) to support large file uploads without blocking.
3. **Automated Evaluation:** Integrate evaluation frameworks (e.g., Ragas, TruLens) to systematically track faithfulness, context recall, and hallucination rates over time.
4. **Containerization & CI/CD:** Package the service with Docker and deploy across managed container runtimes.