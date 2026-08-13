from app.embeddings.provider import EmbeddingProvider
from app.llm.models import ChatMessage, ChatRequest
from app.llm.service import LLMService
from app.rag.models import RAGResponse, RAGSource
from app.rag.retriever import Retriever


class RAGService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        llm_service: LLMService,
        retriever: Retriever,
        min_relevance_score: float = 0.7,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._llm_service = llm_service
        self._retriever = retriever
        self._min_relevance_score = min_relevance_score

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> RAGResponse:

        query_embedding = await self._embedding_provider.embed(question)

        results = await self._retriever.retrieve(
            embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )

        relevant_results = [
            result for result in results if result.score >= self._min_relevance_score
        ]

        sources = [
            RAGSource(
                document_id=result.chunk.document_id,
                chunk_id=result.chunk.id,
                content=result.chunk.content,
                score=result.score,
                filename=result.chunk.filename,
            )
            for result in relevant_results
        ]

        context = "\n\n".join(result.chunk.content for result in relevant_results)

        if not relevant_results:
            return RAGResponse(
                answer=(
                    "I dont have enough information in the available "
                    "knowledge base to answer that question."
                ),
                sources=[],
            )

        prompt = (
            "You are an enterprise knowledge assistance. "
            "Answer the user's questions using only the provided context. "
            "Do not use outside knowledge. "
            "If the context does not contain enough information, "
            "to answer the question,say that you do not have enough information to answer."
            "the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        )

        request = ChatRequest(
            messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "You are an enterprise knowledge "
                        "assistant. Answer using only "
                        "the provided context."
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=prompt,
                ),
            ],
        )

        response = await self._llm_service.chat(request)

        return RAGResponse(
            answer=response.content,
            sources=sources,
        )
