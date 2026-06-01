import unittest

from qdrant_client import QdrantClient

from backend.services.qdrant_store import QdrantStore


class QdrantStoreTest(unittest.TestCase):
    def test_missing_collection_searches_return_empty_results(self) -> None:
        store = QdrantStore(
            client=QdrantClient(":memory:"),
            collection_name="missing_collection",
            vector_size=3,
        )

        self.assertEqual(store.vector_search([0.1, 0.2, 0.3]), [])
        self.assertEqual(store.payload_search(keyword="rag"), [])

    def test_upsert_and_search_papers(self) -> None:
        store = QdrantStore(
            client=QdrantClient(":memory:"),
            collection_name="test_papers",
            vector_size=3,
        )

        store.ensure_collection()
        inserted_count = store.upsert_papers(
            [
                {
                    "id": "arxiv:2401.00001",
                    "vector": [0.1, 0.2, 0.3],
                    "payload": {
                        "title": "Agentic RAG for AI Papers",
                        "authors": ["A Researcher"],
                        "abstract": "Retrieval augmented generation with agents.",
                        "published_date": "2026-05-30",
                        "category": "cs.AI",
                        "pdf_url": "https://arxiv.org/pdf/2401.00001",
                    },
                }
            ]
        )

        self.assertEqual(inserted_count, 1)

        vector_results = store.vector_search(
            [0.1, 0.2, 0.3],
            category="cs.AI",
            limit=1,
        )
        self.assertEqual(len(vector_results), 1)
        self.assertEqual(
            vector_results[0]["payload"]["title"],
            "Agentic RAG for AI Papers",
        )
        self.assertEqual(
            vector_results[0]["payload"]["source_id"],
            "arxiv:2401.00001",
        )

        payload_results = store.payload_search(
            keyword="agentic",
            category="cs.AI",
            limit=10,
        )
        self.assertEqual(len(payload_results), 1)
        self.assertEqual(
            payload_results[0]["payload"]["pdf_url"],
            "https://arxiv.org/pdf/2401.00001",
        )


if __name__ == "__main__":
    unittest.main()
