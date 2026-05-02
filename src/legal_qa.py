"""
Legal Q&A system for the Legal RAG System.
Uses Groq's LLM (llama-3.3-70b-versatile) with a strict legal prompt
that enforces citation-based answers from retrieved context only.
"""

import os
import logging
from typing import List, Dict, Optional, Any

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from src.vector_store import LegalVectorStore

logger = logging.getLogger(__name__)

# System prompt enforcing citation-based legal answers
LEGAL_SYSTEM_PROMPT = """You are a precise legal document assistant. Your role is to answer questions \
strictly based on the provided legal document excerpts.

STRICT RULES:
1. Answer ONLY using information from the provided context excerpts below.
2. If the answer is not found in the context, respond with: \
"Information not found in the provided legal documents."
3. Always cite the specific Article, Section, or § number when available \
(e.g., "According to Article 5...", "As stated in Section 3.2...").
4. Use precise, formal legal language in your responses.
5. Do not infer, speculate, or add information beyond what is explicitly stated.
6. If multiple articles are relevant, cite each one clearly.
7. Keep answers concise but complete — include all relevant legal details.

CONTEXT FROM LEGAL DOCUMENTS:
{context}

CONVERSATION HISTORY:
{chat_history}

Answer the following question based solely on the context above:"""

HUMAN_PROMPT = "{question}"


class LegalQASystem:
    """
    Question-answering system for legal documents.

    Combines semantic search (via LegalVectorStore) with Groq's LLM to
    produce citation-backed answers from uploaded legal documents.
    Maintains conversation history for follow-up questions.
    """

    def __init__(
        self,
        vector_store: LegalVectorStore,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.1,
    ):
        """
        Initialize the Legal Q&A system.

        Args:
            vector_store: Initialized LegalVectorStore instance.
            model: Groq model identifier. Default: llama-3.3-70b-versatile.
            temperature: LLM temperature (0.0-1.0). Low values for factual precision.

        Raises:
            ValueError: If GROQ_API_KEY is not set in environment.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )

        self.vector_store = vector_store
        self.model_name = model
        self.temperature = temperature

        # Initialize Groq LLM
        self.llm = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=2048,
        )
        logger.info(f"Groq LLM initialized: model={model}, temperature={temperature}")

        # Conversation memory for multi-turn Q&A
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        # Build the prompt template
        self.prompt = self.create_legal_prompt()

        logger.info("LegalQASystem initialized successfully")

    def create_legal_prompt(self) -> ChatPromptTemplate:
        """
        Create the legal-specific prompt template.

        The prompt enforces:
        - Answers only from provided context
        - Mandatory citations with article/section numbers
        - Formal legal language
        - "Information not found" fallback

        Returns:
            ChatPromptTemplate ready for use with the Groq LLM.
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", LEGAL_SYSTEM_PROMPT),
                ("human", HUMAN_PROMPT),
            ]
        )
        return prompt

    def ask_question(
        self,
        question: str,
        filter_article: Optional[str] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """
        Answer a legal question using retrieved context and the Groq LLM.

        Process:
        1. Search the vector store for relevant chunks
        2. Format chunks as context for the LLM
        3. Build prompt with context + conversation history
        4. Call Groq LLM for the answer
        5. Update conversation memory
        6. Return answer with source citations

        Args:
            question: The legal question to answer.
            filter_article: Optional article number to restrict search scope.
            k: Number of context chunks to retrieve (default 5).

        Returns:
            Dict with:
            - answer: The LLM's answer string
            - sources: List of source dicts with citation metadata
            - question: The original question
            - model: Model used for the answer

        Raises:
            RuntimeError: If the LLM call fails.
        """
        if not question.strip():
            return {
                "answer": "Please provide a valid question.",
                "sources": [],
                "question": question,
                "model": self.model_name,
            }

        # Step 1: Retrieve relevant chunks
        sources = self.vector_store.search(
            query=question,
            article_filter=filter_article,
            k=k,
        )

        if not sources:
            return {
                "answer": (
                    "Information not found in the provided legal documents. "
                    "Please upload a relevant legal document first."
                ),
                "sources": [],
                "question": question,
                "model": self.model_name,
            }

        # Step 2: Format context from retrieved chunks
        context = self._format_context(sources)

        # Step 3: Get conversation history
        chat_history = self._get_chat_history_text()

        # Step 4: Build and invoke the prompt
        try:
            messages = self.prompt.format_messages(
                context=context,
                chat_history=chat_history,
                question=question,
            )
            response = self.llm.invoke(messages)
            answer = response.content.strip()
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            raise RuntimeError(
                f"Failed to get answer from Groq API: {e}. "
                "Please check your API key and internet connection."
            ) from e

        # Step 5: Update conversation memory
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(answer)

        logger.info(
            f"Q&A completed: question='{question[:60]}...', "
            f"sources={len(sources)}, answer_length={len(answer)}"
        )

        return {
            "answer": answer,
            "sources": sources,
            "question": question,
            "model": self.model_name,
        }

    def _format_context(self, sources: List[Dict[str, Any]]) -> str:
        """
        Format retrieved source chunks into a structured context string for the LLM.

        Args:
            sources: List of source dicts from vector store search.

        Returns:
            Formatted context string with numbered excerpts and citations.
        """
        context_parts = []
        for i, source in enumerate(sources, 1):
            article = source.get("article")
            page = source.get("page", 0)
            source_file = source.get("source_file", "Unknown Document")
            text = source.get("text", "").strip()

            # Build citation header
            citation_parts = [f"[Excerpt {i}]"]
            citation_parts.append(f"Source: {source_file}")
            if article:
                citation_parts.append(f"Reference: {article}")
            if page:
                citation_parts.append(f"Page: {page}")

            header = " | ".join(citation_parts)
            context_parts.append(f"{header}\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def _get_chat_history_text(self) -> str:
        """
        Format conversation history as a readable string for the prompt.

        Returns:
            Formatted conversation history, or empty string if no history.
        """
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No previous conversation."

        history_parts = []
        for msg in messages[-6:]:  # Keep last 3 exchanges (6 messages)
            if isinstance(msg, HumanMessage):
                history_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_parts.append(f"Assistant: {msg.content[:300]}...")

        return "\n".join(history_parts) if history_parts else "No previous conversation."

    def format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """
        Format source citations for display in the UI.

        Args:
            sources: List of source dicts from ask_question().

        Returns:
            Human-readable formatted string of all citations.
        """
        if not sources:
            return "No sources available."

        lines = []
        for i, source in enumerate(sources, 1):
            article = source.get("article", "N/A")
            page = source.get("page", "N/A")
            source_file = source.get("source_file", "Unknown")
            score = source.get("score", 0)
            preview = source.get("text_preview", "")

            lines.append(f"**Source {i}**")
            lines.append(f"- Document: {source_file}")
            lines.append(f"- Reference: {article if article else 'N/A'}")
            lines.append(f"- Page: {page}")
            lines.append(f"- Relevance: {score:.1%}")
            lines.append(f"- Preview: _{preview}_")
            lines.append("")

        return "\n".join(lines)

    def clear_memory(self) -> None:
        """Clear the conversation history."""
        self.memory.clear()
        logger.info("Conversation memory cleared")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Return conversation history as a list of message dicts.

        Returns:
            List of dicts with 'role' ('user'/'assistant') and 'content' keys.
        """
        messages = self.memory.chat_memory.messages
        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history
