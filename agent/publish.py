# PyGithub SDK verified against pygithub 2.9.1:
# - Github(auth=Auth.Token(token))  (github/MainClass.py)
# - repo.create_file(path, message, content, branch=...)  (github/Repository.py:2738)
# - repo.get_contents(path)  (github/Repository.py:2455)
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from github import Auth, Github


def build_index_md(
    *,
    title: str,
    summary: str,
    topic: str,
    source_count: int,
    date_str: str,
) -> str:
    """Build index.md landing page for a published folder."""
    return f"""# {title}

{summary}

- **Topic:** {topic}
- **Date:** {date_str}
- **Sources:** {source_count}

[Read the explainer](./article.md)
"""


def write_artifact_folder(
    *,
    base_dir: Path,
    slug: str,
    date_str: str,
    topic: str,
    article_body: str,
    source_count: int,
) -> Path:
    """Write published/<date>-<slug>/article.md, index.md, assets/."""
    folder = base_dir / f"{date_str}-{slug}"
    assets = folder / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    title_match = re.search(r"^#\s+(.+)$", article_body, re.MULTILINE)
    title = title_match.group(1) if title_match else topic
    (folder / "article.md").write_text(article_body, encoding="utf-8")
    (folder / "index.md").write_text(
        build_index_md(
            title=title,
            summary=f"Experiential explainer on {topic}.",
            topic=topic,
            source_count=source_count,
            date_str=date_str,
        ),
        encoding="utf-8",
    )
    return folder


def resolve_github_repo() -> str:
    """Resolve owner/repo from GITHUB_REPO, git remote origin, or default."""
    configured = os.getenv("GITHUB_REPO", "").strip()
    if configured:
        return configured
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    except Exception:
        pass
    return "rockangator/exe"


def publish_to_github(
    folder: Path,
    *,
    slug: str,
    repo_name: str | None = None,
    branch: str = "main",
) -> str:
    """Commit article.md and index.md via PyGithub; return public article URL."""
    token = os.environ["GITHUB_TOKEN"]
    repo_name = repo_name or resolve_github_repo()

    gh = Github(auth=Auth.Token(token))
    repo = gh.get_repo(repo_name)
    rel = folder.name

    urls: list[str] = []
    for name in ("article.md", "index.md"):
        local = folder / name
        path = f"published/{rel}/{name}"
        content = local.read_text(encoding="utf-8")
        try:
            existing = repo.get_contents(path, ref=branch)
            repo.update_file(
                path,
                f"publish: {slug} ({name})",
                content,
                existing.sha,
                branch=branch,
            )
        except Exception:
            repo.create_file(path, f"publish: {slug} ({name})", content, branch=branch)
        urls.append(f"https://github.com/{repo_name}/blob/{branch}/{path}")

    return urls[0]
