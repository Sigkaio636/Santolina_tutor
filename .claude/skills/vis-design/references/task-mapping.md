# Mapping a free-text question to the abstract vocabulary

Use when the user types their own question (S1.question "Other"). Match phrases in any
of the three languages; combine the data profile (which key types exist) to pick the
archetype. Keep the two best mappings and let the user confirm in S2.task.

| Phrase triggers (ES · CA · EN) | why (goal/search/query) | low-level tasks | temporal | archetype (needs) |
|---|---|---|---|---|
| cuántos por / cuál tiene más / comparar entre · quants per / quin té més · how many per / which has the most / compare across | present/lookup/compare | compare, find-extremum, sort | — | compare-values-across-categories (1 categorical key, 1 value); compare-two-keys if two categorical keys |
| reparto / proporción / porcentaje del total / cuota · repartiment / percentatge · share of / proportion / breakdown / percent of total | present/lookup/identify | gist, retrieve-value | — | part-to-whole-single (parts sum to a whole); part-to-whole-over-time if a time key |
| evolución / tendencia / a lo largo de / cómo ha cambiado · evolució / al llarg de · trend / over time / evolution / how has … changed | present or discover/browse/compare | trend, compare, find-extremum | pattern, rate-of-change | trend-single-series (1 series); trend-few-series (2–7); trend-many-series (8+); category-breakdown-over-time if counts per category |
| entre X y Y / antes y después / respecto a · abans i després · between year X and Y / before vs after / compared with last | present/locate/compare | compare, sort, compute-derived | rate-of-change | rank-change-two-points (two moments, many items) |
| distribución de los valores / cómo se distribuye / histograma / outliers · distribució · distribution of / spread / outliers / histogram | discover/browse/summarize | characterize-distribution, find-anomalies | — | distribution-single (numeric variable per item); **ambiguous**: "distribución de X entre Y" → compare-values-across-categories; show both |
| ha cambiado la distribución / se ha concentrado · s'ha concentrat · has the distribution changed / more concentrated | discover/browse/compare | characterize-distribution, compare, trend | pattern, rate-of-change | distribution-change-over-time when the value is a numeric variable per item (spread); **rank-change-two-points** when the question is the share of each category at the start vs the end (value = share) |
| por grupo / según / diferencias entre grupos en · per grup · by group / differences between groups in | discover/browse/compare | characterize-distribution, compare | — | distribution-compare-groups (categorical key, raw numeric values) |
| dónde / en qué zonas / mapa / por comarca, provincia, región, municipio · on / mapa · where / map / by region, county, district | present/locate/identify | find-extremum, cluster | — | spatial-distribution (geo key, needs geometry; else sorted bars); spatial-change-over-time if time key; point-events-on-map if coordinates per event |
| estacionalidad / por mes / por día de la semana / ciclo · estacionalitat · seasonal / by month / by weekday / cycle | discover/browse/identify | find-anomalies, trend | pattern, temporal-location | seasonality-cycles |
| cuándo / duración / calendario / cronología · quan / durada · when / how long / timeline / schedule | present/lookup/identify | determine-range, sort | existence, interval, sequence | event-timeline-intervals |
| relación entre / correlación / depende de · relació · relationship / correlation / depends on / vs | discover/explore/compare | correlate, find-anomalies | — | correlation-two-quantities (2 values); multivariate-relationships (3+) |
| patrón / combinaciones / matriz / cruce de · patró · pattern / combinations / matrix / cross of | discover/browse/identify | cluster, find-anomalies | — | matrix-pattern-two-keys |
| jerarquía / organigrama / estructura / árbol · jerarquia · hierarchy / org chart / structure / tree | present/lookup/identify | retrieve-value, cluster | — | hierarchy-structure; part-to-whole-hierarchy if sizes matter |
| red / conexiones / quién con quién / comunidades · xarxa · network / connections / who with whom | discover/explore/identify | cluster, find-anomalies | — | network-relationships |
| flujo / de dónde a dónde / transferencias · flux · flow / from … to … / transfers / where does it go | present/browse/compare | find-extremum, compare | — | flow-between-states |
| objetivo / meta / umbral / frente a plan · objectiu / llindar · target / goal / threshold / vs plan | present/lookup/compare | compare, compute-derived | — | compare-against-target |
| rango / mínimo y máximo / intervalo / incertidumbre · rang · range / min and max / interval / uncertainty | present/lookup/compare | determine-range, compare | — | range-per-item |
| palabras / términos / texto · paraules · words / terms / text frequency | discover/browse/summarize | find-extremum, sort | — | text-frequency |
| pasos / proceso / cómo funciona · passos / procés · steps / process / how it works | present/lookup/identify | gist | sequence | process-sequence (not a data chart) |
| solapamiento / en común / conjuntos · solapament · overlap / in common / sets | present/lookup/identify | retrieve-value, compare | — | set-overlap |
| valores exactos / tabla / cifras · valors exactes / taula · exact values / table / figures | present/lookup/identify | retrieve-value, sort | — | exact-values-lookup |

Rules for the mapping:

- The archetype must fit the data profile: a "by region over time" question with no
  temporal column is `spatial-distribution`, and the document notes that time is absent.
- "Distribution" is the known ambiguity: always produce both readings as options.
- "Causes", "reasons", "types" refer to a categorical attribute; if none exists the
  stage-2 validation fails (missing attribute), it does not degrade to another archetype.
- Confidence: high when a trigger phrase and the data shape agree; medium when only the
  phrase matches; low when neither is clear → ask in call 6 instead of guessing.
