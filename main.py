import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.repository.database import engine
from src.routes.document import router as documents_router 
from src.routes.document import router as health_router
from src.utils.error_handler import build_error_response
from src.utils.exceptions.custom_exceptions import AppError
from src.utils.helper import build_response
from src.routes.chat_route import router as chat_router

logging.basicConfig(level=logging.INFO)
logging.getLogger("watchfiles").setLevel(logging.WARNING)  
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()  # closes the connection pool on shutdown


app = FastAPI(title="RAG Job Assistant", version="1.0.0", lifespan=lifespan)

app.include_router(documents_router)
app.include_router(health_router)
app.include_router(chat_router)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = f"req-{uuid4()}"
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return await build_error_response(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(p) for p in e["loc"]), "detail": e["msg"]}
        for e in exc.errors()
    ]
    body = build_response(request, 422, "Invalid request", errors=errors)
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    return await build_error_response(request, exc)