"""Private, live preview: no repository metadata or directory listings."""
import argparse
from contextlib import ExitStack
from threading import Event, Thread
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
    parser = argparse.ArgumentParser(description="Development preview on explicit network addresses")
    parser.add_argument("--bind", action="append", help="Listen address; repeat for multiple interfaces")
    args = parser.parse_args()
    with ExitStack() as stack:
        servers = [stack.enter_context(ThreadingHTTPServer((host, 18135), Preview))
                   for host in (args.bind or ["127.0.0.1"])]
        for server in servers:
            Thread(target=server.serve_forever, daemon=True).start()
            print(f"Development preview: http://{server.server_address[0]}:18135", flush=True)
        try:
            Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            for server in servers:
                server.shutdown()
