"""
Document processor for the Legal RAG System.
Handles loading, cleaning, and chunking of PDF and DOCX legal documents.
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils import extract_article_number, clean_text, get_file_hash

logger = logging.getLogger(__name__)


class LegalDocumentProcessor:
    """
    Processes legal documents (PDF/DOCX) into structured chunks with metadata.

    Designed for legal precision with smaller chunk sizes and legal-aware
    text splitting that respects article and section boundaries.
    """

    # Legal-specific separators ordered by priority
    LEGAL_SEPARATORS = [
        "\n\n",        # Paragraph breaks (highest priority)
        "\nArticle",   # Article boundaries
        "\nARTICLE",
        "\nSection",   # Section boundaries
        "\nSECTION",
        "\n§",         # § symbol boundaries
        "\n",          # Line breaks
        " ",           # Word boundaries (fallback)
        "",            # Character boundaries (last resort)
    ]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize the document processor.

        Args:
            chunk_size: Maximum characters per chunk. Default 500 for legal precision.
            chunk_overlap: Characters of overlap between chunks. Default 100.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.LEGAL_SEPARATORS,
            length_function=len,
            is_separator_regex=False,
        )

        logger.info(
            f"LegalDocumentProcessor initialized: chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )

    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a PDF or DOCX document and return a list of LangChain Documents.

        Each Document contains the page/section text and basic metadata
        (source file, page number for PDFs).

        Args:
            file_path: Absolute or relative path to the document.

        Returns:
            List of Document objects with page_content and metadata.

        Raises:
            ValueError: If the file format is not supported.
            FileNotFoundError: If the file does not exist.
            RuntimeError: If the document cannot be loaded.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        suffix = path.suffix.lower()
        logger.info(f"Loading document: {path.name} (format: {suffix})")

        try:
            if suffix == ".pdf":
                documents = self._load_pdf(file_path)
            elif suffix in (".docx", ".doc"):
                documents = self._load_docx(file_path)
            else:
                raise ValueError(
                    f"Unsupported file format: '{suffix}'. "
                    "Only PDF (.pdf) and Word (.docx) files are supported."
                )
        except (ValueError, FileNotFoundError):
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to load document '{path.name}': {e}") from e

        # Clean text content in each document
        for doc in documents:
            doc.page_content = clean_text(doc.page_content)
            # Ensure source metadata is set
            doc.metadata.setdefault("source", str(path.name))
            doc.metadata.setdefault("file_path", str(file_path))

        # Filter out empty documents
        documents = [d for d in documents if d.page_content.strip()]

        logger.info(f"Loaded {len(documents)} pages/sections from '{path.name}'")
        return documents

    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load a PDF file using PyPDFLoader."""
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        # Normalize page metadata key
        for i, doc in enumerate(documents):
            doc.metadata["page"] = doc.metadata.get("page", i)
        return documents

    def _load_docx(self, file_path: str) -> List[Document]:
        """Load a DOCX file using Docx2txtLoader."""
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        # DOCX loads as a single document — add page placeholder
        for doc in documents:
            doc.metadata.setdefault("page", 0)
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split loaded documents into smaller chunks using legal-aware splitting.

        Preserves and enriches metadata: article numbers are extracted from
        each chunk's content and stored in metadata.

        Args:
            documents: List of Document objects from load_document().

        Returns:
            List of smaller Document chunks with enriched metadata.
        """
        if not documents:
            logger.warning("split_documents called with empty document list")
            return []

        chunks = self.text_splitter.split_documents(documents)

        # Enrich each chunk with article metadata
        enriched_chunks = []
        for chunk in chunks:
            if not chunk.page_content.strip():
                continue

            # Extract article number from chunk content
            article_num = extract_article_number(chunk.page_content)
            if article_num:
                chunk.metadata["article"] = article_num
            else:
                chunk.metadata.setdefault("article", None)

            # Add a short text preview for display in citations
            preview = chunk.page_content[:150].replace("\n", " ").strip()
            chunk.metadata["text_preview"] = preview + ("..." if len(chunk.page_content) > 150 else "")

            enriched_chunks.append(chunk)

        logger.info(
            f"Split {len(documents)} documents into {len(enriched_chunks)} chunks"
        )
        return enriched_chunks

    def process_law_book(self, file_path: str) -> List[Document]:
        """
        Complete pipeline: load a law book and return enriched chunks.

        This is the main entry point for processing a legal document.
        It loads the file, splits it into chunks, and enriches each chunk
        with metadata including article numbers, source file, and page numbers.

        Args:
            file_path: Path to the PDF or DOCX law book.

        Returns:
            List of Document chunks ready for embedding and storage.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.
            RuntimeError: If processing fails.
        """
        path = Path(file_path)
        logger.info(f"Processing law book: {path.name}")

        # Compute file hash for tracking
        try:
            file_hash = get_file_hash(file_path)
            logger.info(f"File hash: {file_hash}")
        except Exception as e:
            logger.warning(f"Could not compute file hash: {e}")
            file_hash = "unknown"

        # Load the document
        documents = self.load_document(file_path)

        if not documents:
            raise RuntimeError(
                f"No content could be extracted from '{path.name}'. "
                "The file may be empty, scanned (image-only PDF), or corrupted."
            )

        # Split into chunks
        chunks = self.split_documents(documents)

        if not chunks:
            raise RuntimeError(
                f"Document '{path.name}' was loaded but produced no text chunks. "
                "The content may be too short or entirely non-textual."
            )

        # Enrich all chunks with file-level metadata
        for chunk in chunks:
            chunk.metadata["source_file"] = path.name
            chunk.metadata["file_hash"] = file_hash
            chunk.metadata.setdefault("page", 0)

        logger.info(
            f"Successfully processed '{path.name}': "
            f"{len(chunks)} chunks from {len(documents)} pages"
        )
        return chunks

    def get_supported_formats(self) -> List[str]:
        """Return list of supported file extensions."""
        return [".pdf", ".docx", ".doc"]

    def is_supported_format(self, file_path: str) -> bool:
        """Check if a file's format is supported."""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.get_supported_formats()
