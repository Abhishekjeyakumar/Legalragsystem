# ⚖️ Legal Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) system for legal documents. Upload law books (PDF/DOCX), ask natural language questions, and receive precise answers with article citations — all powered by local embeddings and Groq's LLM.

---

## Features

- **PDF & DOCX support** — Upload any law book, statute, contract, or regulation
- **Article-aware chunking** — Respects Article, Section, and § boundaries during text splitting
- **Local embeddings** — Uses `sentence-transformers/all-MiniLM-L6-v2` (free, no API key)
- **Persistent vector storage** — Qdrant runs locally (no Docker required)
- **Citation-backed answers** — Every answer references the specific article and page
- **Conversation memory** — Follow-up questions maintain context from previous turns
- **Article filter** — Restrict search to a specific article or section
- **Legal-themed UI** — Professional dark blue interface with citation boxes

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| UI | Streamlit | 1.35.0 |
| Vector DB | Qdrant (local mode) | 1.9.0 |
| Embeddings | sentence-transformers | 2.2.2 |
| Orchestration | LangChain | 0.3.0 |
| LLM | Groq (llama-3.3-70b-versatile) | — |
| PDF parsing | PyPDF | 5.0.0 |
| DOCX parsing | python-docx | 1.1.0 |

---

## Requirements

- **Python 3.11** (critical — do NOT use 3.12, 3.13, or 3.14)
- A free [Groq API key](https://console.groq.com/keys)
- ~2 GB disk space (for the embedding model cache)
- Internet connection (first run only, to download the embedding model)

---

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd legal-rag-system
```

### 2. Create a Python 3.11 virtual environment

```bash
# Using conda (recommended)
conda create -n legal-rag python=3.11
conda activate legal-rag

# Or using pyenv + venv
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The first install downloads PyTorch (~800 MB) and the sentence-transformers model (~90 MB). This is a one-time operation.

### 4. Configure your Groq API key

Open `.env` and replace the placeholder:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

Get a free key at [console.groq.com/keys](https://console.groq.com/keys).

### 5. Run the application

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Usage Guide

### Uploading a Document

1. In the **sidebar**, click "Browse files" under "Upload Legal Document"
2. Select a PDF or DOCX file (law book, statute, contract, etc.)
3. Click **⚙️ Process Document**
4. Wait for the spinner — processing time depends on document size
5. The sidebar stats update to show the number of chunks indexed

### Asking Questions

1. Type your question in the chat input at the bottom
2. Press Enter or click the send button
3. The system retrieves the 5 most relevant passages and generates a cited answer
4. Click **"View Source Citations"** to see the exact passages used

### Using the Article Filter

- In the sidebar under "Search Filter", enter an article number (e.g., `Article 5`)
- All subsequent questions will only search within that article
- Clear the field to search across all documents

### Example Questions

```
What are the penalties for breach of contract under Article 12?
What rights does a tenant have under Section 3?
Explain the conditions for termination of employment.
What is the statute of limitations for civil claims?
```

---

## Project Structure

```
legal-rag-system/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Pinned dependencies
├── .env                      # API key (never commit this)
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── document_processor.py # PDF/DOCX loading and legal-aware chunking
│   ├── vector_store.py       # Qdrant local mode + sentence-transformer embeddings
│   ├── legal_qa.py           # Groq LLM + citation-enforcing prompt + memory
│   └── utils.py              # Article extraction, file hashing, text cleaning
│
├── data/                     # Uploaded documents (auto-created)
└── qdrant_storage/           # Qdrant persistent storage (auto-created)
```

---

## How It Works

```
User uploads PDF/DOCX
        │
        ▼
LegalDocumentProcessor
  ├── PyPDFLoader / Docx2txtLoader
  ├── clean_text() — normalize whitespace
  ├── RecursiveCharacterTextSplitter
  │     separators: [\n\n, \nArticle, \nSection, \n§, \n, " "]
  │     chunk_size: 500, overlap: 100
  └── extract_article_number() — tag each chunk
        │
        ▼
LegalVectorStore (Qdrant local)
  ├── SentenceTransformer("all-MiniLM-L6-v2") → 384-dim vectors
  ├── Cosine similarity index
  └── Persistent storage in ./qdrant_storage/
        │
        ▼
User asks a question
        │
        ▼
LegalVectorStore.search()
  └── Top-5 semantically similar chunks
        │
        ▼
LegalQASystem (Groq llama-3.3-70b-versatile)
  ├── Legal prompt: "Answer ONLY from context, cite articles"
  ├── ConversationBufferMemory (last 3 exchanges)
  └── Returns answer + source citations
        │
        ▼
Streamlit UI renders answer + citation boxes
```

---

## Troubleshooting

### "GROQ_API_KEY missing" error
- Ensure `.env` exists in the project root
- The key must start with `gsk_`
- Restart the app after editing `.env`

### "No module named 'qdrant_client'"
```bash
pip install qdrant-client==1.9.0
```

### Slow first startup
The sentence-transformers model (~90 MB) downloads on first use. Subsequent starts are fast.

### "Information not found in the provided legal documents"
- The document may not contain the answer
- Try rephrasing the question
- Check that the document was processed (sidebar shows chunk count > 0)
- Remove the article filter if one is set

### PDF shows 0 chunks
- The PDF may be scanned (image-only). Use a text-based PDF.
- Try converting with OCR tools like Adobe Acrobat or `ocrmypdf`

### Python version errors
This project requires **Python 3.11 exactly**. Check with:
```bash
python --version
```

### Windows: "python-magic" installation error
The `requirements.txt` uses `python-magic-bin` on Windows automatically. If you still get errors:
```bash
pip install python-magic-bin==0.4.14
```

### Qdrant storage corruption
Delete the storage directory and reprocess your documents:
```bash
rm -rf qdrant_storage/
```

---

## Configuration

Key settings are in the source files:

| Setting | Location | Default | Description |
|---------|----------|---------|-------------|
| `chunk_size` | `app.py` → `get_document_processor()` | 500 | Characters per chunk |
| `chunk_overlap` | `app.py` → `get_document_processor()` | 100 | Overlap between chunks |
| `k` (search results) | `app.py` → `handle_user_question()` | 5 | Chunks retrieved per query |
| `temperature` | `src/legal_qa.py` | 0.1 | LLM creativity (lower = more factual) |
| `model` | `src/legal_qa.py` | llama-3.3-70b-versatile | Groq model |

---

## License

MIT License — free for personal and commercial use.

---

## Acknowledgements

- [Groq](https://groq.com) — Ultra-fast LLM inference
- [Qdrant](https://qdrant.tech) — Vector database
- [Sentence Transformers](https://www.sbert.net) — Local embeddings
- [LangChain](https://langchain.com) — LLM orchestration
- [Streamlit](https://streamlit.io) — UI framework
