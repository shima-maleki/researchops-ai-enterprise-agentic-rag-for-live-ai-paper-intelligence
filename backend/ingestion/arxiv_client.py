from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class RawArxivPaper:
    entry: ET.Element


class ArxivClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def fetch_latest(
        self,
        *,
        categories: list[str],
        limit: int,
    ) -> list[RawArxivPaper]:
        search_query = " OR ".join(f"cat:{category}" for category in categories)
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(self.base_url, params=params)
            response.raise_for_status()

        root = ET.fromstring(response.text)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", namespace)
        return [RawArxivPaper(entry=entry) for entry in entries]
