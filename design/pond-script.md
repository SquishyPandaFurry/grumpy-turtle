# Pond script

The core program. It doesn't think; it builds context for the model and tidies up afterwards.

## Agreed but not built
- Files:
  ```
  pond/animals/{turtle,capybara,hedgehog}.md
  pond/memory/{turtle,capybara,hedgehog}.md
  pond/pond_log.md
  pond/last_seen.txt
  ```
- `ask(animal, text)` flow:
  1. Hours since `last_seen`. If > 6h it's a wake-up: run gossip first, and tell the animal it just woke after N hours.
  2. Prompt = persona file + memory file + last ~10 lines of pond log + the message.
  3. Call the model through the OpenRouter **connector gateway** (no API key in code or on the Sprite).
  4. Second cheap call: "Anything worth remembering long-term? One short line, or NONE." Append if not NONE.
  5. Update `last_seen`, return reply.
- Gossip on wake-up: 3–4 alternating one-line exchanges between animals, appended to `pond_log.md`.
  Optionally push the most dramatic line via Pushover.
- If no animal is picked, a quick model call chooses who answers.
- Model is one config string, easy to swap. Pick a well-known model that follows instructions reliably.
- Gateway URL form: `https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/<path>` — confirm the
  exact OpenRouter path and connection ID in the Fly dashboard.

## Built

## Ideas (not agreed)
- Animals occasionally message first via Pushover ("Hedgehog refuses to come out until someone says sorry").
