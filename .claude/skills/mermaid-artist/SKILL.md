---
name: mermaid-artist
description: Produces well-designed Mermaid diagrams for documentation -- flowcharts, sequence diagrams, state diagrams, architecture/C4 views, ER diagrams, timelines, mindmaps, and more. Use whenever a task calls for a diagram, visual, or infographic in Mermaid, or when writing/editing docs (READMEs, architecture docs, runbooks, design docs, ADRs) that would benefit from one even if not explicitly asked. Also use to review or fix an existing Mermaid diagram that's hard to read, too dense, or won't render. Trigger on requests like "diagram the request flow," "show the architecture," or "visualize this process" -- not just the literal word "mermaid." When a documentation workflow (e.g. a Diataxis tutorial/how-to/reference/explanation) needs a diagram, use this for the diagram step and inherit the established audience, goal, scope, and doc type rather than re-deriving them. Do not use for static images/artwork (SVG illustrations, marketing graphics) -- this is specifically for Mermaid-syntax diagrams in text documentation.
---

# Mermaid Artist

## The one rule everything else follows from

A Mermaid diagram is successful when the reader understands the intended story, relationships, hierarchy, and scope **faster from the diagram than from the equivalent prose**. If it doesn't clear that bar, it isn't done -- no matter how clean the syntax is.

That means quality has three independent dimensions, and all three have to pass:

1. **Semantic correctness** -- does the diagram represent the intended model?
2. **Visual comprehension** -- can a reader understand it quickly, ideally standing alone?
3. **Rendering correctness** -- does the Mermaid source actually render, with no syntax errors?

A diagram that renders but confuses the reader has failed just as much as one that doesn't render at all. Don't stop at "the syntax is valid."

## Workflow: Story -> Model -> View -> Render -> Review (SMVRR)

The most common failure mode is starting to write Mermaid syntax immediately and discovering halfway through that you don't actually know what the diagram is trying to say. Work through these five stages in order -- they're cheap, and skipping them is what produces hairballs and abstraction soup.

### 1. Story

Before touching syntax, pin down:
- **Audience** -- who's reading this, and what do they already know?
- **Question** -- what specific question does this diagram answer? "How does a user request move through the system?" is a story. "Everything about the system" is not.
- **Scope** -- what's deliberately left out?

If the material you're given contains multiple unrelated stories, that's a sign to produce multiple diagrams rather than one diagram trying to do everything. A diagram that tries to be the whole documentation page has already lost -- the diagram should be the visual index, with detail living in the surrounding prose.

**Inherit the story, don't re-derive it.** When this skill is invoked as part of a larger documentation workflow -- especially a Diataxis-style one -- the upstream step has usually already established audience, goal, and scope, and classified the document into a type (tutorial, how-to, reference, explanation). Take that context as given. Don't re-interrogate the user for things already decided, and don't quietly contradict the established scope. The diagram serves the document it lives in; the document's framing *is* the diagram's Story.

**A diagram must stay in its document's lane.** The single most useful thing the Diataxis type tells you is what the diagram is *for* -- and, just as importantly, what it must *not* become. A step-by-step instructional flowchart dropped into an explanation doc is the same failure as step-by-step prose in an explanation doc: a type leak. The "one diagram, one story" rule and Diataxis's "one document, one type" rule are the same discipline. Use the type to steer both the diagram's purpose and its likely Mermaid type:

| Doc type | The diagram is for... | Naturally fits | Keep it *out* of |
|---|---|---|---|
| **Tutorial** (a lesson) | orientation and momentum -- show the end result, or the happy path as one simple line | a simple `flowchart` (no branches), an architecture sketch of the finished thing | decision branches, exhaustive reference structures |
| **How-to guide** (a recipe) | one competent user solving one problem, with real choices at real forks | `flowchart` with decision points, `sequenceDiagram` for an interaction | teaching-oriented conceptual diagrams, background |
| **Reference** (a dictionary) | describing machinery factually, mirroring structure | `erDiagram`, `stateDiagram`, architecture/C4, class-like structure | instructional step-by-step sequences |
| **Explanation** (a discussion) | understanding, relationships, tradeoffs, how things fit | `mindmap`, C4 context/architecture, relationship maps | step-by-step "do this then that" flowcharts |

If you find yourself wanting to put a step-by-step flowchart into a reference or explanation doc, that's usually a signal the *content* belongs in a how-to or tutorial -- flag it the way the doc workflow would flag mixed types, rather than smuggling it in as a diagram.

### 2. Model

Before generating any Mermaid, sketch the underlying model -- entities and labeled relationships -- independent of syntax. This is worth doing explicitly (even just as a short list in your own reasoning) because it's much easier to spot problems like mixed abstraction levels or unlabeled relationships in a plain list than in Mermaid source:

```
entities: User, Harness, Planner, Tool Gateway, Tool, Memory
relationships:
  - User -> Harness: submits request
  - Harness -> Planner: requests plan
  - Planner -> Harness: returns plan
  - Harness -> Tool Gateway: invokes tool
  - Tool Gateway -> Tool: executes
  - Tool -> Harness: returns result
  - Harness -> Memory: persists state
```

Every relationship needs a label that says what actually happens across it -- "sends request," "invokes," "publishes event," "reads state." Never leave an arrow unlabeled, and avoid generic labels like "uses" or "has," which say nothing a reader couldn't already guess.

### 3. View -- choose the diagram type and abstraction level

Match the Mermaid diagram type to what you're actually communicating, rather than defaulting to a flowchart because it's familiar:

