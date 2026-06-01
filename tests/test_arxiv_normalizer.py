import unittest
import xml.etree.ElementTree as ET

from backend.ingestion.arxiv_client import RawArxivPaper
from backend.ingestion.normalizer import ArxivPaperNormalizer


def atom_entry(arxiv_id: str, title: str = " Agentic\n RAG ") -> ET.Element:
    xml = f"""
    <entry xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
      <id>http://arxiv.org/abs/{arxiv_id}</id>
      <title>{title}</title>
      <summary> Retrieval augmented
      generation with agents. </summary>
      <published>2026-05-30T00:00:00Z</published>
      <author><name>A Researcher</name></author>
      <author><name>B Researcher</name></author>
      <link title="pdf" href="https://arxiv.org/pdf/2401.00001" />
      <arxiv:primary_category term="cs.AI" />
    </entry>
    """
    return ET.fromstring(xml)


class ArxivPaperNormalizerTest(unittest.TestCase):
    def test_normalize_cleans_fields_and_uses_stable_id(self) -> None:
        paper = ArxivPaperNormalizer().normalize(atom_entry("2401.00001v2"))

        self.assertEqual(paper.id, "arxiv:2401.00001")
        self.assertEqual(paper.title, "Agentic RAG")
        self.assertEqual(
            paper.abstract,
            "Retrieval augmented generation with agents.",
        )
        self.assertEqual(paper.authors, ["A Researcher", "B Researcher"])
        self.assertEqual(paper.published_date, "2026-05-30")
        self.assertEqual(paper.pdf_url, "https://arxiv.org/pdf/2401.00001")
        self.assertEqual(paper.category, "cs.AI")
        self.assertEqual(paper.payload()["source"], "arxiv")

    def test_normalize_many_deduplicates_versions(self) -> None:
        normalizer = ArxivPaperNormalizer()
        papers = normalizer.normalize_many(
            [
                RawArxivPaper(entry=atom_entry("2401.00001v1", "First")),
                RawArxivPaper(entry=atom_entry("2401.00001v3", "Second")),
            ]
        )

        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].id, "arxiv:2401.00001")
        self.assertEqual(papers[0].title, "First")


if __name__ == "__main__":
    unittest.main()
