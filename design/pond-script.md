# Pond script

The core program. It doesn't think; it builds context for the model and tidies up afterwards.

## Agreed but not built
- "Everyone" answers (agreed 2026-11-27, v03 feedback; queued v04): in the Pond chat, a message to the whole pond ("Morning everyone") gets replies from 2-3 animals in turn, each seeing the replies before it, instead of the one-animal answer agreed for v02. The chooser gets a third answer, "all"; a named or picked animal still answers alone. 2-3 model calls for those messages.
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
- Group chat + private chats (agreed 2026-11-25, v01 feedback): a "Pond" group chat where all three
  animals see the whole chat (labelled with who spoke) and whoever is picked or auto-chosen answers,
  plus a private chat with each animal. Each chat keeps its own last-10 + summary history. Private
  chats are seen only by that animal; anything said in the Pond chat is seen by all three.
  Memory files stay per animal (facts are saved to the animal that replied).
- Private chats know the pond (agreed 2026-11-25, v02 feedback): in a private chat, the animal knows
  the other two exist (from its persona's "The others") and can see what was said in the Pond group chat
  (its recent messages + summary). It never sees another animal's private chat. Goes with character
  knowledge (personas.md). Re-test private-chat privacy once this is built: in v02 the check passed
  only because the animals didn't know about each other at all.
- Gossip on wake-up: 3–4 alternating one-line exchanges between animals, appended to `pond_log.md`.
  Optionally push the most dramatic line via Pushover.
- If no animal is picked, a quick model call chooses who answers.
- Model is one config string, easy to swap. Pick a well-known model that follows instructions reliably.
- Gateway URL form: `https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/<path>` — confirm the
  exact OpenRouter path and connection ID in the Fly dashboard.

## Built
- v01: `ask(animal, text)` steps 2 (persona + memory + message, no pond log yet), 3 (gateway call) and 4 (memory line or NONE). No wake-up, gossip or last_seen yet. Model: `anthropic/claude-haiku-4.5` (`POND_MODEL`).

- v02: prompt = persona + memory + UK time + last 10 pond-log lines + chat (last 10 messages + running summary, per visit and chat, kept in server memory). Pond group chat + private chats; auto-choose (named animal, else a quick model call). `greet()` opens each chat from memory. Memory call logs every answer; non-facts and facts about the animal are dropped. 429s retried (3s, 8s). Not yet: wake-up, gossip, last_seen.

- v03: private chats see the other animals and this visit's Pond chat (never another private chat; checked on the Sprite); Pond prompt says don't echo the last speaker, temperature per animal (0.6 / 0.85 / 1.0); memory call answers CHILD + POND in one call; `last_seen.txt` and wake-up after 6h (`POND_WAKE_HOURS`): 4 lines of gossip into `pond_log.md`, a short gist call saves what happened to each pond memory, the greeting mentions the wake-up. Not yet: Pushover.

- v04: "Everyone" answers: the chooser can answer `all`, and "everyone / all of you / hi all", or naming two animals, skip the choose call; 2-3 animals (the chip: all 3) reply in turn, each told what the others just said; their memory calls run in the background. Pond chat prompt: a friendly chat among the animals, not a check-up; "be a friend, not a carer", few questions. Greetings: at most one per visit brings up one thing he said (picked in code, skipping recently used facts), the rest open with their own news. Wake-up: `last_seen.txt` moves on only once gossip worked (retry every 5 min, `POND_GOSSIP_RETRY_MINUTES`). 402 / credit errors raise OutOfCredit: logged as `OUT OF CREDIT` with the top-up link.

## Ideas (not agreed)
- Animals occasionally message first via Pushover ("Hedgehog refuses to come out until someone says sorry").
