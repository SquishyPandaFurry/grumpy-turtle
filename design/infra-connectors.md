# Infrastructure and connectors

## Agreed but not built
- Fly.io account on the new Free plan ($5/month usage; up to 3 Machines and 3 Sprites). Card required.
- OpenRouter account with a **credit limit** set.
- Pushover connector (optional) for pings to my phone.
- Code in a GitHub repo; the Sprite pulls `main`.

## Built
- v01: Sprite `pond`, URL https://pond-b6vlj.sprites.app (auth public; the key in the link guards it).
- v01: OpenRouter connector `rke83IBGUxHfM8AFs_OVJg`, label `pond-sprite`. Gateway base `https://api.sprites.dev/v1/gateway/openrouter/<id>/v1` (not `/api/v1`).
- v01: service `pond` (`scripts/setup-service.sh`), python3 pond/server.py on port 8080. Wakes with the Sprite: after a cold sleep the same process resumes.
- v01: `.gitignore` covers memory/, pond_log.md, last_seen.txt, secret_key.txt.

## Ideas (not agreed)
