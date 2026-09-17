"""Three deliberately small agents that turn a web query into cited evidence."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urlparse


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    snippet: str
    score: int = 0

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc.removeprefix("www.")


class SearchAgent:
    """Finds public web results. This is the only agent that touches the network."""

    def search(self, query: str, limit: int = 8) -> list[Source]:
        try:
            from ddgs import DDGS
        except ImportError as error:
            raise RuntimeError("Search support is missing. Install the project dependencies first.") from error

        results = DDGS().text(query, max_results=limit)
        return [
            Source(
                title=result.get("title", "Untitled source"),
                url=result.get("href", ""),
                snippet=result.get("body", ""),
            )
            for result in results
            if result.get("href") and result.get("body")
        ]


class EvidenceAgent:
    """Ranks search snippets by direct word overlap with the user's question."""

    @staticmethod
    def _terms(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]{3,}", text.lower()))

    def select(self, query: str, sources: list[Source], limit: int = 5) -> list[Source]:
        query_terms = self._terms(query)
        scored = [
            Source(
                title=source.title,
                url=source.url,
                snippet=source.snippet,
                score=len(query_terms & self._terms(f"{source.title} {source.snippet}")),
            )
            for source in sources
        ]
        return sorted(scored, key=lambda source: (-source.score, source.title.lower()))[:limit]


class WriterAgent:
    """Uses Gemini only when configured, and only with selected source snippets."""

    def answer(self, question: str, evidence: list[Source], api_key: str) -> str:
        if not evidence:
            return "I could not find enough relevant evidence to answer that question."
        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError("AI support is optional. Install it with `pip install -e '.[ai]'`.") from error

        context = "\n\n".join(
            f"[{index}] {source.title}\nURL: {source.url}\nSnippet: {source.snippet}"
            for index, source in enumerate(evidence, start=1)
        )
        prompt = f"""Answer the question using ONLY the source snippets below.
Use bracket citations such as [1] after claims. If the snippets are insufficient, say so.
Do not invent details or citations.

Question: {question}

Sources:
{context}
"""
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text or "I could not produce an answer from the selected evidence."
