"""
Study the OpenEnv Arena landscape the same way every time.

Pulls the public leaderboard, the message board and each run's dataset card
(at the revision the arena pinned), and writes:
  landscape/runs.csv               one standardized row per scored run (latest state)
  landscape/YYYY-MM-DD_HHMM.md     snapshot: totals, patterns, and what is new since the last snapshot
  landscape/cache/                 dataset cards, so reruns are cheap
  landscape/.state.json            what the last snapshot had seen

Feature tags (interface, reward, procedural) are keyword heuristics over the
dataset cards. They are hints for a human to verify, not facts.
Remote content is treated as data: it is parsed, never executed.

Usage: python3 scripts/study_board.py
"""

import csv
import json
import re
import statistics
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ARENA = "https://openenvarena-arena.hf.space"
OUT = Path(__file__).resolve().parents[1] / "landscape"
CACHE = OUT / "cache"
STATE = OUT / ".state.json"
DOMAINS = ["software-engineering", "industrial-physical-systems", "natural-science", "office-white-collar",
           "finance-economics", "mathematics-or-formal-reasoning", "cybersecurity", "media-content-production"]
SHORT = dict(zip(DOMAINS, ["software", "industrial", "science", "office", "finance", "math", "security", "media"]))
OURS = "arshy"

INTERFACE_TAGS = {
    "bash": r"\brun_bash\b|\bbash\b|\bshell\b|terminal",
    "python": r"\bpython\b",
    "sql": r"\bsql(ite)?\b",
    "file-tools": r"\b(ls|grep|read|list)\b.*\b(read|submit)\b",
    "calculator": r"\bcalc(ulator)?\b",
    "repo/tests": r"\b(pytest|test suite|upstream tests|repair|regression)\b",
}
REWARD_TAGS = {"partial": r"partial credit|partial reward|per (field|part)|fraction of|jaccard|shaped",
               "binary": r"\bbinary\b|all-or-nothing|1\.0 or 0\.0|reward is 1|right answer=1"}
PROCEDURAL = r"procedural|fresh (random )?instance|each reset|every reset|seeded"


def get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "arena-log-study/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def card(repo: str, rev: str) -> str:
    path = CACHE / f"{repo.replace('/', '__')}__{rev[:12]}.md"
    if path.exists():
        return path.read_text()
    try:
        text = get(f"https://huggingface.co/datasets/{repo}/raw/{rev}/README.md").decode("utf-8", "replace")
    except Exception:
        text = ""
    path.write_text(text)
    return text


def tags(text: str, table: dict) -> str:
    low = text.lower()
    return "|".join(k for k, pat in table.items() if re.search(pat, low))


