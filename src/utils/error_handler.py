import logging
from functools import wraps

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.utils.error_logger import write_error_log
from src.utils.exceptions.custom_exceptions import AppError
from src.utils.exceptions.error_codes import ErrorCode
from src.utils.helper import build_response

logger = logging.getLogger(__name__)


async def build_error_response(request: Request, exc: Exception) -> JSONResponse:
    """Log the error and build the standard error response.

    Used by the @handle_errors decorator and by the handlers in main.py,
    so every error leaves the app in the same shape.
    """
    if isinstance(exc, AppError):
        error_code = exc.error_code
        detail = exc.detail
        if error_code.http_status >= 500:
            logger.error("%s", error_code.name, exc_info=exc)
    else:
        logger.error("Unhandled error", exc_info=exc)
        error_code = ErrorCode.INTERNAL_ERROR
        detail = None

    await write_error_log(request, exc, error_code.http_status, error_code.name)

    body = build_response(
        request,
        error_code.http_status,
        error_code.message,
        errors=[{"code": error_code.name, "detail": detail}],
    )
    return JSONResponse(
        status_code=error_code.http_status,
        content=body.model_dump(mode="json"),
    )


def handle_errors(func):
    """Decorator for routes. The route must declare `request: Request`."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as exc:
            request = kwargs.get("request")
            if request is None:
                # No request available: let the handlers in main.py deal with it.
                raise
            return await build_error_response(request, exc)

    return wrapper
