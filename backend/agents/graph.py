from __future__ import annotations

from langgraph.graph import END, StateGraph

from backend.agents.state import RagState
from backend.agents.tools import RetrieverTool
from backend.services.llm import ChatGenerationService


class RagAgent:
    def __init__(
        self,
        retriever_tool: RetrieverTool,
        chat_generation_service: ChatGenerationService,
    ) -> None:
        self.retriever_tool = retriever_tool
        self.chat_generation_service = chat_generation_service
        self.graph = self._build_graph()

    def invoke(self, message: str) -> RagState:
        return self.graph.invoke(
            {
                "user_message": message,
                "retrieval_query": "",
                "retrieved_papers": [],
                "answer": "",
                "sources": [],
            }
        )

    def _build_graph(self):
        graph = StateGraph(RagState)
        graph.add_node("analyze_question", self._analyze_question)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("grade_context", self._grade_context)
        graph.add_node("generate_answer", self._generate_answer)
        graph.add_node("fallback_answer", self._fallback_answer)
        graph.add_node("format_sources", self._format_sources)

        graph.set_entry_point("analyze_question")
        graph.add_edge("analyze_question", "retrieve_context")
        graph.add_edge("retrieve_context", "grade_context")
        graph.add_conditional_edges(
            "grade_context",
            self._route_after_grading,
            {
                "generate_answer": "generate_answer",
                "fallback_answer": "fallback_answer",
            },
        )
        graph.add_edge("generate_answer", "format_sources")
        graph.add_edge("fallback_answer", "format_sources")
        graph.add_edge("format_sources", END)
        return graph.compile()

    def _analyze_question(self, state: RagState) -> RagState:
        state["retrieval_query"] = state["user_message"].strip()
        return state

    def _retrieve_context(self, state: RagState) -> RagState:
        state["retrieved_papers"] = self.retriever_tool.search(
            state["retrieval_query"]
        )
        return state

    def _grade_context(self, state: RagState) -> RagState:
        return state

    def _route_after_grading(self, state: RagState) -> str:
        if state["retrieved_papers"]:
            return "generate_answer"
        return "fallback_answer"

    def _generate_answer(self, state: RagState) -> RagState:
        state["answer"] = self.chat_generation_service.generate_answer(
            user_message=state["user_message"],
            retrieved_papers=state["retrieved_papers"],
        )
        return state

    def _fallback_answer(self, state: RagState) -> RagState:
        state["answer"] = (
            "I could not find enough relevant ingested papers to answer this "
            "question. Try ingesting more papers or asking a more specific "
            "research question."
        )
        return state

    def _format_sources(self, state: RagState) -> RagState:
        seen_urls: set[str] = set()
        sources = []

        for paper in state["retrieved_papers"]:
            url = paper.get("url", "")
            title = paper.get("title", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append({"title": title, "url": url})

        state["sources"] = sources
        return state
