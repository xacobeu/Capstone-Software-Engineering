from __future__ import annotations

import json
import os
import random
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

OWNER = "google-gemini"
REPO = "gemini-cli"
DATA_OUT = Path(__file__).resolve().parent / "data" / "project_health_data.json"

# Manual decisions on the candidates from detect_accounts.py (single source of truth for Appendix A)
DECISIONS_IN = Path(__file__).resolve().parent / "account_decisions.json"
_decisions = json.loads(DECISIONS_IN.read_text(encoding="utf-8"))
KNOWN_BOTS = set(_decisions["bots"]) | set(_decisions["spam_accounts"]) | set(_decisions["shared_accounts"])
HUMAN_ACCOUNTS = set(_decisions["humans"])
ALT_ACCOUNT_MAP = {alias: d["canonical"] for alias, d in _decisions["aliases"].items()}


def discover_token() -> str:
    if tok := os.getenv("GITHUB_TOKEN"):
        return tok.strip("\"' ")
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip("\"' ")
            elif line.startswith("ghp_") or line.startswith("github_pat_"):
                return line.strip("\"' ")
    raise RuntimeError("GITHUB_TOKEN not found in .env or environment!")


def is_bot_user(login: str | None) -> bool:
    """Deleted accounts (no login) are excluded too, since they cannot be attributed to a person."""
    if not login:
        return True
    if login in HUMAN_ACCOUNTS:
        return False
    return login in KNOWN_BOTS or login.lower().endswith("[bot]")


def normalize_user(login: str | None) -> str | None:
    if not login:
        return None
    return ALT_ACCOUNT_MAP.get(login, login)


class GitHubGraphQL:
    def __init__(self, token: str) -> None:
        self.token = token

    def query(self, q: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = json.dumps({"query": q, "variables": variables or {}}).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Capstone-ProjectHealth-Analyzer/2.0",
        }
        for attempt in range(5):
            req = urllib.request.Request(
                "https://api.github.com/graphql", data=payload, headers=headers
            )
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "errors" in data and not data.get("data"):
                        print(f"GraphQL error (attempt {attempt+1}): {data['errors']}")
                        time.sleep(3 * (attempt + 1))
                        continue
                    return data
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                print(f"HTTP {e.code} (attempt {attempt+1}): {body[:200]}")
                time.sleep(5 * (attempt + 1))
            except Exception as e:
                print(f"Request error (attempt {attempt+1}): {e}")
                time.sleep(3 * (attempt + 1))
        raise RuntimeError("GraphQL query failed after 5 attempts.")


def get_months_list() -> list[tuple[str, str, str]]:
    """Returns (YYYY-MM, start_date, end_date) from 2025-06 to 2026-09."""
    months = [
        ("2025-06", "2025-06-01", "2025-06-30"),
        ("2025-07", "2025-07-01", "2025-07-31"),
        ("2025-08", "2025-08-01", "2025-08-31"),
        ("2025-09", "2025-09-01", "2025-09-30"),
        ("2025-10", "2025-10-01", "2025-10-31"),
        ("2025-11", "2025-11-01", "2025-11-30"),
        ("2025-12", "2025-12-01", "2025-12-31"),
        ("2026-01", "2026-01-01", "2026-01-31"),
        ("2026-02", "2026-02-01", "2026-02-28"),
        ("2026-03", "2026-03-01", "2026-03-31"),
        ("2026-04", "2026-04-01", "2026-04-30"),
        ("2026-05", "2026-05-01", "2026-05-31"),
        ("2026-06", "2026-06-01", "2026-06-30"),
        ("2026-07", "2026-07-01", "2026-07-31"),
        ("2026-08", "2026-08-01", "2026-08-31"),
        ("2026-09", "2026-09-01", "2026-09-30"),
    ]
    return months


