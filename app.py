"""
Legal Document Q&A System — Main Streamlit Application
Upload law books (PDF/DOCX), ask questions, and get cited answers.
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Bootstrap: load .env before any other imports that need API keys
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Streamlit page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Legal Document Q&A",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — legal-themed dark blue header, citation boxes, chat bubbles
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ── Global ── */
body { font-family: 'Georgia', serif; }

/* ── Header banner ── */
.legal-header {
    background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0d2137 100%);
    color: #f0e6d3;
    padding: 2rem 2.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border-left: 6px solid #c9a84c;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.legal-header h1 { margin: 0; font-size: 2rem; letter-spacing: 1px; }
.legal-header p  { margin: 0.4rem 0 0; font-size: 0.95rem; color: #c9a84c; }

/* ── Citation box ── */
.citation-box {
    background: #f8f4ee;
    border: 1px solid #c9a84c;
    border-left: 4px solid #1a3a5c;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #2c2c2c;
}
.citation-box .cite-header {
    font-weight: bold;
    color: #1a3a5c;
    margin-bottom: 0.3rem;
    font-size: 0.9rem;
}
.citation-box .cite-meta {
    color: #555;
    font-size: 0.82rem;
    margin-bottom: 0.4rem;
}
.citation-box .cite-preview {
    font-style: italic;
    color: #444;
    border-top: 1px solid #ddd;
    padding-top: 0.4rem;
    margin-top: 0.4rem;
}

/* ── Chat messages ── */
.user-message {
    background: #e8f0fe;
    border-radius: 12px 12px 2px 12px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    border-left: 3px solid #1a73e8;
    max-width: 85%;
    margin-left: auto;
}
.assistant-message {
    background: #f0f4f0;
    border-radius: 12px 12px 12px 2px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    border-left: 3px solid #1a3a5c;
    max-width: 90%;
}

/* ── Stats card ── */
.stats-card {
    background: #243358;
    color: #f0e6d3;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    text-align: center;
    border: 1px solid #c9a84c;
}
.stats-card .stat-number {
    font-size: 1.8rem;
    font-weight: bold;
    color: #c9a84c;
}
.stats-card .stat-label {
    font-size: 0.8rem;
    color: #c8bfaf;
    margin-top: 0.2rem;
}

/* ── Upload area ── */
.upload-hint {
    background: #243358;
    border: 2px dashed #c9a84c;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    color: #e8dcc8 !important;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #1a2744;
    border-right: 2px solid #c9a84c;
}

/* All text inside sidebar: white on dark blue */
section[data-testid="stSidebar"] * {
    color: #f0e6d3 !important;
}

/* Sidebar headings */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {
    color: #c9a84c !important;
    font-weight: 700;
}

/* Sidebar markdown paragraphs and labels */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li {
    color: #e8dcc8 !important;
}

/* Sidebar divider */
section[data-testid="stSidebar"] hr {
    border-color: #c9a84c44;
}

/* Sidebar file uploader box */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #243358 !important;
    border: 1px dashed #c9a84c !important;
    border-radius: 8px;
}

/* Sidebar text input */
section[data-testid="stSidebar"] input[type="text"] {
    background: #243358 !important;
    color: #f0e6d3 !important;
    border: 1px solid #c9a84c88 !important;
    border-radius: 6px;
}
section[data-testid="stSidebar"] input[type="text"]::placeholder {
    color: #8899aa !important;
}

/* Sidebar info/success/error/warning boxes */
section[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: #243358 !important;
    border-radius: 6px;
}
section[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #f0e6d3 !important;
}

/* Sidebar success box */
section[data-testid="stSidebar"] .stSuccess {
    background: #1a3a2a !important;
    border-left: 3px solid #4caf50 !important;
}
section[data-testid="stSidebar"] .stError {
    background: #3a1a1a !important;
    border-left: 3px solid #f44336 !important;
}
section[data-testid="stSidebar"] .stInfo {
    background: #1a2a3a !important;
    border-left: 3px solid #2196f3 !important;
}
section[data-testid="stSidebar"] .stWarning {
    background: #3a2a1a !important;
    border-left: 3px solid #ff9800 !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: #c9a84c !important;
    color: #0a1628 !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 6px;
    width: 100%;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8c96a !important;
    color: #0a1628 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1a3a5c;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    transition: background 0.2s;
}
.stButton > button:hover {
    background: #0a1628;
    color: #c9a84c;
}

/* ── Scrollable chat container ── */
.chat-container {
    max-height: 60vh;
    overflow-y: auto;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #fafafa;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialise all required Streamlit session state keys."""
    defaults = {
        "messages": [],          # Chat history: [{"role": ..., "content": ...}]
        "vector_store": None,    # LegalVectorStore instance
        "qa_system": None,       # LegalQASystem instance
        "processed_files": [],   # Names of already-processed files
        "processing": False,     # Flag: document processing in progress
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ---------------------------------------------------------------------------
# Lazy imports (after env is loaded, to avoid import-time API key errors)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_vector_store(persist_dir: str = "./qdrant_storage"):
    """Create or reuse a cached LegalVectorStore instance."""
    from src.vector_store import LegalVectorStore
    store = LegalVectorStore(persist_directory=persist_dir)
    store.create_collection()
    return store


@st.cache_resource(show_spinner=False)
def get_qa_system(_vector_store):
    """Create or reuse a cached LegalQASystem instance."""
    from src.legal_qa import LegalQASystem
    return LegalQASystem(vector_store=_vector_store)


def get_document_processor():
    """Return a fresh LegalDocumentProcessor (not cached — stateless)."""
    from src.document_processor import LegalDocumentProcessor
    return LegalDocumentProcessor(chunk_size=500, chunk_overlap=100)


# ---------------------------------------------------------------------------
# Helper: check API key
# ---------------------------------------------------------------------------
def check_api_key() -> bool:
    """Return True if GROQ_API_KEY is set and non-empty."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    return bool(key) and key != "your_groq_api_key_here"


# ---------------------------------------------------------------------------
# Helper: save uploaded file to temp location
# ---------------------------------------------------------------------------
def save_uploaded_file(uploaded_file) -> str:
    """
    Save a Streamlit UploadedFile to a temporary file and return its path.
    The caller is responsible for deleting the file when done.
    """
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, prefix="legal_upload_"
    ) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Render the sidebar with file upload, processing, and stats."""
    with st.sidebar:
        st.markdown("## ⚖️ Legal RAG System")
        st.markdown("---")

        # ── API Key status ──
        # if check_api_key():
        #     st.success("✅ Groq API key loaded")
        # else:
        #     st.error("❌ GROQ_API_KEY missing")
        #     st.markdown(
        #         "Add your key to `.env`:\n```\nGROQ_API_KEY=gsk_...\n```\n"
        #         "[Get a free key →](https://console.groq.com/keys)"
        #     )
        #     st.markdown("---")

        # ── File upload ──
        st.markdown("### 📄 Upload Legal Document")
        st.markdown(
            '<div class="upload-hint">Supports PDF and DOCX law books</div>',
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx"],
            help="Upload a PDF or DOCX legal document (law book, statute, contract, etc.)",
            label_visibility="collapsed",
        )

        if uploaded_file:
            file_size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
            st.info(
                f"📎 **{uploaded_file.name}**\n\n"
                f"Size: {file_size_mb:.2f} MB"
            )

            already_processed = uploaded_file.name in st.session_state.processed_files

            if already_processed:
                st.success("✅ Already processed")
            else:
                if st.button("⚙️ Process Document", use_container_width=True):
                    process_document(uploaded_file)

        st.markdown("---")

        # ── Collection stats ──
        st.markdown("### 📊 Knowledge Base")
        render_stats()

        st.markdown("---")

        # ── Clear chat ──
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.qa_system:
                st.session_state.qa_system.clear_memory()
            st.rerun()

        # ── Article filter ──
        st.markdown("### 🔍 Search Filter")
        article_filter = st.text_input(
            "Filter by Article/Section",
            placeholder="e.g. Article 5",
            help="Restrict answers to a specific article or section number",
        )
        st.session_state["article_filter"] = article_filter.strip() or None

        st.markdown("---")
        st.markdown(
            "<small style='color:#888'>Legal RAG System v1.0<br>"
            " </small>",
            unsafe_allow_html=True,
        )


def render_stats() -> None:
    """Display collection statistics in the sidebar."""
    try:
        store = get_vector_store()
        stats = store.get_collection_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'<div class="stats-card">'
                f'<div class="stat-number">{stats["total_chunks"]}</div>'
                f'<div class="stat-label">Chunks</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with col2:
            doc_count = len(stats.get("unique_sources", []))
            st.markdown(
                f'<div class="stats-card">'
                f'<div class="stat-number">{doc_count}</div>'
                f'<div class="stat-label">Documents</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if stats.get("unique_sources"):
            st.markdown("**Loaded documents:**")
            for src in stats["unique_sources"]:
                st.markdown(f"- 📄 {src}")
    except Exception as e:
        st.warning(f"Could not load stats: {e}")


# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------
def process_document(uploaded_file) -> None:
    """Process an uploaded document: chunk, embed, and store in Qdrant."""
    tmp_path = None
    try:
        st.session_state.processing = True

        with st.spinner(f"Processing '{uploaded_file.name}'..."):
            # Save to temp file
            tmp_path = save_uploaded_file(uploaded_file)

            # Ensure data directory exists
            os.makedirs("./data", exist_ok=True)

            # Process the document
            processor = get_document_processor()
            chunks = processor.process_law_book(tmp_path)

            # Store in vector database
            store = get_vector_store()
            added = store.add_documents(chunks, source_file=uploaded_file.name)

            # Mark as processed
            st.session_state.processed_files.append(uploaded_file.name)

        st.success(
            f"✅ Processed **{uploaded_file.name}**\n\n"
            f"Added **{added}** chunks to the knowledge base."
        )
        logger.info(f"Processed '{uploaded_file.name}': {added} chunks added")

    except FileNotFoundError as e:
        st.error(f"❌ File error: {e}")
    except ValueError as e:
        st.error(f"❌ Format error: {e}")
    except RuntimeError as e:
        st.error(f"❌ Processing failed: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        logger.exception(f"Unexpected error processing '{uploaded_file.name}'")
    finally:
        st.session_state.processing = False
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Chat interface
# ---------------------------------------------------------------------------
def render_chat() -> None:
    """Render the main chat interface with message history."""
    # Display existing messages
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(content)
                # Show source citations in an expander
                if sources:
                    render_citations(sources)

    # Chat input
    if prompt := st.chat_input(
        "Ask a question about the legal documents...",
        disabled=not check_api_key(),
    ):
        handle_user_question(prompt)


def handle_user_question(question: str) -> None:
    """Process a user question and display the answer with citations."""
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # Check prerequisites
    if not check_api_key():
        error_msg = "⚠️ Please add your GROQ_API_KEY to the `.env` file to use the Q&A system."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant", avatar="⚖️"):
            st.warning(error_msg)
        return

    store = get_vector_store()
    if not store.collection_exists():
        error_msg = (
            "📄 No documents have been processed yet. "
            "Please upload and process a legal document using the sidebar."
        )
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant", avatar="⚖️"):
            st.info(error_msg)
        return

    # Get or create QA system
    try:
        qa = get_qa_system(store)
    except ValueError as e:
        error_msg = f"❌ Configuration error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant", avatar="⚖️"):
            st.error(error_msg)
        return

    # Ask the question
    article_filter = st.session_state.get("article_filter")

    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Searching legal documents and generating answer..."):
            try:
                result = qa.ask_question(
                    question=question,
                    filter_article=article_filter,
                    k=5,
                )
                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)
                if sources:
                    render_citations(sources)

                # Save to session history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except RuntimeError as e:
                error_msg = f"❌ Error getting answer: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
            except Exception as e:
                error_msg = f"❌ Unexpected error: {e}"
                st.error(error_msg)
                logger.exception("Unexpected error in handle_user_question")
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )


