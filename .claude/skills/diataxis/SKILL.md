---
name: diataxis
description: Classify, structure and write documentation with the Diataxis framework -- one document, one type (tutorial, how-to, reference, explanation) -- and set its weight. Use for a reference doc, or for a type split. For a heavy document start with doc-authoring, which calls this first. Not for code comments or chat answers.
---

# Workflow: Diataxis documentation

Use this workflow to produce high-quality documentation guided by the Diataxis
framework. The framework classifies every document along two axes, and the
central discipline is that **one document serves exactly one type** -- mixing
types is the primary failure mode this workflow exists to prevent.

The four types and where they sit on the two axes:

| Type | Axes | Serves | Analogy |
|------|------|--------|---------|
| **Tutorial** | action + acquisition | Learning by doing | A lesson |
| **How-to guide** | action + application | Solving a specific problem | A recipe |
| **Reference** | cognition + application | Looking up facts | A dictionary |
| **Explanation** | cognition + acquisition | Understanding a topic | A discussion |

(action = doing / cognition = thinking; acquisition = learning / application =
using what you already know.)

---

## When this applies

- The user asks to create, review, or restructure documentation.
- The user names a Diataxis type, or a doc that clearly maps to one.
- The user hands you a doc that feels muddled and wants it fixed -- often this
  is a type-mixing problem.

If the request is a code comment, a commit message, or an inline explanation in
chat, this workflow does not apply -- just answer.

## Procedure

1. **Classify the type.** Use the axes above to decide which of the four this
   is. Infer it from the request when you can -- "document the `evaluate()`
   signature" is unmistakably reference; don't interrogate the user over
   something already clear. Only ask when the type is genuinely ambiguous.

   Then **assign the weight**. This is the one definition of weight; every
   other docs skill cites it. A document is *light* when its type is
   reference and its path is not a heavy path. Every other document is
   *heavy*: tutorial, how-to, explanation, and anything under a heavy path.
   Heavy paths are the project `README.md` and anything under `docs/`. Size the output to the
   weight: a light document is short and states only facts the code can
   confirm. A heavy document gets the full structure below.

2. **Fill remaining gaps -- but only the genuine ones.** Beyond type, a doc
   needs: **target audience**, **the user's goal**, and **scope** (what's in,
   and explicitly what's out). Take whatever the request already gives you.
   Put only the underdetermined ones to the user as one `grilling` round:
   numbered questions, each with your recommended answer. If `GLOSSARY.md`
   exists, read it and use its terms; when a term is in dispute, let
   `domain-modeling` settle it.

3. **Propose a structure.** Before writing full content, propose an outline --
   a table of contents with a one-line description per section. Apply the
   type's template (see below). Wait for approval.

4. **Generate content.** On approval, write the full doc in well-formatted
   Markdown, in the voice of its type. Keep to the approved scope.

## The four templates

Apply the skeleton **and the voice** for the classified type. The voice rules
are not stylistic preferences -- they are what keep each type in its lane.

**Tutorial** (a lesson; guarantees a newcomer reaches a working result)
- Voice: "we" / "you", imperative, encouraging. Concrete, never abstract.
- Skeleton: what you'll build (show the end result) -> prerequisites ->
  numbered steps, each with expected output -> "what you learned" recap.
- Rules: guarantee success -- every step must work. No choices, no digressions,
  no explaining *why*. If a concept needs explaining, link out to an
  explanation doc.

**How-to guide** (a recipe; helps a competent user hit one real goal)
- Voice: titled "How to <do X>". Assumes competence. Direct.
- Skeleton: goal statement -> prerequisites/assumptions -> ordered steps ->
  offer real alternatives at genuine decision points -> result.
- Rules: address one concrete problem. Omit teaching and background. Give
  choices where a real user faces them; don't pad with theory.

**Reference** (a dictionary; describes the machinery, factually)
- Voice: austere, neutral, describes rather than instructs. No opinions.
- Skeleton: mirror the structure of the code it documents. Consistent field
  ordering for every entry (e.g. signature -> parameters -> returns -> raises ->
  example).
- Rules: state facts, not instructions or judgments. Be exhaustive and
  consistent. Accuracy above all -- this is the type where a wrong detail does
  the most damage.

**Explanation** (a discussion; deepens understanding)
- Voice: discursive, reflective. Free to say "why", weigh tradeoffs, give
  history and context, make connections to other topics.
- Skeleton: frame the topic/question -> discussion -> alternatives and their
  tradeoffs -> connections to related concepts.
- Rules: no step-by-step instructions -- link to the tutorial or how-to for
  that. Its job is understanding, not action.

## Hard rules

- **One document, one type.** Never blend two quadrants in a single file. If
  material belongs to another type, split it out and cross-link rather than
  inlining it. Catching and separating mixed types is core to this workflow.
- **Propose the outline before writing.** Do not generate full content until
  the structure is approved.
- **Stay in scope.** Write to the agreed in/out boundaries; don't expand.
- **Honor the four guiding principles:** clarity (simple, unambiguous
  language), accuracy (correct, current code and details), user-centricity
  (every doc serves a specific user reaching a specific goal), and consistency
  (steady tone and terminology across the doc set).
- **Match the project's existing voice.** When the user supplies other Markdown
  files, mine them for tone, terminology, and style -- but do **not** copy
  their content unless explicitly asked.
- **No external sources.** Rely on the internalized Diataxis principles; do not
  browse the web. (The framework lives at https://diataxis.fr/ for the user's
  reference, not as a page to fetch.) Consult an external link only if the user
  provides one and asks you to.

## After writing

A new document is not done when it is written. For a heavy document, the
`doc-authoring` chain continues from here. For a light one, run `docsauditor`
on it, then `docsjanitor` on its findings.

## Output to the user

- The finished document as well-formatted Markdown, in the voice of its type.
- A one-line note of which type and weight it is, and the audience/goal/scope
  it was written to.
- Any cross-links needed because material was split out to keep types separate.
- Any places you stayed out of scope on purpose, flagged so the user can decide
  whether to commission a separate doc.

## Example invocation

> Write docs for our new `deconv.evaluate()` function. Developers who already
> use the library will read it to look up the exact signature and what it
> returns -- they're not learning the library from scratch.

Here the type is clear from the request (reference -- looking up machinery),
audience is stated (existing developers), and goal is stated (find the exact
signature/returns). Scope is the one gap worth confirming -- e.g. whether to
cover error cases and edge behavior -- so you'd propose the reference outline
and confirm just that before writing.
