from typing import Literal

from pydantic import BaseModel, Field

PaperCategory = Literal["cs.AI", "cs.CL", "cs.LG", "cs.IR"]


class IngestRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=500)
    categories: list[PaperCategory] = Field(
        default_factory=lambda: ["cs.AI", "cs.CL", "cs.LG", "cs.IR"]
    )


class IngestResponse(BaseModel):
    status: str
    ingested_count: int
    skipped_count: int
