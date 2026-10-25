"""Fetches the head branch name of every PR in the study window (signal for agent-generated PRs)."""
from __future__ import annotations

import json
from pathlib import Path

from fetch_data import OWNER, REPO, GitHubGraphQL, _week_windows, discover_token, get_months_list

OUT = Path(__file__).resolve().parent / "data" / "pr_branches.json"


def main() -> None:
    gql = GitHubGraphQL(discover_token())
    q = """
    query($qStr: String!, $cursor: String) {
      search(query: $qStr, type: ISSUE, first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { ... on PullRequest { number headRefName isCrossRepository } }
      }
    }
    """
    branches: dict[int, dict[str, object]] = {}
    for ym, start_d, end_d in get_months_list():
        for w_start, w_end in _week_windows(start_d, end_d):
            cursor = None
            while True:
                s = gql.query(q, {"qStr": f"repo:{OWNER}/{REPO} is:pr created:{w_start}..{w_end}", "cursor": cursor})[
                    "data"]["search"]
                for n in s["nodes"]:
                    if n and "number" in n:
                        branches[n["number"]] = {"branch": n["headRefName"], "fork": n["isCrossRepository"]}
                if not s["pageInfo"]["hasNextPage"]:
                    break
                cursor = s["pageInfo"]["endCursor"]
        print(f"  [{ym}] {len(branches)} PRs", flush=True)
    OUT.write_text(json.dumps(branches, indent=0), encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
