# Why the tutor answers this way

The [tutor response types](../reference/tutor-response-types.md) (T0 to T9)
did not come from the code. They came from tutoring research, from the
socratic-tutor rules (`.claude/skills/socratic-tutor/SKILL.md`) and from the
papers of the [paper vault](../vault/papers/tutoring_pedagogy/_synthesis.md).
This page gives the reasons for each type, and the limits of that evidence.
The proposal that turns these reasons into rules is
[Tutor response policy](tutor-response-policy.md).

## Help is a ladder

The sources agree on one idea: **help is a ladder of growing explicitness, and
the tutor goes up one step only when the step below fails.**

- **Contingent tutoring** (Wood & Wood 1999). The tutor gives more help after
  a failure and less after a success. In their studies, about three hints of
  growing explicitness came before the tutor showed the step.
- **Cognitive tutors** (tutoring software that follows a model of the
  student's steps). Their hint sequences start with general hints and end in
  the "bottom-out hint", which gives the step away.
- **The socratic-tutor rules.** "Only explain directly after 2-3 failed
  attempts."

This is why five types form a ladder (T0, T1, T4, T5, T7). The three other
types are side moves: what the student wrote decides them, not the step. A
student who brings an attempt needs a correction (T6). Explicit help needs a
check (T8). A message that does not help the lesson needs a redirect (T9).

## The reasons for each type

### T0: ask before you tell

The socratic-tutor rules teach "primarily by asking questions that force the
user to reason, predict, and explain". A question also diagnoses: without it,
the tutor does not know which step is next.

In MathDial, a dataset of 3,000 tutoring dialogues between teachers and a
simulated student, Focus questions are the most frequent teacher move: they
are in 37% of utterances (Macina et al. 2023, §4.2). The first teacher
utterance is "usually generic" and "oftentimes" asks the student to repeat
the question or their attempt. MathDial classes that opener as Generic, not
as Focus or Probing. That is the source of T0b ("What have you tried so
far?").

### T1: a heuristic before the content

Pólya (*How to Solve It*, 1945) gives his questions for the moment when
progress stops, not as a fixed recipe. A heuristic is the least explicit
help that still gives the student a tool. If it works, the student learns to
ask the question alone next time.

### T4: an example, mostly for beginners

- In the Andes physics tutor, worked examples as help were at least as
  effective as hint sequences, and took less time (Ringenberg & VanLehn).
- Worked examples help beginners. They lose value, or do harm, with advanced
  students: the expertise reversal effect (Kalyuga; Leppink et al. 2012).
  That is why the cards move T4 earlier for beginners and skip it for a
  student who only made a slip.
- On the board, a similar problem from the retrieval index needs no text
  generation, so it cannot invent facts.

### T5: tell only what cannot be worked out

The socratic-tutor rules allow a direct explanation only "to introduce
genuinely new material", in "a few sentences". Nobody works out a definition
alone. In MathDial, revealing a strategy already counts as *Telling*, the
most explicit move: T5 is the start of the top of the ladder.

### T6: correct the idea, not only the result

- Errors persist unless the teacher steps in with a strategy (Radatz 1980,
  cited by Bridge, §4.2.2).
- Bridge (Wang et al. 2023) gives a model an expert's decision: the type of
  error, the strategy and the intention. With that decision, GPT-4's replies
  were preferred +76% and judged useful +80%, against replies with no
  decision (§7.1). The gain is for the whole decision. Bridge does not
  measure each strategy alone.
- This is why T6 has subtypes by type of error, and why the type of error
  comes before the form of the reply.

### T7: the solution is the last step, and needs a check

- **Help abuse.** In the Geometry Cognitive Tutor, 36% of student actions
  were help abuse (14% when a burst of requests counts as one action) (Aleven
  et al. 2006). Help abuse goes with less learning.
- **AI without guardrails.** In a field experiment with nearly 1,000
  secondary-school students, a GPT-4 chat like ChatGPT improved practice but
  lowered the score in an exam without help (−17%). A version with teaching
  guardrails ("GPT Tutor") avoided most of the harm (Bastani et al., PNAS
  2025). These figures come from secondary summaries, not from the full text.
- **Counterpoint.** A bottom-out hint can work as a worked example if the
  student studies it (Shih, Koedinger & Scheines 2008).
- In MathDial, *Telling* is the rarest move. It grows late in the dialogue,
  when the student has been stuck for some time (§4.2).

### T8: explicit help needs a re-test

A worked example teaches when the student explains it to themselves. This
page did not check a study for that claim. The socratic-tutor rules ask for
an immediate re-test "from a different angle" after every direct
explanation, and count a skill as learned only on unprompted recall.

### T9: redirect with a question, not a block

- **Gaming the system:** using the help or the feedback to get the answer
  instead of thinking. It goes with less learning (Baker et al. 2004; Aleven
  & Koedinger 2000 for help abuse).
- A 2-second delay on hints, to stop bursts, did not work: students found
  other ways to fish (Baker, retrospective). That is why T9c replies with a
  question that needs thought, not with a block.
- Feedback about the person is the least effective level of feedback (Hattie
  & Timperley 2007). That is why a redirect never judges the student.

## Why a small router needs few labels

People disagree on fine-grained teacher moves. In MathDial, two annotators
labelled the moves of 102 teacher utterances (§4.2):

| Pair | κ, four moves | κ, Focus and Probing merged |
|---|---|---|
| Annotator and annotator | 0.60 | 0.67 |
| Annotator 1 and the teacher | 0.49 | 0.75 |
| Annotator 2 and the teacher | 0.34 | 0.55 |

κ (Cohen's kappa) is agreement corrected for chance: 1 is full agreement, 0
is chance. If trained people agree this little on fine labels, a small model
cannot be expected to do better. This is why the policy asks the intent
router for five labels about the student's message, not for the eight
response types; see
[Labels for the intent router](tutor-response-policy.md#labels-for-the-intent-router).

## Limits of the evidence

- The Bastani et al. figures come from summaries, not from the full paper.
- The five exact levels of Wood, Wood & Middleton (1978) were not checked.
- The T8 claim about self-explanation has no source checked here.
- None of these studies used a 0.8B model on a board, or Kangaroo problems.
  The types are a design choice based on this evidence, not a measured
  result.

## Sources

In the paper vault (with PDF and parsed text):

- Macina et al. 2023, MathDial ([arXiv 2305.14536](https://arxiv.org/abs/2305.14536)): the Focus / Probing / Telling / Generic moves, Table 2 and §4.2.
- Wang et al. 2023, Bridge ([arXiv 2310.10648](https://arxiv.org/abs/2310.10648)): 11 strategies, §4.2; results, §7.1.
- Vault synthesis: [tutoring pedagogy](../vault/papers/tutoring_pedagogy/_synthesis.md).

Found in a literature search:

- Wood, Bruner & Ross 1976, the origin of "scaffolding"; Wood, Wood & Middleton 1978 and Wood & Wood 1999, contingent tutoring: [Glasgow CERE archive](https://www.psy.gla.ac.uk/~steve/courses/archive/CERE11-12-safari-archive/Katie/webarchive-index.html), [Wood & Wood (TLU)](https://www.tlu.ee/~kpata/haridustehnoloogiaTLU/tutoring.pdf), [Hendrick, "We need to talk about scaffolding"](https://carlhendrick.substack.com/p/we-need-to-talk-about-scaffolding).
- Pólya, *How to Solve It* (1945): [copy at uni-sofia.bg](https://omi.fmi.uni-sofia.bg/wp-content/uploads/2020/02/Polya_How-to-solve-it.pdf).
- Ringenberg & VanLehn, examples as help: [LearnLab wiki](https://learnlab.org/research/wiki/index.php/Ringenberg_Examples-as-Help), [core.ac.uk](https://core.ac.uk/works/61693190).
- Aleven, Koedinger and help abuse: [LearnLab wiki, Help abuse](https://learnlab.org/research/wiki/index.php/Help_abuse); Baker, [Gaming the system](https://learninganalytics.upenn.edu/ryanbaker/PSCS-gaming-v6.pdf); [Shih, Koedinger & Scheines 2008](https://www.cmu.edu/dietrich/philosophy/docs/scheines/Shih_Koedinger_Scheines_2008_EDM.pdf).
- Kalyuga, expertise reversal effect: [Chartered College](https://my.chartered.college/impact_article/expertise-reversal-effect-and-its-instructional-implications/), [Leppink et al. 2012](https://link.springer.com/article/10.1007/s10734-011-9476-1).
- Sinha & Kapur 2021, productive failure, *Review of Educational Research*: [ETH summary (phys.org)](https://phys.org/news/2021-09-productively-wiser.html).
- Bastani et al. 2025, PNAS: [IDEAS/RePEc](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html), [Stanford SCALE](https://scale.stanford.edu/ai/repository/generative-ai-can-harm-learning).
- Hattie & Timperley 2007, levels of feedback (task, process, self-regulation, self): [AITSL](https://www.aitsl.edu.au/docs/default-source/research-evidence/spotlight/feedback.pdf).

Further reading, not used on this page:

- Ding et al. 2024, SocraticLLM ([arXiv 2407.17349](https://arxiv.org/abs/2407.17349)).
- Petukhova & Kochmar 2025, "Intent Matters" (11 intents on MathDial): [arXiv 2506.07626](https://arxiv.org/abs/2506.07626).
