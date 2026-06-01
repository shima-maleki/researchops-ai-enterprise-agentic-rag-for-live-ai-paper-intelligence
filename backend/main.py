from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes_chat import router as chat_router
from backend.api.routes_health import router as health_router
from backend.api.routes_ingest import router as ingest_router
from backend.api.routes_papers import router as papers_router
from backend.core.config import get_settings
from backend.core.logging import configure_logging
from backend.core.middleware import RequestLoggingMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise Agentic RAG for Live AI Paper Intelligence",
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(papers_router)
    app.include_router(chat_router)

    return app


app = create_app()
