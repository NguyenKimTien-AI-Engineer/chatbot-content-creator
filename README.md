# KAT Content Studio

An AI-powered content creation platform built for brand teams. It combines a **FastAPI** backend, a **Next.js** web interface, and **Retrieval-Augmented Generation (RAG)** to help teams draft marketing copy, fanpage captions, product descriptions, and conversational answers grounded in uploaded documents and product data.

Designed for premium leather and lifestyle brands (default configuration: **KAT Leather**), the system is model-agnostic at the infrastructure level and currently runs on **Google Gemini** for chat, vision, and embeddings.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Overview](#api-overview)
- [Optional Services](#optional-services)
- [Development](#development)
- [Documentation](#documentation)
- [License & Attribution](#license--attribution)

---

## Overview

KAT Content Studio is an end-to-end chatbot and content assistant that:

- Generates on-brand marketing and social content through customizable prompts
- Retrieves relevant context from vector stores (Qdrant) and product catalogs (MongoDB)
- Streams responses token-by-token for a responsive chat experience
- Persists conversation history for multi-session workflows
- Supports document ingestion (PDF, DOCX, TXT, and more) for knowledge-base Q&A

The application replaces the legacy Streamlit UI with a modern, ChatGPT-style interface featuring sidebar navigation, chat history, bilingual support (English / Vietnamese), and a centralized settings panel.

---

## Key Features

### Content & Chat

- **Custom prompt chatbot** with brand tone, checklist, and template-driven output
- **Server-Sent Events (SSE) streaming** for real-time token delivery
- **Suggested prompts** for marketing, captions, product advice, and strategy
- **Image analysis** via Gemini Vision (upload images in chat)
- **Chart generation** when users request visual summaries

### Knowledge & Retrieval

- **Semantic search** over Qdrant vector collections
- **Multi-format document processing** with OCR support (PDF, DOCX, TXT, HTML, CSV, XLSX)
- **Product-aware responses** with MongoDB-backed catalog lookup
- **Reference citations** linked to retrieved document chunks

### Web Application

- **Next.js 15** frontend with responsive layout
- **Chat history sidebar** synced with MongoDB conversations API
- **Settings hub** for models, API endpoints, brand profile, and chat behavior
- **Internationalization (i18n)** — English and Vietnamese

### Platform

- **FastAPI** REST API with CORS enabled
- **Modular backend** — chatbot, history, products, documents, and image routes
- **Docker-ready** deployment configuration

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Next.js UI  (:3000)                     │
│   Chat · Settings · Home · Sidebar History · i18n           │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / SSE (proxied /api/*)
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend  (:1979)                  │
│  chatbot · history · products · document · image            │
└──────┬──────────────┬──────────────┬─────────────────────────┘
       │              │              │
       ▼              ▼              ▼
  Google Gemini   Qdrant         MongoDB
  (chat/embed)   (vectors)    (history/products)
```

During local development, the Next.js dev server proxies `/api/*` requests to the FastAPI backend on port `1979`.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, Radix UI, Zustand |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, LangChain, LangChain Google GenAI |
| **AI** | Google Gemini (chat, mini, embedding, vision models) |
| **Vector DB** | Qdrant |
| **Document / App DB** | MongoDB |
| **Optional** | MySQL, Neo4j, AWS S3, Tesseract OCR |

---

## Prerequisites

- **Python** 3.10 or newer
- **Node.js** 18+ and npm
- **Google Gemini API key** ([Google AI Studio](https://aistudio.google.com/))
- **Qdrant** (recommended for RAG) — local Docker or remote instance
- **MongoDB** (recommended for chat history and products)

### System dependencies (document processing)

For full document ingestion and OCR capabilities:

```bash
sudo apt-get update && sudo apt-get install -y \
  build-essential tesseract-ocr libtesseract-dev poppler-utils \
  ffmpeg libsm6 libxext6
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/NguyenKimTien-AI-Engineer/chatbot-content-creator.git
cd chatbot-content-creator
```

### 2. Backend setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements_full.txt
pip install 'uvicorn[standard]'

cp .env.example .env
# Edit .env and set at minimum GEMINI_API_KEY
```

### 3. Frontend setup

```bash
cd ui
npm install
cd ..
```

### 4. Start Qdrant (optional but recommended)

```bash
docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage" \
  qdrant/qdrant
```

### 5. Run the services

**Terminal 1 — API**

```bash
source .venv/bin/activate
python app.py
```

**Terminal 2 — UI**

```bash
cd ui
npm run dev
```

Open **http://localhost:3000** in your browser. The API is available at **http://localhost:1979**.

---

## Configuration

Copy `.env.example` to `.env` and configure the variables below.

### Required

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `SERVER_ADDRESS` | Public API base URL (default: `http://localhost:1979`) |

### AI models

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_CHAT_MODEL` | `gemini-2.5-flash` | Primary chat model |
| `GEMINI_CHAT_MODEL_MINI` | `gemini-2.5-flash-lite` | Lightweight / fallback model |
| `GEMINI_EMBEDDING_MODEL` | `models/gemini-embedding-001` | Text embeddings |
| `GEMINI_VISION_MODEL` | `gemini-2.5-flash` | Image understanding |

### Vector search (Qdrant)

| Variable | Description |
|----------|-------------|
| `QDRANT_HOST` | Qdrant host |
| `QDRANT_PORT` | Qdrant port (default: `6333`) |
| `QDRANT_SERVER` | Full Qdrant URL, e.g. `http://localhost:6333` |
| `QDRANT_API_KEY` | API key (if using Qdrant Cloud) |

### Databases

| Variable | Description |
|----------|-------------|
| `MONGODB_HOST`, `MONGODB_PORT`, `MONGODB_DATABASE`, … | MongoDB connection for chat history and products |
| `MYSQL_DB_*` | Optional MySQL integration |

> **Security:** Never commit `.env` or API keys to version control.

---

## Running the Application

### Development

```bash
# Backend
python app.py

# Frontend
cd ui && npm run dev
```

### Production (UI)

```bash
cd ui
npm run build
npm run start:prod
```

Ensure `NEXT_PUBLIC_SERVER_HOST` and `NEXT_PUBLIC_API_PORT` are set so the UI can reach the API in production, or place both services behind a reverse proxy.

### Docker

Build and run the backend container:

```bash
docker build -t kat-content-studio:latest .

docker run -d -p 1979:1979 \
  --name kat-content-studio \
  -e GEMINI_API_KEY="your-key" \
  -e QDRANT_SERVER="http://host.docker.internal:6333" \
  kat-content-studio:latest
```

---

## Project Structure

```text
chatbot-content-creator/
├── api/                    # FastAPI route modules
├── bot/v1/                 # Chatbot logic and prompt orchestration
├── configs/                # Constants, environment, and prompt templates
├── controllers/            # Business logic (RAG, documents, databases, LLM)
├── resources/              # Data, logs, docs, and static assets
├── tests/                  # Backend tests
├── ui/                     # Next.js frontend application
│   ├── app/                # App Router pages (chat, settings, home)
│   ├── components/         # UI and layout components
│   ├── lib/                # API client, i18n, utilities
│   └── store/              # Zustand state (settings, chat sessions)
├── app.py                  # FastAPI entry point
├── .env.example            # Environment template
├── requirements_full.txt   # Python dependencies
└── Dockerfile              # Container build definition
```

---

## API Overview

Base URL: `http://localhost:1979/api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chatbot-custom-prompt` | POST | Custom-prompt chat (JSON response) |
| `/v1/chatbot-custom-prompt-stream` | POST | Custom-prompt chat (SSE stream) |
| `/v1/chatbot-reference` | POST | Reference-grounded chat |
| `/v1/chatbot-chart-stream` | POST | Chart-oriented chat stream |
| `/v1/analyze-image` | POST | Image analysis |
| `/v1/histories/list` | POST | List chat conversations |
| `/v1/histories/get` | POST | Fetch a conversation |
| `/v1/histories/create` | POST | Create a conversation |
| `/v1/histories/delete` | POST | Delete a conversation |
| `/v1/upload-files` | POST | Upload documents to Qdrant *(if document module enabled)* |

Interactive API docs: **http://localhost:1979/docs**

---

## Optional Services

| Service | Purpose |
|---------|---------|
| **Qdrant** | Vector storage and semantic retrieval for RAG |
| **MongoDB** | Persistent chat history and product catalog |
| **Tesseract** | OCR for scanned PDFs and images |
| **AWS S3** | Object storage for media assets |
| **Neo4j** | Graph-based knowledge (optional integration) |

The chatbot works without Qdrant and MongoDB, but document retrieval, product lookup, and sidebar history will be limited or unavailable.

---

## Development

### Frontend tests

```bash
cd ui
npm run test
```

### Backend tests

```bash
source .venv/bin/activate
pytest tests/
```

### Prompt customization

Brand prompts and output templates live under:

```text
configs/prompts/custom/
├── system.py
├── checklist.py
├── template_content.py
└── prompt_chatbot_custom.py
```

Adjust these files to change tone, structure, and compliance rules without modifying core application code.

### UI settings

Runtime preferences (models, API host, brand name, streaming toggle) are managed in the **Settings** page and persisted in the browser via Zustand.

---

## Documentation

Additional technical references:

- [Detailed system functions](enhanced_system/docs/DETAILED_FUNCTIONS.md)
- [Performance optimization](enhanced_system/docs/PERFORMANCE_OPTIMIZATION.md)
- [Project structure (legacy)](resources/docs/project_structure.md)

---

## License & Attribution

This project builds on the MekongAI RAG template architecture and has been extended for brand content creation workflows.

For questions, issues, or contributions, please open an issue or pull request on the repository.

---

**KAT Content Studio** — AI-assisted content creation for modern brand teams.
