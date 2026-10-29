from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.schema.schema import Chunk, Document
from src.utils.exceptions.custom_exceptions import RepositoryError
from src.utils.exceptions.error_codes import ErrorCode
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import delete, func, select
from src.repository.schema.schema import ChatMessage, Chunk, Document, Embedding
from uuid import uuid4

async def create_document_with_chunks(
    session: AsyncSession,
    filename: str,
    file_size: int,
    pages: int,
    chunks: list[dict],
    vectors: list[list[float]],
    embedding_model: str,
) -> Document:
    doc_id = uuid4()
    document = Document(doc_id=doc_id, filename=filename, file_size=file_size, pages=pages)
    chunk_rows = []
    embedding_rows = []
    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk_id = uuid4()
        chunk_rows.append(Chunk(chunk_id=chunk_id, document_id=doc_id, **chunk))
        embedding_rows.append(Embedding(chunk_id=chunk_id, vector=vector, embedding_model=embedding_model))
    try:
        session.add(document); session.add_all(chunk_rows)
        await session.flush()            
        session.add_all(embedding_rows)
        await session.commit()
        await session.refresh(document)
    except SQLAlchemyError as exc:
            await session.rollback()
            raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to save document") from exc
    return document

async def list_documents(
    session: AsyncSession, skip: int, limit: int
) -> tuple[list[tuple[Document, int]], int]:
    try:
        query = (
             select(Document, func.count(Chunk.chunk_id))
             .outerjoin(Chunk, Chunk.document_id == Document.doc_id)
             .group_by(Document.doc_id)
             .order_by(Document.uploaded_at.desc())
             .offset(skip).limit(limit)
             )
        rows = (await session.execute(query)).all()
        total = await session.scalar(select(func.count()).select_from(Document))
        return [(doc, count) for doc, count in rows], total
    except SQLAlchemyError as exc:
        raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to list documents") from exc


async def get_document_with_chunk_count(
    session: AsyncSession, doc_id: UUID
) -> tuple[Document, int] | None:
    """Same query as above, filtered with .where(Document.doc_id == doc_id).
    Use .first() on the result; return (document, count), or None if missing."""
    try:
            query = (
                 select(Document, func.count(Chunk.chunk_id))
                 .where(Document.doc_id == doc_id)
                 .outerjoin(Chunk, Chunk.document_id == Document.doc_id)
                 .group_by(Document.doc_id)
                 )
            row = (await session.execute(query)).first()
            if row is None:
                return None
            document, count = row
            return document, count
    except SQLAlchemyError as exc:
            raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to list documents") from exc


async def delete_document(session: AsyncSession, doc_id: UUID) -> bool:
    """Delete embeddings, chunks, chat messages, then the document, in one transaction."""
    chunk_ids = select(Chunk.chunk_id).where(Chunk.document_id == doc_id)
    try:
        await session.execute(delete(Embedding).where(Embedding.chunk_id.in_(chunk_ids)))
        await session.execute(delete(Chunk).where(Chunk.document_id == doc_id))
        await session.execute(delete(ChatMessage).where(ChatMessage.doc_id == doc_id))
        result = await session.execute(delete(Document).where(Document.doc_id == doc_id))
        await session.commit()
        return result.rowcount > 0
    except SQLAlchemyError as exc:
        await session.rollback()
        raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to delete document") from exc

