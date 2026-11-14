# Canonical palette

One fixed palette, used the same way in every diagram across the doc set. Do not invent per-diagram colors. Each color maps to exactly one semantic role; if a diagram needs a role that isn't here, extend this file rather than picking an ad-hoc color in one diagram.

These tints are tuned for **light document backgrounds** (the common case for rendered docs). Fills are pale, strokes are saturated, text is dark -- so every node keeps readable contrast, and the roles stay distinguishable in grayscale by lightness (see accessibility note).

## Role -> color

| Role | Fill | Stroke | Text | Use for |
|---|---|---|---|---|
| **Internal / primary** | `#E8F0FE` | `#1A73E8` | `#10367A` | components inside the system being documented |
| **External / third-party** | `#F1F3F4` | `#9AA0A6` | `#3C4043` | APIs, services, actors outside the boundary |
| **Data store / state** | `#FEF7E0` | `#F9AB00` | `#7A5900` | databases, caches, queues, persisted state |
| **Success / healthy** | `#E6F4EA` | `#34A853` | `#1E4620` | success paths, healthy end states |
| **Failure / error** | `#FCE8E6` | `#EA4335` | `#8C1D18` | error paths, failure states |
| **Human / decision** | `#F3E8FD` | `#A142F4` | `#4A1E7A` | human actors, manual/agent decision points |

That's the whole vocabulary. Six roles is deliberately few -- if a diagram seems to need a seventh color, first check whether two of your nodes are really the same role, or whether the diagram is trying to say too much (see the hairball rule in SKILL.md).

## Applying it -- flowcharts, state, class, ER

`classDef` is the clean way to attach the palette in diagram types that support it (`flowchart`, `stateDiagram-v2`, `classDiagram`, `erDiagram`). Define the classes once at the top, then tag nodes -- this keeps the color decisions in one place and makes the semantics legible in the source:

```
flowchart LR
    classDef internal fill:#E8F0FE,stroke:#1A73E8,color:#10367A;
    classDef external fill:#F1F3F4,stroke:#9AA0A6,color:#3C4043;
    classDef store    fill:#FEF7E0,stroke:#F9AB00,color:#7A5900;
    classDef success  fill:#E6F4EA,stroke:#34A853,color:#1E4620;
    classDef failure  fill:#FCE8E6,stroke:#EA4335,color:#8C1D18;
    classDef decision fill:#F3E8FD,stroke:#A142F4,color:#4A1E7A;

    User([User]):::decision
    Harness[Agent Harness]:::internal
    Planner[Planner]:::internal
    OpenAI[OpenAI API]:::external
    Memory[(Memory)]:::store
    Done[Result returned]:::success

    User -->|submits request| Harness
    Harness -->|requests plan| Planner
    Planner -->|calls| OpenAI
    Harness -->|persists state| Memory
    Harness -->|returns result| Done
```

For a subgraph boundary background, style the subgraph directly rather than adding a new node color:

```
    style Boundary fill:#F8F9FA,stroke:#DADCE0,color:#3C4043
```

## Applying it -- sequence, journey, timeline, etc.

Diagram types that don't take `classDef` are themed with an init directive. Set only the variables you need and leave the rest to Mermaid's `base` theme so contrast defaults stay sane:

```
%%{init: {'theme':'base','themeVariables':{
    'primaryColor':'#E8F0FE',
    'primaryBorderColor':'#1A73E8',
    'primaryTextColor':'#10367A',
    'actorBkg':'#E8F0FE',
    'actorBorder':'#1A73E8'
}}}%%
sequenceDiagram
    participant U as User
    participant H as Harness
    U->>H: submits request
    H-->>U: returns result
```

Keep the same hex values as the table -- the init directive is just a different delivery mechanism for the identical palette, not a license to recolor.

## Accessibility

- **Never rely on color alone.** The palette is a reinforcement, not the primary signal -- pair it with a label, shape, or line style, per the color rule in SKILL.md. A reader who can't see the colors (grayscale print, screen reader, colorblindness) must still get the full meaning.
- **Grayscale-safe by lightness.** The six fills fall at different lightness levels, so they remain distinguishable when printed black-and-white. Red and green are the classic confusable pair for colorblind readers, so make sure success/failure are *also* separated by label or shape (e.g. `Done` vs `Error`, rounded vs. hexagon), never by hue alone.
- Set `accTitle`/`accDescr` (see `rubric.md`) so the diagram's meaning survives even when color and rendering don't.

## Dark backgrounds

These tints assume a light background. If the docs render on a dark theme, don't hand-darken each fill -- switch to Mermaid's `dark` base theme and use the palette's **stroke** colors as accents on transparent/dark fills, keeping the same hues so a role reads the same across both themes. If a project standardizes on dark rendering, add a dark-variant table here rather than improvising per diagram.
