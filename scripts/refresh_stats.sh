#!/bin/bash
# Refreshes the About page stats. Takes new snapshots from the GitHub CLI and the Claude Code logs on
# this Mac and commits the two JSON files to main; the live page reads them from there
# (assets/js/stats.js), so no deploy is needed. launchd runs it twice a day (install_stats_job.sh).
#
# It works in its own clone under ~/Library/Caches, never in the working copy, and commits only the two
# snapshot files. Pass --dry-run to take the snapshots without committing or pushing.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

REPO="https://github.com/oliveira-teixeira/design-ships.git"
WORK="$HOME/Library/Caches/lucastexr-stats/design-ships"

echo "== $(date '+%Y-%m-%d %H:%M:%S')"
if [ ! -d "$WORK/.git" ]; then
  mkdir -p "$(dirname "$WORK")"
  git clone -q "$REPO" "$WORK"
fi
cd "$WORK"
git fetch -q origin main
git reset -q --hard origin/main

python3 github_snapshot.py
python3 claude_snapshot.py

if [ "${1:-}" = "--dry-run" ]; then
  git --no-pager diff --stat -- github_snapshot.json claude_snapshot.json
  exit 0
fi

git add github_snapshot.json claude_snapshot.json
if git diff --cached --quiet; then
  echo "No change"
  exit 0
fi
git commit -q -m "Refresh the GitHub and Claude Code stats"
git push -q origin HEAD:main
echo "Pushed $(git rev-parse --short HEAD)"
