# Web page

Small Python web server on the Sprite, reached at the Sprite's own URL (wakes the Sprite on request).

## Agreed but not built
- `GET /` — the page: three animal cards (my son's drawings), chat area, "pond news" panel showing the gossip log.
- `POST /talk` — `{animal, text}` → pond script → `{animal, reply, drawing?}`.
- Replies shown with the animal's picture next to them.
- Works well on a tablet.
- Chat history (agreed 2026-11-24, v01 feedback): the page keeps the current chat so the animal can see the last 10 messages plus a summary of older ones (see pond-script.md). A reload starts a fresh chat.
- Group "Pond" chat plus a private chat with each animal (agreed 2026-11-25, see pond-script.md). Tapping an animal card opens its private chat.
- Smaller text on phones (agreed 2026-11-25, v01 feedback): on narrow phone screens the messages are too big; shrink text there while the tablet keeps its big text.
- Opening greeting comes from the animal (friendly, using its memory) instead of the fixed "Hello there!".

## Built
- v01: basic one-animal chat page at `GET /?key=…`; `POST /talk` `{animal, text}` → `{animal, reply}` with `X-Pond-Key` header. No key → 404.
- v01: private via secret key in the link (pond/secret_key.txt on the Sprite).

- v02: 🌿 Pond card + one card per animal (emoji until the drawings), private chat per card, "Who answers?" chips in the Pond chat, greeting per chat, 📰 Pond news panel, smaller text under 600px, app pinned to the visible viewport so the tablet keyboard doesn't hide the top. `POST /greet` added.

- v03: while typing on a touch screen, header and cards fold into a slim bar (tap to unfold); the greeting refreshes the 📰 Pond news panel, with a dot for new gossip.

## Ideas (not agreed)
- Mockup to show my son before building.
- A pond background behind the chat (v01 feedback 2026-11-25, "for later"). Could fit with the Polish step that adds my son's drawings.
- Weather effects on the chat window (snow, rain, fog, etc.) matching the real weather (v01 feedback 2026-11-25, "for later"). Goes with the real-weather idea in personas.md.
