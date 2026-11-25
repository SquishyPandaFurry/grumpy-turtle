# v02 feedback — the full pond

## Part A — what changed in this build
- [x] Three animals: Shelly the turtle, Coco the capybara and Prickles the hedgehog. Coco and Prickles are draft names and personas from personas.md, ready for the session with your son (rename by editing the first line of `pond/animals/capybara.md` / `hedgehog.md`). Each replies in character, kind and age-appropriate.
  - Feedback (2026-11-25): in character, so that works. Final names from my son: Rocky the turtle, Ferdinand the capybara, Colin the hedgehog (queued v03).
- [x] Cards along the top: 🌿 Pond, then one card per animal. Tapping an animal opens a private chat with just that animal.
  - Feedback (2026-11-25): yes.
- [x] Pond group chat: all three animals see the whole chat, labelled with who spoke. "Who answers?" chips under the chat: Anyone (the pond picks; saying an animal's name picks that one) or a chosen animal.
  - Feedback (2026-11-25): yes. But it's funny that in the private chats they don't even know each other: they should know about each other and the Pond conversation there, just not across private chats (queued v03).
- [~] Private chats stay private: tell Prickles something in her chat, then ask Shelly in hers. Shelly shouldn't know it (memory is per animal too).
  - Feedback (2026-11-25): passes, but only technically, because the animals don't know each other at all. Re-test once v03 lets private chats see the other animals and the Pond chat.
- [x] Chat history: each chat remembers what was said this visit (last 10 messages word for word, older ones as a short summary). Try telling Shelly something, chatting for a while, then asking about it. A reload starts fresh chats, but the memory files stay.
  - Feedback (2026-11-25): it remembered green from last time.
- [x] Friendly greeting: each chat opens with a hello from the animal, asking about something it remembers about him (no more fixed "Hello there!"). Pond chat is greeted by a random animal.
  - Feedback (2026-11-25): yes.
- [x] Time of day: the animals know the UK day, time, season and whether it's dark (e.g. Wednesday after school, dark winter evening, bedtime).
  - Feedback (2026-11-25): yes, they know it. But see the next item: it takes over the chat.
- [ ] More variety: each persona has a wider list of pond life (frogs, rain, ducks, stars, leaves, ice…), answers what he said first, and avoids repeating the topic or opening it just used. Shelly's "warm sunny rock" should come up much less.
  - Feedback (2026-11-25): the answers vary, but the context is always the same: five chats about hot chocolate or oranges and it always comes back to bedtime and sleeping because it's late. Bug, queued v03 (bugs.md).
- [x] Pond news: the 📰 button shows the last lines of `pond/pond_log.md` ("All quiet in the pond today" while it's empty). The animals also see the last 10 lines. Gossip that fills it comes in v03.
  - Feedback (2026-11-25): yes.
- [x] Phone: smaller text, chips and cards on phone-sized screens; the tablet keeps the big text.
  - Feedback (2026-11-25): yes.
- [~] Bug fix (tablet keyboard): with the keyboard open, the header, cards and latest message stay on screen.
  - Feedback (2026-11-25): yes, but the keyboard still takes half the screen. Bug, queued v03: fold header and cards while typing (bugs.md).
- [x] Bug fix (Shelly remembering): tell Shelly "my favourite colour is green", then ask her in the same chat and again after a reload. The service log now shows a `memory <animal>: saved / nothing (model said …)` line for every message, and any memory error.
  - Feedback (2026-11-25): works (green remembered on a new visit). Nothing to add.

## Sprite test (2026-11-25, test copy on port 8081, live pond untouched)
- Greetings, private chats, the Pond group chat (auto-choose, named animal, picked animal) and UK time all worked with real replies.
- Shelly remembered "green" later in the same chat, and again on a new visit from her memory file.
- The first run hit OpenRouter's limit for new accounts (20 model calls a minute; each message uses 2–3 calls). The fix: a rate-limited call is retried after 3s and then 8s. Two memory bugs were also fixed: an explanation was saved as a fact, and a fact about the animal was saved instead of one about the child. On the second run a "(none)" answer was saved, which is now fixed and covered by the local test.

## Part B — every build
- [x] Pond page opens from the bookmarked private link (and not without it) — yes, used for all of the above
- [x] Each animal replies in character, kind and age-appropriate — yes (Part A)
- [~] Something told to one animal is remembered next time, and not by the others — remembered yes; "not by the others" only technically (Part A)
- [ ] After the Sprite has slept, the page wakes it and the server is running — not checked yet
- [x] No API key anywhere on the Sprite or in the repo — repo checked 2026-11-25: no key (Sprite not re-checked in this thread)
- [x] Real memory files not committed — checked 2026-11-25: no memory files or secret_key.txt in git
- [~] Works on the tablet — yes, but the keyboard leaves half a screen (bugs.md)

## Part C — anything else you noticed
