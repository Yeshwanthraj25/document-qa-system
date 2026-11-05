from src.services.chat_service import query_document
from src.models.dto.input_dto import ChatQueryRequest
from fastapi import APIRouter,Request,Depends
from src.utils.error_handler import handle_errors
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.database import get_db
from src.models.dto.response_model import APIResponse
from src.utils.helper import build_response

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.post("/query", response_model=APIResponse)
@handle_errors
async def query_route(request: Request, body: ChatQueryRequest, session: AsyncSession = Depends(get_db)):
    data = await query_document(session, body)
    return build_response(request, 200, "Query processed successfully", data=data.model_dump(mode="json"))