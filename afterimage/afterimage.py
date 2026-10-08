#!/usr/bin/env python3
"""CARBON AFTERIMAGE: native execution, live viewing, and portable replay export."""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import webbrowser

import cards
from engine import Press, compile_press, export_replay

ROOT = Path(__file__).resolve().parent


def render(payload: dict) -> str:
    # No external assets and no browser transition evaluator. The offline page
    # only applies observed native trace events to a drawing.
    data = json.dumps(payload, separators=(",", ":")).replace("<", "\\u003c")
    return (ROOT / "viewer.html").read_text().replace("/*__CARBON_DATA__*/null", data)


def serve(press: Press, port: int, open_browser: bool):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def send(self, content: bytes, kind: str = "application/json", status: int = 200):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            if self.path == "/":
                self.send(render(dict(live=True, worlds=[press.snapshot()])).encode(),
                          "text/html; charset=utf-8")
            elif self.path == "/state":
                self.send(json.dumps(press.snapshot()).encode())
            elif self.path == "/checkpoint":
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp) / "afterimage-world.zip"
                    press.checkpoint(path)
                    self.send(path.read_bytes(), "application/zip")
            else:
                self.send(b'{"error":"Not found"}', status=404)

        def do_POST(self):
            # Only this local origin may trigger mutations. The server binds
            # loopback; the browser never submits world file paths.
            host = self.headers.get("Host", "")
            origin = self.headers.get("Origin")
            if host not in (f"127.0.0.1:{port}", f"localhost:{port}") or \
                    (origin is not None and origin not in
                     (f"http://127.0.0.1:{port}", f"http://localhost:{port}")):
                self.send(b'{"error":"Local origin required"}', status=403)
                return
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 65536 or self.headers.get("Content-Type") != "application/json":
                    raise ValueError("JSON request required")
                body = json.loads(self.rfile.read(size))
                with press.lock:
                    if self.path == "/step":
                        response = press.step(body["rounds"])
                    elif self.path == "/paint":
                        press.paint(body["positions"], body["color"])
                        response = press.snapshot()
                    elif self.path == "/fold":
                        press.fold(body["first"], body["second"])
                        response = press.snapshot()
                    elif self.path == "/genome":
                        press.edit_genome(body["index"], body["turns"], body["stamps"])
                        response = press.snapshot()
                    elif self.path == "/seed":
                        if body["preset"] not in cards.PRESETS:
                            raise ValueError("Unknown specimen")
                        cards.seed(press.directory, body["preset"])
                        response = press.snapshot()
                    else:
                        self.send(b'{"error":"Not found"}', status=404)
                        return
                self.send(json.dumps(response).encode())
            except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                self.send(json.dumps(dict(error=str(exc))).encode(), status=400)

    url = f"http://127.0.0.1:{port}"
    print(f"CARBON / AFTERIMAGE  {url}\nNative FORMAT press active. Ctrl-C stops the viewer.")
    if open_browser:
        webbrowser.open(url)
    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=cards.PRESETS, default="afterimage")
    parser.add_argument("--world", type=Path, default=ROOT / "world")
    parser.add_argument("--resume", action="store_true", help="Open an existing world without reseeding")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=1977)
    parser.add_argument("--open", action="store_true", help="Open the local viewer in your browser")
    parser.add_argument("--rounds", type=int, default=0)
    parser.add_argument("--export", type=Path, help="Write an offline viewer with three native replay specimens")
    parser.add_argument("--raw", type=Path, help="Save full native trace for --rounds")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be 1..65535")
    build = compile_press(ROOT / ".build")
    executable = Path(build["executable"])
    if args.export:
        with tempfile.TemporaryDirectory(prefix="carbon-export-") as temp:
            worlds = [export_replay(p, executable, Path(temp) / p) for p in cards.PRESETS]
        args.export.parent.mkdir(parents=True, exist_ok=True)
        args.export.write_text(render(dict(live=False, worlds=worlds, build=build)))
        print(f"Native replay viewer: {args.export.resolve()}")
        return
    if not args.resume:
        cards.seed(args.world, args.preset)
    elif not (args.world / "world.json").is_file():
        parser.error("No checkpoint here. Extract a checkpoint ZIP into --world first.")
    press = Press(args.world, executable)
    if args.rounds:
        result = press.step(args.rounds, raw_path=args.raw)
        print(f"{len(result['trace'])} native transitions; round {result['round']}")
    if args.serve:
        serve(press, args.port, args.open)
    elif not args.rounds:
        print("Seeded world. Add --serve --open for the live instrument, or --rounds N.")


if __name__ == "__main__":
    main()
