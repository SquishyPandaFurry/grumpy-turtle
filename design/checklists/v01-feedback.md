# v01 feedback — one animal talking

## Part A — what changed in this build
- [ ] Test call: `scripts/test-gateway.sh <connection_id>` on the Sprite gets a turtle-ish hello back from OpenRouter through the connector (no API key anywhere)
- [ ] Pond server runs as a Sprite service called `pond` on port 8080 (`sprite-env services get pond` shows it running)
- [ ] The page opens only from the private link `https://<sprite-url>/?key=…`; without the key (or with a wrong one) you get "Nothing here."
- [ ] Shelly the turtle (starter persona from personas.md) answers slowly, with "Ahh..." / "Now then...", max ~4 sentences
- [ ] The shared Rules block (`pond/animals/rules.md`) is kind, gentle and age-appropriate, and Shelly follows it (try "I'm sad today")
- [ ] Tell Shelly something worth keeping ("my favourite colour is green"): one line appears in `pond/memory/turtle.md`; small talk ("hi") adds nothing
- [ ] Ask Shelly about it in a later message: she remembers
- [ ] `pond/memory/`, `pond/secret_key.txt` are not in git (`git status` stays clean after chatting)
- [ ] Page is readable and easy to type into on the tablet (big text, Send button)
- [ ] Sleep/wake: leave the Sprite alone until it sleeps, then open the bookmarked link: the page loads within a few seconds and Shelly replies
- [ ] Note: Shelly only sees the current message plus her memory file, not the earlier chat on the page. Is that OK, or should she see the last few messages?

## Part B — every build
- [ ] Pond page opens from the bookmarked private link (and not without it)
- [ ] Each animal replies in character, kind and age-appropriate
- [ ] Something told to one animal is remembered next time, and not by the others
- [ ] After the Sprite has slept, the page wakes it and the server is running
- [ ] No API key anywhere on the Sprite or in the repo
- [ ] Real memory files not committed
- [ ] Works on the tablet

## Part C — anything else you noticed
