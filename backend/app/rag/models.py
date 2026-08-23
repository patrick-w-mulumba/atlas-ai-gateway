from pydantic import BaseModel, Field, field_validator


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
    question: str = Field(min_length=1)

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    filters: dict[str, str] = Field(
        default_factory=dict,
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("question cannot be empty")

        return value


class RAGSource(BaseModel):
    document_id: str
    chunk_id: str
    content: str
    score: float
    filename: str


class RAGResponse(BaseModel):
    answer: str
    sources: list[RAGSource]
