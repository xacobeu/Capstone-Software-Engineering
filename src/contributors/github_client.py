from __future__ import annotations

import json
import os
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import requests
from rich.console import Console

console = Console()
CONVENTIONAL_REGEX = re.compile(
    r"^(?:fix|refactor|feat|test)\s*\(([^)]+)\)", re.IGNORECASE
)


def normalize_username(username: str) -> str:
    """Normalize bot usernames across GitHub endpoints."""
    if username == "dependabot":
        return "dependabot[bot]"
    if username == "github-actions":
        return "github-actions[bot]"
    return username


class GitHubClient:
    """Handles GitHub REST and GraphQL API communication with automated rate-limit backoff."""

    BASE_URL = "https://api.github.com"
    GRAPHQL_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None) -> None:
        self.session = requests.Session()
        resolved_token = token or self._discover_token()

        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "User-Agent": "GitHub-Contributor-Analyzer/1.0",
            }
        )
        if resolved_token:
            self.session.headers["Authorization"] = f"Bearer {resolved_token}"

    @staticmethod
    def _discover_token() -> str | None:
        if token := os.getenv("GITHUB_TOKEN"):
            return token

        env_path = Path(".env")
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip("\"' ")
        return None

    def _request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> requests.Response:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        while True:
            res = self.session.get(url, params=params)
            if res.status_code in (403, 429):
                reset_ts = int(
                    res.headers.get("X-RateLimit-Reset", time.time() + 60)
                )
                sleep_time = max(1, reset_ts - int(time.time()) + 1)
                console.print(
                    f"[yellow]Rate limit hit on REST API. Sleeping for {sleep_time}s...[/yellow]"
                )
                time.sleep(sleep_time)
                continue
            return res

    def _graphql(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        while True:
            res = self.session.post(self.GRAPHQL_URL, json=payload)
            if res.status_code in (403, 429):
                reset_ts = int(
                    res.headers.get("X-RateLimit-Reset", time.time() + 60)
                )
                sleep_time = max(1, reset_ts - int(time.time()) + 1)
                console.print(
                    f"[yellow]Rate limit hit on GraphQL API. Sleeping for {sleep_time}s...[/yellow]"
                )
                time.sleep(sleep_time)
                continue

            if not res.ok:
                raise RuntimeError(
                    f"GraphQL query failed with status {res.status_code}: {res.text}"
                )

            data = res.json()
            if "errors" in data and not data.get("data"):
                raise RuntimeError(f"GraphQL returned errors: {data['errors']}")

            return data

    def get_total_contributors(self, repo: str) -> int:
        """Total repository contributors (all-time)."""
        res = self._request(
            f"repos/{repo}/contributors", params={"per_page": 1, "anon": "true"}
        )
        if not res.ok:
            return 0
        link = res.headers.get("Link", "")
        if match := re.search(r'page=(\d+)>; rel="last"', link):
            return int(match.group(1))
        payload = res.json()
        return len(payload) if isinstance(payload, list) else 0

    def get_committers_since(
        self, repo: str, since_iso: str
    ) -> Counter[str]:
        """Paginates commit history strictly within the given ISO timestamp."""
        commit_counter: Counter[str] = Counter()
        page = 1
        while True:
            res = self._request(
                f"repos/{repo}/commits",
                params={"since": since_iso, "per_page": 100, "page": page},
            )
            if not res.ok:
                break
            commits = res.json()
            if not commits:
                break

            for c in commits:
                author = c.get("author")
                if author and "login" in author:
                    commit_counter[normalize_username(author["login"])] += 1
                elif committer := c.get("committer"):
                    if "login" in committer:
                        commit_counter[normalize_username(committer["login"])] += 1

            if len(commits) < 100:
                break
            page += 1

        return commit_counter

    def fetch_prs_data_since(
        self, repo: str, since_iso: str, update_fn: Callable[[str], None] | None = None
    ) -> tuple[Counter[str], dict[str, Counter[str]], dict[str, Counter[str]]]:
        """Fetches all PRs created since given date using GraphQL.

        Extracts total PRs per author, focus area/skills distribution, and PR size distribution.
        """
        owner, name = repo.split("/", 1)
        query = """
        query($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            pullRequests(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                createdAt
                title
                author {
                  login
                }
                labels(first: 20) {
                  nodes {
                    name
                  }
                }
              }
            }
          }
        }
        """

        pr_counts: Counter[str] = Counter()
        author_skills: dict[str, Counter[str]] = defaultdict(Counter)
        author_sizes: dict[str, Counter[str]] = defaultdict(Counter)

        cursor: str | None = None
        total_fetched = 0
        since_threshold = f"{since_iso}T00:00:00Z" if len(since_iso) == 10 else since_iso

        while True:
            variables: dict[str, Any] = {"owner": owner, "name": name, "cursor": cursor}
            data = self._graphql(query, variables)
            pr_data = data["data"]["repository"]["pullRequests"]
            nodes = pr_data.get("nodes", [])
            stop = False

            for node in nodes:
                created_at = node.get("createdAt", "")
                if created_at < since_threshold:
                    stop = True
                    break

                total_fetched += 1
                author_obj = node.get("author")
                if not author_obj or "login" not in author_obj:
                    continue

                user = normalize_username(author_obj["login"])
                pr_counts[user] += 1

                pr_areas: set[str] = set()

                # 1. Extract conventional commit scopes: fix(x), refactor(x), feat(x), test(x)
                title = node.get("title", "")
                if match := CONVENTIONAL_REGEX.match(title.strip()):
                    raw_scope = match.group(1)
                    for s in re.split(r"[,/]", raw_scope):
                        s_clean = s.strip().lower()
                        if s_clean and s_clean not in ("unknown", "none", "null"):
                            pr_areas.add(s_clean)

                # 2. Extract repository labels: area/* and size/*
                for label in node.get("labels", {}).get("nodes", []):
                    lname = label.get("name", "")
                    if lname.startswith("area/"):
                        area = lname.removeprefix("area/").strip().lower()
                        if area and area not in ("unknown", "none", "null"):
                            pr_areas.add(area)
                    elif lname.startswith("size/"):
                        author_sizes[user][lname] += 1

                for area in pr_areas:
                    author_skills[user][area] += 1

            if update_fn:
                update_fn(f"Processed {total_fetched} PRs...")

            if stop or not pr_data["pageInfo"]["hasNextPage"]:
                break
            cursor = pr_data["pageInfo"]["endCursor"]

        return pr_counts, dict(author_skills), dict(author_sizes)

    def fetch_issues_since(
        self, repo: str, since_iso: str, update_fn: Callable[[str], None] | None = None
    ) -> Counter[str]:
        """Fetches all authored issues created since given date using GraphQL."""
        owner, name = repo.split("/", 1)
        query = """
        query($owner: String!, $name: String!, $cursor: String) {
          repository(owner: $owner, name: $name) {
            issues(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                createdAt
                author {
                  login
                }
              }
            }
          }
        }
        """

        issue_counts: Counter[str] = Counter()
        cursor: str | None = None
        total_fetched = 0
        since_threshold = f"{since_iso}T00:00:00Z" if len(since_iso) == 10 else since_iso

        while True:
            variables: dict[str, Any] = {"owner": owner, "name": name, "cursor": cursor}
            data = self._graphql(query, variables)
            issue_data = data["data"]["repository"]["issues"]
            nodes = issue_data.get("nodes", [])
            stop = False

            for node in nodes:
                created_at = node.get("createdAt", "")
                if created_at < since_threshold:
                    stop = True
                    break

                total_fetched += 1
                author_obj = node.get("author")
                if not author_obj or "login" not in author_obj:
                    continue

                user = normalize_username(author_obj["login"])
                issue_counts[user] += 1

            if update_fn:
                update_fn(f"Processed {total_fetched} Issues...")

            if stop or not issue_data["pageInfo"]["hasNextPage"]:
                break
            cursor = issue_data["pageInfo"]["endCursor"]

        return issue_counts

    def get_all_activity_since(
        self,
        repo: str,
        since_iso: str,
        cache_path: str | Path | None = None,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Retrieves unified activity data, utilizing local caching when available."""
        target_cache = Path(cache_path) if cache_path else None

        if target_cache and target_cache.is_file() and not force_refresh:
            try:
                cached = json.loads(target_cache.read_text(encoding="utf-8"))
                if (
                    cached.get("repo") == repo
                    and cached.get("since_iso") == since_iso
                ):
                    console.print(
                        f"[bold green]Loaded contributor activity from cache '{target_cache}'[/bold green]"
                    )
                    return cached
            except Exception as e:
                console.print(f"[yellow]Cache read failed ({e}), refetching...[/yellow]")

        total_contributors = self.get_total_contributors(repo)

        with console.status(f"[bold green]Fetching commits since {since_iso} (REST)..."):
            commit_counts = self.get_committers_since(repo, since_iso)

        with console.status(f"[bold green]Fetching pull requests since {since_iso} (GraphQL)...") as status:
            pr_counts, author_skills, author_sizes = self.fetch_prs_data_since(
                repo, since_iso, update_fn=lambda msg: status.update(f"[bold green]{msg}")
            )

        with console.status(f"[bold green]Fetching issues since {since_iso} (GraphQL)...") as status:
            issue_counts = self.fetch_issues_since(
                repo, since_iso, update_fn=lambda msg: status.update(f"[bold green]{msg}")
            )

        data = {
            "repo": repo,
            "since_iso": since_iso,
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "total_contributors_all_time": total_contributors,
            "commits": dict(commit_counts),
            "prs": dict(pr_counts),
            "issues": dict(issue_counts),
            "author_skills": {u: dict(c) for u, c in author_skills.items()},
            "author_sizes": {u: dict(c) for u, c in author_sizes.items()},
        }

        if target_cache:
            target_cache.parent.mkdir(parents=True, exist_ok=True)
            target_cache.write_text(json.dumps(data, indent=2), encoding="utf-8")
            console.print(f"[bold green]Cached contributor activity to '{target_cache}'[/bold green]")

        return data

    def count_search_results(self, repo: str, query: str) -> int:
        res = self._request(
            "search/issues", params={"q": f"repo:{repo} {query}"}
        )
        if res.ok:
            return res.json().get("total_count", 0)
        return 0

    def get_contributor_profile(
        self, repo: str, username: str, since_iso: str, top_n: int = 3
    ) -> tuple[list[tuple[str, int]], dict[str, int]]:
        """Fallback method to fetch contributor profile via search API."""
        skill_counter: Counter[str] = Counter()
        size_counter: Counter[str] = Counter()
        page = 1
        query = f"repo:{repo} is:pr author:{username} created:>={since_iso}"

        while True:
            res = self._request(
                "search/issues",
                params={"q": query, "per_page": 100, "page": page},
            )
            if not res.ok:
                break

            data = res.json()
            items = data.get("items", [])
            if not items:
                break

            for item in items:
                pr_areas: set[str] = set()
                title = item.get("title", "")
                if match := CONVENTIONAL_REGEX.match(title.strip()):
                    raw_scope = match.group(1)
                    for s in re.split(r"[,/]", raw_scope):
                        s_clean = s.strip().lower()
                        if s_clean and s_clean not in ("unknown", "none", "null"):
                            pr_areas.add(s_clean)

                for label in item.get("labels", []):
                    name = label.get("name", "")
                    if name.startswith("area/"):
                        area = name.removeprefix("area/").strip().lower()
                        if area and area not in ("unknown", "none", "null"):
                            pr_areas.add(area)
                    elif name.startswith("size/"):
                        size_counter[name] += 1

                for a in pr_areas:
                    skill_counter[a] += 1

            if len(items) < 100 or page * 100 >= data.get("total_count", 0):
                break
            page += 1

        return skill_counter.most_common(top_n), dict(size_counter)
