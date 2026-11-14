# Catalog extraction protocol (datavizcatalogue.com)

This protocol is handed to the fetch agents that build `chart-catalog.json`. The catalog
records facts from the site (which functions a chart serves, which charts it lists as
similar, which tools draw it) and **our own** characterization of each chart. Nothing
from the site is stored verbatim: descriptions are paraphrased under word caps, and the
anatomy image is never downloaded.

## Pages

- Index: `https://datavizcatalogue.com/index.html` (lists every chart).
- Function pages: `https://datavizcatalogue.com/search/<function>.html` where `<function>`
  is one of: comparisons, proportions, relationships, hierarchy, concepts, location,
  part_to_a_whole, distribution, how_things_work, methods, movement, patterns, range, time,
  text, reference. Each lists its member charts.
- Chart pages: `https://datavizcatalogue.com/methods/<slug>.html`, with sections
  Description, Functions, Anatomy (image only), Similar Charts, Tools, Examples.

## Function ids used in our files

| site slug | our id |
|---|---|
| comparisons | comparisons |
| proportions | proportions |
| relationships | relationships |
| hierarchy | hierarchy |
| concepts | concepts |
| location | location |
| part_to_a_whole | part-to-a-whole |
| distribution | distribution |
| how_things_work | how-things-work |
| methods | processes-and-methods |
| movement | movement-or-flow |
| patterns | patterns |
| range | range |
| time | data-over-time |
| text | analysing-text |
| reference | reference-tool |

## Per-chart record produced by the fetch agents

```json
{
  "id": "<slug exactly as in the URL>",
  "name": "<chart name as titled on the page>",
  "aliases": ["<names after 'Also known as', if any>"],
  "source": {"url": "https://datavizcatalogue.com/methods/<slug>.html",
             "fetched": "YYYY-MM-DD", "fetched_ok": true},
  "functions": ["<our function ids>"],
  "summary": "<own words, what the chart shows and how it is read, <= 60 words>",
  "anatomy": "<own words, the visual parts a reader must recognise, <= 40 words>",
  "fits": ["<= 6 short phrases: situations the chart suits"],
  "limits": ["<= 6 short phrases: limitations and misreadings the page warns about or that are well known"],
  "similar": ["<slugs of the charts listed under Similar Charts>"],
  "tools_listed": ["<= 8 code-based tool names listed on the page"]
}
```

Paraphrase rules: read the page, close it mentally, then write `summary`, `anatomy`,
`fits` and `limits` in your own sentences. No sentence may start the way a sentence on the
page starts; no phrase longer than six consecutive words may be copied. Lists hold at most
twelve words per item. If a page cannot be fetched, keep the slug, set `fetched_ok: false`,
leave `similar`/`tools_listed` empty and write the paraphrase fields from general
knowledge of that chart type.

## Curation (done afterwards, without the web)

The `ours` block is added per entry: `family`, `munzner {mark, channels}`, `data_shape`
(dataset type, key and value types with cardinality bands), `tasks` (Amar / temporal ids
from `profiles/vocab.yaml`), `scalability`, `mode_fit`, `profile_fit`, `discouraged` with
the rule that discourages it, `rules`, `chart_types_md_section` (the heading in the sibling
skill's `chart-types.md`, if any), `library_support` (altair / matplotlib / plotly:
native | workaround | none), `archetypes`. `build_index.py --check` validates ids, word
caps and cross-references, then regenerates `references/chart-catalog.md`.
