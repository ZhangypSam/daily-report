"""Offline check for the publication and WeChat message boundary."""

import tempfile
from pathlib import Path
from notify_wechat import payload

with tempfile.TemporaryDirectory() as folder:
    post = Path(folder) / "post.md"
    post.write_text("---\nlayout: default\n---\n## AI 工具\n### 一\n### 二\n### 三\n### 四\n", encoding="utf-8")
    result = payload(post, "2026-09-30")
    assert result["title"] == "每日精选 2026-09-30"
    assert "一\n\n二\n\n三" in result["desp"] and "四" not in result["desp"]
    assert result["desp"].endswith("/2026-09-30/)")

for post in (Path(__file__).parent / "docs" / "_posts").glob("*.md"):
    text = post.read_text(encoding="utf-8")
    assert text.startswith("---\n") and f"permalink: /{post.name[:10]}/" in text
    assert "sk-proj-" not in text and "SERVERCHAN_SENDKEY=" not in text
print("Publication format and notification payload checks passed.")
