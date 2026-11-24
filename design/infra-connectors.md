# Infrastructure and connectors

## Agreed but not built
- Fly.io account on the new Free plan ($5/month usage; up to 3 Machines and 3 Sprites). Card required.
- One Sprite named e.g. `pond`, holding code and data.
- OpenRouter connector set up in the Fly dashboard (Sprites › Connectors), access granted only to the pond Sprite.
- OpenRouter account with a **credit limit** set.
- Pushover connector (optional) for pings to my phone.
- Pond server runs as a service that starts itself; test early that it comes back after the Sprite sleeps.
- Code in a GitHub repo; the Sprite pulls `main`.
- Keep my son's real memory files out of the repo (`.gitignore` the `memory/` and `pond_log.md` data).

## Built

## Ideas (not agreed)
