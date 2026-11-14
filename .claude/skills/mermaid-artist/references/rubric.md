# Full quality rubric

Use this when auditing an existing diagram, comparing multiple candidate diagrams, or giving a generated diagram a second, more rigorous pass. For first-pass generation, the hard-failure checklist in SKILL.md's Review step is usually enough.

## Scoring

Score each criterion 0-2 (0 = fails, 1 = partial, 2 = clean):

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Purpose | unclear | somewhat clear | immediately clear |
| Scope | absent | implied | explicit |
| Abstraction | mixed | mostly consistent | consistent |
| Diagram type | inappropriate | acceptable | ideal |
| Reading direction | confusing | acceptable | obvious |
| Hierarchy | flat/confusing | adequate | clear |
| Relationships | ambiguous | partly labelled | explicit |
| Layout | cluttered | usable | clean |
| Edge crossings | many | some | minimal |
| Text density | excessive | moderate | concise |
| Color semantics | decorative | partly meaningful | systematic |
| Accessibility | poor | partial | explicit |
| Legend | absent (when needed) | unnecessary/implicit | present when needed |
| Visual hierarchy | weak | adequate | strong |
| Standalone comprehension | poor | moderate | high |

Total out of 30:
- 26-30 Excellent
- 22-25 Good
- 18-21 Acceptable
- Below 18 -- regenerate rather than patch

Independent of the total score, any of these is a hard failure regardless of how the rest scores:
- Cannot identify the diagram's purpose
- Major abstraction levels mixed
- Unlabelled critical relationships
- Unreadable / hairball layout
- Color required to understand semantics
- Diagram doesn't render

## Accessibility

Mermaid supports an accessible title and description on most diagram types (`accTitle` / `accDescr`), which gets surfaced as ARIA metadata. For documentation that's generated automatically or published broadly, set these -- they cost almost nothing and mean the diagram's purpose survives even for a screen reader or when rendering fails:

```
flowchart LR
    accTitle: Agent request lifecycle
    accDescr: Shows how a user request flows from submission through planning, tool invocation, and result return.
```

## Anti-pattern gallery

Illustrative sketches of what each anti-pattern looks like in practice -- useful for recognizing them in existing diagrams you're asked to fix.

**The spaghetti diagram**
```
A ────────────────┐
B ────────┐       │
C ────────┼───────┼──-> Z
D ────────┘       │
E ────────────────┘
```
Fix: group by relationship, use subgraphs, or decompose into separate diagrams per concern.

**Abstraction soup**
```
Agent Harness
   v
Planner
   v
OpenAI API
   v
Python function
   v
Redis key
   v
HTTP request
```
This mixes system, component, external service, implementation, and infrastructure in one hierarchy. Fix: separate into a system-context diagram, then a container/component diagram, then -- only if truly necessary -- an implementation-level diagram. Each stays at one zoom level.

**The mystery arrow** -- arrows with no label, e.g. a bare `A --> B`, when the diagram is meant to communicate anything beyond "these are connected." Fix: every meaningful arrow gets a verb -- sends, invokes, returns, persists, publishes, depends on.

**The rainbow** -- a different color per node with no shared meaning across them. Fix: define a small palette where each color maps to one category (state, ownership, system boundary), and hold that mapping constant across every diagram in the document set, with a legend.

## Diagram planning object (optional, for complex diagrams)

For anything non-trivial, writing out a short planning object before generating Mermaid catches most abstraction and scoping mistakes cheaply:

```yaml
diagram:
  purpose: "Explain how an agent request is executed"
  audience: "Developers"
  scope: "Agent harness runtime"
  abstraction: "container"
  type: "sequence"
  direction: "top-to-bottom time"

entities:
  - User
  - Harness
  - Planner
  - Tool Gateway
  - Tool
  - Memory

relationships:
  - User -> Harness: submits request
  - Harness -> Planner: requests plan
  - Planner -> Harness: returns plan
  - Harness -> Tool Gateway: invokes tool
  - Tool Gateway -> Tool: executes
  - Tool -> Harness: returns result
  - Harness -> Memory: persists state

visual_rules:
  max_nodes: 8
  max_crossings: 0
  labels: explicit
  colors: semantic_only
```

This mirrors C4's distinction between an architecture *model* (structured entities and relationships) and the *views* rendered from it -- the same model can produce a system-context view, a container view, or a component view depending on what's in scope for that particular diagram.

## Authoritative references

If you need to check exact syntax rather than working from memory, these are the sources this skill is grounded in:
- Mermaid syntax reference and flowchart docs -- canonical syntax, node/edge/direction mechanics
- Mermaid layouts documentation -- Dagre, ELK, Tidy Tree, Cose-Bilkent
- Mermaid accessibility docs -- `accTitle`/`accDescr` behavior
- C4 model notation and review checklist -- semantic criteria for elements, relationships, colors, legends, and common diagram failure modes
