from fastapi import FastAPI
from src.repository.database import engine
from fastapi import Request
from contextlib import asynccontextmanager
from uuid import uuid4
from src.utils.exceptions.custom_exceptions import AppError
from src.utils.helper import build_response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging 

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()          # closes the connection pool on shutdown

app = FastAPI(title="RAG Job Assistant", version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = f"req-{uuid4()}"
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    body = build_response(request, exc.error_code.http_status, exc.error_code.message,
                         errors=[{"code": exc.error_code.name, "detail": exc.detail}])
    return JSONResponse(status_code=exc.error_code.http_status,
                         content=body.model_dump(mode="json"))

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": ".".join(str(p) for p in e["loc"]), "detail": e["msg"]} for e in exc.errors()]

@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
