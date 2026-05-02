"""
Vector store operations for the Legal RAG System.
Uses Qdrant in local (file-based) mode — no Docker required.
Embeddings are generated locally using sentence-transformers.
"""

import os
import logging
import uuid
from typing import List, Dict, Optional, Any

from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Embedding model constants
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension
DEFAULT_COLLECTION = "legal_docs"


class LegalVectorStore:
    """
    Manages vector storage and semantic search for legal documents.

    Uses Qdrant in local (path-based) mode for persistence without Docker,
    and sentence-transformers for free, local embeddings.
    """

    def __init__(self, persist_directory: str = "./qdrant_storage"):
        """
        Initialize the vector store with a local Qdrant instance.

        Args:
            persist_directory: Directory path for Qdrant's persistent storage.
                               Created automatically if it does not exist.
        """
        os.makedirs(persist_directory, exist_ok=True)
        self.persist_directory = persist_directory

        # Initialize Qdrant in local file mode (no Docker/server needed)
        self.client = QdrantClient(path=persist_directory)
        logger.info(f"Qdrant client initialized at: {persist_directory}")

        # Load the embedding model (downloads on first use, cached afterward)
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("Embedding model loaded successfully")

        self.collection_name = DEFAULT_COLLECTION

    def create_collection(
        self,
        collection_name: str = DEFAULT_COLLECTION,
        vector_size: int = VECTOR_SIZE,
    ) -> bool:
        """
        Create a Qdrant collection for legal documents if it doesn't exist.

        Uses Cosine distance which is optimal for semantic similarity search
        with normalized sentence-transformer embeddings.

        Args:
            collection_name: Name for the Qdrant collection.
            vector_size: Dimensionality of the embedding vectors (384 for MiniLM).

        Returns:
            True if collection was created, False if it already existed.
        """
        self.collection_name = collection_name

        # Check if collection already exists
        existing = [c.name for c in self.client.get_collections().collections]
        if collection_name in existing:
            logger.info(f"Collection '{collection_name}' already exists — skipping creation")
            return False

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
        logger.info(
            f"Created collection '{collection_name}' "
            f"(vector_size={vector_size}, distance=COSINE)"
        )
        return True

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (each a list of floats).
        """
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,  # Normalize for cosine similarity
        )
        return embeddings.tolist()

    def add_documents(
        self,
        documents: List[Document],
        source_file: str,
    ) -> int:
        """
        Embed and store documents in the Qdrant collection.

        Each document is stored with rich metadata for citation display:
        article number, source file, page number, and a text preview.

        Args:
            documents: List of LangChain Document objects to store.
            source_file: Name of the source file (used in metadata).

        Returns:
            Number of documents successfully added.

        Raises:
            RuntimeError: If the collection does not exist or upsert fails.
        """
        if not documents:
            logger.warning("add_documents called with empty document list")
            return 0

        # Ensure collection exists
        self.create_collection(self.collection_name)

        texts = [doc.page_content for doc in documents]
        logger.info(f"Embedding {len(texts)} chunks from '{source_file}'...")

        # Generate embeddings in batch
        embeddings = self._embed_texts(texts)

        # Build Qdrant points
        points = []
        for doc, embedding in zip(documents, embeddings):
            point_id = str(uuid.uuid4())

            # Build payload with all metadata for citation display
            payload = {
                "text": doc.page_content,
                "source_file": source_file,
                "article": doc.metadata.get("article"),
                "page": doc.metadata.get("page", 0),
                "text_preview": doc.metadata.get(
                    "text_preview",
                    doc.page_content[:150].replace("\n", " ").strip()
                ),
                "file_hash": doc.metadata.get("file_hash", ""),
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        # Upsert in batches of 100 to avoid memory issues with large documents
        batch_size = 100
        total_added = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )
            total_added += len(batch)
            logger.info(f"Upserted batch {i // batch_size + 1}: {len(batch)} points")

        logger.info(
            f"Successfully added {total_added} chunks from '{source_file}' "
            f"to collection '{self.collection_name}'"
        )
        return total_added

    def search(
        self,
        query: str,
        article_filter: Optional[str] = None,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over the legal document collection.

        Args:
            query: Natural language question or search query.
            article_filter: Optional article number to restrict search scope
                            (e.g., "Article 5"). If None, searches all documents.
            k: Number of top results to return (default 5).

        Returns:
            List of result dicts, each containing:
            - text: Full chunk text
            - source_file: Source document name
            - article: Article/section number (or None)
            - page: Page number
            - text_preview: Short preview for display
            - score: Cosine similarity score (0-1)
        """
        # Ensure collection exists before searching
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing:
            logger.warning(f"Collection '{self.collection_name}' does not exist")
            return []

        # Embed the query
        query_embedding = self._embed_texts([query])[0]

        # Build optional article filter
        search_filter = None
        if article_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="article",
                        match=MatchValue(value=article_filter),
                    )
                ]
            )

        # Execute search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=k,
            with_payload=True,
        )

        # Format results
        formatted = []
        for hit in results:
            payload = hit.payload or {}
            formatted.append(
                {
                    "text": payload.get("text", ""),
                    "source_file": payload.get("source_file", "Unknown"),
                    "article": payload.get("article"),
                    "page": payload.get("page", 0),
                    "text_preview": payload.get("text_preview", ""),
                    "score": round(hit.score, 4),
                }
            )

        logger.info(
            f"Search returned {len(formatted)} results for query: "
            f"'{query[:60]}{'...' if len(query) > 60 else ''}'"
        )
        return formatted

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Return statistics about the current collection.

        Returns:
            Dict with keys:
            - collection_name: Name of the collection
            - total_chunks: Total number of stored vectors
            - exists: Whether the collection exists
            - unique_sources: List of unique source file names
        """
        existing = [c.name for c in self.client.get_collections().collections]

        if self.collection_name not in existing:
            return {
                "collection_name": self.collection_name,
                "total_chunks": 0,
                "exists": False,
                "unique_sources": [],
            }

        info = self.client.get_collection(self.collection_name)
        total = info.points_count or 0

        # Retrieve unique source files by scrolling through payloads
        unique_sources = set()
        try:
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=["source_file"],
            )
            for point in scroll_result[0]:
                if point.payload and "source_file" in point.payload:
                    unique_sources.add(point.payload["source_file"])
        except Exception as e:
            logger.warning(f"Could not retrieve unique sources: {e}")

        return {
            "collection_name": self.collection_name,
            "total_chunks": total,
            "exists": True,
            "unique_sources": sorted(unique_sources),
        }

    def collection_exists(self) -> bool:
        """Check if the default collection exists and has data."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing:
            return False
        info = self.client.get_collection(self.collection_name)
        return (info.points_count or 0) > 0

    def delete_collection(self) -> bool:
        """
        Delete the current collection and all its data.

        Returns:
            True if deleted, False if it did not exist.
        """
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing:
            return False
        self.client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection '{self.collection_name}'")
        return True
