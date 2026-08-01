#!/usr/bin/env python3
"""Companion server for 語彙練習帳 (N2 vocabulary practice).

Serves index.html and persists study progress plus voice recordings to disk,
so neither is trapped in one browser's storage.

    python3 server.py                 # http://127.0.0.1:8788
    python3 server.py --port 9000
    python3 server.py --host 0.0.0.0  # reachable from your phone on the LAN

Everything lands in ./data next to this file:

    data/progress.json        statuses, schedule, day log
    data/clips/index.json     word -> {file, date}
    data/clips/*.webm         one recording per word

Python 3.8+, standard library only.
"""

import argparse
import hashlib
import json
import os
import posixpath
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
CLIPS = os.path.join(DATA, "clips")
PROGRESS = os.path.join(DATA, "progress.json")
INDEX = os.path.join(CLIPS, "index.json")

MAX_JSON = 4 * 1024 * 1024        # progress payloads are tiny; this is generous
MAX_CLIP = 12 * 1024 * 1024       # a 12s webm clip is ~100KB
STATIC = {"": "index.html", "/": "index.html", "/index.html": "index.html"}
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".json": "application/json",
         ".webm": "audio/webm", ".ogg": "audio/ogg", ".png": "image/png",
         ".svg": "image/svg+xml", ".ico": "image/x-icon"}


def ensure_dirs():
    os.makedirs(CLIPS, exist_ok=True)


def read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return fallback


def write_json(path, obj):
    """Write via a temp file + replace so a crash can't truncate the real one."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def clip_filename(word_id):
    """Hash the word into a filename.

    Word IDs are Japanese text ('引き受ける'). Hashing sidesteps both filesystem
    encoding quirks and any chance of a crafted ID escaping the clips directory.
    """
    return hashlib.sha1(word_id.encode("utf-8")).hexdigest() + ".webm"


class Handler(BaseHTTPRequestHandler):
    server_version = "GoiRenshucho/1.0"
    protocol_version = "HTTP/1.1"

    # ── plumbing ──────────────────────────────────────────
    def _send(self, code, body=b"", ctype="application/json", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False), "application/json")

    def _err(self, code, msg):
        self._json({"error": msg}, code)

    def _body(self, limit):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None, "bad Content-Length"
        if n <= 0:
            return None, "empty body"
        if n > limit:
            return None, "body too large (%d bytes, limit %d)" % (n, limit)
        return self.rfile.read(n), None

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s  %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    # ── routing ───────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self.api_get(path[4:])
        return self.static(path)

    def do_HEAD(self):
        self.do_GET()

    def do_PUT(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            return self._err(405, "PUT is only supported under /api/")
        return self.api_put(path[4:])

    # ── static files ──────────────────────────────────────
    def static(self, path):
        """Serve the app, and only the app.

        The whole thing is one self-contained index.html, so an allowlist beats
        a traversal-proof file server: server.py, data/, and anything else you
        happen to drop in this folder stay unreachable over HTTP.
        """
        rel = STATIC.get(posixpath.normpath(unquote(path)))
        if rel is None:
            return self._err(404, "not found")

        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            return self._err(404, "not found")

        ctype = TYPES.get(os.path.splitext(full)[1].lower(), "application/octet-stream")
        with open(full, "rb") as fh:
            self._send(200, fh.read(), ctype)

    # ── api ───────────────────────────────────────────────
    def api_get(self, route):
        if route == "/health":
            manifest = read_json(INDEX, {})
            saved = ""
            if os.path.isfile(PROGRESS):
                saved = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(PROGRESS)))
            return self._json({
                "ok": True, "app": "n2-goi", "clips": len(manifest),
                "saved": saved, "dir": os.path.relpath(DATA, ROOT),
            })

        if route == "/progress":
            return self._json(read_json(PROGRESS, {}))

        if route == "/clips":
            manifest = read_json(INDEX, {})
            return self._json({k: v.get("date", "") for k, v in manifest.items()})

        if route.startswith("/clips/"):
            word_id = unquote(route[len("/clips/"):])
            entry = read_json(INDEX, {}).get(word_id)
            if not entry:
                return self._err(404, "no clip for that word")
            full = os.path.join(CLIPS, entry["file"])
            if not os.path.isfile(full):
                return self._err(404, "clip file is missing from disk")
            with open(full, "rb") as fh:
                return self._send(200, fh.read(), "audio/webm")

        return self._err(404, "unknown endpoint")

    def api_put(self, route):
        ensure_dirs()

        if route == "/progress":
            raw, err = self._body(MAX_JSON)
            if err:
                return self._err(413 if "large" in err else 400, err)
            try:
                obj = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return self._err(400, "body was not valid JSON")
            if not isinstance(obj, dict) or "p" not in obj:
                return self._err(400, "not a progress payload (missing 'p')")
            write_json(PROGRESS, obj)
            self.log_message("saved progress (%d words tracked)", len(obj.get("p") or {}))
            return self._json({"ok": True, "words": len(obj.get("p") or {})})

        if route.startswith("/clips/"):
            word_id = unquote(urlparse(route).path[len("/clips/"):])
            if not word_id:
                return self._err(400, "missing word id")
            raw, err = self._body(MAX_CLIP)
            if err:
                return self._err(413 if "large" in err else 400, err)
            date = (parse_qs(urlparse(self.path).query).get("date") or [""])[0]

            fname = clip_filename(word_id)
            with open(os.path.join(CLIPS, fname), "wb") as fh:
                fh.write(raw)
            manifest = read_json(INDEX, {})
            manifest[word_id] = {"file": fname, "date": date, "bytes": len(raw)}
            write_json(INDEX, manifest)
            self.log_message("saved clip for %s (%d bytes)", word_id, len(raw))
            return self._json({"ok": True, "bytes": len(raw)})

        return self._err(404, "unknown endpoint")


def main():
    ap = argparse.ArgumentParser(description="Serve 語彙練習帳 and store its data on disk.")
    ap.add_argument("--host", default="127.0.0.1",
                    help="bind address (default 127.0.0.1; use 0.0.0.0 for LAN access)")
    ap.add_argument("--port", type=int, default=8788, help="port (default 8788)")
    args = ap.parse_args()

    ensure_dirs()
    if not os.path.isfile(os.path.join(ROOT, "index.html")):
        sys.exit("index.html is not next to server.py — keep the exported files together.")

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = "http://%s:%d" % ("localhost" if args.host == "127.0.0.1" else args.host, args.port)
    print("語彙練習帳 — N2 vocabulary practice")
    print("  open    %s" % url)
    print("  data    %s" % DATA)
    if args.host != "127.0.0.1":
        print("  note    bound to %s with no authentication — trusted networks only." % args.host)
    print("  stop    Ctrl-C\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Your data is in %s" % DATA)
        httpd.server_close()


if __name__ == "__main__":
    main()
