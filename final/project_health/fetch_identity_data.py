"""Fetches the extra fields needed for bot / alternate-account detection on the census:
commit author names and emails, PR and issue titles, GitHub account types, and bot-fix PR authors."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fetch_data import OWNER, REPO, GitHubGraphQL, _week_windows, discover_token, get_months_list

CENSUS_IN = Path(__file__).resolve().parent / "data" / "project_health_data.json"
OUT = Path(__file__).resolve().parent / "data" / "identity_data.json"


def fetch_commit_identities(gql: GitHubGraphQL) -> list[dict[str, str | None]]:
    q = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        defaultBranchRef { target { ... on Commit {
          history(first: 100, after: $cursor, since: "2025-06-01T00:00:00Z", until: "2026-10-01T00:00:00Z") {
            pageInfo { hasNextPage endCursor }
            nodes { oid author { name email user { login } } }
          }
        } } }
      }
    }
    """
    rows, cursor = [], None
    while True:
        hist = gql.query(q, {"owner": OWNER, "name": REPO, "cursor": cursor})["data"]["repository"][
            "defaultBranchRef"]["target"]["history"]
        for n in hist["nodes"]:
            a = n.get("author") or {}
            rows.append({
                "oid": n["oid"][:8],
                "login": (a.get("user") or {}).get("login"),
                "name": a.get("name"),
                "email": (a.get("email") or "").lower(),
            })
        if not hist["pageInfo"]["hasNextPage"]:
            break
        cursor = hist["pageInfo"]["endCursor"]
    print(f"  commit identities: {len(rows)}")
    return rows


def fetch_titles(gql: GitHubGraphQL, kind: str) -> dict[int, str]:
    frag = "PullRequest" if kind == "pr" else "Issue"
    q = f"""
    query($qStr: String!, $cursor: String) {{
      search(query: $qStr, type: ISSUE, first: 100, after: $cursor) {{
        pageInfo {{ hasNextPage endCursor }}
        nodes {{ ... on {frag} {{ number title }} }}
      }}
    }}
    """
    titles: dict[int, str] = {}
    for _, start_d, end_d in get_months_list():
        for w_start, w_end in _week_windows(start_d, end_d):
            cursor = None
            while True:
                s = gql.query(q, {"qStr": f"repo:{OWNER}/{REPO} is:{kind} created:{w_start}..{w_end}", "cursor": cursor})[
                    "data"]["search"]
                for n in s["nodes"]:
                    if n and "number" in n:
                        titles[n["number"]] = n["title"]
                if not s["pageInfo"]["hasNextPage"]:
                    break
                cursor = s["pageInfo"]["endCursor"]
    print(f"  {kind} titles: {len(titles)}")
    return titles


def fetch_account_types(gql: GitHubGraphQL, logins: list[str]) -> dict[str, str]:
    """'User', 'Organization', or 'NotFound' (GitHub Apps / bots and deleted accounts are not users)."""
    types: dict[str, str] = {}
    for i in range(0, len(logins), 60):
        chunk = logins[i : i + 60]
        parts = [f'u{j}: repositoryOwner(login: {json.dumps(l)}) {{ __typename }}' for j, l in enumerate(chunk)]
        data = gql.query("{" + " ".join(parts) + "}").get("data") or {}
        for j, login in enumerate(chunk):
            node = data.get(f"u{j}")
            types[login] = node["__typename"] if node else "NotFound"
    print(f"  account types: {len(types)}")
    return types


def fetch_bot_fix_authors(gql: GitHubGraphQL) -> dict[str, int]:
    q = """
    query($cursor: String) {
      search(query: "repo:google-gemini/gemini-cli is:pr label:bot-fix", type: ISSUE, first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { ... on PullRequest { author { login } } }
      }
    }
    """
    counts: dict[str, int] = defaultdict(int)
    cursor = None
    while True:
        s = gql.query(q, {"cursor": cursor})["data"]["search"]
        for n in s["nodes"]:
            login = ((n or {}).get("author") or {}).get("login")
            if login:
                counts[login] += 1
        if not s["pageInfo"]["hasNextPage"]:
            break
        cursor = s["pageInfo"]["endCursor"]
    print(f"  bot-fix authors: {dict(counts)}")
    return dict(counts)


def main() -> None:
    gql = GitHubGraphQL(discover_token())
    census = json.loads(CENSUS_IN.read_text(encoding="utf-8"))
    logins = sorted({
        x["raw_author"] for coll in ("commits", "pr_census", "issue_census") for x in census[coll] if x.get("raw_author")
    })
    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "commit_identities": fetch_commit_identities(gql),
        "pr_titles": fetch_titles(gql, "pr"),
        "issue_titles": fetch_titles(gql, "issue"),
        "bot_fix_authors": fetch_bot_fix_authors(gql),
        "account_types": fetch_account_types(gql, logins),
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
