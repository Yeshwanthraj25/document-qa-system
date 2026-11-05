from pydantic import BaseModel, Field,ConfigDict
from uuid import UUID
from datetime import datetime


class ChatQueryRequest(BaseModel):
    document_id: UUID | None = None 
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=1, ge=1, le=10)

