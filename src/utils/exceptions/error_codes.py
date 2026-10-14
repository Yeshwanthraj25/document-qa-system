from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from pydantic import ConfigDict
from enum import Enum


class ErrorCreation(BaseModel):
    file_name: str
    function_name: str
    status_code: int 
    log_data : str = "no log data" 
    error_details: str

    model_config = ConfigDict(from_attributes=True)

class ErrorLogResponse(BaseModel):
    log_id: UUID
    file_name: str
    function_name: str
    error_code : str
    log_data : str
    error_details: str
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)
 

class ErrorCode(Enum):
    INVALID_FILE_TYPE = (400, "File type not allowed")
    EMPTY_FILE = (400, "Uploaded file is empty")
    FILE_TOO_LARGE =(413,"Over the size limit")
    DOCUMENT_NO_TEXT =(422,"No readable text found in this PDF")
    DOCUMENT_UNREADABLE =(422,"unknown {document_id}")
    INTERNAL_ERROR = (500,"An unexpected error occurred")
    DOCUMENT_NOT_FOUND = (404, "Document not found")
    DATABASE_ERROR = (500, "A database error occurred")

    def __init__(self, http_status: int, message: str):
        self.http_status = http_status
        self.message = message

