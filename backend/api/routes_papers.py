import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from backend.api.error_details import external_service_error_detail
from backend.schemas.ingest import PaperCategory
from backend.schemas.papers import PapersResponse
from backend.services.paper_search import PaperSearchService
from backend.services.qdrant_store import QdrantConfigurationError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["papers"])


@router.get("/papers", response_model=PapersResponse)
async def search_papers(
    keyword: str | None = Query(default=None, min_length=1),
    category: PaperCategory | None = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> PapersResponse:
    try:
        service = PaperSearchService.from_settings()
        papers = await run_in_threadpool(
            service.search,
            keyword=keyword,
            category=category,
            limit=limit,
        )
        return PapersResponse(papers=papers)
    except QdrantConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("paper_search_failed")
        raise HTTPException(
            status_code=502,
            detail=external_service_error_detail(exc, "Paper search failed"),
        ) from exc