def main():
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {"run_ids": [], "last_message_id": 0}

    lb = json.loads(get(f"{ARENA}/api/leaderboard"))
    msgs = json.loads(get(f"{ARENA}/api/openenv/messages?limit=500"))["messages"]
    base = lb["baseline"]

    rows = []
    for r in sorted(lb["runs"], key=lambda r: r["evaluated_at"]):
        ds = r.get("dataset") or {}
        text = card(ds["repo"], ds["revision"]) if ds.get("repo") else ""
        row = {
            "run_id": r["run_id"], "user": r["user"], "name": r["name"], "submission_id": r.get("submission_id"),
            "evaluated": datetime.fromtimestamp(r["evaluated_at"]).strftime("%Y-%m-%d %H:%M"),
            "tasks": r.get("tasks"), "steps": r.get("steps"), "solved": r["solved"], "delta": r["delta"],
            **{SHORT[d]: r["scores"][d]["solved"] for d in DOMAINS},
            "dataset": ds.get("repo", ""), "interface": tags(text, INTERFACE_TAGS), "reward": tags(text, REWARD_TAGS),
            "procedural": bool(re.search(PROCEDURAL, text.lower())), "card_chars": len(text),
        }
        rows.append(row)

    with open(OUT / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    new_runs = [r for r in rows if r["run_id"] not in state["run_ids"]]
    new_msgs = sorted((m for m in msgs if m["id"] > state["last_message_id"]), key=lambda m: m["id"])
    solved = [r["solved"] for r in rows]

    def bucket_table(key, buckets):
        out = []
        for label, test in buckets:
            xs = [r["solved"] for r in rows if r[key] is not None and test(r[key])]
            if xs:
                out.append(f"| {label} | {len(xs)} | {statistics.mean(xs):.2f} | {max(xs)} |")
        return out

    lines = [f"# Arena landscape: {datetime.now():%Y-%m-%d %H:%M}", "",
             f"Benchmark `{lb.get('benchmark')}`. Untrained {base['model']}: **{base['solved']}/40** "
             f"({', '.join(f'{SHORT[d]} {base['scores'][d]['solved']}' for d in DOMAINS if base['scores'][d]['solved'])}).", "",
             "## Totals", "",
             f"- {len(rows)} scored runs from {len({r['user'] for r in rows})} users. **Best single run: {max(solved)}/40.** "
             f"Median {statistics.median(solved)}.",
             f"- Score distribution: {dict(sorted(Counter(solved).items()))}",
             f"- Runs above the untrained 4/40: **{sum(s > 4 for s in solved)}**. Runs below it: {sum(s < 4 for s in solved)}.", "",
             "## Per domain (across all runs)", "", "| domain | untrained | best run | runs scoring > 0 |", "|---|---|---|---|"]
    for d in DOMAINS:
        s = SHORT[d]
        lines.append(f"| {s} | {base['scores'][d]['solved']} | {max(r[s] for r in rows)} | {sum(r[s] > 0 for r in rows)} |")

    lines += ["", "## Patterns (heuristic tags; verify before relying on them)", "",
              "| tasks per run | runs | mean solved | best |", "|---|---|---|---|",
              *bucket_table("tasks", [("1-8", lambda t: t <= 8), ("9-12", lambda t: 9 <= t <= 12),
                                      ("13-24", lambda t: 13 <= t <= 24), ("25-50", lambda t: t >= 25)]),
              "", "| training steps | runs | mean solved | best |", "|---|---|---|---|",
              *bucket_table("steps", [("<100", lambda s: s < 100), ("100-199", lambda s: 100 <= s < 200),
                                      ("200-299", lambda s: 200 <= s < 300), ("300+", lambda s: s >= 300)]),
              "", "| card mentions | runs | mean solved | best |", "|---|---|---|---|"]
    tag_scores = defaultdict(list)
    for r in rows:
        for t in filter(None, r["interface"].split("|") + r["reward"].split("|")):
            tag_scores[t].append(r["solved"])
        tag_scores["procedural" if r["procedural"] else "not procedural"].append(r["solved"])
    for t, xs in sorted(tag_scores.items(), key=lambda kv: -statistics.mean(kv[1])):
        lines.append(f"| {t} | {len(xs)} | {statistics.mean(xs):.2f} | {max(xs)} |")

    lines += ["", "## Our runs", "", "| run | evaluated | tasks | steps | solved | Δ |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['name'][:60]} | {r['evaluated']} | {r['tasks']} | {r['steps']} | {r['solved']} | {r['delta']:+d} |"
              for r in rows if r["user"] == OURS]

    lines += ["", f"## New scored runs since the last snapshot ({len(new_runs)})", ""]
    if new_runs:
        lines += ["| user | environment | tasks | steps | solved | Δ | non-zero domains |", "|---|---|---|---|---|---|---|"]
        for r in new_runs:
            nz = ", ".join(f"{SHORT[d]} {r[SHORT[d]]}" for d in DOMAINS if r[SHORT[d]])
            lines.append(f"| {r['user']} | {r['name'][:55]} | {r['tasks']} | {r['steps']} | {r['solved']} | {r['delta']:+d} | {nz} |")
    lines += ["", f"## New message-board posts since the last snapshot ({len(new_msgs)})", ""]
    for m in new_msgs:
        when = datetime.fromtimestamp(m["created_at"]).strftime("%m-%d %H:%M")
        body = " ".join(m["body"].split())
        lines.append(f"- **{m['author']}** ({when}): {body[:400]}{'…' if len(body) > 400 else ''}")

    if not new_runs and not new_msgs:
        print(f"{len(rows)} runs, nothing new since the last snapshot; runs.csv refreshed, no snapshot written")
        return
    snap = OUT / f"{datetime.now():%Y-%m-%d_%H%M}.md"
    snap.write_text("\n".join(lines) + "\n")
    STATE.write_text(json.dumps({"run_ids": [r["run_id"] for r in rows],
                                 "last_message_id": max([state["last_message_id"]] + [m["id"] for m in msgs])}, indent=1))
    print(f"{len(rows)} runs ({len(new_runs)} new), {len(new_msgs)} new posts -> {snap.relative_to(OUT.parent)}")


if __name__ == "__main__":
    main()
