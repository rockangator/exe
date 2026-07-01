from __future__ import annotations

from unittest.mock import patch

from agent.publish import resolve_github_repo


def test_resolve_github_repo_defaults_to_rockangator(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_REPO", raising=False)
    with patch("agent.publish.subprocess.run", side_effect=OSError("no git")):
        assert resolve_github_repo() == "rockangator/exe"


def test_resolve_github_repo_uses_env(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_REPO", "custom/repo")
    assert resolve_github_repo() == "custom/repo"
