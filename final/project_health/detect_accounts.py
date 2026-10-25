"""Flags bot candidates and alternate-account candidates on the full census (Section 3.1, Appendix A).

Bot measures
  1. Names: known bot usernames, bot naming patterns, and accounts the GitHub API does not resolve as a user.
  2. Behavior: authors of `bot-fix` PRs, >= 90% of actions of one type (min. 10 actions), templated titles.
Alternate-account measures
  1. Name/email similarity: Levenshtein distance <= 1 (strings of 6+ characters) and affix stripping.
  2. Git metadata: one commit email used by several GitHub logins.

The output is a candidate list; every candidate is decided manually in account_decisions.json.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

CENSUS_IN = Path(__file__).resolve().parent / "data" / "project_health_data.json"
IDENTITY_IN = Path(__file__).resolve().parent / "data" / "identity_data.json"
OUT = Path(__file__).resolve().parent / "data" / "account_candidates.json"

# Appendix A lists
KNOWN_BOT_USERNAMES = [
    "gemini-code-assist", "github-actions", "gemini-cli", "github-advanced-security", "google-cla",
    "gemini-code-assist[bot]", "gemini-cli-robot", "dependabot[bot]", "google-labs-jules[bot]",
]
BOT_PATTERNS = ["gemini", "[bot]", "robot", "bot"]
ALT_AFFIXES = ["google", "alt", "dev", "corp", "work", "personal", "team", "github"]

SKEW_THRESHOLD = 0.90
SKEW_MIN_ACTIONS = 10
TEMPLATE_MIN_TITLES = 5
TEMPLATE_SHARE = 0.80
LEV_MIN_LEN = 6


def title_prefix(title: str) -> str:
    """First four words with numbers masked, so 'fix: address issue #123 - x' and '#456 - y' match."""
    t = re.sub(r"\d+", "#", title.lower())
    return " ".join(t.split()[:4])


def within_one_edit(strings: dict[str, set[str]]) -> set[tuple[str, str, str, str]]:
    """Pairs of different owners whose strings are at Levenshtein distance <= 1 (deletion-neighbourhood index)."""
    index: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for owner, values in strings.items():
        for v in values:
            if len(v) < LEV_MIN_LEN:
                continue
            index[v].add((owner, v))
            for i in range(len(v)):
                index[v[:i] + "\0" + v[i + 1:]].add((owner, v))
                index[v[:i] + v[i + 1:]].add((owner, v))
    pairs = set()
    for bucket in index.values():
        for (o1, v1), (o2, v2) in combinations(sorted(bucket), 2):
            if o1 != o2 and lev1(v1, v2):
                pairs.add(tuple(sorted([(o1, v1), (o2, v2)])))
    return {(a[0], b[0], a[1], b[1]) for a, b in pairs}


def lev1(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def strip_affixes(login: str) -> str:
    s = login.lower()
    for affix in ALT_AFFIXES:
        s = re.sub(rf"^{affix}[-_.]|[-_.]{affix}$", "", s)
    return s


def main() -> None:
    census = json.loads(CENSUS_IN.read_text(encoding="utf-8"))
    ident = json.loads(IDENTITY_IN.read_text(encoding="utf-8"))

    counts: dict[str, Counter[str]] = defaultdict(Counter)
    titles: dict[str, list[str]] = defaultdict(list)
    for c in census["commits"]:
        if c.get("raw_author"):
            counts[c["raw_author"]]["commits"] += 1
            titles[c["raw_author"]].append(c.get("headline") or "")
    pr_titles = {int(k): v for k, v in ident["pr_titles"].items()}
    issue_titles = {int(k): v for k, v in ident["issue_titles"].items()}
    for p in census["pr_census"]:
        if p.get("raw_author"):
            counts[p["raw_author"]]["prs"] += 1
            titles[p["raw_author"]].append(pr_titles.get(p["number"], ""))
    for i in census["issue_census"]:
        if i.get("raw_author"):
            counts[i["raw_author"]]["issues"] += 1
            titles[i["raw_author"]].append(issue_titles.get(i["number"], ""))
    logins = sorted(counts)
    types = ident["account_types"]

    # ------------------------------------------------------------------ bots
    bots: dict[str, list[str]] = defaultdict(list)
    for login in logins:
        lo = login.lower()
        if login in KNOWN_BOT_USERNAMES:
            bots[login].append("Known bot username")
        else:
            hit = next((p for p in BOT_PATTERNS if p in lo), None)
            if hit:
                bots[login].append(f"Name pattern `{hit}'")
        if types.get(login) == "NotFound":
            bots[login].append("API: not a user account")
        n = counts[login]
        total = sum(n.values())
        if total >= SKEW_MIN_ACTIONS:
            kind, top = n.most_common(1)[0]
            if top / total >= SKEW_THRESHOLD:
                bots[login].append(f"Task skew: {top / total:.0%} {kind}")
        ts = [t for t in titles[login] if t]
        if len(ts) >= TEMPLATE_MIN_TITLES:
            prefix, k = Counter(title_prefix(t) for t in ts).most_common(1)[0]
            if k / len(ts) >= TEMPLATE_SHARE:
                bots[login].append(f"Template titles: {k}/{len(ts)} start with `{prefix}'")
    for login, k in ident["bot_fix_authors"].items():
        if login in counts:
            bots[login].append(f"Author of {k} bot-fix PR(s)")

    # ------------------------------------------------------------------ alternate accounts
    strings: dict[str, set[str]] = defaultdict(set)
    email_owners: dict[str, set[str]] = defaultdict(set)
    for login in logins:
        strings[login].add(login.lower())
    for ci in ident["commit_identities"]:
        if not ci["login"]:
            continue
        if ci["name"]:
            strings[ci["login"]].add(ci["name"].lower().replace(" ", ""))
        if ci["email"]:
            email_owners[ci["email"]].add(ci["login"])
            local = ci["email"].split("@")[0].split("+")[-1]
            strings[ci["login"]].add(local)

    alts: dict[tuple[str, str], list[str]] = defaultdict(list)
    for a, b, va, vb in within_one_edit(strings):
        reason = "Identical name/email string" if va == vb else "Levenshtein distance: 1 edit"
        alts[tuple(sorted((a, b)))].append(f"{reason} (`{va}' / `{vb}')")
    by_stripped: dict[str, set[str]] = defaultdict(set)
    for login in logins:
        by_stripped[strip_affixes(login)].add(login)
    for group in by_stripped.values():
        for a, b in combinations(sorted(group), 2):
            alts[(a, b)].append("Affix match")
    for email, owners in email_owners.items():
        for a, b in combinations(sorted(owners), 2):
            alts[(a, b)].append(f"Shared Git email ({'noreply' if 'noreply' in email else 'other'})")
    # noreply addresses embed the login at the time of the commit (id+login@users.noreply.github.com)
    for ci in ident["commit_identities"]:
        m = re.match(r"\d+\+([^@]+)@users\.noreply\.github\.com", ci["email"] or "")
        if m and ci["login"] and m.group(1).lower() != ci["login"].lower() and m.group(1) in counts:
            alts[tuple(sorted((ci["login"], m.group(1))))].append("noreply email names another login")

    out = {
        "population": len(logins),
        "bot_candidates": [
            {"login": l, **{k: counts[l][k] for k in ("commits", "prs", "issues")}, "account_type": types.get(l),
             "reasons": sorted(set(r))}
            for l, r in sorted(bots.items(), key=lambda kv: -sum(counts[kv[0]].values()))
        ],
        "alt_candidates": [
            {"accounts": list(k), "reasons": sorted(set(r)),
             "activity": {a: sum(counts[a].values()) for a in k}}
            for k, r in sorted(alts.items())
        ],
    }
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"population {len(logins)}: {len(out['bot_candidates'])} bot candidates, {len(out['alt_candidates'])} alternate pairs")


if __name__ == "__main__":
    main()
