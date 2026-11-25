# The Pond

Three animal friends who live in a pond on a Fly.io Sprite. A child chats with them on a web page.
Built for Fly.io's Hacksgiving 2026. Design docs live in `design/` (start with `design/00-project-summary.md`).

Plain Python standard library, one small web server, plain files. No database, no API keys:
model calls go through the Sprites connector gateway.

## Layout
```
pond/server.py        web server (GET /?key=…, POST /talk, POST /greet, GET /health)
pond/pond.py          ask()/greet(): persona + memory + UK time + pond log + chat (last 10 + summary) → model,
                      then a cheap "anything to remember?" call (logged to the service log)
pond/animals/*.md     personas (rules.md is the shared Rules block, inserted into every persona)
pond/static/          the page
pond/memory/          per-animal memory (runtime data, not in git)
pond/pond_log.md      pond news, last 10 lines go in every prompt (runtime data, not in git)
pond/secret_key.txt   the key in the private link (created on first start, not in git)
scripts/              test-gateway.sh, setup-service.sh
tests/smoke_test.py   local test with a fake gateway
```

## On the Sprite
```bash
git clone <repo> the-pond && cd the-pond
scripts/test-gateway.sh <openrouter_connection_id>     # one test call
scripts/setup-service.sh <openrouter_connection_id>    # self-starting service on port 8080
sprite url update --auth public   # (from your laptop; check `--help`) so the tablet can reach it; the key still guards it
```
Open `https://<your-sprite-url>/?key=<key printed by setup-service.sh>` and bookmark it.

Service commands: `sprite-env services list | get pond | restart pond`, logs in `/.sprite/logs/services/pond.log`.

## Test locally
`python3 tests/smoke_test.py`