| Communicating | Preferred Mermaid type |
|---|---|
| Process / decision / workflow | `flowchart` |
| Request/response over time, temporal interaction | `sequenceDiagram` |
| Lifecycle / states | `stateDiagram` |
| System or software architecture | `architecture-beta` or C4-style flowchart |
| Hierarchy | `mindmap` or `flowchart` |
| Chronology | `timeline` |
| Data relationships | `erDiagram` |
| Requirements -> implementation | `requirementDiagram` |
| User experience stages | `journey` |
| Quantitative relationships | `xychart`, `sankey`, `pie` |

If time/order is the primary thing being communicated, use `sequenceDiagram` even if a flowchart *could* represent it -- Mermaid's sequence syntax has native support for alternatives, loops, and parallel paths that a flowchart would have to fake.

**Abstraction discipline (from C4):** never mix abstraction levels in one diagram unless the diagram's purpose explicitly requires it. A hierarchy that goes `Agent Harness -> Planner -> OpenAI API -> Python function -> Redis key -> HTTP request` is mixing system, component, external service, implementation, and infrastructure in one visual -- that's a common and specific failure mode, not just "too much detail." Instead, produce separate views at consistent zoom levels (system context -> containers -> components), the way C4 does, and let each diagram stay at one level.

If the material naturally splits into multiple perspectives (e.g. context view, request lifecycle, orchestration, tool execution, memory/state), that's a sign to produce multiple focused diagrams rather than one diagram trying to hold all of them.

### 4. Render -- layout and syntax rules

**Reading direction.** Pick direction deliberately, it's one of the strongest levers you have:
- Processes/pipelines -> `flowchart LR` (input -> processing -> output reads naturally left to right; only go vertical if it's genuinely clearer)
- Hierarchies -> `flowchart TB`
- Timelines -> left-to-right chronological
- Sequence diagrams -> participants across the top, time flowing down

**Minimize edge crossings.** A diagram where lines cross all over the page is technically valid and cognitively expensive. Group related nodes spatially, keep strongly-connected nodes close together, and use subgraphs as semantic containers for meaningful boundaries -- this does far more for readability than color-coding boxes ever will.

**Don't build hairballs.** A diagram becomes a hairball when it has too many nodes, too many edges, too many crossing relationships, too many colors, or too much text -- usually because several abstraction levels got mixed into one picture (see above). Mermaid diagrams in documentation usually can't rely on interactive filtering to manage this the way a live graph tool could, so the fix is almost always **decompose into multiple diagrams**, not "make the layout engine work harder." A sophisticated layout algorithm cannot rescue a diagram that's semantically trying to say too much at once.

**Layout engine.** Default `dagre` layout is fine for simple DAGs. For complex architecture/relationship graphs, prefer ELK:
```
---
config:
  layout: elk
---
```
If a graph is dense enough that even ELK produces something unreadable, that's a signal to reconsider whether Mermaid is the right representation at all, or to split the diagram -- not a signal to keep tuning layout.

**Node text.** Keep labels short -- a name plus a short responsibility, not a paragraph. `Orchestrator["Orchestrates agent execution"]` beats a node whose label is a full sentence of implementation detail. Put the detailed explanation in the surrounding prose; the diagram is the index, not the essay.

**Color.** Color must encode meaning or hierarchy -- never use it just because a diagram "needs some color." Use the **canonical palette** in `references/palette.md`: one fixed set of hex values with a defined role each (internal system, external system, data store/state, success, failure, human/decision). Load it before adding any color and apply it the same way in every diagram, so a role reads identically across the whole doc set -- don't invent per-diagram colors. Never make color the *only* signal for something important -- pair it with a label, icon, or line style too, so the diagram still works in black-and-white or for colorblind readers.

**Titles, scope, legend.** Every diagram should be able to stand alone: give it a clear title (via `title` where the diagram type supports it, or a heading in the surrounding markdown), and add a legend whenever you're using color, shape, or line style to encode meaning that isn't otherwise obvious.

### 5. Review -- before calling it done

Check the diagram against these hard failures. Any one of them means regenerate, not ship:

- You can't state the diagram's purpose in one sentence
- Abstraction levels are mixed (system + component + implementation detail in one hierarchy)
- A relationship that matters is unlabeled
- The layout is a hairball -- dense crossings, no clear grouping
- Color is required to understand the diagram (no fallback signal)
- The Mermaid source doesn't actually render

If none of those hit, sanity-check the softer dimensions too: is the reading direction obvious, is node text concise, does someone unfamiliar with the system get the story in a few seconds? For a fuller scoring rubric (useful when auditing existing diagrams or comparing candidates), see `references/rubric.md`.

## Anti-patterns to watch for

These come up often enough to name directly:

- **The spaghetti diagram** -- everything connects to everything, no grouping.
- **The poster** -- node labels containing full paragraphs instead of short names.
- **The rainbow** -- every node a different color for no reason.
- **The mystery arrow** -- unlabeled relationships, unclear direction.
- **Abstraction soup** -- system -> API -> class -> database row -> HTTP request, all in one hierarchy.
- **The legendless notation** -- shapes/colors/line styles carry hidden meaning with nothing explaining them.
- **The everything diagram** -- one diagram trying to explain the whole system instead of being decomposed into focused views.
- **The syntax-first diagram** -- the Mermaid source is technically valid but the rendered result doesn't communicate anything well. Syntactic correctness is not the bar.

More detail, plus the full quality rubric and diagram-type decision notes, is in `references/rubric.md` -- read it when auditing an existing diagram, comparing multiple candidates, or when a generated diagram needs a second, more rigorous pass. The canonical color palette lives in `references/palette.md` -- read it before adding color to any diagram.
