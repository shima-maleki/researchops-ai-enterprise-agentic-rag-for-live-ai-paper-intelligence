import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.api.error_details import external_service_error_detail
from backend.ingestion.pipeline import IngestionPipeline
from backend.schemas.ingest import IngestRequest, IngestResponse
from backend.services.embeddings import EmbeddingConfigurationError
from backend.services.qdrant_store import QdrantConfigurationError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_papers(request: IngestRequest) -> IngestResponse:
    try:
        pipeline = IngestionPipeline.from_settings()
        result = await run_in_threadpool(
            pipeline.ingest,
            limit=request.limit,
            categories=request.categories,
        )
        return IngestResponse(**result)
    except (EmbeddingConfigurationError, QdrantConfigurationError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("ingestion_failed")
        raise HTTPException(
            status_code=502,
            detail=external_service_error_detail(exc, "Paper ingestion failed"),
        ) from exc
