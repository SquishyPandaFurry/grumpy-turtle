"""Local smoke test with a fake gateway (no network, no credits).
Run:  python3 tests/smoke_test.py
"""
import json, os, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
seen = []

class FakeGateway(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        seen.append((self.path, dict(self.headers), body))
        system = body["messages"][0]["content"]
        if "help a pond animal remember" in system:
            text = "His favourite colour is green" if "green" in body["messages"][1]["content"] else "NONE"
        else:
            text = "Ahh... hello, little one..."
        out = json.dumps({"choices": [{"message": {"content": text}}]}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(out))); self.end_headers()
        self.wfile.write(out)

def main():
    gw = ThreadingHTTPServer(("127.0.0.1", 0), FakeGateway)
    threading.Thread(target=gw.serve_forever, daemon=True).start()
    work = Path(tempfile.mkdtemp()); shutil.copytree(ROOT / "pond", work / "pond")
    env = dict(os.environ, POND_PORT="18080", POND_KEY="testkey",
               POND_GATEWAY_BASE=f"http://127.0.0.1:{gw.server_port}/api/v1")
    srv = subprocess.Popen([sys.executable, "server.py"], cwd=work / "pond", env=env)
    base = "http://127.0.0.1:18080"
    try:
        for _ in range(50):
            try: urllib.request.urlopen(base + "/health"); break
            except OSError: time.sleep(0.1)
        def status(req):
            try: return urllib.request.urlopen(req).status
            except urllib.error.HTTPError as e: return e.code
        def talk(text, key="testkey"):
            req = urllib.request.Request(base + "/talk", data=json.dumps({"animal": "turtle", "text": text}).encode(),
                                         headers={"Content-Type": "application/json", "X-Pond-Key": key})
            return req
        assert status(base + "/") == 404, "page must need the key"
        assert status(base + "/?key=wrong") == 404
        page = urllib.request.urlopen(base + "/?key=testkey").read().decode()
        assert "Shelly the turtle" in page and "__ANIMALS__" not in page
        assert status(talk("hi", key="wrong")) == 404, "talk must need the key"
        r = json.load(urllib.request.urlopen(talk("hello turtle")))
        assert r["reply"].startswith("Ahh"), r
        mem = work / "pond/memory/turtle.md"
        assert not mem.exists(), "small talk must not be remembered"
        json.load(urllib.request.urlopen(talk("my favourite colour is green")))
        assert mem.read_text() == "- His favourite colour is green\n", mem.read_text()
        json.load(urllib.request.urlopen(talk("what's my favourite colour?")))
        last_prompt = [b for p, h, b in seen if "help a pond animal" not in b["messages"][0]["content"]][-1]
        sysmsg = last_prompt["messages"][0]["content"]
        assert "favourite colour is green" in sysmsg and "Always be kind" in sysmsg
        assert "(shared rules block)" not in sysmsg
        assert all("Authorization" not in h for _, h, _ in seen), "no auth header to the gateway"
        assert all(p == "/api/v1/chat/completions" for p, _, _ in seen)
        bad = urllib.request.Request(base + "/talk", data=json.dumps({"animal": "../rules", "text": "x"}).encode(),
                                     headers={"X-Pond-Key": "testkey"})
        assert status(bad) == 400
        print("smoke test: all checks passed")
    finally:
        srv.terminate(); gw.shutdown()

if __name__ == "__main__":
    main()
