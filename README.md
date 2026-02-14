# GitHub Achievements

A practical playbook + tools for earning GitHub achievements the *legit* way.

## What's in here

- `docs/ACHIEVEMENTS.md` — Complete list of all GitHub achievements with thresholds, tactics, and guardrails
- `scripts/earn_achievements.py` — CLI tool to track progress and create action items

## Supported Achievements

| Category | Achievements |
|----------|---------------|
| **PR-Based** | Pull Shark, Pair Extraordinaire, Quickdraw, YOLO |
| **Community** | Galaxy Brain, Public Sponsor |
| **Profile** | Starstruck, Hacker, Founder, Developer, Llama, Arctic Code Vault |

## Quick start

```bash
# Show achievement progress
python3 scripts/earn_achievements.py status

# Create action items as GitHub issues
python3 scripts/earn_achievements.py seed

# Run both
python3 scripts/earn_achievements.py auto

# Configure your repo
python3 scripts/earn_achievements.py config --set-repo yourname/yourrepo
```

## Features

- Tracks Pull Shark (merged PRs) and Pair Extraordinaire (co-authored PRs) automatically
- Creates action item issues for manual achievements
- Configurable target repository
- Local config stored in `~/.config/github-achievements/config.json`

## Guardrails

This repo only supports **legitimate** actions (real PRs, real reviews, real issues). No spam, no fake PRs, no abuse.
