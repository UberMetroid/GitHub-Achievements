#!/usr/bin/env python3
"""earn_achievements.py

Local helper to plan *legitimate* GitHub achievement progress.

- Generates real work items (issues) to pursue achievements.
- Tracks basic progress via GitHub API + search.
- Never automates spam or fake activity.

Usage:
  earn_achievements.py status   # Show basic status + progress
  earn_achievements.py seed     # Create legitimate action issues (no prompt)
  earn_achievements.py auto     # Run status + seed
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


def list_open_issue_titles() -> List[str]:
    data = gh_json(["issue", "list", "--repo", REPO, "--state", "open", "--json", "title"])
    return [i.get("title", "") for i in data]


def status():
    data = gh_json(["api", "user"])
    user = data.get("login")
    print(f"GitHub user: {user}\n")

    def search_count(query: str):
        try:
            data = gh_json(["api", "/search/issues", "-f", f"q={query}"])
            return int(data.get("total_count", 0))
        except Exception:
            return "(unavailable)"

    pull_shark = search_count(f"is:pr is:merged author:{user}")
    pair_extra = search_count(f"is:pr is:merged author:{user} co-authored-by")

    galaxy_brain = "(manual)"
    starstruck = "(manual)"

    print("Progress (best-effort):")
    print(f"- Pull Shark (merged PRs): {pull_shark}")
    print(f"- Pair Extraordinaire (approx co-authored PRs): {pair_extra}")
    print(f"- Galaxy Brain (accepted answers): {galaxy_brain}")
    print(f"- Starstruck (stars): {starstruck}\n")


def seed():
    issues = [
        ("Pull Shark: find 2 good starter issues", "List 2 repos/issues to open legit PRs."),
        ("Galaxy Brain: answer 2 Q&A discussions", "Find 2 unanswered Q&A discussions and respond with helpful answers."),
        ("Starstruck: build a star-worthy repo", "Outline plan for a repo that solves a real problem."),
        ("Pair Extraordinaire: co-author a commit", "Coordinate a co-authored PR with a collaborator."),
        ("Quickdraw: open + close a small issue", "Create a tiny issue and close it quickly with a fix."),
        ("YOLO: merge a PR without review (own repo only)", "Create a PR in your repo and merge without review if policy allows."),
        ("Public Sponsor: pick a project to sponsor", "Choose a project and confirm sponsorship plan."),
    ]

    existing = set(list_open_issue_titles())
    for title, body in issues:
        if title in existing:
            continue
        proc = run(["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body])
        if proc.returncode == 0:
            print(proc.stdout.strip())
        else:
            print(proc.stderr.strip() or proc.stdout.strip())


def help():
    print("Usage:")
    print("  earn_achievements.py status   # Show basic status")
    print("  earn_achievements.py seed     # Create legitimate action issues")
    print("  earn_achievements.py auto     # Run status + seed")


def main():
    if len(sys.argv) < 2:
        help()
        return
    cmd = sys.argv[1]
    if cmd == "status":
        status()
    elif cmd == "seed":
        seed()
    elif cmd == "auto":
        status()
        seed()
    else:
        help()


if __name__ == "__main__":
    main()
