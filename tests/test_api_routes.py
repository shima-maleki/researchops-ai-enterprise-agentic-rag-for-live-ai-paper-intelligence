import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.papers import PaperMetadata


class FakePaperSearchService:
    def search(self, *, keyword=None, category=None, limit=50):
        return []


class FakeRagService:
    def answer(self, message: str):
        return {
            "answer": (
                "I could not find enough relevant ingested papers to answer this "
                "question. Try ingesting more papers or asking a more specific "
                "research question."
            ),
            "sources": [],
        }


class FakePaperSearchServiceWithResult:
    def search(self, *, keyword=None, category=None, limit=50):
        return [
            PaperMetadata(
                title="Agentic RAG for AI Papers",
                authors=["A Researcher"],
                published_date="2026-05-30",
                url="https://arxiv.org/pdf/2401.00001",
                category="cs.AI",
            )
        ]


class ApiRoutesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch(
        "backend.api.routes_papers.PaperSearchService.from_settings",
        return_value=FakePaperSearchService(),
    )
    def test_papers_empty_fallback(self, _from_settings) -> None:
        response = self.client.get("/papers", params={"keyword": "rag"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"papers": []})

    @patch(
        "backend.api.routes_papers.PaperSearchService.from_settings",
        return_value=FakePaperSearchServiceWithResult(),
    )
    def test_papers_returns_metadata(self, _from_settings) -> None:
        response = self.client.get(
            "/papers",
            params={"keyword": "rag", "category": "cs.AI"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["papers"][0]["title"], "Agentic RAG for AI Papers")

    @patch(
        "backend.api.routes_chat.RagService.from_settings",
        return_value=FakeRagService(),
    )
    def test_chat_fallback(self, _from_settings) -> None:
        response = self.client.post(
            "/chat",
            json={"message": "What are the latest papers about agentic RAG?"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("could not find enough relevant ingested papers", body["answer"])
        self.assertEqual(body["sources"], [])


if __name__ == "__main__":
    unittest.main()
