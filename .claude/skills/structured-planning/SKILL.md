---
name: structured-planning
description: Use when the user asks for "a plan," "how should we approach this," "design for X," "what's the implementation strategy," or similar. Also when starting non-trivial work where the path isn't obvious. Produces a structured plan with goal, constraints, steps, verification per step, risks, and open questions -- not just a bullet list of "do A then B then C." Not for a trivial change whose path is already obvious; just do it.
---

# Structured planning

Replace "make a step-by-step plan" with something the team can actually execute against. A real plan answers: what's the goal, what must not break, what's each step, how do we verify it, what could go wrong, and what do we still not know.

## Recognize when to apply

Direct asks:
- "Plan this out."
- "How should we approach X?"
- "Design the migration / refactor / new feature."
- "What's the implementation strategy?"

Indirect signals:
- The user describes an outcome but not a path.
- The work spans more than 2-3 files or subsystems.
- You're about to scaffold a durable project folder, or start a multi-step refactor where each step needs its own commit.
- You're about to write code and notice you can't articulate the first three changes in concrete file:line terms.

Skip for trivial requests where the plan is obvious in one read.

## The shape of a real plan

```markdown
# Plan: <short title>

## Goal
One paragraph in concrete terms. Not "improve auth" -- "replace session-token auth with JWT in apps/auth, keeping /api/v1 endpoints up throughout."

## Why now
What's forcing this? Deadline, incident, dependency, stakeholder ask. If nothing's forcing it, say so.

## Constraints
- Must keep working: <e.g. "the /api/v1/* endpoints stay up until step N">
- Must not regress: <e.g. "current auth latency p99">
- Out of scope: <adjacent things people might assume but aren't>

## Approach (one paragraph)
The shape of the solution, in prose. Reviewer should be able to read this and say "yes" or "no, different approach" without reading the steps yet.

## Steps
### Step 1: <short title>
**What:** Concrete change in one sentence.
**Why:** Why this is the right next step (not just "because step 2 depends on it").
**Files touched:** Specific paths.
**Verification:** How we check this step worked (a test, a command, a visible behavior).
**Risk if it goes wrong:** What breaks; how we'd notice; how we'd revert.
**Done when:** Testable criterion, not "feels done."

### Step 2..N

## Risks (cross-cutting)
Things that aren't tied to a single step -- data migration, downtime windows, dependency on someone else's work, anything that requires coordination.

## Open questions
What we still need to learn or decide before this can be executed. Each question has a name attached (who can answer it) and a blocking/non-blocking flag.

## Estimate
Rough complexity (S/M/L) per step. Be honest -- overestimate is fine, fake confidence is not.
```

## What separates a good plan from a bad one

| Good | Bad |
|---|---|
| Each step has a concrete verification | "make sure it works" |
| Files-touched lists actual paths | "the auth code" |
| Risks are named, not implied | (no risk section) |
| Open questions exist (almost always do) | "all questions answered" -- usually false |
| Steps are individually committable | one giant step labeled "implement" |
| Approach is one paragraph, not the whole plan | approach buried in step 1 |

## After writing the plan

1. **Surface the plan to the user.** Wait for confirmation before executing.
2. **Save it somewhere durable** if the work outlives this session -- a project folder for multi-week work, or a plan file committed alongside the branch for a single bounded refactor.
3. **Update the plan as you learn.** Plans are working documents: silent deviation is the problem, not updates.

## Don't

- **Don't pad with motherhood and apple pie.** "We'll write clean code and test thoroughly" adds no information.
- **Don't pre-bind to file paths you haven't read yet.** If you're guessing where something lives, say so.
- **Don't number steps you haven't actually thought through.** Four real steps beats twelve handwaved ones.
- **Don't skip "Open questions"** because you don't have any -- you do; you just haven't surfaced them. Look harder.
