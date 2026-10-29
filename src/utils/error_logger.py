import logging
import traceback
from pathlib import Path

from fastapi import Request

from src.repository.database import AsyncSessionLocal
from src.repository.error_log_repository import create_error_log
from src.utils.exceptions.custom_exceptions import AppError

logger = logging.getLogger(__name__)

MAX_DETAILS_LENGTH = 500
MAX_CHAIN_DEPTH = 10


def _exception_chain(exc: BaseException) -> list[BaseException]:
    """Outermost exception first, root cause last (follows 'raise ... from')."""
    chain = [exc]
    while chain[-1].__cause__ is not None and len(chain) < MAX_CHAIN_DEPTH:
        chain.append(chain[-1].__cause__)
    return chain


def _origin(exc: BaseException) -> tuple[str, str]:
    """File and function of the innermost frame that belongs to this project."""
    frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
    own_frames = [
        frame
        for frame in frames
        if "src" in Path(frame.filename).parts
        and "site-packages" not in Path(frame.filename).parts
    ]
    if not own_frames:
        return "unknown", "unknown"
    frame = own_frames[-1]
    return Path(frame.filename).name, frame.name


async def write_error_log(
    request: Request | None,
    exc: Exception,
    status_code: int,
    error_code: str,
) -> None:
    """Write one row to error_log using its own session. Never raises."""
    try:
        chain = _exception_chain(exc)
        file_name, function_name = _origin(chain[-1])

        # Class names only. str(exc) can contain SQL with document text.
        details = " <- ".join(type(e).__name__ for e in chain)
        if isinstance(exc, AppError) and exc.detail:
            details = f"{details} | {exc.detail}"

        request_id = getattr(request.state, "request_id", "unknown") if request else "unknown"
        log_data = f"{request.method} {request.url.path}" if request else "no request"

        async with AsyncSessionLocal() as log_session:
            await create_error_log(
                log_session,
                file_name=file_name,
                function_name=function_name,
                status_code=status_code,
                error_code=error_code,
                request_id=request_id,
                log_data=log_data,
                error_details=details[:MAX_DETAILS_LENGTH],
            )
    except Exception:
        # Logging must never break the response.
        logger.exception("Failed to write error log")
