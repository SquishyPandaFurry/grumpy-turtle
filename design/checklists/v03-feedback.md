# Build feedback checklist

## Part A — what changed in this build
v03, PR #5, live 2026-11-26.
- [x] The animals are called Rocky, Ferdinand and Colin everywhere
  - Feedback (2026-11-26): yes.
- [~] In the Pond chat they sound like three different animals and sometimes disagree or tease
  - Feedback (2026-11-26): sort of different, but all stuck in a constant reassuring state: every reply turns back to the child with a question or pep talk ("You'll do fine", "Something fun, I hope!") and they rarely react to each other. It should be a friendly chat at the pond: the animals talk among themselves and have their own little dramas, and he joins in. Colin's greeting also assumed "trouble sleeping again". Bug, queued v04 (bugs.md).
- [x] In a private chat, an animal knows what was said in the Pond chat this visit
  - Feedback (2026-11-26): seems good.
- [x] An animal does NOT know what you told another animal in its private chat
  - Feedback (2026-11-26): yes.
- [~] In the evening they follow what you talk about and don't keep going on about bedtime
  - Feedback (2026-11-27): bedtime no longer reported, but the same fixation moved: next morning every greeting asked about kickboxing and school, the only things he'd mentioned. Bug, queued v04 (bugs.md).
- [x] On the tablet, the header and cards fold into a slim bar while typing (tap the bar to get them back)
  - Feedback (2026-11-27): fine on the real tablet.
- [x] After 6+ hours away, 📰 Pond news has new gossip (with a dot) and the greeting mentions missing you
  - Feedback (2026-11-27): all good (gossip after 13h on 2026-11-26 19:59). The 2026-11-27 06:17 wake-up gossip failed (out of credit) and was lost: bug, queued v04.
- [x] Later chats sometimes carry on from the gossip or earlier pond events
  - Feedback (2026-11-27): good, it knew about Colin's beetles from yesterday.

## Part B — every build
- [x] Pond page opens from the bookmarked private link (and not without it) — yes (2026-11-26)
- [x] Each animal replies in character, kind and age-appropriate — yes (2026-11-26)
- [x] Something told to one animal is remembered next time, and not by the others — yes (2026-11-26)
- [x] After the Sprite has slept, the page wakes it and the server is running — yes (2026-11-26)
- [x] No API key anywhere on the Sprite or in the repo — repo checked 2026-11-26: no key (Sprite not re-checked)
- [x] Real memory files not committed — checked 2026-11-26: no memory files or secret_key.txt in git
- [x] Works on the tablet — yes (2026-11-26); keyboard fold fine too (2026-11-27)

## Part C — anything else you noticed
- Feedback (2026-11-27): "Morning everyone" in the Pond chat gets only one reply. It should know when he's talking to the whole pond (it already gets it right when he answers one animal). Agreed, queued v04: "everyone" answers (pond-script.md / web-page.md).
- 2026-11-27 06:18: the page said "The pond is a bit sleepy" after the morning hellos. Cause: OpenRouter credit ran out (402 from the gateway in /.sprite/logs/services/pond.log); credit added, no restart needed. OpenRouter has no top-up by default (an auto top-up option exists in its credits settings). Running out looks the same as a hiccup: bug, queued v04.
