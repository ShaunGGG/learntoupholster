#!/usr/bin/env python3
"""Ping IndexNow (Bing, and other participating engines) with every URL in the sitemap.
Run after each deploy:   python3 indexnow-ping.py
"""
import json, re, urllib.request, sys

KEY = "92086be83c4ff1a244802723e9619bcb"
HOST = "www.learntoupholster.com"

urls = re.findall(r"<loc>(https://[^<]+)</loc>", open("sitemap.xml").read())
if not urls:
    sys.exit("No URLs found in sitemap.xml")

payload = {
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": urls,
}
req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json; charset=utf-8"},
)
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"IndexNow: HTTP {r.status} — {len(urls)} URLs submitted for {HOST}")
except urllib.error.HTTPError as e:
    print(f"IndexNow returned HTTP {e.code}: {e.read().decode()[:200]}")
    print("If this is 403, the key file may not be live yet — deploy first, then ping.")
