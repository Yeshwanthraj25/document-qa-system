import logging
from pathlib import Path
from uuid import UUID
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.dto.response_model import DocumentListData, DocumentMetadata,Pagination
from src.repository.document_repository import create_document_with_chunks,delete_document,get_document_with_chunk_count,list_documents
from src.repository.schema.schema import Document
from src.settings import settings
from src.utils.chunking import split_text
from src.utils.document_loader import load_document
from src.utils.exceptions.custom_exceptions import AppError,DocumentNotFoundError,InvalidDocumentError,ServiceError
from src.utils.exceptions.error_codes import ErrorCode
from src.client.embedding_client import embed_texts

logger = logging.getLogger(__name__)


def _to_metadata(document: Document, chunks_count: int) -> DocumentMetadata:
    return DocumentMetadata(
        id=document.doc_id,
        filename=document.filename,
        file_size=document.file_size,
        pages=document.pages,
        chunks_count=chunks_count,
        uploaded_at=document.uploaded_at,
    )


async def upload_document(
    session: AsyncSession, filename: str | None, file_bytes: bytes
) -> DocumentMetadata:
    try:
        if not file_bytes:
            raise InvalidDocumentError(ErrorCode.EMPTY_FILE)
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise InvalidDocumentError(
                ErrorCode.FILE_TOO_LARGE,
                f"Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB",
            )

        # PDF parsing is blocking, so run it in a worker thread.
        sections = await run_in_threadpool(load_document, filename, file_bytes)

        chunk_rows = []
        chunk_number = 1  
        for page_number, text in sections:
            for start, end, content in split_text(text):
                chunk_rows.append(
                    {
                        "chunk_number": chunk_number,
                        "page_number": page_number,
                        "start_char": start,
                        "end_char": end,
                        "content": content,
                    }
                )
                chunk_number += 1

        pages = max(page_number for page_number, _ in sections)
        vectors = await embed_texts([row["content"] for row in chunk_rows])
        document = await create_document_with_chunks(session, Path(filename).name, len(file_bytes), pages, chunk_rows,vectors, settings.EMBEDDING_MODEL)
        logger.info("Uploaded %s: %d pages, %d chunks", document.filename, pages, len(chunk_rows))
        return _to_metadata(document, len(chunk_rows))
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Document upload failed") from exc


async def list_documents_service(
    session: AsyncSession, skip: int, limit: int
) -> DocumentListData:
    try:
        rows, total = await list_documents(session, skip, limit)
        return DocumentListData(
            documents=[_to_metadata(doc, count) for doc, count in rows],
            pagination = Pagination(total_count=total,skip=skip,limit=limit),
        )
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to list documents") from exc


async def get_document_service(session: AsyncSession, doc_id: UUID) -> DocumentMetadata:
    try:
        result = await get_document_with_chunk_count(session, doc_id)
        if result is None:
            raise DocumentNotFoundError(
                ErrorCode.DOCUMENT_NOT_FOUND, f"No document with id {doc_id}"
            )
        document, count = result
        return _to_metadata(document, count)
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to get document") from exc


async def delete_document_service(session: AsyncSession, doc_id: UUID) -> None:
    try:
        deleted = await delete_document(session, doc_id)
        if not deleted:
            raise DocumentNotFoundError(
                ErrorCode.DOCUMENT_NOT_FOUND, f"No document with id {doc_id}"
            )
        logger.info("Deleted document %s", doc_id)
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to delete document") from exc