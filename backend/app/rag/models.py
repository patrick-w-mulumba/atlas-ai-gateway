from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    chunk: DocumentChunk
    score: float
