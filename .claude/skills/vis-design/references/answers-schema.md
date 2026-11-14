# answers.json (stages 1–2) — input of `match_decision.py`

The skill writes this file after call 2 (and updates it after call 3–4 before recording).
It is a decision record without the `solution`, `rationale`, `confidence` and `provenance`
blocks. Enumerated values come from `profiles/vocab.yaml`; free text may be in the user's
language.

```json
{
  "title": "Incidents per region, whole period",
  "language": "es",
  "problem": {
    "archetype": "compare-values-across-categories",
    "catalog_functions": ["comparisons"],
    "statement": "¿Qué regiones concentran más incidentes en el periodo?",
    "mode": "explanatory"
  },
  "user": {"profile": "general-public", "modifiers": ["cvd"]},
  "tasks": {
    "why": {"goal": "present", "search": "lookup", "query": "compare"},
    "low_level": ["compare", "find-extremum", "sort", "retrieve-value"],
    "temporal": [],
    "shneiderman": ["overview"]
  },
  "data": {
    "dataset_type": "table",
    "source_file": "data.csv",
    "keys": [{"role": "category", "type": "categorical", "cardinality": 42, "source_column": "REGION"}],
    "values": [{"role": "measure", "type": "quantitative", "semantics": "count",
                "derived": true, "derivation": "count of rows per REGION", "unit": "incidents"}],
    "items": "tiny",
    "filters": [],
    "normalization": null,
    "parse": {"delimiter": ",", "decimal": ".", "date_format": "%d/%m/%Y", "code_columns": ["REGION_CODE"]}
  },
  "constraints": ["static-only"],
  "library": "altair",
  "host": "script",
  "stage_validation": {"stage1": "confirmed", "stage2": "confirmed"}
}
```

Notes:

- `data.keys[].cardinality` may be an integer (distinct levels) or a band; the scripts
  compute the band and the signature. `source_column`, `unit`, `parse`, `filters` and
  `normalization` are kept for code generation and ignored by the matcher.
- `library` and `host` are optional here; they are stored in `project.yaml`, not in the
  record key.
- `stage_validation` values: `confirmed` | `assumed` | `failed`. A `failed` stage 2
  (missing attribute) ends the run with a design document and no code.
- After call 3 the skill adds `solution`, `rationale`, `confidence` and passes the whole
  object to `record_decision.py`.
