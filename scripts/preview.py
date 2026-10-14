"""Preview the static site locally with its production-style clean URLs."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path):
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
