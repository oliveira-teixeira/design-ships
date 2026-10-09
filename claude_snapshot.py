#!/usr/bin/env python3
"""Writes claude_snapshot.json: Lucas's Claude Code activity on this Mac, for the About page.

Run:  python3 claude_snapshot.py && python3 build.py
Reads the session logs Claude Code keeps in ~/.claude/projects/*/*.jsonl. Counts sessions, active
days, requests (messages Lucas typed), actions (tool calls Claude made) per day, and groups the
actions by the tool or connector they went through. Totals only: no project, file or client names
leave this script.
"""
import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LOGS = Path.home() / ".claude" / "projects"

# Connector ids as they appear in tool names (mcp__<id>__tool), mapped to what they are.
CONNECTORS = {
    "f9e6999d": "Figma", "figma": "Figma",
    "Claude_Browser": "Browser", "claude-in-chrome": "Browser",
    "2fed72f8": "Google Workspace", "a23961a3": "Google Workspace", "f48a8f41": "Google Workspace",
    "b1f6ce70": "Webflow", "1a59c906": "Claude Docs", "f6a46cad": "Adobe", "577aa93c": "Klaviyo",
    "ce749f3d": "Shopify", "90a6f6d4": "Supabase", "pencil": "Pencil", "410191e1": "Netlify",
}
BUILT_IN = {
    "Bash": "Terminal", "Read": "Code and files", "Write": "Code and files", "Edit": "Code and files",
    "Glob": "Code and files", "Grep": "Code and files", "NotebookEdit": "Code and files",
    "Agent": "Agents", "Task": "Agents", "Workflow": "Agents",
    "Artifact": "Claude Docs", "ArtifactComments": "Claude Docs", "ArtifactData": "Claude Docs",
    "WebSearch": "Web research", "WebFetch": "Web research",
}


def group(tool):
    if tool.startswith("mcp__"):
        server = tool.split("__")[1]
        for key, name in CONNECTORS.items():
            if server.startswith(key):
                return name
        return "Other connectors"
    return BUILT_IN.get(tool, "Other")


def typed_text(msg):
    content = msg.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
            return ""
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


sessions, days, requests = set(), Counter(), 0
actions_by_day, groups = Counter(), Counter()
for path in LOGS.glob("*/*.jsonl"):
    with path.open(errors="ignore") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            ts = rec.get("timestamp")
            if not ts:
                continue
            day = ts[:10]
            msg = rec.get("message") or {}
            if rec.get("type") == "user" and not rec.get("isMeta"):
                text = typed_text(msg).strip()
                # typed requests only: not tool results, not command or system wrappers
                if text and not text.startswith("<"):
                    requests += 1
                    sessions.add(path.stem)
                    days[day] += 1
            elif rec.get("type") == "assistant":
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        actions_by_day[day] += 1
                        groups[group(block.get("name", ""))] += 1

first = min(set(days) | set(actions_by_day))
today = datetime.now(timezone.utc).date()
span = (today - date.fromisoformat(first)).days + 1
daily = [{"date": (date.fromisoformat(first) + timedelta(days=i)).isoformat(),
          "actions": actions_by_day.get((date.fromisoformat(first) + timedelta(days=i)).isoformat(), 0)}
         for i in range(span)]
total = sum(groups.values())
top = [{"name": name, "actions": n, "share": round(n / total, 4)} for name, n in groups.most_common() if name not in ("Other",)][:7]

snapshot = {
    "from": first,
    "to": today.isoformat(),
    "sessions": len(sessions),
    "active_days": len([d for d in days if days[d]]),
    "requests": requests,
    "actions": total,
    "daily": daily,
    "tools": top,
}
Path(__file__).with_name("claude_snapshot.json").write_text(json.dumps(snapshot, indent=2))
print(f"{len(sessions)} sessions, {snapshot['active_days']} active days, {requests} requests, {total} actions since {first}")
print("tools:", ", ".join(f"{t['name']} {t['actions']}" for t in top))
