"""Preview the static site locally with its production-style clean URLs."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

try:
    from .service_routes import CATEGORIES, SERVICE_ROUTES
except ImportError:  # Direct execution: python scripts/preview.py
    from service_routes import CATEGORIES, SERVICE_ROUTES


ROOT = Path(__file__).resolve().parents[1]
ROUTE_FILES = {route: ROOT / f"{stem}.html" for stem, route in SERVICE_ROUTES.items()}


class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
        clean_path = urlsplit(path).path.lstrip("/")
        if clean_path in ROUTE_FILES:
            return str(ROUTE_FILES[clean_path])
        if clean_path.startswith("services/") and clean_path.removeprefix("services/") in CATEGORIES:
            return str(ROOT / "categories" / f"{clean_path.removeprefix('services/')}.html")
        translated = Path(super().translate_path(path))
        if not translated.exists() and not translated.suffix:
            html_page = translated.with_suffix(".html")
            if html_page.is_file():
                return str(html_page)
        return str(translated)


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    print(f"Preview: http://{address[0]}:{address[1]}/")
    ThreadingHTTPServer(address, CleanURLHandler).serve_forever()
