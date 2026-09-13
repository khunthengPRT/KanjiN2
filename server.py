#!/usr/bin/env python3
"""Companion server for 語彙練習帳 (N2 vocabulary practice).

Serves index.html and persists study progress plus voice recordings to disk,
so neither is trapped in one browser's storage.

    python3 server.py                 # http://127.0.0.1:8788
    python3 server.py --port 9000
    python3 server.py --host 0.0.0.0  # reachable from your phone on the LAN
                                      # (switches to https so the mic works)

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
import socket
import ssl
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
CLIPS = os.path.join(DATA, "clips")
CERT = os.path.join(DATA, "cert")
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


def lan_ip():
    """Best guess at this machine's address on the local network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))      # no packets sent; just picks the route
        return s.getsockname()[0]
    except OSError:
        return ""
    finally:
        s.close()


def ensure_cert(ip):
    """Create a self-signed certificate for this machine, once.

    Browsers only expose the microphone on a "secure context". localhost
    counts; a plain-HTTP LAN address does not, so a phone on the wifi gets no
    microphone at all over http://. A self-signed certificate is what turns
    that back on — the browser will warn once, because nothing vouches for
    this certificate but the machine that made it.

    Returns (certfile, keyfile) or None if openssl isn't available.
    """
    os.makedirs(CERT, exist_ok=True)
    cert, key = os.path.join(CERT, "cert.pem"), os.path.join(CERT, "key.pem")
    if os.path.isfile(cert) and os.path.isfile(key):
        return cert, key

    alt = "DNS:localhost,IP:127.0.0.1" + (",IP:" + ip if ip else "")
    cmd = ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
           "-keyout", key, "-out", cert,
           "-days", "825",                      # iOS refuses longer-lived certs
           "-subj", "/CN=goi-renshucho",
           "-addext", "subjectAltName=" + alt]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        for f in (cert, key):
            if os.path.isfile(f):
                os.remove(f)
        return None
    os.chmod(key, 0o600)
    return cert, key


def main():
    ap = argparse.ArgumentParser(description="Serve 語彙練習帳 and store its data on disk.")
    ap.add_argument("--host", default="127.0.0.1",
                    help="bind address (default 127.0.0.1; use 0.0.0.0 for LAN access)")
    ap.add_argument("--port", type=int, default=8788, help="port (default 8788)")
    ap.add_argument("--https", action="store_true",
                    help="serve over TLS with a self-signed certificate, so phones "
                         "on the LAN can use the microphone")
    ap.add_argument("--no-https", dest="no_https", action="store_true",
                    help="force plain HTTP even when binding to the network")
    ap.add_argument("--quiet", action="store_true",
                    help="skip the banner (SETUP.sh prints its own)")
    args = ap.parse_args()

    ensure_dirs()
    if not os.path.isfile(os.path.join(ROOT, "index.html")):
        sys.exit("index.html is not next to server.py — keep the exported files together.")

    ip = lan_ip() if args.host != "127.0.0.1" else ""
    # Binding to the network is pointless for this app without TLS, since the
    # microphone is unavailable on an insecure origin. Default it on.
    want_tls = args.https or (args.host != "127.0.0.1" and not args.no_https)
    pair = ensure_cert(ip) if want_tls else None
    scheme = "https" if pair else "http"

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    if pair:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(pair[0], pair[1])
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    if not args.quiet:
        # 0.0.0.0 is a bind address, not something you can type into a browser.
        print("語彙練習帳 — N2 vocabulary practice")
        print("  open    %s://localhost:%d" % (scheme, args.port))
        if args.host != "127.0.0.1" and ip:
            print("  phone   %s://%s:%d" % (scheme, ip, args.port))
        print("  data    %s" % DATA)
        if want_tls and not pair:
            print("  warn    couldn't make a certificate (openssl not found), so this is")
            print("          plain HTTP — phones on the LAN will have no microphone.")
        elif pair:
            print("  cert    self-signed; your phone will warn once, then remember")
        if args.host != "127.0.0.1":
            print("  note    bound to %s with no password — trusted networks only." % args.host)
        print("  stop    Ctrl-C\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Your data is in %s" % DATA)
        httpd.server_close()


if __name__ == "__main__":
    main()
