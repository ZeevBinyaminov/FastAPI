from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response

from app.api.routes.auth import router as auth_router
from app.api.routes.forward import router as forward_router
from app.api.routes.history import router as history_router
from app.api.routes.stats import router as stats_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return 400 with 'bad request' message."""
    return Response(
        content="bad request",
        status_code=status.HTTP_400_BAD_REQUEST,
        media_type="text/plain",
    )


app.include_router(forward_router)
app.include_router(history_router)
app.include_router(stats_router)
app.include_router(auth_router)
