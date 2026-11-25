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
- Chat history (agreed 2026-11-24, v01 feedback): the prompt also includes the last 10 messages of the
  current chat word for word. Older messages aren't dropped: they're rolled into a short running summary
  of the chat so far, which goes into the prompt too. Long-lasting facts still go to the memory file.
  The chat and its summary last for one visit: a reload starts a fresh chat, keeping only the memory file.
- Friendly greeting (agreed 2026-11-24, v01 feedback): when the page opens, the animal greets the child
  like a friend would, using what's in its memory file (e.g. asking about something he told it before),
  instead of the fixed "Hello there!".
- Gossip on wake-up: 3–4 alternating one-line exchanges between animals, appended to `pond_log.md`.
  Optionally push the most dramatic line via Pushover.
- If no animal is picked, a quick model call chooses who answers.
- Model is one config string, easy to swap. Pick a well-known model that follows instructions reliably.
- Gateway URL form: `https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/<path>` — confirm the
  exact OpenRouter path and connection ID in the Fly dashboard.

## Built
- v01: `ask(animal, text)` steps 2 (persona + memory + message, no pond log yet), 3 (gateway call) and 4 (memory line or NONE). No wake-up, gossip or last_seen yet. Model: `anthropic/claude-haiku-4.5` (`POND_MODEL`).

## Ideas (not agreed)
- OPEN QUESTION before v02 (raised in v01 feedback 2026-11-25): how does the chat (last 10 messages +
  running summary) work with three animals? Option A: one shared group chat, every animal sees the
  whole chat and replies are labelled with who spoke. Option B: a separate chat per animal card.
  Note for A: memory files stay per animal, but within one visit every animal would see what was
  said to the others, which bends "telling the turtle doesn't tell the hedgehog".
- Animals occasionally message first via Pushover ("Hedgehog refuses to come out until someone says sorry").
