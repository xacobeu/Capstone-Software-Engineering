import os
import json
import urllib.request
from collections import Counter
from itertools import combinations
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN missing from .env file!")

OWNER = "google-gemini"
REPO = "gemini-cli"
TARGET_PRS = 500


def is_bot(login: str) -> bool:
    if not login:
        return True
    lo = login.lower()
    return (
        lo.endswith("[bot]")
        or lo in {
            "github-actions",
            "gemini-code-assist",
            "gemini-cli",
            "gemini-cli-robot",
            "google-cla",
        }
    )


GRAPHQL_QUERY = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 50, after: $cursor, states: CLOSED, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        merged
        author { login }
        files(first: 50) {
          nodes { path }
        }
        comments(first: 30) {
          nodes {
            author { login }
            body
          }
        }
        reviews(first: 30) {
          nodes {
            author { login }
            body
            comments(first: 30) {
              nodes {
                author { login }
                body
              }
            }
          }
        }
      }
    }
  }
}
"""


def run_query(cursor=None):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Python-Analysis",
    }
    payload = json.dumps({
        "query": GRAPHQL_QUERY,
        "variables": {"owner": OWNER, "repo": REPO, "cursor": cursor},
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/graphql", data=payload, headers=headers
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def main():
    print(f"Fetching {TARGET_PRS} closed PRs via GraphQL API...")

    pair_interactions = Counter()
    awareness_evidence = []
    pr_file_map = {}

    cursor = None
    fetched = 0

    while fetched < TARGET_PRS:
        result = run_query(cursor)
        if "errors" in result:
            print("GraphQL Error:", result["errors"])
            break

        data = result["data"]["repository"]["pullRequests"]
        prs = data["nodes"]
        page_info = data["pageInfo"]

        for pr in prs:
            pr_num = pr["number"]
            author = pr["author"]["login"] if pr.get("author") else None
            participants = set()

            if author and not is_bot(author):
                participants.add(author)

            # 1. Collect Issue Comments
            for c in pr["comments"]["nodes"]:
                c_author = c["author"]["login"] if c.get("author") else None
                if c_author and not is_bot(c_author):
                    participants.add(c_author)
                    body = c.get("body", "")
                    if any(
                        w in body.lower()
                        for w in [
                            "#",
                            "@",
                            "blocked by",
                            "per your",
                            "ptal",
                            "superseded",
                        ]
                    ):
                        awareness_evidence.append({
                            "pr": pr_num,
                            "author": c_author,
                            "quote": body.replace("\n", " ").strip()[:140],
                        })

            # 2. Collect Reviews & Inline Review Comments
            for r in pr["reviews"]["nodes"]:
                r_author = r["author"]["login"] if r.get("author") else None
                if r_author and not is_bot(r_author):
                    participants.add(r_author)
                    r_body = r.get("body", "")
                    if r_body and any(
                        w in r_body.lower()
                        for w in [
                            "#",
                            "@",
                            "blocked by",
                            "ptal",
                            "superseded",
                        ]
                    ):
                        awareness_evidence.append({
                            "pr": pr_num,
                            "author": r_author,
                            "quote": r_body.replace("\n", " ").strip()[:140],
                        })

                for rc in r["comments"]["nodes"]:
                    rc_author = rc["author"]["login"] if rc.get("author") else None
                    if rc_author and not is_bot(rc_author):
                        participants.add(rc_author)

            # Record collaboration pairs
            for pair in combinations(sorted(participants), 2):
                pair_interactions[pair] += 1

            # Map files for counter-example detection
            file_paths = [f["path"] for f in pr["files"]["nodes"]]
            pr_file_map[pr_num] = {
                "author": author or "unknown",
                "merged": pr["merged"],
                "files": set(file_paths),
            }

        fetched += len(prs)
        print(f"  Processed {fetched}/{TARGET_PRS} PRs...")

        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    print("\n=== Top Collaborating Human Pairs (Sample size: 500 PRs) ===")
    for (u1, u2), count in pair_interactions.most_common(10):
        print(f"  {u1} <-> {u2}: {count} shared PR discussions")

    print("\n=== Candidate Awareness Quotes ===")
    for item in awareness_evidence[:8]:
        print(f"  PR #{item['pr']} [{item['author']}]: \"{item['quote']}...\"")

    print("\n=== Candidate Counter-Examples (Overlapping Files, One Unmerged) ===")
    file_to_prs = {}
    ignored_files = {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        ".gitignore",
    }

    # Build inverted index
    for pr_id, data in pr_file_map.items():
        if is_bot(data["author"]):
            continue
        for file_path in data["files"]:
            if any(ign in file_path for ign in ignored_files):
                continue
            file_to_prs.setdefault(file_path, []).append(pr_id)

    seen_pairs = set()
    found = 0

    for file_path, pr_list in file_to_prs.items():
        if len(pr_list) < 2:
            continue

        for id_1, id_2 in combinations(pr_list, 2):
            pair_key = tuple(sorted([id_1, id_2]))
            if pair_key in seen_pairs:
                continue

            d1 = pr_file_map[id_1]
            d2 = pr_file_map[id_2]

            # Ensure distinct human authors
            if (
                d1["author"] == d2["author"]
                or is_bot(d1["author"])
                or is_bot(d2["author"])
            ):
                continue

            # One merged, one closed unmerged
            if d1["merged"] != d2["merged"]:
                seen_pairs.add(pair_key)
                shared = d1["files"].intersection(d2["files"])

                print(f"  PR #{id_1} ({d1['author']}) vs PR #{id_2} ({d2['author']})")
                print(f"  Shared files: {list(shared)[:3]}")
                print(f"  Merged status: #{id_1}={d1['merged']}, #{id_2}={d2['merged']}\n")

                found += 1
                if found >= 5:
                    break
        if found >= 5:
            break

    if found == 0:
        print("  No unmerged/merged file collisions found in the sampled window.")


if __name__ == "__main__":
    main()
