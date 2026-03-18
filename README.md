# 🖥️ DevOps Expert Assistant

> A locally-hosted, Windows 95-themed RAG chatbot that answers DevOps questions from real documentation — powered by Ollama, FAISS, and LangChain. No API keys. No cloud. No cost.

---

## 📸 Overview

This is a **Retrieval-Augmented Generation (RAG)** system built specifically for DevOps knowledge. It scrapes documentation from Kubernetes, Docker, CI/CD, Terraform, Helm, and GitOps sources, indexes it into a local FAISS vector store, and answers your questions strictly from that knowledge using a locally-running LLM.

The UI is styled as a **Windows 95 desktop application** — complete with title bars, a taskbar, retro fonts, green-on-black code blocks, and sound effects.

---

## ⚙️ Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| Language | Python 3.10 | Core runtime |
| LLM | llama3.2 (via Ollama) | Generates answers |
| Embeddings | nomic-embed-text (via Ollama) | Converts text to vectors |
| Vector DB | FAISS | Stores and searches embeddings |
| Reranker | ms-marco-MiniLM-L-6-v2 | Re-scores retrieved chunks |
| Orchestration | LangChain | Connects all pipeline components |
| Web Scraping | requests + BeautifulSoup4 | Fetches documentation pages |
| Document Loading | PyPDFLoader + TextLoader | Loads PDF, TXT, MD files |
| UI | Streamlit | Web interface on localhost:8501 |
| Config | python-dotenv | Loads .env variables |

**Total running cost: $0** — everything runs locally.

---

## 🗂️ Project Structure

```
devops-rag/
├── app/
│   ├── __init__.py
│   ├── config.py          # All settings loaded from .env
│   ├── scraper.py         # Web + local document loader
│   ├── chunker.py         # Clean, chunk, tag with metadata
│   ├── embedder.py        # Embed + cache + build FAISS index
│   ├── retriever.py       # FAISS search + cross-encoder rerank
│   ├── prompt.py          # LLM prompt template
│   └── pipeline.py        # Orchestrates query → answer flow
├── ui/
│   ├── __init__.py
│   ├── app.py             # Streamlit chat interface
│   └── static/            # Sound effect .wav files
├── data/
│   └── docs/              # Drop your PDF/TXT/MD files here
├── vector_store/          # Auto-generated FAISS index + cache
├── ingest.py              # CLI entry point for ingestion
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

### Step 1 — Clone and install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Pull Ollama models

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Step 3 — Configure environment

```bash
cp .env.example .env
```

Your `.env` file (no API keys needed for Ollama):

```env
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3.2
LLM_TEMPERATURE=0.0
MAX_TOKENS=1024
CHUNK_SIZE=800
CHUNK_OVERLAP=150
TOP_K=5
RERANK_TOP_K=3
SIMILARITY_THRESHOLD=0.30
```

### Step 4 — Add documents (optional)

Drop any `.pdf`, `.txt`, or `.md` files into `data/docs/`

### Step 5 — Run ingestion

```bash
# Test without API calls
python ingest.py --dry-run

# Ingest local files only
python ingest.py --local-only

# Full ingestion (scrapes web docs + local files)
python ingest.py

# Rebuild index from scratch
python ingest.py --rebuild
```

### Step 6 — Launch the chatbot

```bash
streamlit run ui/app.py
```

Open your browser at **http://localhost:8501**

---

## 🧠 How It Works

```
User Question
    ↓
nomic-embed-text converts question → vector
    ↓
FAISS searches for top 5 similar document chunks
    ↓
cross-encoder reranker re-scores → top 3 chunks
    ↓
LangChain formats chunks + question into prompt
    ↓
llama3.2 reads prompt → generates grounded answer
    ↓
