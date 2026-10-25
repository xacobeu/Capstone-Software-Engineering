from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from bisect import bisect_left
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Ensure writable matplotlib cache directory
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplcache"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_data import is_bot_user, normalize_user  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_IN = Path(__file__).resolve().parent / "data" / "project_health_data.json"
FIG_DIR = Path(__file__).resolve().parent / "figures"
SUMMARY_OUT = Path(__file__).resolve().parent / "data" / "computed_metrics_summary.json"

# Every figure is one full-width graph; titles and definitions live in the LaTeX captions and text
FIG_SIZE = (10.5, 4.0)
TIER_LABEL = {"Frequent / Core": "Frequent", "Episodic Community": "Episodic", "Newcomer (≤ 3 Actions)": "Newcomer"}
QUAL_OUT = Path(__file__).resolve().parent / "data" / "qualitative_sample.json"
QUAL_IDS = Path(__file__).resolve().parent / "qualitative_sample_ids.json"


def set_pub_style() -> None:
    plt.style.use(
        "seaborn-v0_8-whitegrid"
        if "seaborn-v0_8-whitegrid" in plt.style.available
        else "default"
    )
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "bold",
        "legend.fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "figure.dpi": 300,
    })


def save_fig(fig: plt.Figure, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / f"{name}.png"
    pdf_path = FIG_DIR / f"{name}.pdf"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path} and {pdf_path}")


