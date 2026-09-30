"""Offline check for the publication and WeChat message boundary."""

import tempfile
import contextlib
import datetime as dt
import io
from pathlib import Path
from unittest.mock import patch
import notify_wechat
from notify_wechat import payload

with tempfile.TemporaryDirectory() as folder:
    post = Path(folder) / "post.md"
    post.write_text("---\nlayout: default\n---\n## AI 工具\n### 一\n### 二\n### 三\n### 四\n", encoding="utf-8")
    result = payload(post, "2026-09-30")
    assert result["title"] == "每日精选 2026-09-30"
    assert "一\n\n二\n\n三" in result["desp"] and "四" not in result["desp"]
    assert result["desp"].endswith("/2026-09-30/)")

    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    (Path(folder) / ".wechat_sent_date").write_text(today, encoding="utf-8")
    with patch.object(notify_wechat, "ROOT", Path(folder)), patch.dict(
        "os.environ", {"SERVERCHAN_SENDKEY": "SCTsample"}
    ), patch.object(notify_wechat, "urlopen") as request, contextlib.redirect_stdout(io.StringIO()):
        notify_wechat.main()
        request.assert_not_called()
    with patch.dict("os.environ", {"SERVERCHAN_SENDKEY": "invalid"}):
        try:
            notify_wechat.main()
        except SystemExit as error:
            assert "SCT SendKey" in str(error)
        else:
            raise AssertionError("Invalid credentials must be rejected before network access")

for post in (Path(__file__).parent / "docs" / "_posts").glob("*.md"):
    text = post.read_text(encoding="utf-8")
    assert text.startswith("---\n") and f"permalink: /{post.name[:10]}/" in text
    assert "sk-proj-" not in text and "SERVERCHAN_SENDKEY=" not in text
print("Publication format and notification payload checks passed.")
