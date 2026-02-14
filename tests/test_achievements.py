import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import earn_achievements as ea


@pytest.fixture
def temp_config_dir(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / ".config" / "github-achievements"
        config_dir.mkdir(parents=True)
        monkeypatch.setattr(ea, "CONFIG_FILE", config_dir / "config.json")
        yield config_dir


def test_load_config_default(temp_config_dir):
    config = ea.load_config()
    assert "repo" in config
    assert "achievements" in config
    assert "pull_shark" in config["achievements"]


def test_save_and_load_config(temp_config_dir):
    test_config = {"repo": "testuser/testrepo", "achievements": {}}
    ea.save_config(test_config)
    loaded = ea.load_config()
    assert loaded["repo"] == "testuser/testrepo"


def test_get_config_value(temp_config_dir):
    test_config = {"repo": "myuser/myrepo", "achievements": {"pull_shark": {"threshold": [2, 16]}}}
    ea.save_config(test_config)
    assert ea.get_config_value("repo") == "myuser/myrepo"
    assert ea.get_config_value("achievements.pull_shark.threshold") == [2, 16]


def test_get_config_value_default(temp_config_dir):
    assert ea.get_config_value("nonexistent", "default") == "default"


def test_check_gh_installed():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        assert ea.check_gh_installed() is True


def test_check_gh_not_installed():
    with patch("subprocess.run", side_effect=FileNotFoundError):
        assert ea.check_gh_installed() is False


@patch("earn_achievements.run")
def test_gh_json_success(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = '{"login": "testuser"}'
    result = ea.gh_json(["api", "user"])
    assert result == {"login": "testuser"}


@patch("earn_achievements.run")
def test_gh_json_error(mock_run):
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "Not found"
    with pytest.raises(RuntimeError, match="Not found"):
        ea.gh_json(["api", "user"])


@patch("earn_achievements.gh_json")
def test_get_merged_prs_count(mock_gh_json):
    mock_gh_json.return_value = {"total_count": 42}
    result = ea.get_merged_prs_count("testuser")
    assert result == "42"


@patch("earn_achievements.gh_json")
def test_get_merged_prs_count_error(mock_gh_json):
    mock_gh_json.side_effect = Exception("API error")
    result = ea.get_merged_prs_count("testuser")
    assert result == "(unavailable)"


@patch("earn_achievements.gh_json")
def test_get_coauthored_prs_count(mock_gh_json):
    mock_gh_json.return_value = {"total_count": 10}
    result = ea.get_coauthored_prs_count("testuser")
    assert result == "10"


@patch("earn_achievements.gh_json")
def test_get_total_stars(mock_gh_json):
    mock_gh_json.return_value = [
        {"stargazers_count": 100},
        {"stargazers_count": 50},
        {"stargazers_count": 25},
    ]
    result = ea.get_total_stars("testuser")
    assert result == "175"


@patch("earn_achievements.gh_json")
def test_get_public_repos(mock_gh_json):
    mock_gh_json.return_value = {"public_repos": 15}
    result = ea.get_public_repos("testuser")
    assert result == "15"


@patch("earn_achievements.gh_json")
def test_get_followers(mock_gh_json):
    mock_gh_json.return_value = {"followers": 100, "following": 50}
    result = ea.get_followers("testuser")
    assert result == "100"


@patch("earn_achievements.gh_json")
def test_get_following(mock_gh_json):
    mock_gh_json.return_value = {"followers": 100, "following": 50}
    result = ea.get_following("testuser")
    assert result == "50"


@patch("earn_achievements.gh_json")
def test_get_total_prs(mock_gh_json):
    mock_gh_json.return_value = {"total_count": 75}
    result = ea.get_total_prs("testuser")
    assert result == "75"


@patch("earn_achievements.gh_json")
def test_get_total_issues(mock_gh_json):
    mock_gh_json.return_value = {"total_count": 20}
    result = ea.get_total_issues("testuser")
    assert result == "20"


@patch("earn_achievements.gh_json")
def test_get_gists_count(mock_gh_json):
    mock_gh_json.return_value = [1, 2, 3, 4, 5]
    result = ea.get_gists_count("testuser")
    assert result == "5"


def test_status_help(capsys):
    with patch.object(sys, "argv", ["earn_achievements.py"]):
        with pytest.raises(SystemExit):
            ea.main()


def test_config_show(temp_config_dir, capsys):
    with patch.object(sys, "argv", ["earn_achievements.py", "config", "--show"]):
        ea.main()
    output = capsys.readouterr().out
    assert "repo" in output


def test_config_set_repo(temp_config_dir, capsys):
    with patch.object(sys, "argv", ["earn_achievements.py", "config", "--set-repo", "newuser/newrepo"]):
        ea.main()
    config = ea.load_config()
    assert config["repo"] == "newuser/newrepo"


@patch("earn_achievements.check_gh_installed")
def test_status_no_gh(mock_check, capsys):
    mock_check.return_value = False
    with patch.object(sys, "argv", ["earn_achievements.py", "status"]):
        result = ea.main()
    assert result == 1
    output = capsys.readouterr().err
    assert "gh" in output.lower()


@patch("earn_achievements.check_gh_installed")
@patch("earn_achievements.gh_json")
def test_status_not_authenticated(mock_gh_json, mock_check, capsys):
    mock_check.return_value = True
    mock_gh_json.side_effect = RuntimeError("Not authenticated")
    with patch.object(sys, "argv", ["earn_achievements.py", "status"]):
        result = ea.main()
    assert result == 1
    output = capsys.readouterr().err
    assert "auth" in output.lower()


def test_seed_no_gh(capsys):
    with patch("earn_achievements.check_gh_installed") as mock_check:
        mock_check.return_value = False
        with patch.object(sys, "argv", ["earn_achievements.py", "seed"]):
            result = ea.main()
    assert result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
