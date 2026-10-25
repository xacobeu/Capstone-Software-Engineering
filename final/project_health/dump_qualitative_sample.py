"""Writes the stratified qualitative sample as a readable Markdown file for manual coding."""
from __future__ import annotations

import json
from pathlib import Path

QUAL_IN = Path(__file__).resolve().parent / "data" / "qualitative_sample.json"
OUT = Path(__file__).resolve().parent / "data" / "qualitative_sample_threads.md"


def fmt_hours(h: float | None) -> str:
    return "none" if h is None else f"{h:.1f}h"


def main() -> None:
    data = json.loads(QUAL_IN.read_text(encoding="utf-8"))
    lines = ["# Qualitative sample threads", ""]
    for kind in ("prs", "issues"):
        lines += [f"## {kind.upper()}", ""]
        for i, it in enumerate(data[kind], 1):
            head = (
                f"### {kind[:-1].upper()}-{i:02d} #{it['number']} | {it.get('tier', '-')} | {it['phase']} | "
                f"{'merged' if it.get('merged') else it.get('stateReason') or it['state']}"
            )
            lines += [
                head,
                f"{it['url']} | author `{it['author']}` ({it['authorAssociation']}) | created {it['createdAt'][:10]} | "
                f"closed {str(it.get('closedAt'))[:10]} | TTFR {fmt_hours(it.get('ttfr_hrs'))} | labels {', '.join(it.get('labels', []))}",
            ]
            if kind == "prs":
                lines.append(
                    f"+{it['additions']}/-{it['deletions']} LOC, {it['changedFiles']} files, linked issues {it.get('linked_issues')}, "
                    f"merged by {it.get('merged_by')}"
                )
            lines += [f"**Title:** {it['title']}", f"**Body:** {it.get('body', '')[:400]}", ""]
            for q in it.get("quotes", []):
                lines.append(f"- `{q['author']}` ({str(q.get('createdAt'))[:10]}): {q['text']}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
