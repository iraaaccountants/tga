"""Check the static site's crawlable pages and sitemap before publishing."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.tga-uae.com/"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.in_title = False
        self.h1_count = 0
        self.description = ""
        self.canonical = ""
        self.og_url = ""
        self.icon = ""
        self.images: list[tuple[str, bool]] = []
        self.links: list[str] = []
        self.json_ld: list[str] = []
        self.in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and a.get("name") == "description":
            self.description = a.get("content") or ""
        elif tag == "meta" and a.get("property") == "og:url":
            self.og_url = a.get("content") or ""
        elif tag == "link":
            rel = (a.get("rel") or "").split()
            if "canonical" in rel:
                self.canonical = a.get("href") or ""
            if "icon" in rel:
                self.icon = a.get("href") or ""
        elif tag == "img":
            self.images.append((a.get("src") or "", "alt" in a))
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"] or "")
        elif tag == "script" and a.get("type") == "application/ld+json":
            self.in_json_ld = True
            self.json_ld.append("")

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self.in_json_ld:
            self.json_ld[-1] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_json_ld = False


def main() -> None:
    errors: list[str] = []
    pages = sorted(ROOT.glob("*.html"))
    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    links: dict[str, set[str]] = {}
    canonical_urls: set[str] = set()

    for path in pages:
        parsed = PageParser()
        parsed.feed(path.read_text(encoding="utf-8"))
        expected = SITE if path.name == "index.html" else SITE + path.name
        canonical_urls.add(expected)
        titles[parsed.title.strip()].append(path.name)
        descriptions[parsed.description.strip()].append(path.name)

        for field, value in (("title", parsed.title), ("description", parsed.description), ("icon", parsed.icon)):
            if not value:
                errors.append(f"{path.name}: missing {field}")
        if parsed.h1_count != 1:
            errors.append(f"{path.name}: expected one H1, found {parsed.h1_count}")
        if parsed.canonical != expected or parsed.og_url != expected:
            errors.append(f"{path.name}: canonical/Open Graph URL differs from {expected}")
        if parsed.icon != "/assets/favicon-tga.png":
            errors.append(f"{path.name}: unexpected favicon {parsed.icon}")

        for source, has_alt in parsed.images:
            if not has_alt:
                errors.append(f"{path.name}: missing image alt for {source}")
            if source and not urlparse(source).scheme and not (ROOT / source.lstrip("/")).is_file():
                errors.append(f"{path.name}: missing image {source}")
        for payload in parsed.json_ld:
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}: invalid JSON-LD: {exc}")

        outgoing: set[str] = set()
        for href in parsed.links:
            if href.startswith("index.html"):
                errors.append(f"{path.name}: home link uses /index.html: {href}")
            url = urlparse(href)
            if url.scheme in ("mailto", "tel", "javascript", "data"):
                continue
            if url.scheme and url.netloc not in ("www.tga-uae.com", "tga-uae.com"):
                continue
            if not url.path and href.startswith("#"):
                continue
            target = unquote(url.path).lstrip("/") or "index.html"
            if target.endswith(".html"):
                outgoing.add(target)
                if not (ROOT / target).is_file():
                    errors.append(f"{path.name}: broken page link {href}")
        links[path.name] = outgoing

    for label, values in (("title", titles), ("description", descriptions)):
        for value, files in values.items():
            if len(files) > 1:
                errors.append(f"Duplicate {label} on {', '.join(files)}: {value}")

    root = ET.parse(ROOT / "sitemap.xml").getroot()
    urls = root.findall(f"{{{SITEMAP_NS}}}url")
    listed: list[str] = []
    for item in urls:
        loc = item.findtext(f"{{{SITEMAP_NS}}}loc") or ""
        listed.append(loc)
        updated = item.findtext(f"{{{SITEMAP_NS}}}lastmod") or ""
        try:
            date.fromisoformat(updated)
        except ValueError:
            errors.append(f"Invalid lastmod on {loc}: {updated}")
        for image in item.findall(f"{{{IMAGE_NS}}}image"):
            image_url = image.findtext(f"{{{IMAGE_NS}}}loc") or ""
            if not image_url.startswith(SITE) or not (ROOT / image_url.removeprefix(SITE)).is_file():
                errors.append(f"Invalid sitemap image {image_url}")

    if len(listed) != len(set(listed)):
        errors.append("Sitemap has duplicate URLs")
    if set(listed) != canonical_urls:
        errors.append(f"Sitemap URLs differ from canonical pages: missing={canonical_urls-set(listed)}, extra={set(listed)-canonical_urls}")
    if f"Sitemap: {SITE}sitemap.xml" not in (ROOT / "robots.txt").read_text(encoding="utf-8"):
        errors.append("robots.txt does not point to the canonical sitemap")

    reached = {"index.html"}
    queue = deque(reached)
    while queue:
        for target in links[queue.popleft()]:
            if target not in reached and target in links:
                reached.add(target)
                queue.append(target)
    if set(links) != reached:
        errors.append(f"Pages unreachable from homepage: {sorted(set(links)-reached)}")

    if errors:
        raise SystemExit("SEO check failed:\n- " + "\n- ".join(errors))
    print(f"SEO check passed: {len(pages)} pages, {len(listed)} sitemap URLs, all pages reachable.")


if __name__ == "__main__":
    main()
