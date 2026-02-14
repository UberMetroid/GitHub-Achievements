# Contributing to GitHub-Achievements

Thank you for your interest in contributing!

## How to Contribute

1. **Fork the repo**
2. **Create a branch:** `git checkout -b feature/your-feature`
3. **Make changes** and test locally
4. **Run tests:** `pytest`
5. **Run linting:** `ruff check scripts/ tests/`
6. **Commit with clear messages**
7. **Push and create a PR**

## Adding New Achievements

1. Update `docs/ACHIEVEMENTS.md` with achievement details
2. Add tracking function in `scripts/earn_achievements.py` if auto-trackable
3. Add seed issue in the `seed()` function
4. Add tests for new functions

## Code Style

- Use Python 3.9+ syntax
- Run `ruff check` before committing
- Add type hints where helpful
- Keep functions small and focused

## Issues

- Check existing issues before creating new ones
- Use clear, descriptive titles
- Include steps to reproduce for bugs

## Guardrails

This project only supports **legitimate** GitHub achievements. No spam, fake PRs, or gaming the system.
