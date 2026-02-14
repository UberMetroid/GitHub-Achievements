import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

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


def test_status_help(capsys):
    with patch.object(sys, "argv", ["earn_achievements.py"]):
        with pytest.raises(SystemExit):
            ea.main()
    # Just verify it doesn't crash on help


def test_config_show(capsys):
    with patch.object(sys, "argv", ["earn_achievements.py", "config", "--show"]):
        ea.main()
    output = capsys.readouterr().out
    assert "repo" in output


def test_config_set_repo(temp_config_dir, capsys):
    with patch.object(sys, "argv", ["earn_achievements.py", "config", "--set-repo", "newuser/newrepo"]):
        ea.main()
    config = ea.load_config()
    assert config["repo"] == "newuser/newrepo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
