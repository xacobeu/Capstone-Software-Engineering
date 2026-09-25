from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .github_client import GitHubClient

console = Console()

ORDERED_SIZES = ["size/xs", "size/s", "size/m", "size/l", "size/xl", "size/xxl"]

# ===========
# == Model ==
# ===========


@dataclass(slots=True)
class ContributorStats:
    username: str
    commits: int | None = None
    prs: int | None = None
    issues: int | None = None
    position: str = ""
    level: str = ""
    skills: list[tuple[str, int]] = field(default_factory=list)
    size_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def total_activity(self) -> int:
        return (self.commits or 0) + (self.prs or 0) + (self.issues or 0)


# ===============================
# Presentation & Visualization ==
# ===============================


def escape_latex(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    parts = re.split(r"(\\href\{[^{}]*\}\{[^{}]*\})", text)
    for i in range(0, len(parts), 2):
        for char, rep in replacements.items():
            parts[i] = parts[i].replace(char, rep)
    res = "".join(parts)
    if "[" in res or "]" in res:
        res = f"{{{res}}}"
    return res


def format_count_latex(val: int | None) -> str:
    return str(val) if val is not None else "\\textendash"


def export_latex_tables(
    unified_matrix_users: list[ContributorStats],
    top_committers: list[ContributorStats],
    output_path: str,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Table 7.1: Unified Matrix Sorted by Total Amount
    t1_rows = []
    for c in unified_matrix_users:
        u = escape_latex(c.username)
        cm = format_count_latex(c.commits)
        pr = format_count_latex(c.prs)
        iss = format_count_latex(c.issues)
        tot = str(c.total_activity)
        t1_rows.append(
            f"    {u:<24} & {cm:>8} & {pr:>8} & {iss:>8} & {tot:>8} \\\\"
        )
    t1_body = "\n".join(t1_rows)

    # 2. Table 7.2: Top Committers with Position & Level left empty
    t2_rows = []
    for c in top_committers:
        u = escape_latex(c.username)
        cm = str(c.commits or 0)
        pr = str(c.prs or 0)
        iss = str(c.issues or 0)
        t2_rows.append(
            f"    {u:<24} & {cm:>4} & {pr:>4} & {iss:>5} & {'':<30} & {'':<4} \\\\"
        )
    t2_body = "\n".join(t2_rows)

    # 3. Table 7.3: Top Focus Areas
    t3_rows = []
    for c in top_committers:
        u = escape_latex(c.username)
        skills_str = (
            ", ".join(f"{area} ({cnt})" for area, cnt in c.skills)
            or "\\textendash"
        )
        skills_escaped = escape_latex(skills_str)
        t3_rows.append(f"    {u:<24} & {skills_escaped} \\\\")
    t3_body = "\n".join(t3_rows)

    latex_content = f"""{{
\\small
\\begin{{longtable}}{{@{{}} l rrr r @{{}}}}
    \\caption{{Unified Matrix of Top 10 Users by Commits, Pull Requests (PRs) and Issues Sorted by Total Amount.}} \\label{{tab:unified_matrix}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Commits}} & \\textbf{{PRs}} & \\textbf{{Issues}} & \\textbf{{Total}} \\\\
    \\midrule
    \\endfirsthead

    \\multicolumn{{5}}{{@{{}}l}}{{\\small\\textit{{Continued from previous page}}}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Commits}} & \\textbf{{PRs}} & \\textbf{{Issues}} & \\textbf{{Total}} \\\\
    \\midrule
    \\endhead

    \\midrule
    \\multicolumn{{5}}{{r@{{}}}}{{\\small\\textit{{Continued on next page}}}} \\\\
    \\endfoot

    \\bottomrule
    \\endlastfoot

    % --- Data rows ---
{t1_body}
\\end{{longtable}}
}}

{{
\\small
\\begin{{longtable}}{{@{{}} l rrr l c @{{}}}}
    \\caption{{Top 10 Contributors by Number of Commits. Included Number of PRs and Issues. Included Professional Roles and Seniority Level (Sources Linked).}} \\label{{tab:top_committers}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Commits}} & \\textbf{{PRs}} & \\textbf{{Issues}} & \\textbf{{Position}} & \\textbf{{Level}} \\\\
    \\midrule
    \\endfirsthead

    \\multicolumn{{6}}{{@{{}}l}}{{\\small\\textit{{Continued from previous page}}}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Commits}} & \\textbf{{PRs}} & \\textbf{{Issues}} & \\textbf{{Position}} & \\textbf{{Level}} \\\\
    \\midrule
    \\endhead

    \\midrule
    \\multicolumn{{6}}{{r@{{}}}}{{\\small\\textit{{Continued on next page}}}} \\\\
    \\endfoot

    \\bottomrule
    \\endlastfoot

    % --- Data rows ---
{t2_body}
\\end{{longtable}}
}}

{{
\\small
\\begin{{longtable}}{{@{{}} l p{{11.5cm}} @{{}}}}
    \\caption{{Top 10 Commit Contributors Focus Areas.}} \\label{{tab:top_committers_skills}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Top Focus Areas}} \\\\
    \\midrule
    \\endfirsthead

    \\multicolumn{{2}}{{@{{}}l}}{{\\small\\textit{{Continued from previous page}}}} \\\\
    \\toprule
    \\textbf{{Contributor}} & \\textbf{{Top Focus Areas}} \\\\
    \\midrule
    \\endhead

    \\midrule
    \\multicolumn{{2}}{{r@{{}}}}{{\\small\\textit{{Continued on next page}}}} \\\\
    \\endfoot

    \\bottomrule
    \\endlastfoot

    % --- Data rows ---
{t3_body}
\\end{{longtable}}
}}
"""
    path.write_text(latex_content, encoding="utf-8")
    console.print(f"[bold green]Exported LaTeX tables to '{output_path}'[/bold green]")


def render_tables(
    unified_top: list[ContributorStats],
    top_committers: list[ContributorStats],
) -> None:
    # Table 7.1 Display
    u_table = Table(
        title="Unified Matrix: Top Users in Last 1 Year",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold green",
    )
    u_table.add_column("Contributor", style="bold white", no_wrap=True)
    u_table.add_column("Commits", justify="right", style="green")
    u_table.add_column("PRs", justify="right", style="cyan")
    u_table.add_column("Issues", justify="right", style="yellow")
    u_table.add_column("Total", justify="right", style="bold magenta")

    for c in unified_top:
        u_table.add_row(
            c.username,
            str(c.commits) if c.commits is not None else "--",
            str(c.prs) if c.prs is not None else "--",
            str(c.issues) if c.issues is not None else "--",
            str(c.total_activity),
        )
    console.print(u_table)

    # Table 7.2 Display
    act_table = Table(
        title="Top 10 Commit Contributors Activity (Last 1 Year)",
        box=box.ROUNDED,
        header_style="bold cyan",
        title_style="bold green",
    )
    act_table.add_column("Contributor", style="bold white", no_wrap=True)
    act_table.add_column("Commits", justify="right", style="green")
    act_table.add_column("PRs", justify="right", style="cyan")
    act_table.add_column("Issues", justify="right", style="yellow")
    act_table.add_column("Total", justify="right", style="bold magenta")

    for c in top_committers:
        act_table.add_row(
            c.username,
            str(c.commits or 0),
            str(c.prs or 0),
            str(c.issues or 0),
            str(c.total_activity),
        )
    console.print(act_table)

    # Table 7.3 Display
    skills_table = Table(
        title="Top 10 Commit Contributors — Focus Areas (Last 1 Year)",
        box=box.ROUNDED,
        header_style="bold yellow",
        title_style="bold yellow",
    )
    skills_table.add_column("Contributor", style="bold white", no_wrap=True)
    skills_table.add_column("Top Focus Areas", justify="left", style="cyan")

    for c in top_committers:
        skills_str = ", ".join(f"{area} ({cnt})" for area, cnt in c.skills) or "--"
        skills_table.add_row(c.username, skills_str)
    console.print(skills_table)


def plot_pr_size_distribution(
    contributors: list[ContributorStats],
    output_filename: str = "output/pr_sizes_distribution.pdf",
) -> None:
    path = Path(output_filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {c.username: c.size_distribution for c in contributors}
    df = pd.DataFrame(data).T.fillna(0)

    valid_sizes = [s for s in ORDERED_SIZES if s in df.columns]
    if not valid_sizes:
        console.print("[yellow]No size/* tags found to plot.[/yellow]")
        return

    df = df[valid_sizes]
    totals = df.sum(axis=1)
    df_pct = df.div(totals.replace(0, 1), axis=0) * 100

    plt.style.use(
        "seaborn-v0_8-whitegrid"
        if "seaborn-v0_8-whitegrid" in plt.style.available
        else "default"
    )
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    colors = plt.cm.YlGnBu(np.linspace(0.3, 0.9, len(valid_sizes)))

    left = np.zeros(len(df_pct))
    for i, col in enumerate(valid_sizes):
        label_clean = col.removeprefix("size/").upper()
        ax.barh(
            df_pct.index,
            df_pct[col],
            left=left,
            label=label_clean,
            color=colors[i],
            edgecolor="white",
            linewidth=0.8,
            height=0.65,
        )
        left += df_pct[col]

    ax.set_xlabel("Percentage of Authored PRs (%)", fontsize=11, fontweight="bold")
    ax.set_title(
        f"PR Size Distribution by Top {len(contributors)} Commit Contributors (Last 1 Year)",
        fontsize=13,
        fontweight="bold",
        pad=16,
    )
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.grid(axis="y")
    ax.legend(
        title="PR Size",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=True,
    )

    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    console.print(
        f"[bold green]Saved PR size distribution chart to '{path}'[/bold green]"
    )


# ================
# Orchestration ==
# ================


def analyze_repository(
    repo: str,
    top_n: int = 10,
    output_chart: str = "output/pr_sizes_distribution.pdf",
    latex_output: str | None = "output/contributor_tables.tex",
    cache_path: str = "output/.contributors_cache.json",
    force_refresh: bool = False,
) -> None:
    client = GitHubClient()

    # Dynamic 1-year window
    since_dt = datetime.now(timezone.utc) - timedelta(days=365)
    since_iso = since_dt.strftime("%Y-%m-%d")

    activity = client.get_all_activity_since(
        repo=repo,
        since_iso=since_iso,
        cache_path=cache_path,
        force_refresh=force_refresh,
    )

    total_contributors = activity.get("total_contributors_all_time", 0)
    console.print(
        Panel(
            f"[bold cyan]{total_contributors}[/bold cyan] total contributors (All-Time)\n"
            f"[bold cyan]Window:[/bold cyan] {since_iso} to Present (1 Year)",
            title=f"Contributor Count — {repo}",
            border_style="cyan",
        )
    )

    commit_counts = Counter(activity.get("commits", {}))
    pr_counts = Counter(activity.get("prs", {}))
    issue_counts = Counter(activity.get("issues", {}))
    author_skills = activity.get("author_skills", {})
    author_sizes = activity.get("author_sizes", {})

    # Extract Top N lists for each category
    top_commit_list = commit_counts.most_common(top_n)
    top_pr_list = pr_counts.most_common(top_n)
    top_issue_list = issue_counts.most_common(top_n)

    top_commit_users = {u for u, _ in top_commit_list}
    top_pr_users = {u for u, _ in top_pr_list}
    top_issue_users = {u for u, _ in top_issue_list}

    # Combined pool of everyone who made at least one top 10
    all_qualified_users = top_commit_users | top_pr_users | top_issue_users

    # 1. Build Unified Matrix (Table 7.1)
    # Only keep the count if the user reached the top 10 for that metric
    unified_users: list[ContributorStats] = []
    for user in all_qualified_users:
        cm = commit_counts.get(user) if user in top_commit_users else None
        pr = pr_counts.get(user) if user in top_pr_users else None
        iss = issue_counts.get(user) if user in top_issue_users else None

        unified_users.append(
            ContributorStats(
                username=user,
                commits=cm,
                prs=pr,
                issues=iss,
            )
        )

    # Sort descending by Total, with tie breakers
    unified_users.sort(
        key=lambda c: (c.total_activity, c.commits or 0, c.prs or 0, c.issues or 0),
        reverse=True,
    )

    # 2. Build Top 10 Committers (Table 7.2 & 7.3)
    top_committers: list[ContributorStats] = []
    for user, cm in top_commit_list:
        pr = pr_counts.get(user, 0)
        iss = issue_counts.get(user, 0)
        user_skills_dict = author_skills.get(user, {})
        skills = sorted(
            [
                (k, v)
                for k, v in user_skills_dict.items()
                if k and k.lower() not in ("unknown", "none", "null")
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        sizes = author_sizes.get(user, {})
        top_committers.append(
            ContributorStats(
                username=user,
                commits=cm,
                prs=pr,
                issues=iss,
                skills=skills,
                size_distribution=sizes,
            )
        )

    # 3. Display & Export
    render_tables(unified_top=unified_users, top_committers=top_committers)
    plot_pr_size_distribution(top_committers, output_filename=output_chart)

    if latex_output:
        export_latex_tables(
            unified_matrix_users=unified_users,
            top_committers=top_committers,
            output_path=latex_output,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze GitHub repository contributors.")
    parser.add_argument(
        "--output",
        type=str,
        default="output/pr_sizes_distribution.pdf",
        help="File path to save the stacked bar chart (default: output/pr_sizes_distribution.pdf)",
    )
    parser.add_argument(
        "--latex",
        type=str,
        nargs="?",
        const="output/contributor_tables.tex",
        default="output/contributor_tables.tex",
        help="Export LaTeX tables to file (default: output/contributor_tables.tex)",
    )
    parser.add_argument(
        "--no-latex",
        action="store_true",
        help="Disable LaTeX export",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-fetching activity data from GitHub API",
    )
    args = parser.parse_args()

    latex_file = None if args.no_latex else args.latex

    analyze_repository(
        repo="google-gemini/gemini-cli",
        top_n=10,
        output_chart=args.output,
        latex_output=latex_file,
        force_refresh=args.refresh,
    )


if __name__ == "__main__":
    main()
