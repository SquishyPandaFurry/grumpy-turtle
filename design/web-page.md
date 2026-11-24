# Web page

Small Python web server on the Sprite, reached at the Sprite's own URL (wakes the Sprite on request).

## Agreed but not built
- `GET /` — the page: three animal cards (my son's drawings), chat area, "pond news" panel showing the gossip log.
- `POST /talk` — `{animal, text}` → pond script → `{animal, reply, drawing?}`.
- Replies shown with the animal's picture next to them.
- Works well on a tablet.

## Built
- v01: basic one-animal chat page at `GET /?key=…`; `POST /talk` `{animal, text}` → `{animal, reply}` with `X-Pond-Key` header. No key → 404.
- v01: private via secret key in the link (pond/secret_key.txt on the Sprite).

## Ideas (not agreed)
- Mockup to show my son before building.
