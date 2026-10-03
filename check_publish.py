"""Offline check for the publication and WeChat message boundary."""

import tempfile
import contextlib
import datetime as dt
import io
import json
import re
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
from unittest.mock import patch
import notify_wechat
from notify_wechat import payload
from image_policy import validate_image

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

metadata_path = Path(__file__).parent / 'docs/_data/source_metadata.json'
if metadata_path.exists():
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    fields = {'role', 'site', 'url', 'section', 'author', 'author_label', 'author_url',
              'category', 'category_label', 'published', 'posted', 'updated', 'note'}
    for date, entries in metadata.items():
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', date)
        report = (Path(__file__).parent / f'docs/_posts/{date}-summary-zh.md').read_text(encoding='utf-8')
        headlines = re.findall(r'^### (.+)$', report, re.M)
        assert [entry['title'] for entry in entries] == headlines, 'Metadata must match every exact headline in order'
        assert len(headlines) == len(set(headlines)), 'Metadata requires unique full headlines'
        for entry in entries:
            assert {'title', 'sources'} <= set(entry) <= {'title', 'sources', 'image'} and entry['sources']
            if 'image' in entry:
                validate_image(entry['image'], entry['sources'])
            assert entry['sources'][0]['role'] == '主来源'
            for source in entry['sources']:
                assert {'role', 'site', 'url'} <= set(source) <= fields
                assert all(isinstance(value, str) and value.strip() for value in source.values())
                assert source['role'] in {'主来源', '辅来源', '社媒线索', '作者展示帖'}
                assert not ('published' in source and 'posted' in source), 'Original publication and social posting belong to separate sources'
                for name in ('url', 'author_url'):
                    if name not in source:
                        continue
                    url = urlsplit(source[name])
                    assert url.scheme == 'https' and url.hostname and not url.username and not url.password
                    assert not {key.lower() for key in parse_qs(url.query)} & {'token', 'key', 'signature', 'access_token', 'x-amz-signature'}
    print('Source metadata headline coverage, field boundaries and URL checks passed.')
print("Publication format and notification payload checks passed.")
