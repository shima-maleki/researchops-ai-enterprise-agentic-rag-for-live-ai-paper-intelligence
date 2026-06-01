import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.embeddings import EmbeddingConfigurationError
from backend.services.qdrant_store import QdrantConfigurationError
from backend.services.rag_service import RagService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        service = RagService.from_settings()
        result = await run_in_threadpool(service.answer, request.message)
        return ChatResponse(**result)
    except (EmbeddingConfigurationError, QdrantConfigurationError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("chat_failed")
        raise HTTPException(status_code=502, detail="Chat request failed") from exc
