import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.core.logging import get_logger
from app.core.exception_handlers import register_exception_handlers

from app.api.routes import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo(app)
    logger.info("🚀 Application startup complete")
    yield
    await close_mongo_connection(app)
    logger.info("🛑 Application shutdown complete")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan, description=settings.DESCRIPTION, version=settings.VERSION)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
