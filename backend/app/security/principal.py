import uuid

from pydantic import BaseModel, Field


class Principal(BaseModel):
    subject_id: uuid.UUID
    tenant_id: uuid.UUID
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    auth_type: str
