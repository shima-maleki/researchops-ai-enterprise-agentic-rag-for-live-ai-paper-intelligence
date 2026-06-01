from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from backend.ingestion.arxiv_client import RawArxivPaper

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_NS = {"arxiv": "http://arxiv.org/schemas/atom"}


@dataclass(frozen=True)
class NormalizedPaper:
    id: str
    title: str
    authors: list[str]
    abstract: str
    published_date: str
    pdf_url: str
    category: str

    @property
    def embedding_text(self) -> str:
        return f"{self.title}\n\n{self.abstract}"

    def payload(self) -> dict[str, object]:
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "published_date": self.published_date,
            "pdf_url": self.pdf_url,
            "category": self.category,
            "source": "arxiv",
            "arxiv_id": self.id.removeprefix("arxiv:"),
        }


class ArxivPaperNormalizer:
    def normalize_many(self, papers: list[RawArxivPaper]) -> list[NormalizedPaper]:
        normalized: list[NormalizedPaper] = []
        seen_ids: set[str] = set()

        for raw_paper in papers:
            paper = self.normalize(raw_paper.entry)
            if paper.id in seen_ids:
                continue
            seen_ids.add(paper.id)
            normalized.append(paper)

        return normalized

    def normalize(self, entry: ET.Element) -> NormalizedPaper:
        arxiv_id = self._stable_arxiv_id(self._text(entry, "atom:id"))
        return NormalizedPaper(
            id=f"arxiv:{arxiv_id}",
            title=self._clean_text(self._text(entry, "atom:title")),
            authors=self._authors(entry),
            abstract=self._clean_text(self._text(entry, "atom:summary")),
            published_date=self._text(entry, "atom:published")[:10],
            pdf_url=self._pdf_url(entry),
            category=self._category(entry),
        )

    def _text(self, entry: ET.Element, path: str) -> str:
        element = entry.find(path, ATOM_NS)
        return element.text or "" if element is not None else ""

    def _authors(self, entry: ET.Element) -> list[str]:
        authors: list[str] = []
        for author in entry.findall("atom:author", ATOM_NS):
            name = author.find("atom:name", ATOM_NS)
            if name is not None and name.text:
                authors.append(self._clean_text(name.text))
        return authors

    def _pdf_url(self, entry: ET.Element) -> str:
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                return link.attrib.get("href", "")
            if link.attrib.get("type") == "application/pdf":
                return link.attrib.get("href", "")
        return ""

    def _category(self, entry: ET.Element) -> str:
        primary_category = entry.find("arxiv:primary_category", ARXIV_NS)
        if primary_category is not None:
            return primary_category.attrib.get("term", "")

        category = entry.find("atom:category", ATOM_NS)
        if category is not None:
            return category.attrib.get("term", "")
        return ""

    def _stable_arxiv_id(self, raw_id: str) -> str:
        arxiv_id = raw_id.rstrip("/").split("/")[-1]
        return re.sub(r"v\d+$", "", arxiv_id)

    def _clean_text(self, value: str) -> str:
        return " ".join(value.split())
