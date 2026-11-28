# The Pond — project summary

A personal agent for Fly.io's Hacksgiving 2026 (23–29 Nov 2026, submissions close midnight PST Sun 29 Nov = 08:00 Mon 30 Nov UK).
Aimed mainly at the **Weird Uncle Award** ($1,000, strangest agent).

Three animal characters live together in a "pond" on a Fly.io Sprite. My son chats with them on a web page.
Each has its own personality and its own memory. They gossip while he's away (generated on wake-up),
and Shelly the turtle draws wobbly LOGO-style turtle-graphics pictures.

- 🐢 Turtle — slow, old, remembers everything, the artist (turtle graphics)
- 🦫 Capybara — chilled, friends with everyone, fetches outside news via connectors
- 🦔 Hedgehog — prickly, dramatic, curls up when worried, secretly kind

Names, ages, foods and quirks are chosen by my son (see `personas.md`).

## Hackathon rules that matter
- Must run on a Fly.io **Sprite** and use **at least one Sprites connector** (we use OpenRouter; Pushover optional).
- Built during Hacksgiving week. One entry per developer.
- Submit: code link + demo + short description via the form, and post a demo tagging @flydotio on X / Bluesky / LinkedIn / Reddit.
- Demo video = bonus points. Winners announced Tue 1 Dec by email.

## Section docs
- `personas.md` — the three animals' personality files and memory files
- `pond-script.md` — the core script: prompt building, memory, wake-up, gossip
- `web-page.md` — the page my son uses
- `turtle-drawing.md` — LOGO-style drawing commands, interpreter, animation
- `infra-connectors.md` — Sprite, OpenRouter connector, Pushover, privacy, service restart
- `demo-submission.md` — video, social post, submission form

## Project settings
- `build_output`: GitHub repo, branch `build/vNN` + pull request (repo: `SquishyPandaFurry/grumpy-turtle`; cloned on the Sprite at `~/the-pond`)
- `version_label`: `vNN` (v01, v02, …)
- `test`: on the Sprite — restart the service, open the pond page, send one message to each animal, check replies and memory files; for v02+ also let the Sprite sleep and re-open the page
- `publish`: merge the PR to `main`, pull on the Sprite, restart the pond service
- `sign_off`: I approve in chat after seeing what changed and the test result
- `art_rule`: none (my son's drawings are used for the animal pictures)

## Change log
- 2026-11-24 — project set up; v01–v04 queued from the agreed plan.
- 2026-11-24 — v01 built and merged (PR #1): Shelly the turtle chats on the private page, with memory; pond service on the Sprite.
- 2026-11-25 — v02 built and merged (PR #3): Coco the capybara and Prickles the hedgehog (draft names), Pond group chat + private chats, last 10 + summary, greeting from memory, UK time of day, persona variety, phone text; fixed tablet keyboard and memory saving; 429 retry.
- 2026-11-26 — v03 built and merged (PR #5): final names Rocky / Ferdinand / Colin, character knowledge, private chats know the Pond chat, memory summarising, wake-up gossip; fixed bedtime takeover, one-voice Pond chat, tablet keyboard space. Pushover still to come.
- 2026-11-27 — v03 feedback: 4 bugs (always reassuring, same fact in every greeting, lost gossip, out of credit looks like a hiccup) and "everyone" answers in the Pond chat queued for v04; tablet keyboard fold passed on the real tablet.
- 2026-11-27 — v04 built (PR pending): Everyone answers, Rocky draws (interpreter, animated drawing, morning picture, draw-your-own box); fixed always reassuring, same fact in every greeting, lost gossip, out of credit looking like a hiccup.
