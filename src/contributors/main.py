import os
import re
import sys
import time
from typing import Any

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def get_headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    if not token and os.path.exists(".env"):
        for line in open(".env"):
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                token = line.split("=", 1)[1].strip("\"'")
                break

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Capstone-Software-Engineering-Script",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


HEADERS = get_headers()


def fetch_total_contributors(repo: str) -> int:
    url = f"https://api.github.com/repos/{repo}/contributors?per_page=1&anon=true"
    res = requests.get(url, headers=HEADERS)
    if not res.ok:
        return 0
    link = res.headers.get("Link", "")
    if match := re.search(r'page=(\d+)>; rel="last"', link):
        return int(match.group(1))
    return len(res.json()) if isinstance(res.json(), list) else 0


def fetch_committers(repo: str, limit: int = 15) -> dict[str, int]:
    url = f"https://api.github.com/repos/{repo}/contributors?per_page={limit}"
    res = requests.get(url, headers=HEADERS)
    if not res.ok:
        return {}
    return {
        item.get("login", "Anon"): item.get("contributions", 0)
        for item in res.json()[:limit]
        if "login" in item
    }


def fetch_search_count(repo: str, query: str) -> int:
    url = "https://api.github.com/search/issues"
    params = {"q": f"repo:{repo} {query}"}
    while True:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            return res.json().get("total_count", 0)
        elif res.status_code in (403, 429):
            reset_ts = int(res.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(1, reset_ts - int(time.time()) + 1)
            console.print(
                f"[yellow]Rate limit reached on GitHub Search API. Waiting {sleep_time}s to reset...[/yellow]"
            )
            time.sleep(sleep_time)
        else:
            return 0


def create_activity_table(
    title: str,
    rows: list[dict[str, Any]],
    title_style: str = "bold cyan",
) -> Table:
    table = Table(
        title=title,
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style=title_style,
    )
    table.add_column("Contributor", style="bold white", no_wrap=True)
    table.add_column("Commits", justify="right", style="green")
    table.add_column("PRs", justify="right", style="cyan")
    table.add_column("Issues", justify="right", style="yellow")
    table.add_column("Total", justify="right", style="bold magenta")

    for r in rows:
        table.add_row(
            r["user"],
            str(r["commits"]) if r["commits"] is not None else "--",
            str(r["prs"]) if r["prs"] is not None else "--",
            str(r["issues"]) if r["issues"] is not None else "--",
            str(r["total"]),
        )
    return table


def generate_latex_table(
    rows: list[dict[str, Any]],
    caption: str,
    label: str = "tab:contributors",
) -> str:
    lines = [
        "{\n\\small",
        "\\begin{longtable}{@{} l rrr r @{}}",
        f"    \\caption{{{caption}}} \\label{{{label}}} \\\\",
        "    \\toprule",
        "    \\textbf{Contributor} & \\textbf{Commits} & \\textbf{PRs} & \\textbf{Issues} & \\textbf{Total} \\\\",
        "    \\midrule",
        "    \\endfirsthead\n",
        "    \\multicolumn{5}{@{}l}{\\small\\textit{Continued from previous page}} \\\\",
        "    \\toprule",
        "    \\textbf{Contributor} & \\textbf{Commits} & \\textbf{PRs} & \\textbf{Issues} & \\textbf{Total} \\\\",
        "    \\midrule",
        "    \\endhead\n",
        "    \\midrule",
        "    \\multicolumn{5}{r@{}}{\\small\\textit{Continued on next page}} \\\\",
        "    \\endfoot\n",
        "    \\bottomrule",
        "    \\endlastfoot\n",
        "    % --- Data rows ---",
    ]

    for r in rows:
        c_str = str(r["commits"]) if r["commits"] is not None else "--"
        p_str = str(r["prs"]) if r["prs"] is not None else "--"
        i_str = str(r["issues"]) if r["issues"] is not None else "--"
        user_escaped = r["user"].replace("_", "\\_")
        if "[" in user_escaped or "]" in user_escaped:
            user_escaped = f"{{{user_escaped}}}"
        lines.append(f"    {user_escaped:<26} & {c_str:<4} & {p_str:<4} & {i_str:<4} & {r['total']:<4} \\\\")

    lines.extend(["\\end{longtable}", "}"])
    return "\n".join(lines)


def main():
    repo = "google-gemini/gemini-cli"

    # 1. Total contributors
    total_contributors = fetch_total_contributors(repo)
    console.print(
        Panel(
            f"[bold cyan]{total_contributors}[/bold cyan] total contributors",
            title="Contributor Count",
            border_style="cyan",
        )
    )

    # 2. Gather candidates for Top 10 across Commits, PRs, and Issues
    with console.status("[bold green]Fetching contributors and activity data from GitHub..."):
        committers = fetch_committers(repo, limit=15)

        candidates = list(committers.keys())
        # Add prominent issue/PR creators who might not be in top 15 committers
        for extra in ["aniruddhaadak80", "sehoon38", "gundermanc"]:
            if extra not in candidates:
                candidates.append(extra)

        user_data: dict[str, dict[str, int]] = {}
        for user in candidates:
            c = committers.get(user, 0)
            prs = fetch_search_count(repo, f"type:pr author:{user}")
            issues = fetch_search_count(repo, f"type:issue author:{user}")
            user_data[user] = {
                "commits": c,
                "prs": prs,
                "issues": issues,
            }

    # 3. Determine the True Top 10 for each category
    top_10_commits = set(
        sorted(user_data.keys(), key=lambda u: user_data[u]["commits"], reverse=True)[:10]
    )
    top_10_prs = set(
        sorted(user_data.keys(), key=lambda u: user_data[u]["prs"], reverse=True)[:10]
    )
    top_10_issues = set(
        sorted(user_data.keys(), key=lambda u: user_data[u]["issues"], reverse=True)[:10]
    )

    # 4. Build Table 1: Unified Matrix
    # "--" only appears in slots that a person is NOT top 10 for
    unified_users = top_10_commits | top_10_prs | top_10_issues
    unified_rows: list[dict[str, Any]] = []

    for user in unified_users:
        c = user_data[user]["commits"] if user in top_10_commits else None
        p = user_data[user]["prs"] if user in top_10_prs else None
        i = user_data[user]["issues"] if user in top_10_issues else None
        total = (c or 0) + (p or 0) + (i or 0)
        unified_rows.append({
            "user": user,
            "commits": c,
            "prs": p,
            "issues": i,
            "total": total,
        })

    # Sort descending by Total
    unified_rows.sort(key=lambda r: (r["total"], r["commits"] or 0, r["prs"] or 0, r["issues"] or 0), reverse=True)

    unified_table = create_activity_table(
        title="Unified Matrix of Top 10 Users by Commits, PRs, and Issues Sorted by Total Amount",
        rows=unified_rows,
        title_style="bold magenta",
    )
    console.print(unified_table)

    # 5. Build Table 2: Top 10 Commit Contributors Activity (Full breakdown without --)
    top_committers_sorted = sorted(top_10_commits, key=lambda u: user_data[u]["commits"], reverse=True)
    commit_rows: list[dict[str, Any]] = []

    for user in top_committers_sorted:
        c = user_data[user]["commits"]
        p = user_data[user]["prs"]
        i = user_data[user]["issues"]
        commit_rows.append({
            "user": user,
            "commits": c,
            "prs": p,
            "issues": i,
            "total": c + p + i,
        })

    commit_table = create_activity_table(
        title="Top 10 Commit Contributors — Pull Requests and Issues Activity",
        rows=commit_rows,
        title_style="bold green",
    )
    console.print(commit_table)

    if "--latex" in sys.argv:
        console.print("\n[bold]LaTeX Output (Unified Table):[/bold]\n")
        print(generate_latex_table(unified_rows, "Unified Matrix of Top 10 Users by Commits, Pull Requests (PRs) and Issues Sorted by Total Amount.", label="tab:contributors"))
        console.print("\n[bold]LaTeX Output (Top Committers Table):[/bold]\n")
        print(generate_latex_table(commit_rows, "Top 10 Commit Contributors Activity (Commits, PRs, and Issues).", label="tab:top_committers"))


if __name__ == "__main__":
    main()