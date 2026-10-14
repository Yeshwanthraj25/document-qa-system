import logging
from pathlib import Path
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.dto.response_model import DocumentMetadata
from src.repository.document_repository import create_document_with_chunks
from src.settings import settings
from src.utils.chunking import chunking
from src.utils.document_loader import load_document
from src.utils.exceptions.custom_exceptions import InvalidDocumentError
from src.utils.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)


async def upload_document(session: AsyncSession, filename: str | None, file_bytes: bytes) -> DocumentMetadata:
    if not file_bytes :
        raise InvalidDocumentError(ErrorCode.EMPTY_FILE)
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise InvalidDocumentError(ErrorCode.FILE_TOO_LARGE, f"Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB")
    sections = await run_in_threadpool(load_document, filename, file_bytes)
    chunk_rows = [] 
    chunk_number = 1
    for page_number, text in sections:
        for start, end, content in chunking(text):
            chunk_rows.append({"chunk_number": chunk_number, "page_number": page_number, "start_char": start,"end_char": end, "content":  content})
            chunk_number += 1
    pages = max(page_number for page_number,_ in sections)
    document = await create_document_with_chunks(session, Path(filename).name, len(file_bytes), pages, chunk_rows)
    logger.info("Uploaded %s: %d pages, %d chunks", filename, pages, len(chunk_rows))
    return DocumentMetadata(id=document.doc_id, filename=document.filename,
    file_size=document.file_size, pages=document.pages,
    chunks_count=len(chunk_rows), uploaded_at=document.uploaded_at)