import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.api.error_details import external_service_error_detail
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
        raise HTTPException(
            status_code=502,
            detail=external_service_error_detail(exc, "Chat request failed"),
        ) from exc


@router.post("/chat/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    try:
        service = RagService.from_settings()
    except (EmbeddingConfigurationError, QdrantConfigurationError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    def event_stream():
        try:
            for event in service.stream_answer(request.message):
                yield f"{json.dumps(event)}\n"
        except Exception as exc:
            logger.exception("chat_stream_failed")
            yield json.dumps(
                {
                    "type": "error",
                    "detail": external_service_error_detail(
                        exc,
                        "Chat stream failed",
                    ),
                }
            )
            yield "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
    )
