"""Private, live preview: no repository metadata or directory listings."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from site_tools import site_files

ROOT = Path(__file__).resolve().parents[1]


class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        path = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
        allowed = {p.relative_to(ROOT).as_posix() for p in site_files()}
        if path not in allowed:
            self.send_error(404)
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        super().end_headers()


if __name__ == "__main__":
    print("Private preview: http://127.0.0.1:18135", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18135), Preview).serve_forever()
