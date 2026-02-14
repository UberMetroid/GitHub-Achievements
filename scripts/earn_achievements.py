#!/usr/bin/env python3
"""earn_achievements.py

Local helper to plan *legitimate* GitHub achievement progress.

- Generates real work items (issues) to pursue achievements.
- Tracks basic progress via GitHub API + search.
- Never automates spam or fake activity.

Usage:
  earn_achievements.py status   # Show basic status + progress
  earn_achievements.py seed     # Create legitimate action issues
  earn_achievements.py auto     # Run status + seed
  earn_achievements.py config   # Show/edit configuration
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

CONFIG_FILE = Path.home() / ".config" / "github-achievements" / "config.json"
DEFAULT_CONFIG = {
    "repo": "owner/repo",
    "achievements": {
        "pull_shark": {"threshold": [2, 16, 128, 1024], "enabled": True},
        "galaxy_brain": {"threshold": [2, 8, 16, 32], "enabled": True},
        "starstruck": {"threshold": [16, 128, 512, 4096], "enabled": True},
        "pair_extraordinaire": {"threshold": [1, 10, 24, 48], "enabled": True},
        "quickdraw": {"enabled": True},
        "yolo": {"enabled": True},
        "public_sponsor": {"enabled": True},
    }
}


def ensure_config_dir() -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict:
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict) -> None:
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str, default=None):
    config = load_config()
    keys = key.split(".")
    value = config
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, default)
        else:
            return default
    return value


def run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def gh_json(args: List[str]) -> Dict:
    proc = run(["gh"] + args, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def check_gh_installed() -> bool:
    try:
        run(["gh", "--version"], check=False)
        return True
    except FileNotFoundError:
        return False


def list_open_issue_titles(repo: str) -> List[str]:
    data = gh_json(["issue", "list", "--repo", repo, "--state", "open", "--json", "title"])
    return [str(i.get("title", "")) for i in data]


def get_merged_prs_count(user: str) -> str:
    try:
        data = gh_json(["api", "/search/issues", "-f", f"q=is:pr is:merged author:{user}"])
        return str(data.get("total_count", 0))  # type: ignore[arg-type]
    except Exception:
        return "(unavailable)"


def get_coauthored_prs_count(user: str) -> str:
    try:
        data = gh_json(["api", "/search/issues", "-f", f"q=is:pr is:merged author:{user} co-authored-by:{user}"])
        return str(data.get("total_count", 0))  # type: ignore[arg-type]
    except Exception:
        return "(unavailable)"


def cmd_status(args):
    if not check_gh_installed():
        print("Error: GitHub CLI (gh) is not installed.", file=sys.stderr)
        print("Install it from: https://cli.github.com/", file=sys.stderr)
        return 1

    try:
        data = gh_json(["api", "user"])
        user = str(data.get("login", ""))
    except RuntimeError:
        print("Error: Not authenticated with GitHub. Run 'gh auth login' first.", file=sys.stderr)
        return 1

    repo = str(get_config_value("repo", "owner/repo"))
    print(f"GitHub user: {user}")
    print(f"Tracking repo: {repo}\n")

    pull_shark = get_merged_prs_count(user)
    pair_extra = get_coauthored_prs_count(user)

    print("Progress (best-effort):")
    print(f"- Pull Shark (merged PRs): {pull_shark}")
    print(f"- Pair Extraordinaire (co-authored PRs): {pair_extra}")
    print(f"- Galaxy Brain (accepted answers): (manual)")
    print(f"- Starstruck (repo stars): (manual)")
    print(f"- Quickdraw: (manual)")
    print(f"- YOLO: (manual)")
    print(f"- Public Sponsor: (manual)")
    print()
    return 0


def cmd_seed(args):
    if not check_gh_installed():
        print("Error: GitHub CLI (gh) is not installed.", file=sys.stderr)
        return 1

    repo = str(get_config_value("repo", "owner/repo"))
    issues = [
        ("Pull Shark: find 2 good starter issues", "List 2 repos/issues to open legit PRs."),
        ("Galaxy Brain: answer 2 Q&A discussions", "Find 2 unanswered Q&A discussions and respond with helpful answers."),
        ("Starstruck: build a star-worthy repo", "Outline plan for a repo that solves a real problem."),
        ("Pair Extraordinaire: co-author a commit", "Coordinate a co-authored PR with a collaborator."),
        ("Quickdraw: open + close a small issue", "Create a tiny issue and close it quickly with a fix."),
        ("YOLO: merge a PR without review (own repo only)", "Create a PR in your repo and merge without review if policy allows."),
        ("Public Sponsor: pick a project to sponsor", "Choose a project and confirm sponsorship plan."),
    ]

    existing = set(list_open_issue_titles(repo))
    created = 0
    for title, body in issues:
        if title in existing:
            continue
        proc = run(["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body], check=False)
        if proc.returncode == 0:
            print(f"Created: {title}")
            created += 1
        else:
            print(f"Error creating '{title}': {proc.stderr.strip() or proc.stdout.strip()}")

    if created == 0:
        print("All achievement issues already exist.")
    return 0


def cmd_config(args):
    config = load_config()
    
    if args.set_repo:
        config["repo"] = args.set_repo
        save_config(config)
        print(f"Repo set to: {args.set_repo}")
        return 0
    
    if args.show:
        print(json.dumps(config, indent=2))
        return 0
    
    print(f"Config file: {CONFIG_FILE}")
    print(f"Current repo: {config.get('repo', 'not set')}")
    print("\nUse --set-repo <owner/repo> to change the tracked repository")
    print("Use --show to see full config")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Track and plan legitimate GitHub achievements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status         Show achievement progress
  %(prog)s seed           Create action items as issues
  %(prog)s auto           Run status then seed
  %(prog)s config         Show configuration
  %(prog)s config --set-repo myname/myrepo
"""
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("status", help="Show achievement progress")
    subparsers.add_parser("seed", help="Create action items as issues")
    subparsers.add_parser("auto", help="Run status then seed")
    
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--show", action="store_true", help="Show full config")
    config_parser.add_argument("--set-repo", type=str, help="Set the tracked repository (owner/repo)")
    
    args = parser.parse_args()
    
    if args.command == "status":
        return cmd_status(args)
    elif args.command == "seed":
        return cmd_seed(args)
    elif args.command == "auto":
        cmd_status(args)
        return cmd_seed(args)
    elif args.command == "config":
        return cmd_config(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
