#!/usr/bin/env python3
"""Writes github_snapshot.json: the last 12 months of Lucas's work on GitHub, week by week.

Run:  python3 github_snapshot.py && python3 build.py
Needs the GitHub CLI signed in as oliveira-teixeira. Counts commits he authored on the default
branch of every repository he can reach (his own, Fetchly's and client orgs), de-duplicated by
SHA so a repository mirrored into two orgs counts once, plus the pull requests he opened.
GitHub's own contribution graph undercounts this (it showed 40 commits for the same year), so
the page counts from commit history. Repository names are not stored: most are client work.
"""
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOGIN = "oliveira-teixeira"
WEEKS = 52
now = datetime.now(timezone.utc)
# Weeks start on Monday; the last bar is the current week.
this_monday = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
start = this_monday - timedelta(weeks=WEEKS - 1)
since = start.strftime("%Y-%m-%dT%H:%M:%SZ")


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


repos = [json.loads(line) for line in gh(
    "api", "user/repos?affiliation=owner,collaborator,organization_member&per_page=100", "--paginate",
    "--jq", ".[] | {name: .full_name, pushed: .pushed_at, private: .private} | @json").splitlines()]
active = [r for r in repos if (r["pushed"] or "") >= since]

seen = {}
touched = set()
private_touched = set()
for r in active:
    try:
        rows = gh("api", f"repos/{r['name']}/commits?author={LOGIN}&since={since}&per_page=100", "--paginate",
                  "--jq", '.[] | [.sha, .commit.author.date, (.commit.message | split("\\n")[0])] | @tsv').splitlines()
    except subprocess.CalledProcessError:
        continue  # empty or archived repositories answer 409
    for row in rows:
        sha, date, _ = row.split("\t", 2)
        if sha in seen:
            continue
        seen[sha] = date
        # counted by short name, so a repository mirrored into a second org counts once
        touched.add(r["name"].split("/")[1].lower())
        if r["private"]:
            private_touched.add(r["name"].split("/")[1].lower())


def search_count(q):
    return int(gh("api", "-X", "GET", "search/issues", "-f", f"q={q}", "--jq", ".total_count").strip())


day = start.strftime("%Y-%m-%d")
prs = search_count(f"author:{LOGIN} type:pr created:>={day}")
merged = search_count(f"author:{LOGIN} type:pr is:merged created:>={day}")

weeks = [0] * WEEKS
for date in seen.values():
    d = datetime.fromisoformat(date.replace("Z", "+00:00"))
    i = (d - start).days // 7
    if 0 <= i < WEEKS:
        weeks[i] += 1

snapshot = {
    "login": LOGIN,
    "url": f"https://github.com/{LOGIN}",
    "from": start.strftime("%Y-%m-%d"),
    "to": now.strftime("%Y-%m-%d"),
    "commits": sum(weeks),
    "pull_requests": prs,
    "pull_requests_merged": merged,
    "repositories": len(touched),
    "private_repositories": len(private_touched),
    "active_weeks": sum(1 for w in weeks if w),
    "weeks": [{"start": (start + timedelta(weeks=i)).strftime("%Y-%m-%d"), "commits": c} for i, c in enumerate(weeks)],
    "public_repo": {"name": "textlab-analysis-app", "url": f"https://github.com/{LOGIN}/textlab-analysis-app"},
}
Path(__file__).with_name("github_snapshot.json").write_text(json.dumps(snapshot, indent=2))
print(f"{snapshot['commits']} commits, {prs} pull requests ({merged} merged), "
      f"{len(touched)} repositories, {snapshot['active_weeks']} active weeks")
