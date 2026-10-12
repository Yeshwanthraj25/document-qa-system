from pydantic import BaseModel, Field
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
    
   