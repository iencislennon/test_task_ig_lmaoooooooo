"""ResearchAgent: turn a natural-language request into summarized GitHub project matches.

Example:
    agent = ResearchAgent()
    result = agent.research("find a github project for parsing pdf files in python")
    print(result.summary)
    for p in result.projects:
        print(p.name, p.url, p.relevance)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .github_search import fetch_readme, search_repositories
from .llm import LLMEngine
from .readme_parser import clean_readme, extract_title

_LEAD_IN = re.compile(
    r"^\s*(find|search( for)?|look for|show me|get me|get|recommend)\s+"
    r"(a|an|some)?\s*(github\s+)?(repositories|repository|projects|project|repos|repo)\s*"
    r"(for|about|on|related to|regarding|that (does|do|can))?\s*",
    re.IGNORECASE,
)

_SYSTEM_PROMPT = (
    "You are a research assistant that summarizes open-source GitHub projects. "
    "Given a user's topic of interest and a project's README, write a concise "
    "2-3 sentence summary of what the project does and why it is or isn't a good "
    "match for the topic. Be factual and only use information from the README."
)


@dataclass
class ProjectResult:
    name: str
    url: str
    stars: int
    relevance: str  # LLM-generated summary of fit for the query


@dataclass
class ResearchResult:
    query: str
    topic: str
    projects: list[ProjectResult] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if not self.projects:
            return f"No matching GitHub projects found for '{self.topic}'."
        lines = [f"Top GitHub projects for '{self.topic}':"]
        for p in self.projects:
            lines.append(f"\n- {p.name} ({p.stars}★) — {p.url}\n  {p.relevance}")
        return "\n".join(lines)


def extract_topic(user_query: str) -> str:
    """Strip conversational lead-ins ('find a github project for ...') to get the search topic."""
    topic = _LEAD_IN.sub("", user_query).strip()
    return topic or user_query.strip()


class ResearchAgent:
    def __init__(self, model_name: str | None = None, top_k: int = 5, llm: LLMEngine | None = None):
        self.top_k = top_k
        if llm is not None:
            self.llm = llm
        elif model_name:
            self.llm = LLMEngine(model_name=model_name)
        else:
            self.llm = LLMEngine()

    def research(self, user_query: str) -> ResearchResult:
        topic = extract_topic(user_query)
        candidates = search_repositories(topic, limit=self.top_k)

        result = ResearchResult(query=user_query, topic=topic)
        for candidate in candidates:
            raw_readme = fetch_readme(candidate.full_name)
            if not raw_readme:
                continue

            readme_text = clean_readme(raw_readme)
            title = extract_title(raw_readme) or candidate.full_name

            user_prompt = (
                f"Topic of interest: {topic}\n\n"
                f"Project: {candidate.full_name}\n"
                f"Description: {candidate.description}\n\n"
                f"README (truncated):\n{readme_text[:4000]}"
            )
            relevance = self.llm.chat(_SYSTEM_PROMPT, user_prompt, max_new_tokens=150)

            result.projects.append(
                ProjectResult(
                    name=title,
                    url=candidate.url,
                    stars=candidate.stars,
                    relevance=relevance,
                )
            )

        return result
