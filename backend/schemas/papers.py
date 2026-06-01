from pydantic import BaseModel


class PaperMetadata(BaseModel):
    title: str
    authors: list[str]
    published_date: str
    url: str
    category: str


class PapersResponse(BaseModel):
    papers: list[PaperMetadata]
