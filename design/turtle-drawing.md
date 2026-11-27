# Turtle drawing (LOGO)

Shelly the turtle draws pictures with classic turtle-graphics commands.

## Agreed but not built
- Allowed commands only (never run model-written code): FORWARD, BACK, LEFT, RIGHT, PENUP, PENDOWN, COLOUR, REPEAT n [ ... ].
- Turtle persona gets a section: when asked to draw, reply with a short comment then commands inside `<draw>...</draw>`.
- Script extracts `<draw>`, interprets to line segments, renders SVG (no graphics library).
- Page animates the drawing slowly, line by line, with a small turtle icon following the pen.
- Morning picture during wake-up gossip, shown in pond news; other animals react (hedgehog critiques, capybara loves everything).
- A box where my son types turtle commands himself and watches Shelly draw them.
- Cap command count / canvas bounds so a bad drawing can't hang the page.

## Built
- v04: `pond/turtle_draw.py` interprets FORWARD/FD, BACK/BK, LEFT/LT, RIGHT/RT, PENUP/PU, PENDOWN/PD, COLOUR/COLOR (15 named colours), REPEAT n [ ... ] into line segments; caps: 600 tokens, REPEAT ≤ 72, 4 levels deep, 4000 steps, 1500 lines, canvas ±200. Never runs model text.
- v04: Rocky's prompt has a Drawing section; a `<draw>` block in his reply becomes a drawing (other animals' blocks are dropped). The page draws it slowly in the bubble (whole picture in ≤ 14 s) with a 🐢 following the pen.
- v04: morning picture after each wake-up gossip (one model call: title, commands, Colin's critique, Ferdinand's delight) saved to `pond/picture.json`, announced in pond news, drawn at the top of 📰 Pond news.
- v04: 🖍️ button (Rocky's chat and the Pond chat) opens a commands box with Square / Star / Sun / Flower examples; `POST /draw` interprets without a model call and Rocky knows the child drew.

## Ideas (not agreed)
- Gallery of past drawings.
