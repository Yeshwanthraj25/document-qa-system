from fastapi import APIRouter, Depends, File, Request, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.database import get_db
from src.models.dto.response_model import APIResponse
from fastapi import Request
from src.utils.helper import build_response
from src.services.document_service import upload_document,get_document_service,list_documents_service,delete_document_service
from src.utils.error_handler import handle_errors
from uuid import UUID

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

@router.post("/upload", status_code=201, response_model=APIResponse)
async def upload(request: Request, file: UploadFile = File(...),session: AsyncSession = Depends(get_db)):
    file_bytes = await file.read()
    metadata = await upload_document(session, file.filename, file_bytes)
    return build_response(request, 201, "Document uploaded successfully",data=metadata.model_dump(mode="json"))

@router.get("/health",status_code =200,response_model=APIResponse)
async def health():
    return "API is healthy"

@router.get("/list", response_model=APIResponse)
@handle_errors
async def list_documents_route(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    data = await list_documents_service(session, skip, limit)
    return build_response(request, 200, "Documents retrieved successfully",
                          data=data.model_dump(mode="json"))


@router.get("/{document_id}", response_model=APIResponse)
@handle_errors
async def get_document_route(request: Request, document_id: UUID, session: AsyncSession = Depends(get_db)):
    metadata = await get_document_service(session, document_id)
    return build_response(request, 200, "Document retrieved successfully", data=metadata.model_dump(mode="json"))


@router.delete("/{document_id}", response_model=APIResponse)
@handle_errors
async def delete_document_route(request: Request, document_id: UUID, session: AsyncSession = Depends(get_db)):
    await delete_document_service(session, document_id)
    return build_response(request, 200, "Document deleted successfully")
