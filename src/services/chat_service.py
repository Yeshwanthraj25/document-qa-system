from sqlalchemy.ext.asyncio import AsyncSession
from src.services.document_service import get_document_with_chunk_count,embed_texts
from src.utils.exceptions.custom_exceptions import AppError,ServiceError
from src.utils.exceptions.error_codes import ErrorCode
from src.utils.exceptions.custom_exceptions import DocumentNotFoundError
from src.settings import settings
from src.models.dto.input_dto import ChatQueryRequest
from src.models.dto.response_model import ChatQueryData,Citation
from src.repository.document_repository import search_similar_chunks
from src.client.ai_model_invoke import generate_answer
from src.client.ai_model_invoke import REFUSAL
from src.utils.helper import is_refusal
import logging

logger = logging.getLogger(__name__)



async def query_document(session: AsyncSession, request: ChatQueryRequest) -> ChatQueryData:
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
        if not rows or (1 - rows[0][2]) < settings.MIN_RELEVANCE_SCORE:
                    return ChatQueryData(query=request.query, answer= REFUSAL, citations=[])
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
            return ChatQueryData(query=request.query, answer=REFUSAL, citations=[])
        return ChatQueryData(query=request.query, answer=response, citations=citations) 
    except AppError:
        raise
    except Exception as exc:
        raise ServiceError(ErrorCode.INTERNAL_ERROR, "Failed to process chat query") from exc
