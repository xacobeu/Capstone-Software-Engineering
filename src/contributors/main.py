from datetime import datetime, timedelta, timezone
from typing import Callable, Any
from collections import Counter

import requests
import re

HEADERS = {"Accept": "application/vnd.github+json"}
Extractor = Callable[[requests.Response], dict[str, int]]

def fetch(url: str, extractor: Extractor) -> dict[str, int]:
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        return {}
    return extractor(response)


def main():
    repo = "google-gemini/gemini-cli"

    one_year_ago: str = (
        (datetime.now(timezone.utc) - timedelta(days=365))
        .isoformat()
        .replace("+00:00", "Z")
    )

    activities: dict[str, tuple[str, Extractor]] = {
        "contributors": (
            f"https://api.github.com/repos/{repo}/contributors?per_page=1&anon=true",
            lambda res: {
                "total": int(match.group(1))
                if (match := re.search(r'page=(\d+)>; rel="last"', res.headers.get("Link", "")))
                else len(res.json())
            },
        ),

        "commits": (
            f"https://api.github.com/repos/{repo}/contributors?since={one_year_ago}&per_page=10",
            lambda res: {
                item.get("login", "Anon"): item.get("contributions", 0)
                for item in res.json()[:10]
            },
        ),

        "pull requests": (
            f"https://api.github.com/repos/{repo}/pulls?since={one_year_ago}&state=all&per_page=100",
            lambda res: {
                str(user): count
                for user, count in Counter(
                    item["user"]["login"]
                    for item in res.json()
                    if item.get("user")
                ).most_common(10)
            },
        ),

        "issues": (
            f"https://api.github.com/repos/{repo}/issues?since={one_year_ago}&state=all&per_page=100",
            lambda res: dict(
                Counter(
                    item["user"]["login"]
                    for item in res.json()
                    if "pull_request" not in item and item.get("user")
                ).most_common(10)
            ),
        ),
    }

    url, extractor = activities.pop("contributors")
    print(f"\n=== CONTRIBUTOR COUNT ===\n{fetch(url, extractor).get("total", "Total not found")}")

    for activity, (url, extractor) in activities.items():
        print(f"\n=== TOP 10 FOR {activity.upper()} ===")
        for name, count in fetch(url, extractor).items():
            print(f"{name}: {count} {activity}")


if __name__ == "__main__":
    main()
