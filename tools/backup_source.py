#!/usr/bin/env python3
"""Archive source pages and sitemap URLs before canceling Shopify.

Uses the standard library and inherited proxy/TLS configuration. Raw backups
are evidence for migration, not deployable pages. Run from the repository root.
"""
import argparse
import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import urlopen
import xml.etree.ElementTree as ET

SITE = "https://prorecoverytech.com"
SITE_HOSTS = {"prorecoverytech.com", "www.prorecoverytech.com"}
ASSET_HOSTS = SITE_HOSTS | {"cdn.shopify.com"}


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.assets = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.add(attrs["href"])
        if tag in {"img", "source"}:
            for name in ("src", "data-src"):
                if attrs.get(name) and "{" not in attrs[name]:
                    self.assets.add(attrs[name])
            for name in ("srcset", "data-srcset"):
                for candidate in attrs.get(name, "").split(","):
                    if candidate.strip() and "{" not in candidate:
                        self.assets.add(candidate.strip().split()[0])
        if tag == "link" and "icon" in attrs.get("rel", ""):
            if attrs.get("href"):
                self.assets.add(attrs["href"])
        if tag == "meta" and attrs.get("property") == "og:image":
            if attrs.get("content"):
                self.assets.add(attrs["content"])


def normalize(base, reference):
    parsed = urlsplit(urljoin(base, reference))
    if parsed.scheme not in {"https", "http"}:
        return None
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))


def backup(destination):
    destination.mkdir(parents=True, exist_ok=False)
    queue = deque((SITE + p, "page") for p in (
        "/", "/blogs/news", "/blogs/health-performance",
        "/policies/privacy-policy", "/policies/refund-policy",
        "/policies/shipping-policy", "/policies/terms-of-service",
    ))
    queue.append((SITE + "/sitemap.xml", "sitemap"))
    seen, records = set(), []
    while queue:
        url, kind = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        record = {"url": url, "kind": kind}
        try:
            with urlopen(url, timeout=30) as response:
                data = response.read()
                record.update(status=response.status, final_url=response.url,
                              content_type=response.headers.get("Content-Type", ""))
            digest = hashlib.sha256(data).hexdigest()
            suffix = ".xml" if kind == "sitemap" else ".html" if kind == "page" else ".bin"
            filename = hashlib.sha256(url.encode()).hexdigest() + suffix
            (destination / filename).write_bytes(data)
            record.update(file=filename, sha256=digest, bytes=len(data))
            if kind == "sitemap":
                root = ET.fromstring(data)
                child_kind = "sitemap" if root.tag.endswith("sitemapindex") else "page"
                for loc in root.findall(".//{*}loc"):
                    target = normalize(url, loc.text or "")
                    if target and urlsplit(target).hostname in SITE_HOSTS:
                        queue.append((target, child_kind))
            elif kind == "page":
                parser = References()
                parser.feed(data.decode("utf-8", errors="replace"))
                for reference in sorted(parser.links):
                    target = normalize(url, reference)
                    if target and urlsplit(target).hostname in SITE_HOSTS:
                        path = urlsplit(target).path
                        if path.startswith(("/blogs/news", "/blogs/health-performance")):
                            queue.append((target, "page"))
                for reference in sorted(parser.assets):
                    target = normalize(url, reference)
                    if target and urlsplit(target).hostname in ASSET_HOSTS:
                        queue.append((target, "asset"))
            print(f"Saved {kind}: {url}")
        except Exception as error:
            record["error"] = str(error)
            print(f"FAILED {url}: {error}")
        records.append(record)
        (destination / "manifest.json").write_text(json.dumps({
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "records": records,
        }, indent=2) + "\n")
    failures = sum("error" in record for record in records)
    print(f"Archived {len(records) - failures} URLs; {failures} failures.")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("backups") /
                        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    args = parser.parse_args()
    raise SystemExit(backup(args.output))
