#!/usr/bin/env python3
"""generate_stats_page.py

Generates an HTML page with GitHub achievement stats.
Run this locally or in CI to update GitHub Pages.
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

REPO = "UberMetroid/GitHub-Achievements"


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def gh_json(args):
    proc = run(["gh"] + args)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def get_stats():
    user_data = gh_json(["api", "user"])
    user = user_data.get("login")

    stats = {
        "user": user,
        "updated": datetime.now().isoformat(),
    }

    try:
        merged = gh_json(["api", "/search/issues", "-f", "q=is:pr is:merged author:{}".format(user)])
        stats["merged_prs"] = merged.get("total_count", 0)
    except:
        stats["merged_prs"] = "N/A"

    try:
        coauthored = gh_json(["api", "/search/issues", "-f", "q=is:pr is:merged author:{} co-authored-by:{}".format(user, user)])
        stats["coauthored_prs"] = coauthored.get("total_count", 0)
    except:
        stats["coauthored_prs"] = "N/A"

    try:
        repos = gh_json(["api", "/users/{}/repos".format(user), "--paginate"])
        stats["total_stars"] = sum(r.get("stargazers_count", 0) for r in repos)
        stats["public_repos"] = len([r for r in repos if r.get("visibility") == "public"])
    except:
        stats["total_stars"] = "N/A"
        stats["public_repos"] = "N/A"

    try:
        user_details = gh_json(["api", "/users/{}".format(user)])
        stats["followers"] = user_details.get("followers", 0)
        stats["following"] = user_details.get("following", 0)
    except:
        stats["followers"] = "N/A"
        stats["following"] = "N/A"

    return stats


def generate_html(stats):
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Achievements - {user}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{
            color: #58a6ff;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .updated {{
            color: #8b949e;
            font-size: 0.9em;
            margin-bottom: 40px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #58a6ff;
        }}
        .stat-label {{
            color: #8b949e;
            margin-top: 5px;
        }}
        .achievements {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 30px;
        }}
        .achievements h2 {{
            color: #58a6ff;
            margin-bottom: 20px;
        }}
        .badge {{
            display: inline-block;
            background: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 10px 20px;
            margin: 5px;
        }}
        .badge-earned {{
            border-color: #3fb950;
        }}
        .badge-progress {{
            border-color: #d29922;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            color: #8b949e;
            font-size: 0.9em;
        }}
        a {{
            color: #58a6ff;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 GitHub Achievements</h1>
        <p class="updated">Last updated: {updated}</p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{merged_prs}</div>
                <div class="stat-label">Merged PRs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{coauthored_prs}</div>
                <div class="stat-label">Co-authored PRs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_stars}</div>
                <div class="stat-label">Total Stars</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{public_repos}</div>
                <div class="stat-label">Public Repos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{followers}</div>
                <div class="stat-label">Followers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{following}</div>
                <div class="stat-label">Following</div>
            </div>
        </div>

        <div class="achievements">
            <h2>Achievement Badges</h2>
            <p style="color: #8b949e; margin-bottom: 20px;">
                Track your progress at <a href="https://github.com/{user}">github.com/{user}</a>
            </p>
            <p style="color: #8b949e;">
                See <a href="https://github.com/UberMetroid/GitHub-Achievements">GitHub-Achievements</a> 
                repo for tools to track and earn achievements.
            </p>
        </div>

        <footer>
            <p>Generated by <a href="https://github.com/UberMetroid/GitHub-Achievements">GitHub-Achievements</a></p>
        </footer>
    </div>
</body>
</html>""".format(**{**stats, "updated": stats["updated"].replace("T", " ").split(".")[0]})


def main():
    try:
        stats = get_stats()
    except Exception as e:
        print(f"Error fetching stats: {e}")
        print("Generating demo page...")
        stats = {
            "user": "YourUsername",
            "updated": datetime.now().isoformat(),
            "merged_prs": 0,
            "coauthored_prs": 0,
            "total_stars": 0,
            "public_repos": 0,
            "followers": 0,
            "following": 0,
        }

    html = generate_html(stats)
    output = Path("docs/index.html")
    output.write_text(html)
    print(f"Generated {output}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
