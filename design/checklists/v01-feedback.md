# v01 feedback — one animal talking

## Part A — what changed in this build
- [x] Test call: `scripts/test-gateway.sh <connection_id>` on the Sprite gets a turtle-ish hello back from OpenRouter through the connector (no API key anywhere)
  - Checked 2026-11-24: the gateway works (Shelly replies, memory call works by hand); no API key on the Sprite or in the repo.
- [x] Pond server runs as a Sprite service called `pond` on port 8080 (`sprite-env services get pond` shows it running)
- [x] The page opens only from the private link `https://<sprite-url>/?key=…`; without the key (or with a wrong one) you get "Nothing here."
  - Feedback (2026-11-24): yes, and a partial key is refused too.
- [x] Shelly the turtle (starter persona from personas.md) answers slowly, with "Ahh..." / "Now then...", max ~4 sentences
  - Feedback (2026-11-24): yes, replies are short, but a little too repetitive.
- [x] The shared Rules block (`pond/animals/rules.md`) is kind, gentle and age-appropriate, and Shelly follows it (try "I'm sad today")
  - Feedback (2026-11-24): yes.
- [~] Tell Shelly something worth keeping ("my favourite colour is green"): one line appears in `pond/memory/turtle.md`; small talk ("hi") adds nothing
  - Checked 2026-11-24: turtle.md has 2 lines incl. "Favourite colour is green.", but only 2 facts from ~16 messages. See bugs.md.
- [ ] Ask Shelly about it in a later message: she remembers
  - Feedback (2026-11-24): NO. She doesn't remember, not even within the same conversation.
- [x] `pond/memory/`, `pond/secret_key.txt` are not in git (`git status` stays clean after chatting)
  - Checked 2026-11-24: repo and Sprite checkout are clean.
- [ ] Page is readable and easy to type into on the tablet (big text, Send button)
  - Feedback (2026-11-24): mostly yes, but the on-screen keyboard pushes the top of the page away so the top message can't be read (bug).
- [x] Sleep/wake: leave the Sprite alone until it sleeps, then open the bookmarked link: the page loads within a few seconds and Shelly replies
  - Feedback (2026-11-24): yes.
- [x] Note: Shelly only sees the current message plus her memory file, not the earlier chat on the page. Is that OK, or should she see the last few messages?
  - Feedback (2026-11-24): she should see the last 10 messages, with older ones rolled into a running summary so context isn't lost. Agreed, queued for v02. A reload starts fresh, keeping only the memory file. Also agreed: a friendly greeting on page open that uses her memory.

## Part B — every build
- [x] Pond page opens from the bookmarked private link (and not without it) — yes (Part A)
- [ ] Each animal replies in character, kind and age-appropriate — Shelly only so far: yes, but a little repetitive
- [ ] Something told to one animal is remembered next time, and not by the others — not working reliably (bugs.md); only one animal so far
- [x] After the Sprite has slept, the page wakes it and the server is running — yes (Part A)
- [x] No API key anywhere on the Sprite or in the repo — yes (checked)
- [x] Real memory files not committed — yes (checked)
- [ ] Works on the tablet — mostly; keyboard hides the top message (bugs.md)

## Part C — anything else you noticed
- 2026-11-25: Shelly has no sense of time of day; it's always warm and sunny on her rock and that's all she talks about. Wants more variety and answers that fit the context. → Agreed: time/day/season in the prompt + wider persona topics and no repeating (queued v02). Real weather stays an idea.
- 2026-11-25: on a phone the text is too big, so messages are gigantic. → Agreed: smaller text on phone screens only, tablet keeps big text (queued v02).
- 2026-11-25: the screen could do with a little background, for later. → Idea in web-page.md (not queued).
- 2026-11-25: later, weather effects on the chat window (snow, rain, fog). → Idea in web-page.md, alongside real weather (not queued).
- 2026-11-25: think about how this chat style works with multiple characters. → Decided: a "Pond" group chat that all animals see, plus a private chat with each animal (queued v02).
