import requests
import re

def fetch_contributor_count(url: str) -> int:
    response = requests.get(url)
    
    if "Link" in response.headers:
        links = response.headers["Link"]
        match = re.search(r'page=(\d+)>; rel="last"', links)
        if match:
            return int(match.group(1))
            
    return 0

def fetch_top_10_for(activity: str) -> dict[str, int]:

    return {}

def main():

    print(f"Contributor count: {
        fetch_contributor_count("https://api.github.com/repos/google-gemini/gemini-cli/contributors?per_page=1&anon=true")
    }")

    activities: list[str] = [
        "commits",
        "issues"
    ]

    for activity in activities:
        for name, count in fetch_top_10_for(activity):
            print(f"User {name} has {count} {activity} in this repository.")


if __name__ == "__main__":
    main()
