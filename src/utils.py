"""
Utility functions for the Legal RAG System.
Handles text cleaning, article extraction, file hashing, and legal-specific chunking.
"""

import re
import hashlib
from typing import Optional, List


def extract_article_number(text: str) -> Optional[str]:
    """
    Extract article or section numbers from legal text using regex patterns.

    Supports formats:
    - Article 1, Article 12, ARTICLE 5
    - Section 1, Section 2.3, SECTION 10
    - § 1, §12, § 1.2.3

    Args:
        text: The text to search for article/section numbers.

    Returns:
        The first matched article/section reference, or None if not found.
    """
    if not text:
        return None

    patterns = [
        # Article patterns: "Article 1", "Article 1.2", "ARTICLE 12"
        r"(?i)\bArticle\s+\d+(?:\.\d+)*\b",
        # Section patterns: "Section 1", "Section 2.3.1", "SECTION 10"
        r"(?i)\bSection\s+\d+(?:\.\d+)*\b",
        # § symbol patterns: "§ 1", "§12", "§ 1.2.3"
        r"§\s*\d+(?:\.\d+)*",
        # Numbered clauses at line start: "1.2.", "1.2.3."
        r"^\s*\d+(?:\.\d+)+\.",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(0).strip()

    return None


def get_file_hash(file_path: str) -> str:
    """
    Compute the MD5 hash of a file for tracking and deduplication.

    Args:
        file_path: Path to the file to hash.

    Returns:
        Hexadecimal MD5 hash string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Cannot read file {file_path}: {e}")

    return hasher.hexdigest()


def clean_text(text: str) -> str:
    """
    Clean and normalize legal text for processing.

    Operations performed:
    - Normalize line endings (CRLF -> LF)
    - Remove null bytes and control characters
    - Collapse multiple blank lines into a single blank line
    - Strip leading/trailing whitespace per line
    - Normalize multiple spaces to single space

    Args:
        text: Raw text to clean.

    Returns:
        Cleaned and normalized text string.
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove null bytes and non-printable control characters (keep \n and \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize multiple spaces to single space (but preserve newlines)
    text = re.sub(r"[ \t]+", " ", text)

    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse more than 2 consecutive blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace from the whole text
    text = text.strip()

    return text


def chunk_legal_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Split legal text into chunks that respect article and section boundaries.

    Strategy:
    1. First split on major legal boundaries (articles, sections, §)
    2. If a segment is still too large, split on paragraph boundaries
    3. If still too large, split on sentence boundaries with overlap

    Args:
        text: The legal text to chunk.
        chunk_size: Target maximum characters per chunk (default 500).
        overlap: Number of characters to overlap between chunks (default 100).

    Returns:
        List of text chunks, each respecting legal structure where possible.
    """
    if not text:
        return []

    text = clean_text(text)

    # Legal boundary patterns (split points, keeping the delimiter)
    legal_boundaries = re.compile(
        r"(?=\n(?:Article|Section|ARTICLE|SECTION)\s+\d|§\s*\d)",
        re.MULTILINE
    )

    # Split on legal boundaries first
    segments = legal_boundaries.split(text)
    segments = [s.strip() for s in segments if s.strip()]

    chunks = []
    for segment in segments:
        if len(segment) <= chunk_size:
            chunks.append(segment)
        else:
            # Segment too large — split on paragraphs
            paragraphs = re.split(r"\n\n+", segment)
            current_chunk = ""

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if len(current_chunk) + len(para) + 2 <= chunk_size:
                    current_chunk = (current_chunk + "\n\n" + para).strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    # Para itself may be too large — split by sentences
                    if len(para) > chunk_size:
                        sentence_chunks = _split_by_sentences(
                            para, chunk_size, overlap
                        )
                        chunks.extend(sentence_chunks)
                        # Start new chunk with overlap from last sentence chunk
                        if sentence_chunks:
                            last = sentence_chunks[-1]
                            current_chunk = last[-overlap:] if len(last) > overlap else last
                        else:
                            current_chunk = ""
                    else:
                        current_chunk = para

            if current_chunk:
                chunks.append(current_chunk)

    # Final pass: ensure no chunk exceeds chunk_size * 1.5 (hard limit)
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= chunk_size * 1.5:
            final_chunks.append(chunk)
        else:
            final_chunks.extend(_split_by_sentences(chunk, chunk_size, overlap))

    return [c for c in final_chunks if c.strip()]


def _split_by_sentences(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into chunks by sentence boundaries with overlap.

    Args:
        text: Text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Characters of overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Carry overlap from previous chunk
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-overlap:]
                current_chunk = (overlap_text + " " + sentence).strip()
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
