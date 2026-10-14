from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.schema.schema import Chunk, Document
from src.utils.exceptions.custom_exceptions import RepositoryError
from src.utils.exceptions.error_codes import ErrorCode
from sqlalchemy.exc import SQLAlchemyError


async def create_document_with_chunks(
    session: AsyncSession ,
    filename: str,
    file_size: int,
    pages: int,
    chunks: list[dict],
) -> Document:
    doc_id = uuid4()
    document = Document(doc_id=doc_id, filename= filename, file_size= file_size, pages= pages)
    chunk_rows = [Chunk(document_id=doc_id, **chunk) for chunk in chunks]
    try:
         session.add(document)
         session.add_all(chunk_rows)
         await session.commit()
         await session.refresh(document)
    except SQLAlchemyError as exc:
        await session.rollback()
        raise  RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to save document") from exc
    return document

