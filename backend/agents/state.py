from typing import TypedDict


class PaperContext(TypedDict):
    title: str
    authors: list[str]
    abstract: str
    published_date: str
    category: str
    url: str
    score: float


class Source(TypedDict):
    title: str
    url: str


class RagState(TypedDict):
    user_message: str
    retrieval_query: str
    retrieved_papers: list[PaperContext]
    answer: str
    sources: list[Source]
