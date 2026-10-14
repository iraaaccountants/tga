"""Build the seven service category pages and normalize service URLs."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from check_seo import PageParser
from service_routes import CATEGORIES, SERVICE_ROUTES, SPECIAL_LEAVES, category_for_stem


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.tga-uae.com/"
ABSOLUTE_PAGE = re.compile(r"https://www\.tga-uae\.com/([a-z0-9-]+)(?![a-z0-9./-])")
ATTRIBUTE = re.compile(r'(?P<name>\b(?:href|src|action))="(?P<value>[^"]*)"')
JSON_LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.DOTALL)
BREADCRUMBS = re.compile(r'<nav class="breadcrumbs" aria-label="Breadcrumb">.*?</nav>', re.DOTALL)
ANCHOR_TO_CATEGORY = {
    "business-setup": "business-setup",
    "pro-services": "pro-visas",
    "accounting": "accounting-finance",
    "tax": "tax-transfer-pricing",
    "compliance": "compliance-governance",
    "trade-ip": "trade-ip",
    "banking-wills": "banking-wills",
}


def replace_absolute_page(match: re.Match[str]) -> str:
    stem = match.group(1)
    return SITE + SERVICE_ROUTES[stem] if stem in SERVICE_ROUTES else match.group(0)


def replace_attribute(match: re.Match[str]) -> str:
    value = match.group("value")
    if value.startswith(("#", "//", "/")) or re.match(r"^[a-z][a-z0-9+.-]*:", value, re.I):
        return match.group(0)
    url = urlsplit(value)
    route = SERVICE_ROUTES.get(url.path, url.path)
    updated = urlunsplit(("", "", "/" + route, url.query, url.fragment))
    return f'{match.group("name")}="{updated}"'


def service_schema_and_crumbs(text: str, stem: str) -> str:
    category = category_for_stem(stem)
    category_url = SITE + "services/" + category
    current_url = SITE + SERVICE_ROUTES[stem]
    old_nav = BREADCRUMBS.search(text)
    if old_nav is None:
        raise ValueError(f"Missing visible breadcrumb on {stem}")
    old_links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', old_nav.group(0))
    current = re.search(r'<span aria-current="page">([^<]+)</span>', old_nav.group(0))
    if current is None:
        raise ValueError(f"Missing breadcrumb current page on {stem}")
    parent_links = [(href, label) for href, label in old_links[2:] if href != "/services/" + category]
    parts = ['<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a>',
             '<span aria-hidden="true">/</span><a href="/services">Services</a>',
             f'<span aria-hidden="true">/</span><a href="/services/{category}">{escape(CATEGORIES[category]["label"])}</a>']
    for href, label in parent_links:
        parts.append(f'<span aria-hidden="true">/</span><a href="{href}">{label}</a>')
    parts.append(f'<span aria-hidden="true">/</span><span aria-current="page">{current.group(1)}</span></nav>')
    text = text[:old_nav.start()] + "".join(parts) + text[old_nav.end():]

    def update_schema(match: re.Match[str]) -> str:
        payload = json.loads(match.group(2))
        for node in payload.get("@graph", []):
            if node.get("@type") != "BreadcrumbList":
                continue
            old = node["itemListElement"]
            parents = old[2:-1]
            # Keep any existing service parent after the new category crumb.
            parents = [item for item in parents if item.get("item") != category_url]
            items = [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "Services", "item": SITE + "services"},
                {"@type": "ListItem", "position": 3, "name": CATEGORIES[category]["label"], "item": category_url},
                *parents,
                {**old[-1], "item": current_url},
            ]
            for position, item in enumerate(items, 1):
                item["position"] = position
            node["itemListElement"] = items
        return match.group(1) + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    return JSON_LD.sub(update_schema, text)


def update_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = ABSOLUTE_PAGE.sub(replace_absolute_page, text)
    text = ATTRIBUTE.sub(replace_attribute, text)
    for anchor, category in ANCHOR_TO_CATEGORY.items():
        text = text.replace(f"/services#{anchor}", f"/services/{category}")
        text = text.replace(SITE + f"services#{anchor}", SITE + f"services/{category}")
    if path.stem in SERVICE_ROUTES:
        text = service_schema_and_crumbs(text, path.stem)
    if path.name == "services.html":
        for anchor, category in ANCHOR_TO_CATEGORY.items():
            heading = re.compile(rf'(<section class="category-block" id="{anchor}".*?<h2 id="[^"]+">)(.*?)(</h2>)', re.DOTALL)
            text = heading.sub(
                lambda m: m.group(0) if "<a " in m.group(2) else
                m.group(1) + f'<a href="/services/{category}">' + m.group(2) + '</a>' + m.group(3),
                text,
                count=1,
            )
    path.write_text(text, encoding="utf-8")


def generate_category_pages() -> None:
    source = (ROOT / "services.html").read_text(encoding="utf-8")
    header = re.search(r'<header class="site-header".*?</header>', source, re.DOTALL).group(0)
    footer = re.search(r'<footer class="site-footer".*?</body>', source, re.DOTALL).group(0)
    output = ROOT / "categories"
    output.mkdir(exist_ok=True)
    for category, details in CATEGORIES.items():
        label = details["label"]
        summary = details["summary"]
        url = SITE + "services/" + category
        title = f"{label} in Dubai & UAE | TGA"
        cards = []
        items = []
        for number, stem in enumerate(details["pages"], 1):
            parser = PageParser()
            parser.feed((ROOT / f"{stem}.html").read_text(encoding="utf-8"))
            service = next(node for raw in parser.json_ld for node in json.loads(raw).get("@graph", []) if node.get("@type") == "Service")
            name = service["name"]
            description = service.get("description", "")
            service_url = SITE + SERVICE_ROUTES[stem]
            items.append({"@type": "ListItem", "position": number, "name": name, "url": service_url})
            cards.append(f'<article class="category-service-card"><span>{number:02d}</span><h3><a href="/{SERVICE_ROUTES[stem]}">{escape(name)}</a></h3><p>{escape(description)}</p><a class="inline-link" href="/{SERVICE_ROUTES[stem]}">Explore service <span aria-hidden="true">↗</span></a></article>')
        graph = {"@context": "https://schema.org", "@graph": [
            {"@type": "CollectionPage", "@id": url + "#webpage", "url": url, "name": title,
             "description": summary, "inLanguage": "en-AE", "isPartOf": {"@id": SITE + "#website"},
             "mainEntity": {"@id": url + "#service-list"}, "breadcrumb": {"@id": url + "#breadcrumb"}},
            {"@type": "ItemList", "@id": url + "#service-list", "name": label, "itemListElement": items},
            {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": "Services", "item": SITE + "services"},
                {"@type": "ListItem", "position": 3, "name": label, "item": url},
            ]},
        ]}
        content = f'''<!doctype html>
<html lang="en-AE"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#083f91">
  <title>{escape(title)}</title><meta name="description" content="{escape(summary, quote=True)}">
  <link rel="canonical" href="{url}"><link rel="describedby" href="{SITE}llms.txt"><link rel="icon" href="/assets/favicon-tga.png" type="image/png" sizes="256x256"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png" sizes="180x180">
  <meta property="og:type" content="website"><meta property="og:locale" content="en_AE"><meta property="og:site_name" content="TGA"><meta property="og:url" content="{url}"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(summary, quote=True)}"><meta property="og:image" content="{SITE}assets/dubai-skyline.webp">
  <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(summary, quote=True)}"><meta name="twitter:image" content="{SITE}assets/dubai-skyline.webp">
  <link rel="stylesheet" href="/styles.css"><script type="application/ld+json">{json.dumps(graph, ensure_ascii=False, separators=(',', ':'))}</script>
</head><body class="service-category-page"><a class="skip-link" href="#main">Skip to content</a>
{header}
<main id="main">
  <section class="service-hero category-hero" aria-labelledby="category-title"><div class="service-hero-shade"></div><div class="container service-hero-inner"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/services">Services</a><span aria-hidden="true">/</span><span aria-current="page">{escape(label)}</span></nav><p class="eyebrow eyebrow-on-dark"><span class="eyebrow-line"></span>Service category</p><h1 id="category-title">{escape(label)}</h1><p class="service-hero-lead">{escape(summary)}</p><a class="button button-light" href="#category-services">Explore services <span aria-hidden="true">↓</span></a></div></section>
  <section class="category-landing-list section" id="category-services"><div class="container"><div class="category-landing-heading"><p class="eyebrow"><span class="eyebrow-line"></span>Explore this category</p><h2>Find the support that fits your next step.</h2><p>{escape(summary)} Select a service below to see the scope and how we can help.</p></div><div class="category-service-grid">{''.join(cards)}</div></div></section>
  <section class="service-directory-cta"><div class="container service-directory-cta-inner"><div><p class="eyebrow eyebrow-on-dark"><span class="eyebrow-line"></span>Need help choosing?</p><h2>Start with a conversation.</h2><p>Tell us what you are working through. We can help identify the relevant service and next step.</p></div><div><a class="button button-light" href="/contact">Contact TGA <span aria-hidden="true">↗</span></a><a class="text-link light-link" href="https://wa.me/971569210222" target="_blank" rel="noopener noreferrer">Chat on WhatsApp <span aria-hidden="true">→</span></a></div></div></section>
</main>
{footer}'''
        (output / f"{category}.html").write_text(content, encoding="utf-8")


def update_sitemap() -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("image", "http://www.google.com/schemas/sitemap-image/1.1")
    path = ROOT / "sitemap.xml"
    tree = ET.parse(path)
    root = tree.getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    known = {item.findtext(ns + "loc") for item in root.findall(ns + "url")}
    for position, category in enumerate(CATEGORIES, 2):
        url = SITE + "services/" + category
        if url in known:
            continue
        item = ET.Element(ns + "url")
        ET.SubElement(item, ns + "loc").text = url
        ET.SubElement(item, ns + "lastmod").text = date.today().isoformat()
        root.insert(position, item)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    for path in ROOT.glob("*.html"):
        update_html(path)
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in (".md", ".json", ".txt", ".xml") and path.name != "README.md":
            text = path.read_text(encoding="utf-8")
            text = ABSOLUTE_PAGE.sub(replace_absolute_page, text)
            for anchor, category in ANCHOR_TO_CATEGORY.items():
                text = text.replace(SITE + f"services#{anchor}", SITE + f"services/{category}")
            path.write_text(text, encoding="utf-8")
    generate_category_pages()
    update_sitemap()


if __name__ == "__main__":
    main()
