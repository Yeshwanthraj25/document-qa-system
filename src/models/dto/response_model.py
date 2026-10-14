from pydantic import BaseModel, Field,ConfigDict,UUID
from datetime import datetime
from typing import Optional

class APIResponse(BaseModel):
    status: str = Field(..., description="Response status: success or error")
    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Human-readable message")
    data: Optional[dict | list] = Field(default=None, description="Response payload")
    errors: list = Field(default_factory=list, description="List of errors if any")
    timestamp: datetime = Field(..., description="Response timestamp")
    request_id: str = Field(..., description="Unique request identifier")
    

class DocumentMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID = Field(validation_alias="doc_id")
    filename:str = Field(description="The upload the file name will be shown here")
    file_size: int = Field(description="The fize will be shown in bytes")
    pages:int = Field(description="The no pages there in file will be show")
    chunks_count:int = Field(description="The chunk count will be after the file been chunk")
    uploaded_at:datetime = Field(description="The uploaded time will be shown here")