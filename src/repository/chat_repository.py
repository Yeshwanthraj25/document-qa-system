from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.schema.schema import ChatMessage
from src.utils.exceptions.custom_exceptions import RepositoryError
from src.utils.exceptions.error_codes import ErrorCode


async def create_chat_message(
    session: AsyncSession,
    doc_id: UUID | None,
    query: str,
    answer: str,
    citations: list[dict],
    processing_time_ms: int,
) -> ChatMessage:
    try:
        message = ChatMessage(
            doc_id=doc_id,
            query=query,
            answer=answer,
            citations=citations,
            processing_time_ms=processing_time_ms,
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message
    except SQLAlchemyError as exc:
        await session.rollback()
        raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to save chat message") from exc


async def list_chat_messages(
    session: AsyncSession, doc_id: UUID | None, skip: int, limit: int
) -> tuple[list[ChatMessage], int]:
    try:
        conditions = []
        if doc_id is not None:
            conditions.append(ChatMessage.doc_id == doc_id)
        query = (
            select(ChatMessage)
            .where(*conditions)
            .order_by(ChatMessage.created_at.desc(), ChatMessage.chat_id)
            .offset(skip)
            .limit(limit)
        )
        messages = list((await session.execute(query)).scalars().all())
        total = await session.scalar(
            select(func.count()).select_from(ChatMessage).where(*conditions)
        )
        return messages, total or 0
    except SQLAlchemyError as exc:
        raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to list chat messages") from exc
