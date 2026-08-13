from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)
    filename: str


class RetrievalResult(BaseModel):
    chunk: DocumentChunk
    score: float


class RAGRequest(BaseModel):
    question: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    filters: dict[str, str] = Field(
        default_factory=dict,
    )


class RAGSource(BaseModel):
    document_id: str
    chunk_id: str
    content: str
    score: float
    filename: str


class RAGResponse(BaseModel):
    answer: str
    sources: list[RAGSource]
