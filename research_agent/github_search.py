"""Minimal GitHub client: find repositories for a topic, fetch their raw README."""

from __future__ import annotations

from dataclasses import dataclass

import requests

_API_ROOT = "https://api.github.com"
_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "research-agent",
}
_README_HEADERS = {
    "Accept": "application/vnd.github.raw+json",
    "User-Agent": "research-agent",
}
_TIMEOUT = 10


@dataclass
class RepoCandidate:
    full_name: str
    url: str
    description: str
    stars: int


def search_repositories(topic: str, limit: int = 5) -> list[RepoCandidate]:
    """Search public GitHub repositories matching `topic`, best-starred first."""
    resp = requests.get(
        f"{_API_ROOT}/search/repositories",
        params={"q": topic, "sort": "stars", "order": "desc", "per_page": limit},
        headers=_HEADERS,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return [
        RepoCandidate(
            full_name=item["full_name"],
            url=item["html_url"],
            description=item.get("description") or "",
            stars=item.get("stargazers_count", 0),
        )
        for item in items[:limit]
    ]


def fetch_readme(full_name: str, max_chars: int = 6000) -> str | None:
    """Fetch a repo's raw README text via GitHub's dedicated readme endpoint.

    Returns None if the repo has no README or the request fails (private repo,
    rate limit, network error) -- callers should treat that as "skip this one".
    """
    try:
        resp = requests.get(
            f"{_API_ROOT}/repos/{full_name}/readme",
            headers=_README_HEADERS,
            timeout=_TIMEOUT,
        )
    except requests.RequestException:
        return None
    if resp.status_code != 200:
        return None
    return resp.text[:max_chars]
