from app.embeddings.provider import EmbeddingProvider
from app.llm.models import ChatMessage, ChatRequest
from app.llm.service import LLMService
from app.rag.models import RAGResponse, RAGSource
from app.rag.retriever import Retriever


class RAGService:
    def __init__(
        self, embedding_provider: EmbeddingProvider, llm_service: LLMService, retriever: Retriever
    ) -> None:
        self._embedding_provider = embedding_provider
        self._llm_service = llm_service
        self._retriever = retriever

    async def answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> RAGResponse:

        query_embedding = await self._embedding_provider.embed(question)

        results = await self._retriever.retrieve(
            embedding=query_embedding,
            top_k=top_k,
        )

        sources = [
            RAGSource(
                document_id=result.chunk.document_id,
                chunk_id=result.chunk.id,
                content=result.chunk.content,
                score=result.score,
            )
            for result in results
        ]

        context = "\n\n".join(result.chunk.content for result in results)

        prompt = (
            "Answer the user's questions using only "
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