def finish(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    save_fig(fig, name)


def compute_lorenz_and_gini(values: list[int | float]) -> tuple[np.ndarray, np.ndarray, float]:
    arr = np.sort(np.array([v for v in values if v > 0], dtype=float))
    if len(arr) == 0:
        return np.array([0.0, 1.0]), np.array([0.0, 1.0]), 0.0
    cum_people = np.linspace(0.0, 100.0, len(arr) + 1)
    cum_val = np.concatenate([[0.0], np.cumsum(arr) / arr.sum() * 100.0])
    # Flip so x-axis is "Top X% of contributors" -> "Cumulative % of output"
    desc_arr = np.sort(arr)[::-1]
    top_x = np.linspace(0.0, 100.0, len(desc_arr) + 1)
    top_y = np.concatenate([[0.0], np.cumsum(desc_arr) / desc_arr.sum() * 100.0])

    n = len(arr)
    index = np.arange(1, n + 1)
    gini = float((np.sum((2 * index - n - 1) * arr)) / (n * np.sum(arr)))
    return top_x, top_y, gini


def main() -> None:
    set_pub_style()
    payload = json.loads(DATA_IN.read_text(encoding="utf-8"))

    months: list[str] = payload["months"]
    search_counts: dict[str, dict[str, int]] = payload["monthly_search_counts"]
    commits: list[dict[str, Any]] = payload["commits"]
    sampled_prs: list[dict[str, Any]] = payload["sampled_prs"]
    sampled_issues: list[dict[str, Any]] = payload["sampled_issues"]

    pr_census: list[dict[str, Any]] = payload["pr_census"]
    issue_census: list[dict[str, Any]] = payload["issue_census"]

    # Re-apply bot and alias decisions (account_decisions.json) so they take effect without re-fetching
    for coll in (commits, pr_census, issue_census, sampled_prs, sampled_issues):
        for x in coll:
            x["is_bot"] = is_bot_user(x.get("raw_author"))
            x["author"] = normalize_user(x.get("raw_author"))

    # Filter to human commits, PRs, issues
    human_commits = [c for c in commits if not c.get("is_bot") and c.get("author")]
    human_prs = [p for p in sampled_prs if not p.get("is_bot") and p.get("author")]
    human_issues = [i for i in sampled_issues if not i.get("is_bot") and i.get("author")]
    human_pr_census = [p for p in pr_census if not p.get("is_bot") and p.get("author")]
    human_issue_census = [i for i in issue_census if not i.get("is_bot") and i.get("author")]

    # Monthly human-only PR/issue counts from the census (search counts include bot-authored items)
    census_m: dict[str, Counter[str]] = defaultdict(Counter)
    for p in human_pr_census:
        census_m[p["month"]]["prs_opened"] += 1
        census_m[p["month"]]["prs_merged_cohort"] += int(p["merged"])
        if p.get("mergedAt"):
            census_m[p["mergedAt"][:7]]["prs_merged_in_month"] += 1
    for i in human_issue_census:
        census_m[i["month"]]["issues_opened"] += 1
        census_m[i["month"]]["issues_closed_cohort"] += int(i["state"] == "CLOSED")
        if i.get("closedAt"):
            census_m[i["closedAt"][:7]]["issues_closed_in_month"] += 1

    # Group commits by month
    commits_by_m: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in human_commits:
        commits_by_m[c["month"]].append(c)

    prs_by_m: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in human_prs:
        prs_by_m[p["month"]].append(p)

    issues_by_m: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for i in human_issues:
        issues_by_m[i["month"]].append(i)

    # Filter active months (where there is meaningful activity)
    active_months = [m for m in months if (
        len(commits_by_m[m]) + search_counts[m]["prs_opened"] + search_counts[m]["issues_opened"]
    ) > 0]

    # Build monthly dataframe
    rows = []
    for m in active_months:
        m_commits = commits_by_m[m]
        c_cnt = len(m_commits)
        c_loc = sum(c["additions"] + c["deletions"] for c in m_commits)
        c_files = sum(c["files"] for c in m_commits)

        sc = census_m[m]
        pr_open = sc["prs_opened"]
        pr_merged_in_m = sc["prs_merged_in_month"]
        pr_merged_cohort = sc["prs_merged_cohort"]
        iss_open = sc["issues_opened"]
        iss_closed_in_m = sc["issues_closed_in_month"]
        iss_closed_cohort = sc["issues_closed_cohort"]

        # Sampled PR metrics for month m
        m_prs = prs_by_m[m]
        m_merged_prs = [p for p in m_prs if p["merged"]]
        avg_review_per_merged = (
            np.mean([p["human_review_interactions"] for p in m_merged_prs])
            if m_merged_prs
            else np.mean([p["human_review_interactions"] for p in m_prs]) if m_prs else 0.0
        )
        avg_pr_loc = np.mean([p["additions"] + p["deletions"] for p in m_prs]) if m_prs else 0.0
        avg_pr_files = np.mean([p["changedFiles"] for p in m_prs]) if m_prs else 0.0

        m_iss = issues_by_m[m]
        avg_iss_comments = np.mean([i["total_comments"] for i in m_iss]) if m_iss else 0.0

        rows.append({
            "month": m,
            "commits": c_cnt,
            "commit_loc": c_loc,
            "commit_files": c_files,
            "normalized_churn": c_loc / c_cnt if c_cnt > 0 else 0.0,
            "avg_files_per_commit": c_files / c_cnt if c_cnt > 0 else 0.0,
            "prs_opened": pr_open,
            "prs_merged_in_month": pr_merged_in_m,
            "prs_merged_cohort": pr_merged_cohort,
            "pr_acceptance_rate": (pr_merged_cohort / pr_open * 100.0) if pr_open > 0 else 0.0,
            "pr_throughput_ratio": (pr_merged_in_m / pr_open * 100.0) if pr_open > 0 else 0.0,
            "issues_opened": iss_open,
            "issues_closed_in_month": iss_closed_in_m,
            "issues_closed_cohort": iss_closed_cohort,
            "issue_resolution_ratio": (iss_closed_in_m / iss_open * 100.0) if iss_open > 0 else 0.0,
            "issue_cohort_resolution": (iss_closed_cohort / iss_open * 100.0) if iss_open > 0 else 0.0,
            "monthly_activity_volume": c_cnt + pr_open + iss_open,
            "review_engagement_ratio": float(avg_review_per_merged),
            "issue_discussion_depth": float(avg_iss_comments),
            "avg_pr_loc": float(avg_pr_loc),
            "avg_pr_files": float(avg_pr_files),
            "all_prs_opened_incl_bots": search_counts[m]["prs_opened"],
            "all_issues_opened_incl_bots": search_counts[m]["issues_opened"],
        })

    df = pd.DataFrame(rows)

    # =========================================================================
    # Monthly activity and compound metrics: one full-width graph per figure
    # (titles live in the LaTeX captions)
    # =========================================================================
    x = np.arange(len(df))
    month_labels = list(df["month"])
    p1_end = month_labels.index("2025-12")
    p2_end = month_labels.index("2026-04")

    def month_axis(ax: plt.Axes) -> None:
        ax.set_xticks(x)
        ax.set_xticklabels(month_labels, rotation=45, ha="right")
        ax.set_xlim(-0.6, len(x) - 0.4)

    def shade_phases(ax: plt.Axes) -> None:
        spans = [(-0.6, p1_end + 0.5, "I"), (p1_end + 0.5, p2_end + 0.5, "II"), (p2_end + 0.5, len(x) - 0.4, "III")]
        for i, (a, b, name) in enumerate(spans):
            if i != 1:
                ax.axvspan(a, b, color="#f0f0f0", zorder=0)
            ax.text((a + b) / 2, 1.01, f"Phase {name}", transform=ax.get_xaxis_transform(),
                    ha="center", va="bottom", fontsize=9, color="#555555")

    # Activity by type
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    shade_phases(ax)
    ax.plot(x, df["issues_opened"], marker="o", linewidth=2, color="#d95f02", label="Issues opened")
    ax.plot(x, df["issues_closed_in_month"], marker="o", linestyle="--", linewidth=1.6, color="#fdae6b", label="Issues closed")
    ax.plot(x, df["prs_opened"], marker="o", linewidth=2, color="#1f78b4", label="PRs opened")
    ax.plot(x, df["prs_merged_in_month"], marker="o", linestyle="--", linewidth=1.6, color="#6baed6", label="PRs merged")
    ax.plot(x, df["commits"], marker="o", linewidth=2, color="#2ca02c", label="Commits")
    ax.set_ylabel("Count per month")
    month_axis(ax)
    ax.legend(loc="upper left", ncol=3, frameon=True)
    finish(fig, "activity_by_type")

    # Monthly activity volume
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.bar(x, df["commits"], color="#2ca02c", width=0.6, label="Commits")
    ax.bar(x, df["prs_opened"], bottom=df["commits"], color="#1f78b4", width=0.6, label="PRs")
    ax.bar(x, df["issues_opened"], bottom=df["commits"] + df["prs_opened"], color="#d95f02", width=0.6, label="Issues")
    ax.set_ylabel("Events per month")
    month_axis(ax)
    ax.legend(loc="upper right", frameon=True)
    finish(fig, "activity_volume")

    # PR acceptance (CHAOSS Change Request Acceptance Ratio: accepted vs. declined per period)
    cohort = {m: Counter() for m in month_labels}
    for p in human_pr_census:
        if p["month"] in cohort:
            cohort[p["month"]]["merged" if p["merged"] else "open" if p["state"] == "OPEN" else "closed"] += 1
    n_merged = np.array([cohort[m]["merged"] for m in month_labels])
    n_closed = np.array([cohort[m]["closed"] for m in month_labels])
    n_open = np.array([cohort[m]["open"] for m in month_labels])
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.bar(x, n_merged, color="#1b9e77", width=0.6, label="Merged")
    ax.bar(x, n_closed, bottom=n_merged, color="#d95f02", width=0.6, label="Closed without merge")
    ax.bar(x, n_open, bottom=n_merged + n_closed, color="#bdbdbd", width=0.6, label="Still open")
    totals = n_merged + n_closed + n_open
    for i in range(len(x)):
        ax.text(x[i], totals[i] + totals.max() * 0.01, f"{n_merged[i] / totals[i] * 100:.0f}%",
                ha="center", va="bottom", fontsize=8, color="#333333")
    ax.set_ylabel("Human PRs opened per month")
    ax.set_ylim(0, totals.max() * 1.1)
    month_axis(ax)
    ax.legend(loc="upper left", frameon=True)
    finish(fig, "pr_acceptance")

    # Issue resolution ratio
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.axhline(100.0, color="#999999", linestyle=":", linewidth=1.2)
    ax.plot(x, df["issue_resolution_ratio"], marker="o", linewidth=2, color="#d95f02")
    ax.set_ylabel("Issues closed per 100 opened")
    month_axis(ax)
    finish(fig, "issue_resolution")

    # Review engagement and issue discussion depth
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(x, df["review_engagement_ratio"], marker="o", linewidth=2, color="#756bb1", label="Review interactions per merged PR")
    ax.plot(x, df["issue_discussion_depth"], marker="o", linewidth=2, color="#31a354", label="Comments per issue")
    ax.set_ylabel("Comments per item")
    month_axis(ax)
    ax.legend(loc="upper left", frameon=True)
    finish(fig, "engagement_depth")

    # Normalized churn
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(x, df["normalized_churn"], marker="o", linewidth=2, color="#e7298a")
    ax.set_ylabel("Lines changed per commit")
    month_axis(ax)
    finish(fig, "churn")

    # =========================================================================
    # FIGURE 3: Contributor Threshold Justification (Lorenz Curve & Survival)
    # =========================================================================
    # Aggregate all events per human author
    author_events: dict[str, list[datetime]] = defaultdict(list)
    author_commits_cnt: Counter[str] = Counter()
    author_prs_cnt: Counter[str] = Counter()
    author_issues_cnt: Counter[str] = Counter()

    for c in human_commits:
        u = c["author"]
        author_commits_cnt[u] += 1
        author_events[u].append(datetime.fromisoformat(c["date"].replace("Z", "+00:00")))
    # Full census of PRs and issues, so contributor histories are complete
    for p in human_pr_census:
        u = p["author"]
        author_prs_cnt[u] += 1
        author_events[u].append(datetime.fromisoformat(p["createdAt"].replace("Z", "+00:00")))
    for i in human_issue_census:
        u = i["author"]
        author_issues_cnt[u] += 1
        author_events[u].append(datetime.fromisoformat(i["createdAt"].replace("Z", "+00:00")))

    all_authors = set(author_events.keys())
    total_actions_per_user = [len(author_events[u]) for u in all_authors]

    # Also compute inter-action gaps for returning users
    inter_gaps_days: list[float] = []
    first_to_third_days: list[float] = []
    for u, dts in author_events.items():
        dts_sorted = sorted(dts)
        if len(dts_sorted) >= 2:
            for idx in range(1, len(dts_sorted)):
                gap = (dts_sorted[idx] - dts_sorted[idx - 1]).total_seconds() / 86400.0
                if gap > 0.01:
                    inter_gaps_days.append(gap)
            span = (dts_sorted[min(2, len(dts_sorted) - 1)] - dts_sorted[0]).total_seconds() / 86400.0
            first_to_third_days.append(span)

    # Concentration of activity (Lorenz curves)
    tx_c, ty_c, gini_c = compute_lorenz_and_gini(list(author_commits_cnt.values()))
    tx_p, ty_p, gini_p = compute_lorenz_and_gini(list(author_prs_cnt.values()))
    tx_all, ty_all, gini_all = compute_lorenz_and_gini(total_actions_per_user)
    idx_20 = np.searchsorted(tx_c, 20.0)
    pct_commits_at_20 = float(ty_c[min(idx_20, len(ty_c) - 1)])

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(tx_c, ty_c, linewidth=2.2, color="#2ca02c", label=f"Commits (Gini {gini_c:.2f})")
    ax.plot(tx_p, ty_p, linewidth=2.2, color="#1f78b4", label=f"PRs (Gini {gini_p:.2f})")
    ax.plot(tx_all, ty_all, linewidth=1.8, linestyle="--", color="#756bb1", label=f"All actions (Gini {gini_all:.2f})")
    ax.axvline(20.0, color="#999999", linestyle=":", linewidth=1.2)
    ax.scatter([20.0], [pct_commits_at_20], color="#2ca02c", zorder=5, s=40)
    ax.text(19, pct_commits_at_20 + 3, f"Top 20%: {pct_commits_at_20:.1f}% of commits", ha="right", fontsize=9, color="#333333")
    ax.set_xlabel("Most active contributors (%)")
    ax.set_ylabel("Share of activity (%)")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 102)
    ax.legend(loc="lower right", frameon=True)
    finish(fig, "concentration")

    # Survival of contributors by number of actions (bar chart: discrete k)
    k_vals = np.arange(1, 16)
    surv_pct = [np.mean([cnt >= k for cnt in total_actions_per_user]) * 100.0 for k in k_vals]
    pct_at_4 = surv_pct[3]  # share with more than 3 actions
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.bar(k_vals, surv_pct, width=0.7, color=["#d95f02" if k <= 3 else "#9e9e9e" for k in k_vals])
    for k, v in zip(k_vals, surv_pct):
        ax.text(k, v + 1, f"{v:.0f}%", ha="center", va="bottom", fontsize=8, color="#333333")
    ax.set_xlabel("At least k actions")
    ax.set_ylabel("Contributors (%)")
    ax.set_xticks(k_vals)
    ax.set_ylim(0, 108)
    finish(fig, "survival")

    # =========================================================================
    # FIGURE 4: Contributor Composition Over Time (Stacked Area + Counts)
    # =========================================================================
    # Classify every known contributor at the end of each month
    comp_rows = []
    for m in active_months:
        # End of month timestamp
        yr, mo = map(int, m.split("-"))
        if mo == 12:
            m_end = datetime(yr + 1, 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
        else:
            m_end = datetime(yr, mo + 1, 1, tzinfo=datetime.now().astimezone().tzinfo)
        # Last second of month m in UTC (first instant of the next month minus one second)
        m_end_utc = m_end.replace(tzinfo=timezone.utc) - timedelta(seconds=1)

        w60_start = m_end_utc - timedelta(days=60)
        w120_start = m_end_utc - timedelta(days=120)

        # Users who have acted on or before m_end_utc
        active_w60_counts: dict[str, int] = {}
        user_state: dict[str, dict[str, Any]] = {}

        for u, dts in author_events.items():
            past_dts = [d for d in dts if d <= m_end_utc]
            if not past_dts:
                continue
            first_dt = min(past_dts)
            last_dt = max(past_dts)
            tot_cnt = len(past_dts)
            cnt_60 = sum(1 for d in past_dts if d >= w60_start)
            if cnt_60 > 0:
                active_w60_counts[u] = cnt_60
            user_state[u] = {
                "first_dt": first_dt,
                "last_dt": last_dt,
                "tot_cnt": tot_cnt,
                "cnt_60": cnt_60,
            }

        # Determine top 20% threshold among active users in last 60 days
        sorted_w60 = sorted(active_w60_counts.items(), key=lambda x: x[1], reverse=True)
        top_20_n = max(1, int(np.ceil(len(sorted_w60) * 0.20)))
        freq_set = {u for u, _ in sorted_w60[:top_20_n]}

        freq_cnt = 0
        newcomer_cnt = 0
        episodic_cnt = 0
        dormant_cnt = 0

        for u, st in user_state.items():
            days_since_first = (m_end_utc - st["first_dt"]).total_seconds() / 86400.0
            days_since_last = (m_end_utc - st["last_dt"]).total_seconds() / 86400.0

            if u in freq_set and st["tot_cnt"] > 1:
                freq_cnt += 1
            elif days_since_first <= 60.0 and st["tot_cnt"] <= 3:
                newcomer_cnt += 1
            elif (st["tot_cnt"] > 3 and days_since_last > 120.0) or (st["tot_cnt"] <= 3 and days_since_last > 60.0):
                dormant_cnt += 1
            else:
                episodic_cnt += 1

        tot_known = max(1, freq_cnt + newcomer_cnt + episodic_cnt + dormant_cnt)
        comp_rows.append({
            "month": m,
            "frequent": freq_cnt,
            "newcomers": newcomer_cnt,
            "episodic": episodic_cnt,
            "dormant": dormant_cnt,
            "frequent_pct": freq_cnt / tot_known * 100.0,
            "newcomers_pct": newcomer_cnt / tot_known * 100.0,
            "episodic_pct": episodic_cnt / tot_known * 100.0,
            "dormant_pct": dormant_cnt / tot_known * 100.0,
        })

    comp_df = pd.DataFrame(comp_rows)

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    cx = np.arange(len(comp_df))
    ax.stackplot(
        cx,
        comp_df["frequent_pct"],
        comp_df["episodic_pct"],
        comp_df["newcomers_pct"],
        comp_df["dormant_pct"],
        labels=["Frequent", "Episodic", "Newcomer", "Dormant"],
        colors=["#1b9e77", "#66a61e", "#7570b3", "#d95f02"],
        alpha=0.85,
    )
    ax.set_xticks(cx)
    ax.set_xticklabels(comp_df["month"], rotation=45, ha="right")
    ax.set_xlim(0, len(comp_df) - 1)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Contributors (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=4, frameon=False)
    finish(fig, "contributor_composition")

    # =========================================================================
    # FIGURE 5: Process-Oriented Metrics: Newcomer vs Core Asymmetry
    # =========================================================================
    # Classify each PR by its author's tier at the moment the PR was opened, using only prior activity.
    # (Using lifetime activity would be circular: authors whose PRs get merged accumulate commits.)
    sorted_events = {u: sorted(dts) for u, dts in author_events.items()}

    def get_pr_tier(pr: dict[str, Any]) -> str:
        u = pr["author"]
        t = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
        evs = sorted_events.get(u, [])
        k_prior = bisect_left(evs, t)
        # Newcomer: this PR is among the author's first 3 actions, all within the last 60 days
        if k_prior < 3 and (k_prior == 0 or (t - evs[0]).days <= 60):
            return "Newcomer (≤ 3 Actions)"
        # Frequent: top 20% of contributors active in the 60 days before the PR (same rule as Figure 4)
        w_start = t - timedelta(days=60)
        counts = []
        own = 0
        for v, v_evs in sorted_events.items():
            c = bisect_left(v_evs, t) - bisect_left(v_evs, w_start)
            if c > 0:
                counts.append(c)
                if v == u:
                    own = c
        if own > 0 and counts:
            counts.sort(reverse=True)
            cutoff = counts[max(0, int(np.ceil(len(counts) * 0.20)) - 1)]
            if own >= cutoff:
                return "Frequent / Core"
        return "Episodic Community"

    def get_phase(ym: str) -> str:
        if ym <= "2025-12":
            return "Phase I\n(Jun–Dec '25)"
        if ym <= "2026-04":
            return "Phase II\n(Jan–Apr '26)"
        return "Phase III\n(May–Sep '26)"

    for p in human_prs:
        p["tier"] = get_pr_tier(p)
        p["phase"] = get_phase(p["month"])

    tiers = ["Frequent / Core", "Episodic Community", "Newcomer (≤ 3 Actions)"]
    phases = ["Phase I\n(Jun–Dec '25)", "Phase II\n(Jan–Apr '26)", "Phase III\n(May–Sep '26)"]

    tier_colors = {"Frequent / Core": "#1b9e77", "Episodic Community": "#7570b3", "Newcomer (≤ 3 Actions)": "#d95f02"}

    # PR acceptance per tier and phase
    bar_w = 0.25
    px = np.arange(len(phases))
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    for idx, t in enumerate(tiers):
        rates = []
        for ph in phases:
            sub = [p for p in human_prs if p["tier"] == t and p["phase"] == ph]
            rates.append((sum(1 for p in sub if p["merged"]) / len(sub) * 100.0) if sub else 0.0)
        ax.bar(px + (idx - 1) * bar_w, rates, width=bar_w, color=tier_colors[t], label=TIER_LABEL[t])
        for j, r in enumerate(rates):
            ax.text(px[j] + (idx - 1) * bar_w, r + 1, f"{r:.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(px)
    ax.set_xticklabels([ph.replace("\n", " ") for ph in phases])
    ax.set_ylabel("PRs merged (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", frameon=True)
    finish(fig, "tier_acceptance")

    # Median time to first response / to merge per tier
    ttfr_meds = []
    ttm_meds = []
    for t in tiers:
        sub_ttfr = [p["ttfr_hrs"] for p in human_prs if p["tier"] == t and p["ttfr_hrs"] is not None]
        sub_ttm = [p["ttm_hrs"] for p in human_prs if p["tier"] == t and p["ttm_hrs"] is not None]
        ttfr_meds.append(float(np.median(sub_ttfr)) if sub_ttfr else 0.0)
        ttm_meds.append(float(np.median(sub_ttm)) if sub_ttm else 0.0)

    # Time-to-first-response heat map (CHAOSS / Augur style): months x tier and outcome
    heat_rows = [
        ("Frequent / Core", True), ("Frequent / Core", False),
        ("Newcomer (≤ 3 Actions)", True), ("Newcomer (≤ 3 Actions)", False),
    ]
    heat = np.full((len(heat_rows), len(month_labels)), np.nan)
    heat_table = {}
    for r, (t, merged) in enumerate(heat_rows):
        row_key = f"{TIER_LABEL[t]}, {'merged' if merged else 'not merged'}"
        heat_table[row_key] = {}
        for c_i, m in enumerate(month_labels):
            sub = [p for p in human_prs if p["tier"] == t and p["month"] == m and p["merged"] == merged and p["state"] != "OPEN"]
            resp = [p["ttfr_hrs"] / 24.0 for p in sub if p["ttfr_hrs"] is not None]
            heat_table[row_key][m] = {"n": len(sub), "responded": len(resp),
                                      "median_days": float(np.median(resp)) if resp else None}
            if len(sub) >= 3 and resp:
                heat[r, c_i] = float(np.median(resp))
    cmap = plt.get_cmap("YlOrRd").copy()
    cmap.set_bad("#e6e6e6")
    fig, ax = plt.subplots(figsize=(10.5, 3.4))
    im = ax.imshow(np.ma.masked_invalid(np.minimum(heat, 7.0)), aspect="auto", cmap=cmap, vmin=0, vmax=7)
    for r in range(heat.shape[0]):
        for c_i in range(heat.shape[1]):
            if not np.isnan(heat[r, c_i]):
                v = heat[r, c_i]
                ax.text(c_i, r, f"{v:.1f}", ha="center", va="center", fontsize=8,
                        color="white" if v >= 4.5 else "#222222")
    ax.set_yticks(range(len(heat_rows)))
    ax.set_yticklabels(list(heat_table))
    ax.set_xticks(range(len(month_labels)))
    ax.set_xticklabels(month_labels, rotation=45, ha="right")
    ax.grid(False)
    cbar = fig.colorbar(im, ax=ax, pad=0.01, ticks=[0, 1, 2, 3, 4, 5, 6, 7])
    cbar.ax.set_yticklabels(["0", "1", "2", "3", "4", "5", "6", "≥7"])
    cbar.set_label("Median days")
    finish(fig, "ttfr_heatmap")

    # Median time to merge per tier
    tx = np.arange(len(tiers))
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.bar(tx, ttm_meds, width=0.5, color=[tier_colors[t] for t in tiers])
    for i_t in range(len(tiers)):
        ax.text(tx[i_t], ttm_meds[i_t] + max(ttm_meds) * 0.02, f"{ttm_meds[i_t]:.1f} h", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(tx)
    ax.set_xticklabels([TIER_LABEL[t] for t in tiers])
    ax.set_ylabel("Median hours to merge")
    ax.set_ylim(0, max(ttm_meds) * 1.15)
    finish(fig, "ttm_by_tier")

    # PR acceptance by PR size
    size_bins = [
        ("XS\n(≤10 LOC)", 0, 10),
        ("S\n(11–50)", 11, 50),
        ("M\n(51–250)", 51, 250),
        ("L\n(251–1k)", 251, 1000),
        ("XL\n(>1k LOC)", 1001, 10**9),
    ]
    core_sz_rates = []
    ext_sz_rates = []
    for _, lo_b, hi_b in size_bins:
        c_sub = [
            p for p in human_prs
            if p["tier"] == "Frequent / Core" and lo_b <= (p["additions"] + p["deletions"]) <= hi_b
        ]
        e_sub = [
            p for p in human_prs
            if p["tier"] != "Frequent / Core" and lo_b <= (p["additions"] + p["deletions"]) <= hi_b
        ]
        core_sz_rates.append((sum(1 for p in c_sub if p["merged"]) / len(c_sub) * 100.0) if c_sub else 0.0)
        ext_sz_rates.append((sum(1 for p in e_sub if p["merged"]) / len(e_sub) * 100.0) if e_sub else 0.0)

    sx = np.arange(len(size_bins))
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(sx, core_sz_rates, marker="o", linewidth=2, color="#1b9e77", label="Frequent")
    ax.plot(sx, ext_sz_rates, marker="o", linewidth=2, color="#d95f02", label="Episodic + Newcomer")
    ax.set_xticks(sx)
    ax.set_xticklabels([b[0].replace("\n", " ") for b in size_bins])
    ax.set_xlabel("PR size (lines changed)")
    ax.set_ylabel("PRs merged (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", frameon=True)
    finish(fig, "size_acceptance")

    # =========================================================================
    # Export Computed Summary Statistics & Qualitative Candidates for Report
    # =========================================================================
    unmerged_newcomer_prs = [
        {
            "number": p["number"],
            "month": p["month"],
            "author": p["author"],
            "title": p["title"],
            "url": p["url"],
            "additions": p["additions"],
            "deletions": p["deletions"],
            "labels": p["labels"],
            "ttfr_hrs": p["ttfr_hrs"],
            "ttc_hrs": p["ttc_hrs"],
            "quotes": p["quotes"],
        }
        for p in human_prs
        if p["tier"] == "Newcomer (≤ 3 Actions)" and not p["merged"] and p["state"] == "CLOSED"
    ]

    merged_newcomer_prs = [
        {
            "number": p["number"],
            "month": p["month"],
            "author": p["author"],
            "title": p["title"],
            "url": p["url"],
            "additions": p["additions"],
            "deletions": p["deletions"],
            "labels": p["labels"],
            "ttfr_hrs": p["ttfr_hrs"],
            "ttm_hrs": p["ttm_hrs"],
            "quotes": p["quotes"],
        }
        for p in human_prs
        if p["tier"] == "Newcomer (≤ 3 Actions)" and p["merged"]
    ]

    notable_issues = [
        {
            "number": i["number"],
            "month": i["month"],
            "author": i["author"],
            "title": i["title"],
            "url": i["url"],
            "state": i["state"],
            "stateReason": i["stateReason"],
            "labels": i["labels"],
            "total_comments": i["total_comments"],
            "ttfr_hrs": i["ttfr_hrs"],
            "quotes": i["quotes"],
        }
        for i in human_issues
        if i["quotes"] or i["total_comments"] >= 4
    ]

    # Stratified random qualitative sample: Tier x Phase x Outcome for PRs, Phase x Outcome for issues
    rng = np.random.default_rng(2026)
    qual_prs = []
    for t in tiers:
        for ph in phases:
            for merged in (True, False):
                cell = [p for p in human_prs if p["tier"] == t and p["phase"] == ph and p["merged"] == merged and p["state"] != "OPEN"]
                k = min(3 if t == "Frequent / Core" else 2 if merged else 3, len(cell))
                for j in rng.choice(len(cell), size=k, replace=False) if k else []:
                    qual_prs.append({**cell[int(j)], "phase": ph.replace("\n", " ")})
    for i in human_issues:
        i["phase"] = get_phase(i["month"]).replace("\n", " ")
    qual_issues = []
    for ph in {i["phase"] for i in human_issues}:
        for outcome in ("COMPLETED", "OTHER"):
            cell = [
                i for i in human_issues
                if i["phase"] == ph and i["state"] == "CLOSED"
                and ((i.get("stateReason") == "COMPLETED") == (outcome == "COMPLETED"))
            ]
            k = min(5, len(cell))
            for j in rng.choice(len(cell), size=k, replace=False) if k else []:
                qual_issues.append({**cell[int(j)], "outcome": outcome})
    # The coded sample is frozen: later changes to the bot decisions must not redraw items already coded
    if QUAL_IDS.is_file():
        frozen = json.loads(QUAL_IDS.read_text(encoding="utf-8"))
        pr_by_num = {p["number"]: p for p in human_prs}
        iss_by_num = {i["number"]: i for i in human_issues}
        qual_prs = [{**pr_by_num[n], "phase": pr_by_num[n]["phase"].replace("\n", " ")} for n in frozen["prs"]]
        qual_issues = [
            {**iss_by_num[n], "outcome": "COMPLETED" if iss_by_num[n].get("stateReason") == "COMPLETED" else "OTHER"}
            for n in frozen["issues"]
        ]
    QUAL_OUT.write_text(json.dumps({"prs": qual_prs, "issues": qual_issues}, indent=2), encoding="utf-8")
    print(f"Saved qualitative sample ({len(qual_prs)} PRs, {len(qual_issues)} issues) to {QUAL_OUT}")

    # Bot footprint across the full census
    # Items whose author account was deleted ("ghost", login None) are excluded too, but reported separately
    bot_footprint = {
        "bot_commits": sum(1 for c in commits if c.get("is_bot") and c.get("raw_author")),
        "bot_prs": sum(1 for p in pr_census if p.get("is_bot") and p.get("raw_author")),
        "bot_issues": sum(1 for i in issue_census if i.get("is_bot") and i.get("raw_author")),
        "deleted_author_prs": sum(1 for p in pr_census if not p.get("raw_author")),
        "deleted_author_issues": sum(1 for i in issue_census if not i.get("raw_author")),
        "total_prs": len(pr_census),
        "total_issues": len(issue_census),
        "bot_accounts_seen": sorted({
            x["raw_author"] for x in commits + pr_census + issue_census if x.get("is_bot") and x.get("raw_author")
        }),
    }

    # Newcomer-friendliness (session 5 example): share with >1 contribution, time from first to second
    first_to_second_days = [
        (dts[1] - dts[0]).total_seconds() / 86400.0 for dts in sorted_events.values() if len(dts) >= 2
    ]

    # Acceptance by GitHub author association (MEMBER = google-gemini org member)
    assoc_summary = {}
    for a in sorted({p["authorAssociation"] for p in human_prs}):
        sub = [p for p in human_prs if p["authorAssociation"] == a]
        assoc_summary[a] = {
            "count": len(sub),
            "acceptance_rate_pct": sum(p["merged"] for p in sub) / len(sub) * 100.0,
            "median_ttfr_hrs": float(np.median([p["ttfr_hrs"] for p in sub if p["ttfr_hrs"] is not None]))
            if any(p["ttfr_hrs"] is not None for p in sub) else None,
        }

    tier_phase = {
        t: {
            ph.replace("\n", " "): {
                "n": len(sub := [p for p in human_prs if p["tier"] == t and p["phase"] == ph]),
                "acceptance_rate_pct": (sum(p["merged"] for p in sub) / len(sub) * 100.0) if sub else None,
            }
            for ph in phases
        }
        for t in tiers
    }

    # Frequent tier split by write access (COLLABORATOR/MEMBER/OWNER = maintainer role) vs. outside authors
    frequent_split = {
        group: {
            ph.replace("\n", " "): {
                "n": len(sub := [
                    p for p in human_prs
                    if p["tier"] == "Frequent / Core" and p["phase"] == ph
                    and (p["authorAssociation"] in ("COLLABORATOR", "MEMBER", "OWNER")) == (group == "write_access")
                ]),
                "acceptance_rate_pct": (sum(p["merged"] for p in sub) / len(sub) * 100.0) if sub else None,
            }
            for ph in phases
        }
        for group in ("write_access", "no_write_access")
    }

    size_rates = {
        "bins": [b[0].replace("\n", " ") for b in size_bins],
        "frequent": core_sz_rates,
        "others": ext_sz_rates,
        "newcomer_only": [
            (sum(p["merged"] for p in s) / len(s) * 100.0) if (s := [
                p for p in human_prs if p["tier"] == "Newcomer (≤ 3 Actions)" and lo <= p["additions"] + p["deletions"] <= hi
            ]) else None
            for _, lo, hi in size_bins
        ],
    }

    summary = {
        "census_sizes": {
            "prs": len(pr_census), "issues": len(issue_census),
            "human_prs": len(human_pr_census), "human_issues": len(human_issue_census),
            "human_participants": len(all_authors),
        },
        "bot_footprint": bot_footprint,
        "pct_with_more_than_one_action": float(np.mean([n > 1 for n in total_actions_per_user]) * 100.0),
        "median_first_to_second_action_days": float(np.median(first_to_second_days)) if first_to_second_days else None,
        "acceptance_by_association": assoc_summary,
        "tier_phase_acceptance": tier_phase,
        "size_bracket_acceptance": size_rates,
        "frequent_split_by_write_access": frequent_split,
        "ttfr_heatmap": heat_table,
        "open_pr_share_by_tier": {
            t: sum(1 for p in human_prs if p["tier"] == t and p["state"] == "OPEN") / max(1, sum(1 for p in human_prs if p["tier"] == t)) * 100.0
            for t in tiers
        },
        "total_commits_fetched": len(commits),
        "human_commits_count": len(human_commits),
        "bot_commits_count": len(commits) - len(human_commits),
        "unique_human_committers": len(author_commits_cnt),
        "top_15_committers": author_commits_cnt.most_common(15),
        "gini_commits": gini_c,
        "gini_prs": gini_p,
        "gini_all": gini_all,
        "pct_commits_by_top_20_pct": pct_commits_at_20,
        "pct_users_le_3_actions": 100.0 - pct_at_4,
        "inter_gap_90th_percentile_days": float(np.percentile(inter_gaps_days, 90)) if inter_gaps_days else 0.0,
        "inter_gap_median_days": float(np.median(inter_gaps_days)) if inter_gaps_days else 0.0,
        "monthly_table": rows,
        "contributor_composition_monthly": comp_rows,
        "tier_process_summary": {
            t: {
                "count": sum(1 for p in human_prs if p["tier"] == t),
                "acceptance_rate_pct": (
                    sum(1 for p in human_prs if p["tier"] == t and p["merged"])
                    / max(1, sum(1 for p in human_prs if p["tier"] == t))
                    * 100.0
                ),
                "median_ttfr_hrs": ttfr_meds[idx],
                "median_ttm_hrs": ttm_meds[idx],
                "no_human_response_pct": (
                    sum(1 for p in human_prs if p["tier"] == t and p["ttfr_hrs"] is None)
                    / max(1, sum(1 for p in human_prs if p["tier"] == t))
                    * 100.0
                ),
            }
            for idx, t in enumerate(tiers)
        },
        "sample_unmerged_newcomer_prs": unmerged_newcomer_prs[:25],
        "sample_merged_newcomer_prs": merged_newcomer_prs[:20],
        "sample_notable_issues": notable_issues[:30],
    }

    SUMMARY_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved computed summary to {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
