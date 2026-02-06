#!/usr/bin/env python3
"""earn_achievements.py

Local helper to plan *legitimate* GitHub achievement progress.

- Generates real work items (issues/PR templates) to pursue achievements.
- Tracks progress by querying GitHub via `gh`.
- Never automates spam or fake activity.
"""
import json
import subprocess
import sys
from typing import Dict, List

REPO = "UberMetroid/GitHub-Achievements"


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def gh_json(args: List[str]) -> Dict:
    proc = run(["gh"] + args)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def status():
    # Basic stats from GitHub API (placeholder; can be expanded)
    data = gh_json(["api", "user"])
    user = data.get("login")
    print(f"GitHub user: {user}")
    print("\nAchievements progress should be tracked manually or via repo metrics.")
    print("(Extend this script with specific repo/org queries as needed.)")


def seed():
    # Create legitimate issues to drive action (opt-in)
    issues = [
        ("Pull Shark: find 2 good starter issues", "List 2 repos/issues to open legit PRs."),
        ("Galaxy Brain: answer 2 Q&A discussions", "Find 2 unanswered Q&A discussions and respond with helpful answers."),
        ("Starstruck: build a star-worthy repo", "Outline plan for a repo that solves a real problem."),
        ("Pair Extraordinaire: co-author a commit", "Coordinate a co-authored PR with a collaborator."),
        ("Quickdraw: open + close a small issue", "Create a tiny issue and close it quickly with a fix."),
        ("YOLO: merge a PR without review (own repo only)", "Create a PR in your repo and merge without review if policy allows."),
        ("Public Sponsor: pick a project to sponsor", "Choose a project and confirm sponsorship plan."),
    ]

    for title, body in issues:
        proc = run(["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body])
        if proc.returncode == 0:
            print(proc.stdout.strip())
        else:
            print(proc.stderr.strip() or proc.stdout.strip())


def help():
    print("Usage:")
    print("  earn_achievements.py status   # Show basic status")
    print("  earn_achievements.py seed     # Create legitimate action issues")


def main():
    if len(sys.argv) < 2:
        help()
        return
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "seed":
        seed()
    else:
        help()


if __name__ == "__main__":
    main()