def render_citations(sources: list) -> None:
    """Render source citations in a collapsible expander."""
    if not sources:
        return

    with st.expander(f"📚 View {len(sources)} Source Citation(s)", expanded=False):
        for i, source in enumerate(sources, 1):
            article = source.get("article") or "N/A"
            page = source.get("page", "N/A")
            source_file = source.get("source_file", "Unknown Document")
            score = source.get("score", 0)
            preview = source.get("text_preview", "No preview available")

            # Relevance badge color
            if score >= 0.8:
                relevance_color = "#2e7d32"  # green
                relevance_label = "High"
            elif score >= 0.6:
                relevance_color = "#e65100"  # orange
                relevance_label = "Medium"
            else:
                relevance_color = "#c62828"  # red
                relevance_label = "Low"

            st.markdown(
                f"""
                <div class="citation-box">
                    <div class="cite-header">📖 Source {i} — {article}</div>
                    <div class="cite-meta">
                        📄 <strong>{source_file}</strong> &nbsp;|&nbsp;
                        📃 Page {page} &nbsp;|&nbsp;
                        <span style="color:{relevance_color}">
                            ● {relevance_label} relevance ({score:.1%})
                        </span>
                    </div>
                    <div class="cite-preview">{preview}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Database Viewer page
# ---------------------------------------------------------------------------
def render_db_viewer() -> None:
    """Full database viewer — browse every chunk stored in Qdrant."""
    st.markdown(
        """
        <div class="legal-header">
            <h1>🗄️ Database Viewer</h1>
            <p>Browse every chunk, vector, and metadata record stored in Qdrant</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    store = get_vector_store()
    stats = store.get_collection_stats()

    # ── Top summary cards ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("📦 Total Chunks", stats["total_chunks"])
    with c2:
        st.metric("📄 Documents", len(stats.get("unique_sources", [])))
    with c3:
        st.metric("🔢 Vector Dimensions", "384")
    with c4:
        st.metric("📐 Distance Metric", "Cosine")

    st.markdown("---")

    if not stats["exists"] or stats["total_chunks"] == 0:
        st.info(
            "### 📭 Database is empty\n\n"
            "Upload and process a legal document from the **Q&A Chat** tab "
            "to populate the database."
        )
        return

    # ── Connection info ────────────────────────────────────────────────────
    with st.expander("🔌 Connection Details", expanded=False):
        st.markdown(
            f"""
            | Property | Value |
            |---|---|
            | **Mode** | Local file (no Docker/server) |
            | **Storage path** | `./qdrant_storage/` |
            | **Storage file** | `storage.sqlite` |
            | **Collection** | `{stats['collection_name']}` |
            | **Status** | 🟢 Connected & Active |
            | **Vector size** | 384 dimensions |
            | **Distance** | Cosine similarity |
            | **Embedding model** | sentence-transformers/all-MiniLM-L6-v2 |
            """
        )

    # ── Per-document breakdown ─────────────────────────────────────────────
    st.markdown("### 📄 Documents in Database")
    sources = stats.get("unique_sources", [])
    if sources:
        for src in sources:
            st.markdown(
                f"""
                <div class="citation-box">
                    <div class="cite-header">📄 {src}</div>
                    <div class="cite-meta">Stored in collection: <strong>{stats['collection_name']}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Browse chunks ──────────────────────────────────────────────────────
    st.markdown("### 🔍 Browse Stored Chunks")

    # Controls row
    ctrl1, ctrl2, ctrl3 = st.columns([2, 2, 1])
    with ctrl1:
        filter_source = st.selectbox(
            "Filter by document",
            options=["All documents"] + sources,
            key="db_filter_source",
        )
    with ctrl2:
        search_text = st.text_input(
            "Search in chunk text",
            placeholder="e.g. termination, wages, Article 5...",
            key="db_search_text",
        )
    with ctrl3:
        page_size = st.selectbox(
            "Rows per page",
            options=[10, 25, 50, 100],
            index=1,
            key="db_page_size",
        )

    # Fetch all records via scroll
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        scroll_filter = None
        if filter_source != "All documents":
            scroll_filter = Filter(
                must=[FieldCondition(key="source_file", match=MatchValue(value=filter_source))]
            )

        all_points = []
        offset = None
        while True:
            batch, next_offset = store.client.scroll(
                collection_name=store.collection_name,
                scroll_filter=scroll_filter,
                limit=250,
                offset=offset,
                with_payload=True,
                with_vectors=False,   # don't load 384-float arrays into UI
            )
            all_points.extend(batch)
            if next_offset is None:
                break
            offset = next_offset

    except Exception as e:
        st.error(f"Could not fetch records: {e}")
        return

    # Apply text search filter
    if search_text.strip():
        q = search_text.strip().lower()
        all_points = [
            p for p in all_points
            if q in (p.payload.get("text", "") or "").lower()
            or q in (p.payload.get("article", "") or "").lower()
        ]

    total_filtered = len(all_points)
    st.caption(f"Showing **{total_filtered}** chunk(s) matching your filters")

    if total_filtered == 0:
        st.warning("No chunks match the current filters.")
        return

    # Pagination
    total_pages = max(1, (total_filtered + page_size - 1) // page_size)
    if "db_page" not in st.session_state:
        st.session_state.db_page = 1
    # Reset page when filters change
    if st.session_state.get("_last_filter") != (filter_source, search_text):
        st.session_state.db_page = 1
        st.session_state["_last_filter"] = (filter_source, search_text)

    page = st.session_state.db_page
    start = (page - 1) * page_size
    end = min(start + page_size, total_filtered)
    page_points = all_points[start:end]

    # ── Table view ─────────────────────────────────────────────────────────
    import pandas as pd

    rows = []
    for p in page_points:
        pl = p.payload or {}
        rows.append({
            "ID (short)":    str(p.id)[:8] + "...",
            "Source File":   pl.get("source_file", "—"),
            "Article":       pl.get("article") or "—",
            "Page":          pl.get("page", "—"),
            "Text Preview":  (pl.get("text", "") or "")[:120].replace("\n", " ") + "...",
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID (short)":   st.column_config.TextColumn("ID", width="small"),
            "Source File":  st.column_config.TextColumn("Document", width="medium"),
            "Article":      st.column_config.TextColumn("Article/Section", width="medium"),
            "Page":         st.column_config.TextColumn("Page", width="small"),
            "Text Preview": st.column_config.TextColumn("Chunk Preview", width="large"),
        },
    )

    # Pagination controls
    pg_col1, pg_col2, pg_col3 = st.columns([1, 3, 1])
    with pg_col1:
        if st.button("◀ Prev", disabled=(page <= 1), key="db_prev"):
            st.session_state.db_page = max(1, page - 1)
            st.rerun()
    with pg_col2:
        st.markdown(
            f"<div style='text-align:center; padding-top:0.5rem; color:#555'>"
            f"Page <strong>{page}</strong> of <strong>{total_pages}</strong> "
            f"&nbsp;·&nbsp; records {start+1}–{end} of {total_filtered}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with pg_col3:
        if st.button("Next ▶", disabled=(page >= total_pages), key="db_next"):
            st.session_state.db_page = min(total_pages, page + 1)
            st.rerun()

    st.markdown("---")

    # ── Full chunk detail expander ─────────────────────────────────────────
    st.markdown("### 🔎 Inspect Full Chunk")
    st.caption("Pick a row number from the table above to read the complete text")

    row_num = st.number_input(
        "Row number (1-based from current page)",
        min_value=1,
        max_value=len(page_points),
        value=1,
        step=1,
        key="db_row_select",
    )
    selected = page_points[int(row_num) - 1]
    pl = selected.payload or {}

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("**Metadata**")
        st.markdown(
            f"""
            | Field | Value |
            |---|---|
            | **ID** | `{selected.id}` |
            | **Document** | {pl.get('source_file', '—')} |
            | **Article** | {pl.get('article') or '—'} |
            | **Page** | {pl.get('page', '—')} |
            | **File hash** | `{(pl.get('file_hash') or '—')[:16]}...` |
            """
        )
    with col_b:
        st.markdown("**Full Chunk Text**")
        st.text_area(
            label="chunk_text",
            value=pl.get("text", ""),
            height=220,
            disabled=True,
            label_visibility="collapsed",
            key="db_chunk_text",
        )

    # ── Semantic search test ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🧪 Test Semantic Search")
    st.caption("Type a query to see which chunks the vector search retrieves — exactly what the LLM sees")

    test_query = st.text_input(
        "Test query",
        placeholder="e.g. What is the penalty for unfair dismissal?",
        key="db_test_query",
    )
    k_results = st.slider("Number of results", 1, 10, 5, key="db_k")

    if st.button("🔍 Run Search", key="db_run_search"):
        if not test_query.strip():
            st.warning("Enter a query first.")
        else:
            with st.spinner("Searching..."):
                results = store.search(query=test_query, k=k_results)

            if not results:
                st.info("No results found.")
            else:
                st.success(f"Found {len(results)} result(s)")
                for i, r in enumerate(results, 1):
                    score = r.get("score", 0)
                    bar_color = "#2e7d32" if score >= 0.8 else "#e65100" if score >= 0.6 else "#c62828"
                    with st.expander(
                        f"#{i} — {r.get('article') or 'No article'} | "
                        f"{r.get('source_file','?')} | Score: {score:.1%}",
                        expanded=(i == 1),
                    ):
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <div class="cite-header">
                                    📖 {r.get('article') or 'No article reference'}
                                    &nbsp;
                                    <span style="color:{bar_color}; font-size:0.85rem">
                                        ● {score:.1%} similarity
                                    </span>
                                </div>
                                <div class="cite-meta">
                                    📄 {r.get('source_file','Unknown')} &nbsp;|&nbsp;
                                    Page {r.get('page','?')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.text_area(
                            "Full text",
                            value=r.get("text", ""),
                            height=160,
                            disabled=True,
                            key=f"db_result_{i}",
                        )


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
def main() -> None:
    """Main application entry point."""

    # ── Sidebar (always visible) ──
    render_sidebar()

    # ── Tab navigation ──
    tab_chat, tab_db = st.tabs(["💬 Q&A Chat", "🗄️ Database Viewer"])

    with tab_chat:
        # Header
        st.markdown(
            """
            <div class="legal-header">
                <h1>⚖️ Legal Document Q&amp;A System</h1>
                <p>Upload law books · Ask questions · Get cited answers from your documents</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not check_api_key():
            st.warning(
                "### ⚠️ Setup Required\n\n"
                "Your **GROQ_API_KEY** is not configured. To get started:\n\n"
                "1. Visit [console.groq.com/keys](https://console.groq.com/keys) "
                "to get a free API key\n"
                "2. Open the `.env` file in this project\n"
                "3. Replace `your_groq_api_key_here` with your actual key\n"
                "4. Restart the application\n\n"
                "The embedding model (sentence-transformers) works locally — "
                "only the LLM requires an API key."
            )
            st.stop()

        store = get_vector_store()
        if not store.collection_exists():
            st.info(
                "### 👋 Welcome to the Legal Document Q&A System\n\n"
                "**Getting started:**\n"
                "1. 📄 Upload a PDF or DOCX legal document using the **sidebar**\n"
                "2. ⚙️ Click **Process Document** to extract and index the content\n"
                "3. 💬 Ask questions in the chat below — answers include article citations\n\n"
                "**Supported documents:** Law books, statutes, contracts, regulations, "
                "court decisions, and any structured legal text."
            )

        render_chat()

    with tab_db:
        render_db_viewer()


if __name__ == "__main__":
    main()
