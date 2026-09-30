"""Send today's published digest through ServerChan Turbo; never log the key."""

import datetime as dt
import json
import os
from pathlib import Path
import re
import ssl
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE = "https://zhangypsam.github.io/daily-report"

# The local Windows root store contains an expired chain; use installed CA roots.
try:
    import certifi
except ImportError:
    certifi = None
TLS = ssl.create_default_context(cafile=certifi.where() if certifi else None)


def payload(post, date):
    body = post.read_text(encoding="utf-8")
    headlines = re.findall(r"^### (.+)$", body, re.MULTILINE)
    return {
        "title": f"每日精选 {date}",
        "desp": "\n\n".join(headlines[:3]) + f"\n\n[阅读完整日报]({BASE}/{date}/)",
    }


def main():
    key = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
    if not key:
        print("WeChat pending: SERVERCHAN_SENDKEY is not configured.")
        return
    if not re.fullmatch(r"SCT[A-Za-z0-9]+", key):
        raise SystemExit("Expected a ServerChan Turbo SCT SendKey.")
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    post = ROOT / "docs" / "_posts" / f"{today}-summary-zh.md"
    if not post.exists():
        print("No current-day report; WeChat skipped.")
        return
    # Confirm the report URL is reachable before sending its link.
    try:
        with urlopen(f"{BASE}/{today}/", timeout=30, context=TLS) as response:
            if response.status != 200:
                raise SystemExit("Report is not published; WeChat skipped.")
        request = Request(
            f"https://sctapi.ftqq.com/{key}.send",
            data=urlencode(payload(post, today)).encode(),
        )
        with urlopen(request, timeout=30, context=TLS) as response:
            result = json.load(response)
    except URLError:
        raise SystemExit("WeChat network request failed; check service availability.") from None
    if result.get("code") != 0:
        raise SystemExit(f"WeChat service rejected delivery (code={result.get('code')}).")
    print("WeChat notification accepted by ServerChan.")


if __name__ == "__main__":
    main()
