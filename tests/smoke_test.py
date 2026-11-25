"""Local smoke test with a fake gateway (no network, no credits).
Run:  python3 tests/smoke_test.py
"""
import json, os, shutil, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
seen = []


def kind(body):
    system = body["messages"][0]["content"]
    if "help a pond animal remember" in system: return "memory"
    if "running summary" in system: return "summary"
    if "pick who should answer" in system: return "choose"
    if "opened the chat" in body["messages"][-1]["content"]: return "greet"
    return "chat"


class FakeGateway(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        seen.append((self.path, dict(self.headers), body))
        k, user = kind(body), body["messages"][-1]["content"]
        if "please rate limit" in user and not getattr(FakeGateway, "limited", False):
            FakeGateway.limited = True
            out = b'{"error":{"message":"Rate limit exceeded","code":429}}'
            self.send_response(429); self.send_header("Content-Length", str(len(out))); self.end_headers()
            self.wfile.write(out); return
        system = body["messages"][0]["content"]
        if k == "memory":
            said = user.split("Child said:")[1]
            text = "His favourite colour is green" if "green" in said else "NONE"
        elif k == "summary":
            text = "They talked about frogs and colours."
        elif k == "choose":
            text = "hedgehog"
        elif k == "greet":
            text = "Hello again, friend!"
        else:
            name = system.splitlines()[0].lstrip("# ").split(" the ")[0]
            text = f"{name}: Ahh... hello, little one..."
        out = json.dumps({"choices": [{"message": {"content": text}}]}).encode()
        self.send_response(200); self.send_header("Content-Length", str(len(out))); self.end_headers()
        self.wfile.write(out)


def check_time_of_day():
    sys.path.insert(0, str(ROOT / "pond"))
    import pond
    # 25 Nov 2026 16:00 UTC = 16:00 GMT, Wednesday, after school, dark, autumn
    s = pond.time_of_day(datetime(2026, 11, 25, 16, 30, tzinfo=timezone.utc))
    assert "Wednesday" in s and "16:30" in s and "after school" in s and "autumn" in s and "dark" in s, s
    # 1 Jul 2026 07:30 UTC = 08:30 BST, morning, daylight, summer
    s = pond.time_of_day(datetime(2026, 7, 1, 7, 30, tzinfo=timezone.utc))
    assert "08:30" in s and "morning" in s and "summer" in s and "daylight" in s, s
    # Saturday 19:30 GMT in January: bedtime, weekend, winter
    s = pond.time_of_day(datetime(2026, 1, 3, 19, 30, tzinfo=timezone.utc))
    assert "Saturday" in s and "weekend" in s and "bedtime" in s and "winter" in s, s


def check_clean_fact():
    import pond
    assert pond.clean_fact("Favourite colour is green.", "turtle") == "Favourite colour is green."
    assert pond.clean_fact("- His dog is called Biscuit", "turtle") == "His dog is called Biscuit"
    for bad in ("NONE", "None", "none.", "Nothing new.",
                "No new lasting facts to remember. The child only asked a question, and the animal's reply",
                "The animal's name is Prickles.", "Coco the pond animal loves oranges."):
        assert pond.clean_fact(bad, "hedgehog") is None, bad
    assert pond.clean_fact("Prickles is his favourite", "hedgehog") is None


def main():
    check_time_of_day()
    check_clean_fact()
    gw = ThreadingHTTPServer(("127.0.0.1", 0), FakeGateway)
    threading.Thread(target=gw.serve_forever, daemon=True).start()
    work = Path(tempfile.mkdtemp()); shutil.copytree(ROOT / "pond", work / "pond")
    (work / "pond/pond_log.md").write_text("- Hedgehog found a shiny button.\n")
    env = dict(os.environ, POND_PORT="18080", POND_KEY="testkey",
               POND_GATEWAY_BASE=f"http://127.0.0.1:{gw.server_port}/api/v1", POND_RETRY_WAITS="0.2")
    srv = subprocess.Popen([sys.executable, "server.py"], cwd=work / "pond", env=env,
                           stderr=open(work / "server.log", "w"))
    base = "http://127.0.0.1:18080"
    try:
        for _ in range(50):
            try: urllib.request.urlopen(base + "/health"); break
            except OSError: time.sleep(0.1)

        def status(req):
            try: return urllib.request.urlopen(req).status
            except urllib.error.HTTPError as e: return e.code

        def req(path, body, key="testkey"):
            return urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                          headers={"Content-Type": "application/json", "X-Pond-Key": key})

        def talk(text, room="turtle", animal="", visit="v1", key="testkey"):
            return req("/talk", {"visit": visit, "room": room, "animal": animal, "text": text}, key)

        def call(r): return json.load(urllib.request.urlopen(r))

        def chat_prompts(): return [b for _, _, b in seen if kind(b) == "chat"]

        # Private link
        assert status(base + "/") == 404, "page must need the key"
        assert status(base + "/?key=wrong") == 404
        page = urllib.request.urlopen(base + "/?key=testkey").read().decode()
        for name in ("Shelly", "Coco", "Prickles"):
            assert name in page, name
        assert "__ANIMALS__" not in page and "__NEWS__" not in page and "shiny button" in page
        assert status(talk("hi", key="wrong")) == 404, "talk must need the key"
        assert status(req("/greet", {"visit": "v1", "room": "pond"}, key="wrong")) == 404

        # Greeting uses memory and is only made once per chat per visit
        (work / "pond/memory").mkdir()
        (work / "pond/memory/turtle.md").write_text("- He has a dog called Biscuit\n")
        g = call(req("/greet", {"visit": "v1", "room": "turtle"}))
        assert g["animal"] == "turtle" and g["reply"] == "Hello again, friend!", g
        greet_prompt = [b for _, _, b in seen if kind(b) == "greet"][-1]["messages"][0]["content"]
        assert "Biscuit" in greet_prompt and "In the child's world (UK)" in greet_prompt
        n = len(seen); call(req("/greet", {"visit": "v1", "room": "turtle"})); assert len(seen) == n

        # Private chat: reply, name prefix stripped, small talk not remembered
        r = call(talk("hello turtle"))
        assert r["animal"] == "turtle" and r["reply"].startswith("Ahh"), r
        mem = work / "pond/memory/turtle.md"
        assert mem.read_text().count("\n") == 1, "small talk must not be remembered"
        call(talk("my favourite colour is green"))
        assert "His favourite colour is green" in mem.read_text(), mem.read_text()
        call(talk("what's my favourite colour?"))
        sysmsg = chat_prompts()[-1]["messages"][0]["content"]
        user = chat_prompts()[-1]["messages"][1]["content"]
        assert "favourite colour is green" in sysmsg and "Always be kind" in sysmsg
        assert "(shared rules block)" not in sysmsg and "shiny button" in sysmsg
        assert "Answer what the child actually said first" in sysmsg
        assert "Child: my favourite colour is green" in user, "chat history must be in the prompt"
        log = (work / "server.log").read_text()
        assert "memory turtle: saved" in log and "memory turtle: nothing" in log, log

        # Memory is per animal
        assert not (work / "pond/memory/hedgehog.md").exists()
        call(talk("hello hedgehog", room="hedgehog"))
        hsys = chat_prompts()[-1]["messages"][0]["content"]
        assert "Prickles" in hsys and "green" not in hsys and "Biscuit" not in hsys

        # Private chats are private
        assert "favourite colour" not in chat_prompts()[-1]["messages"][1]["content"]

        # Pond group chat: auto-choose, picked animal, name mentioned
        r = call(talk("tell me a story", room="pond"))
        assert r["animal"] == "hedgehog" and r["name"] == "Prickles", r  # fake chooser says hedgehog
        r = call(talk("and you?", room="pond", animal="capybara"))
        assert r["animal"] == "capybara", r
        n_choose = sum(kind(b) == "choose" for _, _, b in seen)
        r = call(talk("Shelly, are you there?", room="pond"))
        assert r["animal"] == "turtle", r
        assert sum(kind(b) == "choose" for _, _, b in seen) == n_choose, "a named animal needs no choose call"
        user = chat_prompts()[-1]["messages"][1]["content"]
        assert "Prickles: Ahh" in user and "Coco: Ahh" in user, "group chat is labelled with who spoke"
        assert "Pond group chat" in chat_prompts()[-1]["messages"][0]["content"]

        # Last 10 + running summary
        for i in range(10):
            call(talk(f"frog number {i}", visit="v2"))
        user = chat_prompts()[-1]["messages"][1]["content"]
        sysmsg = chat_prompts()[-1]["messages"][0]["content"]
        assert any(kind(b) == "summary" for _, _, b in seen), "older messages must be summarised"
        assert "They talked about frogs" in sysmsg
        assert user.count("\nChild:") + user.startswith("Last messages in this chat:\nChild:") <= 6
        assert "frog number 0" not in user and "frog number 8" in user and "frog number 4" in user

        # A new visit starts fresh
        call(talk("hello", visit="v3"))
        assert "(nothing yet)" in chat_prompts()[-1]["messages"][1]["content"]

        # A rate limit (429) is retried once
        r = call(talk("please rate limit me", visit="v4"))
        assert r["reply"].startswith("Ahh") and FakeGateway.limited, r
        assert "rate limited, retrying" in (work / "server.log").read_text()

        # Gateway use
        assert all("Authorization" not in h for _, h, _ in seen), "no auth header to the gateway"
        assert all(p == "/api/v1/chat/completions" for p, _, _ in seen)

        # Bad input
        assert status(req("/talk", {"room": "../rules", "text": "x"})) == 400
        assert status(talk("x", room="pond", animal="shark")) == 400
        assert status(talk("x", visit="../../etc")) == 400
        assert status(talk("   ")) == 400
        print("smoke test: all checks passed")
    finally:
        srv.terminate(); gw.shutdown()


if __name__ == "__main__":
    main()
