# Brief: an accessibility panel on the student page

This brief is for whoever implements it in `student_app/`. It describes what to build and why. It isn't built yet.

## Why

The organizers' guide lists "Problems for students with dyslexia or dyscalculia" as one of the ideas to teach ([BOARD_SETUP §13.2](BOARD_SETUP.md#problems-for-students-with-dyslexia-or-dyscalculia)). In the kickoff talk (around 10:26) the organizer said they love this idea, and told the story of a maths teacher with dyslexia who mixed up + and −, and 0 and 1. For dyslexia, the guide asks for:

- short sentences, one idea per line, the question at the end and on its own line, the options one per line;
- on the web page, a large, well-spaced font that's installed on the board, not loaded from the internet;
- a mode the student or the teacher chooses: "Nobody is labelled by the copilot."

We build two of these, the cheap ones, in about half a day: a readable font and an easy-read layout of the problem text. We leave out dyscalculia mode and LLM rewrites.

## What the student sees

An **Aa** button in the top bar, next to "not you?", on every screen, including the middle of an exercise. It opens a small panel with two switches:

| Switch (cat / eng / esp) | Effect |
|---|---|
| Lletra fàcil de llegir / Easy-to-read font / Letra fácil de leer | The readable font, larger and more spaced |
| Lectura fàcil / Easy read / Lectura fácil | The problem text one sentence per line, with the question last |

Both switches are off by default. Each one works without the other. The change shows at once, with no reload.

## 1. Readable font

- Font: [Atkinson Hyperlegible](https://github.com/googlefonts/atkinson-hyperlegible) (SIL Open Font License), regular and bold, as `.woff2` in `student_app/static/fonts/`, with its `OFL.txt`. About 30 KB per weight. The board has no internet, so no Google Fonts link.
- Why not OpenDyslexic: Atkinson Hyperlegible was designed so that similar characters (0/O, 1/l/I) are hard to confuse, which matches the teacher's story. A study with dyslexic readers (Rello & Baeza-Yates, 2013, "Good fonts for dyslexia") found that sans-serif, roman, larger fonts helped, and OpenDyslexic didn't.
- CSS, under a `body.a11y-font` class: the font, body size about 19 px, line height 1.7, `letter-spacing: .03em`, `word-spacing: .12em`, text aligned left. No italics anywhere in this mode: today `.msg.thinking` is italic.
- This applies to the whole page: the problem, the options, the chat and the buttons.

## 2. Easy read

- It's a code transform of the problem text, with no LLM, so it's instant and can't change the maths.
- The rules:
  1. One sentence per line.
  2. The question sentence (the last sentence that ends in `?`) moves to the end, after a blank line.
  3. The options stay as they are: they're already one per line.
- Where: a new module `student_app/easy_read.py` with one function, `easy_read(text: str) -> str`. The server adds `prompt_easy` next to `prompt` in each exercise it sends. The page shows `prompt_easy` when the switch is on, and `prompt` otherwise. `.prompt` already has `white-space: pre-wrap`, so line breaks show as they are.
- The sentence splitter must not split on:
  - decimals and numbers: `3.5`, `1.000`, `2,5`;
  - abbreviations: `p. ex.`, `e.g.`, `i.e.`, `etc.`, `cm.`, `km.`, `min.`, `Fig.`, `núm.`;
  - a `?` or a `.` inside brackets or quotes;
  - an ellipsis `...`.
- If a text has no `?`, only rule 1 applies. If splitting fails or gives a single sentence, return the text unchanged.

### Tests (pytest, `tests/test_easy_read.py`)

- Nothing is lost: the words and numbers of the output are the words and numbers of the input, with the same count. Only the order of the question sentence may change.
- The hard cases above, each as a short invented example. Don't paste M3Kang problem text into a test file: it's committed (see `CLAUDE.md`, red line 1).
- For the write-up, a small script prints words per sentence and long words per sentence, before and after, over `data/val.jsonl` in `cat` and `eng`. It reads the data locally and prints numbers only. The guide asks for readability measured "with numbers, such as words per sentence".

## Where the setting lives

- On the phone, in `localStorage` (key `a11y`, value `{font: bool, easy: bool}`), wrapped in `try/catch`. It survives a new visit on the same phone. The visit itself stays in `sessionStorage` as today.
- The page applies the setting as two classes on `<body>`: `a11y-font` and `a11y-easy`.
- Don't log the switches as events for the teacher. It's a reading preference, and logging it would let a teacher guess which student may be dyslexic, which goes against "nobody is labelled" and against the data rules in the teacher-data note (commit `8659aa4`).

## Strings

Add to `student_app/strings.py` in `cat`, `eng` and `esp`: the panel title (Accessibilitat / Accessibility / Accesibilidad), the two switch labels, and a one-line description under each.

## Check before calling it done

1. `pytest tests/test_easy_read.py` passes.
2. Screenshots at phone width (390 px) of one exercise in four states: both switches off, font on, easy read on, both on. Check that nothing overflows sideways.
3. With the board's Wi-Fi and no internet, the font still loads: the browser's network tab shows `/static/fonts/...woff2`, served by the board.

## Out of scope

- Dyscalculia mode (smaller numbers first, dots on the LED matrix).
- LLM rewrites of the problems.
- A teacher setting that turns the modes on for a student.
