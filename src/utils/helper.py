from datetime import datetime, timezone
from fastapi import Request
from src.models.dto.response_model import APIResponse
from src.settings import settings
from src.client.ai_model_invoke import REFUSAL

def build_response(request: Request, code: int, message: str,data=None, errors=None) -> APIResponse:
    status = "success" if code < 400 else "error"
    request_id = getattr(request.state, "request_id", "unknown")
    return APIResponse(status= status, code=code, message=message, data=data,errors=errors or [], timestamp=datetime.now(timezone.utc),request_id=request_id)

def is_refusal(answer: str) -> bool:
    return REFUSAL.lower().rstrip(".") in answer.lower()