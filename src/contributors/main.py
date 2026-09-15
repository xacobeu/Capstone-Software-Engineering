from datetime import datetime, timedelta, timezone
from typing import Callable, Any
from collections import Counter

import requests
import re

HEADERS = {"Accept": "application/vnd.github+json"}
Extractor = Callable[[list[dict[str, Any]]], dict[str, int]]

def fetch_contributor_count(url: str) -> int:
    response = requests.get(url)
    
    if "Link" in response.headers:
        links = response.headers["Link"]
        match = re.search(r'page=(\d+)>; rel="last"', links)
        if match:
            return int(match.group(1))
            
    return 0

def fetch_top_10(url: str, extractor: Extractor) -> dict[str, int]:
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        return {}
    return extractor(response.json())


def main():
    repo = "google-gemini/gemini-cli"
    contributors_url = f"https://api.github.com/repos/{repo}/contributors?per_page=1&anon=true"

    print(f"\n=== CONTRIBUTOR COUNT ===\n{fetch_contributor_count(contributors_url)}")

    one_year_ago: str = (
        (datetime.now(timezone.utc) - timedelta(days=365))
        .isoformat()
        .replace("+00:00", "Z")
    )

    activities: dict[str, tuple[str, Extractor]] = {

        "commits": (f"https://api.github.com/repos/{repo}/contributors?since={one_year_ago}&per_page=10",
            lambda data: {
                item.get("login", "Anon"): item.get("contributions", 0) for item in data[:10]
            },
        ),

        "pull requests": (
            f"https://api.github.com/repos/{repo}/pulls?since={one_year_ago}&state=all&per_page=100",
            lambda data: {
                str(user): count
                for user, count in Counter(
                    item["user"]["login"]
                    for item in data
                    if item.get("user")
                ).most_common(10)
            },
        ),

        "issues": (f"https://api.github.com/repos/{repo}/issues?since={one_year_ago}&state=all&per_page=100",
            lambda data: dict(
                Counter(
                    item["user"]["login"]
                    for item in data
                    if "pull_request" not in item and item.get("user")
                ).most_common(10)
            ),
        ),
    }

    for activity, (url, extractor) in activities.items():
        print(f"\n=== TOP 10 FOR {activity.upper()} ===")
        for name, count in fetch_top_10(url, extractor).items():
            print(f"User {name} has {count} {activity} in this repository.")


if __name__ == "__main__":
    main()
