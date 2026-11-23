from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import time
from src.services.document_service import get_document_with_chunk_count,embed_texts
from src.utils.exceptions.custom_exceptions import AppError,ServiceError
from src.utils.exceptions.error_codes import ErrorCode
from src.utils.exceptions.custom_exceptions import DocumentNotFoundError
from src.settings import settings
from src.models.dto.input_dto import ChatQueryRequest
from src.models.dto.response_model import ChatHistoryData,ChatMessageData,ChatQueryData,Citation,Pagination
from src.repository.chat_repository import create_chat_message, list_chat_messages
from src.repository.document_repository import search_similar_chunks
from src.client.ai_model_invoke import generate_answer
from src.client.ai_model_invoke import REFUSAL
from src.utils.helper import is_refusal
import logging

logger = logging.getLogger(__name__)



async def query_document(session: AsyncSession, request: ChatQueryRequest) -> ChatQueryData:
    started_at = time.perf_counter()
    try:
        if request.document_id is not None:
            result = await get_document_with_chunk_count(session, request.document_id)
            if result is None:
                raise DocumentNotFoundError(
                    ErrorCode.DOCUMENT_NOT_FOUND,
                    f"No document with id {request.document_id}",
                )
        vectors = await embed_texts([settings.QUERY_PREFIX + request.query])
        query_vector = vectors[0]
        rows = await search_similar_chunks(session, request.document_id, query_vector, request.top_k)
        if rows:
            logger.info("Top chunk #%d, score %.4f", rows[0][0].chunk_number, 1 - rows[0][2])
        citations = []
        if not rows or (1 - rows[0][2]) < settings.MIN_RELEVANCE_SCORE:
            response = REFUSAL
        else:
            citations = [
                        Citation(
                            chunk_id=chunk.chunk_id,
                            document_id=chunk.document_id,
                            document_name=filename,
                            page_number=chunk.page_number,
                            chunk_text=chunk.content,
                            relevance_score=round(1 - distance, 4),
                            passage_number = passage_number
                        )
                         for passage_number,(chunk, filename, distance) in enumerate(rows,start=1)
                    ]
            chunk_content = [chunk.content for chunk, filename, distance in rows]
            response = await generate_answer(request.query, chunk_content)
            if is_refusal(response):
                response = REFUSAL
                citations = []

        processing_time_ms = int((time.perf_counter() - started_at) * 1000)
        message_id = None
        try:
            saved = await create_chat_message(
                session,
                request.document_id,
                request.query,
                response,
                [citation.model_dump(mode="json", exclude={"chunk_text"}) for citation in citations],
                processing_time_ms,
            )
            message_id = saved.chat_id
        except Exception:
            logger.warning("Failed to save chat history")

        return ChatQueryData(message_id=message_id, query=request.query, answer=response,
                             citations=citations, processing_time_ms=processing_time_ms)
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to process chat query") from exc


async def get_chat_history(
    session: AsyncSession, document_id: UUID | None, skip: int, limit: int
) -> ChatHistoryData:
    try:
        if document_id is not None:
            document = await get_document_with_chunk_count(session, document_id)
            if document is None:
                raise DocumentNotFoundError(
                    ErrorCode.DOCUMENT_NOT_FOUND, f"No document with id {document_id}"
                )
        messages, total = await list_chat_messages(session, document_id, skip, limit)
        return ChatHistoryData(
            messages=[ChatMessageData.model_validate(message) for message in messages],
            pagination=Pagination(total_count=total, skip=skip, limit=limit),
        )
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to retrieve chat history") from exc
