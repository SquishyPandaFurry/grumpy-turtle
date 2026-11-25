"""The pond web server. Python standard library only.

GET  /?key=SECRET   the chat page
POST /talk          {"visit": "...", "room": "pond"|"turtle"|..., "animal": "" or id, "text": "..."}
POST /greet         {"visit": "...", "room": ...}  -> the animal's hello for that chat
(both POSTs need header X-Pond-Key: SECRET; they answer {"animal", "name", "face", "reply"})
GET  /health        "ok" (no key needed, says nothing about the pond)

Anything without the right key gets a plain 404, so strangers can't chat or spend credits.
"""
import hmac
import json
import os
import re
import secrets
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pond

HERE = Path(__file__).resolve().parent
KEY_FILE = HERE / "secret_key.txt"  # gitignored, created on first start
PORT = int(os.environ.get("POND_PORT", "8080"))
MAX_BODY = 4096
VISIT_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")


def load_key():
    if os.environ.get("POND_KEY"):
        return os.environ["POND_KEY"]
    if not KEY_FILE.exists():
        KEY_FILE.write_text(secrets.token_urlsafe(24) + "\n")
        KEY_FILE.chmod(0o600)
    return KEY_FILE.read_text().strip()


KEY = load_key()


def key_ok(given):
    return bool(given) and hmac.compare_digest(given.encode(), KEY.encode())


class Handler(BaseHTTPRequestHandler):
    server_version = "pond"
    sys_version = ""

    def log_message(self, fmt, *args):
        # Never log the query string (it holds the key).
        path = urlparse(self.path).path
        sys.stderr.write(f"{self.command} {path} {args[1] if len(args) > 1 else ''}\n")

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(data)

    def _not_found(self):
        self._send(404, "Nothing here.", "text/plain")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            return self._send(200, "ok", "text/plain")
        if url.path == "/":
            key = parse_qs(url.query).get("key", [""])[0]
            if not key_ok(key):
                return self._not_found()
            page = (HERE / "static" / "index.html").read_text(encoding="utf-8")
            page = page.replace("__ANIMALS__", json.dumps(pond.animal_info()))
            page = page.replace("__NEWS__", json.dumps(pond.read_pond_log()))
            return self._send(200, page, "text/html")
        self._not_found()

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/talk", "/greet") or not key_ok(self.headers.get("X-Pond-Key", "")):
            return self._not_found()
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self._send(400, json.dumps({"error": "Message too long."}))
        try:
            req = json.loads(self.rfile.read(length))
            visit = str(req.get("visit") or "default")
            room = str(req.get("room") or req.get("animal") or "")
            animal = str(req.get("animal") or "")
            text = str(req.get("text", ""))
        except (ValueError, AttributeError):
            return self._send(400, json.dumps({"error": "Bad request."}))
        animals = pond.list_animals()
        if (not VISIT_RE.fullmatch(visit) or room not in animals + [pond.POND_ROOM]
                or (animal and animal not in animals) or (path == "/talk" and not text.strip())):
            return self._send(400, json.dumps({"error": "Bad request."}))
        try:
            if path == "/greet":
                who, reply = pond.greet(visit, room)
            else:
                who, reply = pond.ask(animal or None, text, visit=visit, room=room)
        except pond.PondError as e:
            sys.stderr.write(f"pond error: {e}\n")
            return self._send(502, json.dumps({"error": "The pond is a bit sleepy. Try again in a moment."}))
        self._send(200, json.dumps({"animal": who, "name": pond.short_name(who),
                                    "face": pond.face(who), "reply": reply}))


def main():
    print(f"The pond is listening on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
