# v02 feedback — the full pond

## Part A — what changed in this build
- [ ] Three animals: Shelly the turtle, Coco the capybara and Prickles the hedgehog. Coco and Prickles are draft names and personas from personas.md, ready for the session with your son (rename by editing the first line of `pond/animals/capybara.md` / `hedgehog.md`). Each replies in character, kind and age-appropriate.
- [ ] Cards along the top: 🌿 Pond, then one card per animal. Tapping an animal opens a private chat with just that animal.
- [ ] Pond group chat: all three animals see the whole chat, labelled with who spoke. "Who answers?" chips under the chat: Anyone (the pond picks; saying an animal's name picks that one) or a chosen animal.
- [ ] Private chats stay private: tell Prickles something in her chat, then ask Shelly in hers. Shelly shouldn't know it (memory is per animal too).
- [ ] Chat history: each chat remembers what was said this visit (last 10 messages word for word, older ones as a short summary). Try telling Shelly something, chatting for a while, then asking about it. A reload starts fresh chats, but the memory files stay.
- [ ] Friendly greeting: each chat opens with a hello from the animal, asking about something it remembers about him (no more fixed "Hello there!"). Pond chat is greeted by a random animal.
- [ ] Time of day: the animals know the UK day, time, season and whether it's dark (e.g. Wednesday after school, dark winter evening, bedtime).
- [ ] More variety: each persona has a wider list of pond life (frogs, rain, ducks, stars, leaves, ice…), answers what he said first, and avoids repeating the topic or opening it just used. Shelly's "warm sunny rock" should come up much less.
- [ ] Pond news: the 📰 button shows the last lines of `pond/pond_log.md` ("All quiet in the pond today" while it's empty). The animals also see the last 10 lines. Gossip that fills it comes in v03.
- [ ] Phone: smaller text, chips and cards on phone-sized screens; the tablet keeps the big text.
- [ ] Bug fix (tablet keyboard): with the keyboard open, the header, cards and latest message stay on screen.
- [ ] Bug fix (Shelly remembering): tell Shelly "my favourite colour is green", then ask her in the same chat and again after a reload. The service log now shows a `memory <animal>: saved / nothing (model said …)` line for every message, and any memory error.

## Part B — every build
- [ ] Pond page opens from the bookmarked private link (and not without it)
- [ ] Each animal replies in character, kind and age-appropriate
- [ ] Something told to one animal is remembered next time, and not by the others
- [ ] After the Sprite has slept, the page wakes it and the server is running
- [ ] No API key anywhere on the Sprite or in the repo
- [ ] Real memory files not committed
- [ ] Works on the tablet

## Part C — anything else you noticed