Streamlit displays answer + source citations
```

### Key Design Decisions

**Why RAG instead of fine-tuning?**
RAG is cheaper, faster to update, and more explainable. You can add new documents without retraining the model.

**Why FAISS instead of a cloud vector DB?**
FAISS runs entirely on disk locally. No Pinecone account, no API, no latency, no cost.

**Why Ollama instead of OpenAI?**
Ollama runs models locally. No API key, no rate limits, no cost per query, data never leaves your machine.

**Why reranking?**
Vector similarity finds chunks that are semantically close but not always the most relevant. The cross-encoder reranker reads the question and each chunk together to give a more accurate relevance score.

---

## 💬 Ingestion CLI Reference

```bash
python ingest.py                      # Ingest all (web + local)
python ingest.py --local-only         # Local files only (no web scraping)
python ingest.py --dry-run            # Validate pipeline, no embedding
python ingest.py --rebuild            # Clear index and rebuild from scratch
python ingest.py --domain kubernetes  # Single domain only
```

---

## 📚 DevOps Knowledge Domains

| Domain | Sources |
|---|---|
| ☸ Kubernetes | kubernetes.io/docs |
| 🐳 Docker | docs.docker.com |
| ⚙ CI/CD | docs.github.com/actions, docs.gitlab.com/ee/ci |
| 🏗 Terraform | developer.hashicorp.com/terraform/docs |
| ⛵ Helm | helm.sh/docs |
| 🔄 GitOps | argo-cd.readthedocs.io, fluxcd.io/docs |

---

## 🎨 UI Features

- **Windows 95 aesthetic** — authentic retro styling with VT323 font, raised/sunken borders, teal desktop background
- **Boot screen** — Windows 95 style loading screen on first launch
- **Typing animation** — blinking `█` cursor while answer generates
- **Sound effects** — retro beep sounds on startup, click, success, and error
- **PDF drag and drop** — upload documents directly from the sidebar
- **Domain filters** — filter retrieval to specific DevOps domains
- **Source viewer** — expandable section showing exactly which chunks were used
- **Win95 error dialogs** — errors shown as authentic Windows 95 pop-up boxes

---

## 🛡️ Privacy & Security

- All processing happens **locally on your machine**
- Documents never leave your computer
- No telemetry, no cloud calls, no API keys required
- `.env` and `vector_store/` are gitignored by default

---

## 🐛 Common Issues

**`ModuleNotFoundError: No module named 'app'`**
Always run from the project root:
```bash
cd devops-rag
streamlit run ui/app.py
```

**Embedding model not found**
Make sure Ollama is running and the model is pulled:
```bash
ollama pull nomic-embed-text
ollama list
```

**Out of memory error with LLM**
Switch to a smaller model:
```bash
ollama pull llama3.2
# Update LLM_MODEL=llama3.2 in .env
```

**Rate limit errors (if using Gemini)**
Switch to Ollama (free, local) or wait for quota reset at midnight Pacific time.

**Fewer than 10 chunks indexed**
Add more documents to `data/docs/` or run `python ingest.py` to scrape web docs.

---

## 📦 Requirements

```
google-generativeai>=0.7.0
langchain>=0.2.0
langchain-google-genai>=1.0.0
langchain-community>=0.2.0
langchain-ollama>=1.0.0
faiss-cpu>=1.7.4
sentence-transformers>=2.7.0
beautifulsoup4>=4.12.0
pypdf>=3.0.0
python-dotenv>=1.0.0
tiktoken>=0.6.0
requests>=2.31.0
streamlit>=1.35.0
```

---

## 🏗️ Built With

- **[Antigravity](https://antigravity.dev)** — AI coding assistant that generated the initial codebase
- **[Ollama](https://ollama.com)** — Local LLM runtime
- **[LangChain](https://langchain.com)** — LLM orchestration framework
- **[FAISS](https://github.com/facebookresearch/faiss)** — Vector similarity search
- **[Streamlit](https://streamlit.io)** — Python web UI framework

---

## 📄 License

MIT License — free to use, modify, and distribute.
