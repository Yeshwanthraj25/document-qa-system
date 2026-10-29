from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.schema.schema import  ErrorLog
from src.utils.exceptions.custom_exceptions import RepositoryError
from src.utils.exceptions.error_codes import ErrorCode


async def create_error_log(
    session: AsyncSession,
    *,
    file_name: str,
    function_name: str,
    status_code: int,
    error_code: str,
    request_id: str,
    log_data: str,
    error_details: str,
) -> None:
    """Insert one row into error_log. Caller passes its own session."""
    try:
        session.add(
            ErrorLog(
                file_name=file_name,
                function_name=function_name,
                status_code=status_code,
                error_code=error_code,
                request_id=request_id,
                log_data=log_data,
                error_details=error_details,
            )
        )
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        raise RepositoryError(ErrorCode.DATABASE_ERROR, "Failed to write error log") from exc