def fetch_monthly_search_counts(gql: GitHubGraphQL, months: list[tuple[str, str, str]]) -> dict[str, dict[str, int]]:
    """Uses GraphQL aliases to batch-fetch monthly PR/Issue opened/closed/merged counts."""
    print("Fetching monthly PR & Issue aggregate counts via GraphQL aliases...")
    results: dict[str, dict[str, int]] = {m[0]: {} for m in months}

    # Split into batches of 4 months per query to stay well under GraphQL complexity limits
    for i in range(0, len(months), 4):
        batch = months[i : i + 4]
        alias_Parts = []
        for idx, (ym, start_d, end_d) in enumerate(batch):
            key = f"m{idx}"
            alias_Parts.append(
                f'{key}_pr_open: search(query: "repo:{OWNER}/{REPO} is:pr created:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
            alias_Parts.append(
                f'{key}_pr_merged: search(query: "repo:{OWNER}/{REPO} is:pr is:merged created:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
            alias_Parts.append(
                f'{key}_pr_closed_in_m: search(query: "repo:{OWNER}/{REPO} is:pr is:merged merged:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
            alias_Parts.append(
                f'{key}_iss_open: search(query: "repo:{OWNER}/{REPO} is:issue created:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
            alias_Parts.append(
                f'{key}_iss_closed_cohort: search(query: "repo:{OWNER}/{REPO} is:issue is:closed created:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
            alias_Parts.append(
                f'{key}_iss_closed_in_m: search(query: "repo:{OWNER}/{REPO} is:issue is:closed closed:{start_d}..{end_d}", type: ISSUE, first: 1) {{ issueCount }}'
            )
        q = "{\n" + "\n".join(alias_Parts) + "\n}"
        resp = gql.query(q)["data"]
        for idx, (ym, _, _) in enumerate(batch):
            key = f"m{idx}"
            results[ym] = {
                "prs_opened": resp[f"{key}_pr_open"]["issueCount"],
                "prs_merged_cohort": resp[f"{key}_pr_merged"]["issueCount"],
                "prs_merged_in_month": resp[f"{key}_pr_closed_in_m"]["issueCount"],
                "issues_opened": resp[f"{key}_iss_open"]["issueCount"],
                "issues_closed_cohort": resp[f"{key}_iss_closed_cohort"]["issueCount"],
                "issues_closed_in_month": resp[f"{key}_iss_closed_in_m"]["issueCount"],
            }
    return results


def fetch_commits_history(gql: GitHubGraphQL) -> list[dict[str, Any]]:
    """Fetches commit history with LOC additions, deletions, changedFiles, and author."""
    print("Fetching commit history via GraphQL...")
    q = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 100, after: $cursor, since: "2025-06-01T00:00:00Z", until: "2026-10-01T00:00:00Z") {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  oid
                  committedDate
                  messageHeadline
                  additions
                  deletions
                  changedFilesIfAvailable
                  author {
                    name
                    email
                    user {
                      login
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    commits = []
    cursor = None
    page = 0
    while True:
        page += 1
        data = gql.query(q, {"owner": OWNER, "name": REPO, "cursor": cursor})
        hist = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]
        nodes = hist["nodes"]
        for n in nodes:
            u_obj = (n.get("author") or {}).get("user")
            raw_login = u_obj.get("login") if u_obj else (n.get("author") or {}).get("name")
            commits.append({
                "oid": n["oid"][:8],
                "date": n["committedDate"],
                "month": n["committedDate"][:7],
                "headline": n["messageHeadline"],
                "additions": n.get("additions") or 0,
                "deletions": n.get("deletions") or 0,
                "files": n.get("changedFilesIfAvailable") or 0,
                "raw_author": raw_login,
                "author": normalize_user(raw_login),
                "is_bot": is_bot_user(raw_login),
            })
        if page % 5 == 0 or not hist["pageInfo"]["hasNextPage"]:
            print(f"  Fetched {len(commits)} commits (page {page})...")
        if not hist["pageInfo"]["hasNextPage"]:
            break
        cursor = hist["pageInfo"]["endCursor"]
    return commits


SAMPLE_SEED = 2026
SAMPLE_PER_MONTH = 50
DETAIL_BATCH = 8

PR_DETAIL_FIELDS = """
            number
            title
            url
            state
            merged
            createdAt
            closedAt
            mergedAt
            additions
            deletions
            changedFiles
            authorAssociation
            bodyText
            author { login }
            mergedBy { login }
            closingIssuesReferences(first: 5) { totalCount }
            labels(first: 10) { nodes { name } }
            comments(first: 20) {
              totalCount
              nodes { createdAt author { login } bodyText }
            }
            reviews(first: 20) {
              totalCount
              nodes { createdAt state author { login } bodyText comments { totalCount } }
            }
"""

ISSUE_DETAIL_FIELDS = """
            number
            title
            url
            state
            stateReason
            createdAt
            closedAt
            authorAssociation
            bodyText
            author { login }
            labels(first: 10) { nodes { name } }
            comments(first: 20) {
              totalCount
              nodes { createdAt author { login } bodyText }
            }
"""


def _hours_between(start_iso: str, end_iso: str | None) -> float | None:
    if not end_iso:
        return None
    s = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    e = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    return max(0.0, (e - s).total_seconds() / 3600.0)


def _first_response_hrs(created_iso: str, author: str | None, items: list[dict[str, Any]]) -> float | None:
    """Earliest reply by a human other than the author (bots excluded)."""
    times = []
    for it in items:
        login = (it.get("author") or {}).get("login")
        if is_bot_user(login):
            continue
        if normalize_user(login) == author or not it.get("createdAt"):
            continue
        h = _hours_between(created_iso, it["createdAt"])
        if h is not None:
            times.append(h)
    return min(times) if times else None


def _quotes(items: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    out = []
    for it in items:
        login = (it.get("author") or {}).get("login")
        if is_bot_user(login):
            continue
        txt = (it.get("bodyText") or "").strip().replace("\n", " ")
        if len(txt) > 25:
            out.append({"author": login, "createdAt": it.get("createdAt"), "text": txt[:600]})
    out.sort(key=lambda q: q["createdAt"] or "")
    return out[:limit]


def process_pr_node(node: dict[str, Any], ym: str) -> dict[str, Any]:
    raw_author = (node.get("author") or {}).get("login")
    norm_author = normalize_user(raw_author)
    reviews_nodes = [r for r in ((node.get("reviews") or {}).get("nodes") or []) if r]
    comments_nodes = [c for c in ((node.get("comments") or {}).get("nodes") or []) if c]
    human_reviews = [r for r in reviews_nodes if not is_bot_user((r.get("author") or {}).get("login"))]
    human_comments = [c for c in comments_nodes if not is_bot_user((c.get("author") or {}).get("login"))]
    inline_review_comments = sum((r.get("comments") or {}).get("totalCount", 0) for r in human_reviews)
    return {
        "number": node["number"],
        "month": ym,
        "title": node.get("title", ""),
        "url": node.get("url", ""),
        "state": node.get("state", ""),
        "merged": bool(node.get("merged")),
        "createdAt": node["createdAt"],
        "closedAt": node.get("closedAt"),
        "mergedAt": node.get("mergedAt"),
        "additions": node.get("additions") or 0,
        "deletions": node.get("deletions") or 0,
        "changedFiles": node.get("changedFiles") or 0,
        "authorAssociation": node.get("authorAssociation", ""),
        "raw_author": raw_author,
        "author": norm_author,
        "is_bot": is_bot_user(raw_author),
        "merged_by": (node.get("mergedBy") or {}).get("login"),
        "linked_issues": (node.get("closingIssuesReferences") or {}).get("totalCount", 0),
        "labels": [l["name"] for l in ((node.get("labels") or {}).get("nodes") or []) if l],
        "body": (node.get("bodyText") or "")[:600],
        "total_comments": (node.get("comments") or {}).get("totalCount", 0),
        "total_reviews": (node.get("reviews") or {}).get("totalCount", 0),
        "inline_review_comments": inline_review_comments,
        "human_review_interactions": len(human_reviews) + inline_review_comments + len(human_comments),
        "ttfr_hrs": _first_response_hrs(node["createdAt"], norm_author, human_reviews + human_comments),
        "ttm_hrs": _hours_between(node["createdAt"], node.get("mergedAt")),
        "ttc_hrs": None if node.get("merged") else _hours_between(node["createdAt"], node.get("closedAt")),
        "quotes": _quotes(comments_nodes + reviews_nodes),
    }


def process_issue_node(node: dict[str, Any], ym: str) -> dict[str, Any]:
    raw_author = (node.get("author") or {}).get("login")
    norm_author = normalize_user(raw_author)
    comments_nodes = [c for c in ((node.get("comments") or {}).get("nodes") or []) if c]
    human_comments = [c for c in comments_nodes if not is_bot_user((c.get("author") or {}).get("login"))]
    return {
        "number": node["number"],
        "month": ym,
        "title": node.get("title", ""),
        "url": node.get("url", ""),
        "state": node.get("state", ""),
        "stateReason": node.get("stateReason", ""),
        "createdAt": node["createdAt"],
        "closedAt": node.get("closedAt"),
        "authorAssociation": node.get("authorAssociation", ""),
        "raw_author": raw_author,
        "author": norm_author,
        "is_bot": is_bot_user(raw_author),
        "labels": [l["name"] for l in ((node.get("labels") or {}).get("nodes") or []) if l],
        "body": (node.get("bodyText") or "")[:600],
        "total_comments": (node.get("comments") or {}).get("totalCount", 0),
        "human_comments_count": len(human_comments),
        "ttfr_hrs": _first_response_hrs(node["createdAt"], norm_author, human_comments),
        "ttr_hrs": _hours_between(node["createdAt"], node.get("closedAt")),
        "quotes": _quotes(comments_nodes),
    }


def _week_windows(start_d: str, end_d: str) -> list[tuple[str, str]]:
    """Splits a month into <=7-day windows so each search stays below GitHub's 1,000-result cap."""
    s = datetime.fromisoformat(start_d)
    e = datetime.fromisoformat(end_d)
    out = []
    while s <= e:
        w_end = min(s + timedelta(days=6), e)
        out.append((s.date().isoformat(), w_end.date().isoformat()))
        s = w_end + timedelta(days=1)
    return out


def fetch_census(gql: GitHubGraphQL, months: list[tuple[str, str, str]], kind: str) -> list[dict[str, Any]]:
    """Fetches every PR or issue (light fields only) created in the study window."""
    print(f"Fetching full {kind.upper()} census (author, dates, outcome)...")
    fields = (
        "number createdAt closedAt mergedAt merged state authorAssociation author { login }"
        if kind == "pr"
        else "number createdAt closedAt state stateReason authorAssociation author { login }"
    )
    frag = "PullRequest" if kind == "pr" else "Issue"
    q = f"""
    query($qStr: String!, $cursor: String) {{
      search(query: $qStr, type: ISSUE, first: 100, after: $cursor) {{
        issueCount
        pageInfo {{ hasNextPage endCursor }}
        nodes {{ ... on {frag} {{ {fields} }} }}
      }}
    }}
    """
    rows: list[dict[str, Any]] = []
    for ym, start_d, end_d in months:
        for w_start, w_end in _week_windows(start_d, end_d):
            q_str = f"repo:{OWNER}/{REPO} is:{kind} created:{w_start}..{w_end}"
            cursor = None
            while True:
                data = gql.query(q, {"qStr": q_str, "cursor": cursor})["data"]["search"]
                if data["issueCount"] > 1000:
                    raise RuntimeError(f"Window {q_str} exceeds the 1,000-result search cap")
                for n in data["nodes"]:
                    if not n or "number" not in n:
                        continue
                    raw = (n.get("author") or {}).get("login")
                    rows.append({
                        "number": n["number"],
                        "month": ym,
                        "createdAt": n["createdAt"],
                        "closedAt": n.get("closedAt"),
                        "mergedAt": n.get("mergedAt"),
                        "merged": bool(n.get("merged")),
                        "state": n.get("state", ""),
                        "stateReason": n.get("stateReason"),
                        "authorAssociation": n.get("authorAssociation", ""),
                        "raw_author": raw,
                        "author": normalize_user(raw),
                        "is_bot": is_bot_user(raw),
                    })
                if not data["pageInfo"]["hasNextPage"]:
                    break
                cursor = data["pageInfo"]["endCursor"]
        print(f"  [{ym}] {kind} census so far: {len(rows)}")
    # Weekly windows never overlap, but de-duplicate defensively
    return list({r["number"]: r for r in rows}.values())


def draw_random_sample(census: list[dict[str, Any]], months: list[tuple[str, str, str]]) -> dict[str, list[int]]:
    """Time-stratified simple random sample: SAMPLE_PER_MONTH human items per calendar month (fixed seed)."""
    rng = random.Random(SAMPLE_SEED)
    by_month: dict[str, list[int]] = defaultdict(list)
    for r in census:
        if not r["is_bot"]:
            by_month[r["month"]].append(r["number"])
    picked = {}
    for ym, _, _ in months:
        pool = sorted(by_month[ym])
        picked[ym] = sorted(rng.sample(pool, min(SAMPLE_PER_MONTH, len(pool))))
    return picked


def fetch_details(gql: GitHubGraphQL, picked: dict[str, list[int]], kind: str) -> list[dict[str, Any]]:
    """Fetches full thread metadata for the sampled numbers, batched with GraphQL aliases."""
    print(f"Fetching details for sampled {kind.upper()}s...")
    field = "pullRequest" if kind == "pr" else "issue"
    body = PR_DETAIL_FIELDS if kind == "pr" else ISSUE_DETAIL_FIELDS
    process = process_pr_node if kind == "pr" else process_issue_node
    out: list[dict[str, Any]] = []
    for ym, numbers in picked.items():
        for i in range(0, len(numbers), DETAIL_BATCH):
            chunk = numbers[i : i + DETAIL_BATCH]
            parts = [f"n{num}: {field}(number: {num}) {{ {body} }}" for num in chunk]
            q = f'{{ repository(owner: "{OWNER}", name: "{REPO}") {{ {" ".join(parts)} }} }}'
            repo = gql.query(q)["data"]["repository"]
            for num in chunk:
                node = repo.get(f"n{num}")
                if node:
                    out.append(process(node, ym))
        print(f"  [{ym}] {kind} details: {len(out)}")
    return out


def main() -> None:
    token = discover_token()
    gql = GitHubGraphQL(token)
    months = get_months_list()

    monthly_counts = fetch_monthly_search_counts(gql, months)
    commits = fetch_commits_history(gql)
    pr_census = fetch_census(gql, months, "pr")
    issue_census = fetch_census(gql, months, "issue")
    pr_pick = draw_random_sample(pr_census, months)
    issue_pick = draw_random_sample(issue_census, months)
    sampled_prs = fetch_details(gql, pr_pick, "pr")
    sampled_issues = fetch_details(gql, issue_pick, "issue")

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "repo": f"{OWNER}/{REPO}",
        "months": [m[0] for m in months],
        "sampling": {
            "method": "time-stratified simple random sample of human-authored items per calendar month",
            "seed": SAMPLE_SEED,
            "per_month": SAMPLE_PER_MONTH,
        },
        "monthly_search_counts": monthly_counts,
        "commits": commits,
        "pr_census": pr_census,
        "issue_census": issue_census,
        "sampled_prs": sampled_prs,
        "sampled_issues": sampled_issues,
    }

    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Saved dataset to {DATA_OUT} ({len(commits)} commits, {len(pr_census)} PRs / {len(issue_census)} issues in census, "
        f"{len(sampled_prs)} sampled PRs, {len(sampled_issues)} sampled issues)"
    )


if __name__ == "__main__":
    main()
