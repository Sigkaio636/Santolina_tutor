# Diseño: El reparto global de la superficie se mantiene (las 10 regiones con más superficie pasan del 40 % al 41 %), pero 7 de 40 regiones cambian ≥ 2 puntos: Region J gana más (+4,6 pp) y Region AB pierde más (−4,3 pp)

| | |
|---|---|
| Registro de decisión | `p-rank-change-two-points--area-share-shift-by-region-20261107` v1 · nuevo, derivado del seed `rank-change-two-points--slope-chart` (tier REUSE, 0,83) con el idioma cambiado · **status candidate** (ejecución autónoma, nada confirmado por el usuario; guardado con `--assumed`) |
| Librería / host | matplotlib 3.10.7 (`project.yaml`: library matplotlib, host script, output_dir out) · script |
| Datos | `events.csv`, 1 200 filas, firma `table\|k:categorical:many+k:temporal:few\|v:quantitative:share`, periodo 2015-01-01 … 2024-12-29; dos ventanas: 2015-2017 (370 eventos) y 2022-2024 (364 eventos) |
| Salidas | `out/area_share_shift_by_region.py`, `out/area_share_shift_by_region.png`, `out/area_share_shift_by_region.svg`, `out/answers.json`, `out/record.json`, `out/run_check.json`, `out/inspect/*` (escala de grises y simulaciones CVD) |
| Idioma | diálogo es, código en |

## 1. Caracterización del problema (dominio)
- Lector: `domain-expert` — conoce las regiones y la unidad (ha); lee durante minutos; tolera 40 filas si las etiquetas son las suyas; literacy media; sin interacción. Modificadores: ninguno. **Inferido**: el prompt no nombra al lector; la regla de `stage1-domain.md` ("otherwise `domain-expert`") se aplica.
- Modo: `analysis` (default del perfil `domain-expert`): hay una hipótesis que verificar ("¿ha cambiado el reparto?"), no un mensaje conocido de antemano. El título, aun así, enuncia el hallazgo calculado, como exigen las reglas del skill.
- Pregunta, en palabras del lector: "¿Ha cambiado el reparto de la superficie (AREA_HA) entre regiones entre el inicio y el final del periodo de events.csv?"
- Medio y restricciones: figura estática (`static-only`): el usuario pidió matplotlib, que no tiene interacción; se asume informe o cuaderno.
- Lecturas rechazadas del problema: (a) "¿cómo ha evolucionado la superficie por región año a año?" (trend-many-series: 10 años × 40 regiones, otra figura); (b) "¿ha cambiado la distribución de los tamaños de evento (AREA_HA por evento)?" (distribution-change-over-time con ridges/histogramas: el prompt dice "reparto entre regiones", es decir cuota por región, no tamaño por evento); (c) "¿qué regiones tienen más superficie en todo el periodo?" (compare-values-across-categories: ignora el "inicio vs final").
- Validación (amenaza: problema equivocado): reformulación "un experto del dominio quiere saber si la cuota de superficie de cada región al final del periodo difiere de la del inicio, en una figura estática de análisis" — **asumida, no confirmada por el usuario** (ausente). No hecho: observar/entrevistar lectores reales; adopción.

## 2. Abstracción de datos y tareas
| atributo | tipo | rol | niveles/rango | notas (parseo, faltantes, grano) |
|---|---|---|---|---|
| EVENT_DATE | temporal | clave `time` (reducida a 2 periodos) | 2015-01-01 … 2024-12-29, 10 años, grano día | formato `%d/%m/%Y`; sin faltantes |
| REGION_CODE | identificador | descartado | 40 códigos con ceros a la izquierda | leído como texto; redundante con REGION |
| REGION | categórico (geo-code sin geometría) | clave `category` | 40 niveles (banda `many`) | sin fichero de geometría → sin mapa |
| CAUSE | categórico | no usado | 4 niveles | la pregunta no lo menciona |
| AREA_HA | cuantitativo | valor (base de la cuota) | 0,00 … 30,39 ha; 2 eventos con 0 ha | suma por periodo y región |
| COST_EUR | cuantitativo | no usado | 0,87 … 3 718,75 | la pregunta habla de superficie |
- Datos derivados (mismos nombres en `derive()`):
  - `period` = "inicio" si año(EVENT_DATE) ∈ {2015, 2016, 2017}; "final" si ∈ {2022, 2023, 2024}; el resto (2018-2021) se excluye.
  - `area_period` = Σ AREA_HA por (period, REGION); `n_events` = nº de eventos por (period, REGION).
  - `share_pct` = 100 · area_period / Σ AREA_HA del periodo (las cuotas de cada periodo suman 100 %).
  - `delta_pp` = share_pct(final) − share_pct(inicio), en puntos porcentuales.
  - `top10_share(period)` = suma de las 10 cuotas mayores del periodo (resumen de concentración para el título).
  - Normalización: cuota sobre el total del periodo (parte/todo), que es lo que "reparto" significa; no hace falta un denominador externo (superficie o población de la región) porque la pregunta es sobre el reparto, no sobre la incidencia.
  - Grano temporal: dos ventanas de 3 años. Con un solo año habría ~3 eventos por región (mediana) y las cuotas serían casi todo ruido; con 3 años la mediana es 9 eventos por región y periodo. Las ventanas no se solapan y dejan fuera 2018-2021.
- Tareas: why present / locate / compare; low-level (ordenadas) gist ("¿ha cambiado?"), find-extremum (qué región gana/pierde más), compare (cuota inicio vs final por región), sort, compute-derived (delta); temporal rate-of-change; Shneiderman overview.
- Abstracciones rechazadas: cuota por año (10 columnas × 40 regiones: tendencia, no "inicio vs final"); un solo año en cada extremo (demasiado ruido, ver arriba); superficie absoluta en vez de cuota (no responde a "reparto"); mediana de AREA_HA por evento (es tamaño de evento, no reparto).
- Validación (amenaza: abstracción equivocada): "reparto de la superficie" → `share_pct` sobre Σ AREA_HA; "entre regiones" → REGION (40); "inicio y final del periodo" → `period` definido como las 3 primeras y 3 últimas años de EVENT_DATE; "ha cambiado" → `delta_pp` + resumen de concentración. Ningún término exige un atributo que falte. Las tareas bastan: gist se responde con el título calculado y la longitud de los segmentos; find-extremum con el orden. **Asumida, no confirmada por el usuario**; la definición de los periodos es el supuesto más fuerte (ver §6).

## 3. Codificación visual e interacción
- Idioma: `dumbbell_plot` (catálogo, familia slope), 40 filas ordenadas por cambio.
| atributo | marca + canal | rango (Mackinlay) | comprobación de expresividad |
|---|---|---|---|
| REGION (category) | fila: position-y ordinal, ordenada por `delta_pp` desc | position: 1.º para nominal | nominal en posición; el orden codifica el cambio, dicho en el título del eje |
| share_pct (measure) | point: position-x lineal desde 0 | position en escala común: 1.º para cuantitativo | marca de posición; el eje empieza en 0 porque la cuota tiene cero natural |
| period (time, 2 niveles) | shape (círculo hueco = inicio, relleno = final) + color-luminance (claro → oscuro) | luminancia: ordenada; shape: nominal | 2 niveles ordenados; la luminancia conserva el orden, la forma lo redunda (EXP-02 evitado: no hay tono por periodo) |
| REGION (connection) | segmento entre los dos puntos; longitud = \|delta_pp\| | length: 3.º para cuantitativo | la longitud sale de dos posiciones en escala común (EFF-06) |
| highlight (\|delta_pp\| ≥ 2 pp) | color-hue: azul gana, bermellón pierde; resto gris | — | un solo rasgo pop-out; umbral declarado en la leyenda |
| delta_pp (derived) | text al final de cada fila, con signo | — | valor exacto para el experto (retrieve-value) |
- Orden, escalas, líneas base, facetas: filas por `delta_pp` descendente (ganancias arriba, pérdidas abajo; CMP-01); eje x lineal 0-8,2 % con rejilla vertical gris claro para leer cuotas; sin facetas; figura alta (10 × 14,4 in) para 40 filas legibles sin rotar etiquetas (SCL-12).
- Plan de color: propósito highlight; paleta neutral + acento: gris `#8c8c8c`, azul Okabe-Ito `#0072b2` (gana), bermellón Okabe-Ito `#d55e00` (pierde); puntos `#bdbdbd` / `#4d4d4d` por periodo. `colorcheck.check_palette` → `ok_for_cvd: true`, sin pares confundibles en deuteranopía, protanopía ni tritanopía. Segundo indicio: signo impreso en la etiqueta, orden de las filas, negrita en las regiones destacadas, hueco/relleno para el periodo (COL-02/04/05).
- Plan de texto: título calculado en `takeaway()` → renderizado: **"El reparto global de la superficie se mantiene: las 10 regiones con más superficie pasan del 40 % al 41 % del total / pero 7 de 40 regiones cambian ≥ 2 puntos: Region J gana más (+4,6 pp) y Region AB pierde más (−4,3 pp)"**; subtítulo con la definición de la medida, los dos periodos con sus eventos y hectáreas, y los años excluidos; títulos de eje con unidades ("% de la suma de AREA_HA del periodo"; "Región (ordenadas por cambio de cuota, pp)"); etiquetas directas de delta en cada fila; leyenda mínima de 4 entradas que explica la lectura de una fila (periodo hueco/relleno, umbral de acento); pie con fuente, n, mediana de eventos por región y aviso de ruido muestral (TXT-01/02/04/08, DAT-03).
- Plan de interacción: ninguna (medio estático, matplotlib); el estado único responde a la tarea principal (INT-02).
- Idiomas rechazados:
| idioma | motivo | regla |
|---|---|---|
| slope_chart (default almacenado, seed `rank-change-two-points--slope-chart`) | 40 regiones con cuotas apiñadas entre 0,5 y 6,7 %: 40 etiquetas directas en cada extremo colisionan (separación mediana ≈ 0,15 puntos) y las 40 líneas se cruzan en espagueti; perdería la etiqueta directa que es su razón de ser | EFF-16, TXT-10 |
| bar_chart de `delta_pp` | una barra por región oculta los niveles de los que sale el cambio (una subida de 1 pp desde 1 % no es lo mismo que desde 5 %) | EFF-19 |
| multiset_barchart (barras pareadas) | 80 barras; la dirección del cambio se lee comparando alturas, no es inmediata | EFF-19 |
| bump_chart | solo rangos; la magnitud de la cuota importa | EXP-18 |
| heatmap región × periodo | dos columnas de color: un cambio de 1-2 pp es invisible en luminancia | EFF-01 |
| pie_chart (dos tartas) | 40 porciones, dos tartas no comparables | IDM-PIE |
| stacked_bar_graph 100 % (dos barras) | 40 segmentos sin línea base común | IDM-STACK |
| choropleth / small-multiple maps | no hay fichero de geometría (`no-geometry-file`) | IDM-MAP |
- Validación (amenaza: idioma equivocado):
  a. Lista de reglas: CMP-01 pass (filas ordenadas por delta); TXT-04 pass (delta impreso por fila; la leyenda solo explica la codificación, no identifica elementos); EFF-09 pass (los únicos tonos van a las 7 regiones que el título nombra como cambios relevantes); EXP-13 pass (ventanas simétricas de 3 años en ambos extremos, declaradas en el subtítulo, años excluidos nombrados); COL-05 pass (`colorcheck` ok; gris/azul/bermellón distinguibles en las tres simulaciones de `out/inspect/`); SCL-06 pass (ambos ejes con título y unidad; el inspector lo señaló en la primera versión y se corrigió); TXT-08 pass (fuente, n, periodos, definición); DAT-03 parcial (el ruido muestral se avisa en el pie con la mediana de eventos por región, pero no se dibuja un intervalo; ver §6); EXP-08 n/a (no hay marcas de longitud desde un eje: los segmentos unen dos posiciones); EXP-02 pass (periodo por luminancia y forma, no por tono); SCL-12 pass (etiquetas horizontales).
  b. Tabla tarea-tiempo: gist → inmediato (título + longitud de los segmentos: casi todos cortos); find-extremum → inmediato (primera y última fila, acento); compare inicio/final por región → inmediato (dos puntos en la misma fila y escala); sort → inmediato (ya ordenado); compute-derived → inmediato (delta impreso); retrieve-value de una cuota → trabajo (leer la posición contra la rejilla, precisión ≈ 0,1 pp).
  c. Render inspeccionado: `out/area_share_shift_by_region.png`; escala de grises `out/inspect/area_share_shift_by_region_grayscale.png` (ganancias y pérdidas se distinguen por el signo y el orden; las 7 regiones destacadas por grosor y negrita); deuteranopía/protanopía/tritanopía en `out/inspect/` (azul y bermellón siguen separados). Hallazgo del inspector de imagen: CLT-03 minor (menos del 5 % de píxeles con tinta) — inherente a 40 filas con marcas finas; aceptado.
  d. Crítica (opcional): no ejecutada (`vis-value-critique` está instalado; sus inspectores deterministas corrieron dentro de `run_check.py`).
  e. Aceptación del lector: **asumida, no confirmada** (usuario ausente). Una sola revisión interna: título del eje y, cabecera compacta, leyenda sin glifos duplicados.

## 4. Algoritmo
- matplotlib 3.10.7 (pandas 2.3.3), host script, pipeline `load → derive → build_chart → save` (`takeaway()` calcula el título). `DATA_PATH` se resuelve relativo al script (`../events.csv`) para que los inspectores, que importan el módulo desde `out/`, encuentren los datos.
- Filas de entrada 1 200; filas en los dos periodos 734; filas tras derivar 40 (una por región); tiempo de ejecución 2,3 s (script) + 2,4 s (inspectores); límites: sin interacción; figura de 14,4 in de alto (200 dpi → 2 664 × 2 867 px); PNG y SVG.
- Alternativas rechazadas: Altair (no instalado; sin `vl_convert` no renderizaría PNG); Plotly (instalado, pero sin `kaleido` no hay PNG y la interacción no se necesita); Streamlit (no instalado, no pedido). El usuario pidió matplotlib explícitamente.
- Validación (amenaza: algoritmo equivocado): `run_check.py` → `ok: true`; salidas PNG + SVG; inspectores del sibling: 0 hallazgos tras corregir SCL-06 (primera pasada: "y axis has no title", major, corregido); `inspect_image.py`: CLT-03 minor; sin hallazgos bloqueantes. El render coincide con §3: 40 filas ordenadas por delta, eje x desde 0 con unidades, hueco/relleno por periodo, 3 azules arriba y 4 bermellones abajo, delta impreso, título calculado, pie con fuente y n. Primer intento de `run_check.py` falló por rutas relativas (el script se ejecuta con cwd = carpeta del script); se repitió con rutas absolutas.

## 5. Registro de decisión
Guardado por `record_decision.py --assumed` en `.claude/vis-decisions/p-rank-change-two-points--area-share-shift-by-region-20261107.yaml` (`project.yaml`: library matplotlib, host script, output_dir out). Clave: (rank-change-two-points, analysis, domain-expert, `table|k:categorical:many+k:temporal:few|v:quantitative:share`).
```yaml
# vis-design decision record (project)
schema_version: 1
status: candidate
title: Area share shift by region
language: es
problem:
  archetype: rank-change-two-points
  catalog_functions:
  - comparisons
  - data-over-time
  statement: ¿Ha cambiado el reparto de la superficie (AREA_HA) entre regiones entre el inicio (2015-2017)
    y el final (2022-2024) del periodo?
  mode: analysis
  domain_examples:
  - share of burnt area per region at the start vs the end of a decade of events
user:
  profile: domain-expert
  modifiers: []
tasks:
  why:
    goal: present
    search: locate
    query: compare
  low_level:
  - compare
  - compute-derived
  - sort
  - find-extremum
  - gist
  temporal:
  - rate-of-change
  shneiderman:
  - overview
data:
  dataset_type: table
  keys:
  - role: time
    type: temporal
    cardinality: few
    grain: year
    n_levels: 2
  - role: category
    type: categorical
    cardinality: many
    n_levels: 40
  values:
  - role: measure
    type: quantitative
    semantics: share
    derived: true
    derivation: share_pct = 100 * sum(AREA_HA) per (period, REGION) / sum(AREA_HA) per period
  items: tiny
  signature: table|k:categorical:many+k:temporal:few|v:quantitative:share
constraints:
- static-only
solution:
  idiom: dumbbell_plot
  family: slope
  mark: point
  encodings:
  - attribute: category
    channel: position-y
    scale: ordinal
    sort: delta_pp descending (gains on top, losses at the bottom)
  - attribute: measure
    channel: position-x
    scale: linear
    zero: true
    note: share of the period total, %
  - attribute: time
    channel: shape
    scale: nominal
    note: open circle = first period, filled circle = last period
  - attribute: time
    channel: color-luminance
    scale: ordinal
    note: light grey = first period, dark = last period
  - attribute: category
    channel: connection
    note: segment joining the two dots of a region; its length is |delta_pp|
  - attribute: highlight
    channel: color-hue
    scale: nominal
    note: 'accent only on regions with |delta_pp| >= 2: blue gain, vermillion loss; the rest grey'
  - attribute: derived
    channel: text
    note: delta_pp printed at the row end with its sign
  derived_data:
  - period = 'inicio' if year(EVENT_DATE) in 2015..2017, 'final' if year in 2022..2024, else excluded
  - area_period = sum(AREA_HA) per (period, REGION)
  - share_pct = 100 * area_period / sum(AREA_HA) per period
  - delta_pp = share_pct(final) - share_pct(inicio)
  - top10_share(period) = sum of the 10 largest share_pct in that period
  - n_events per (period, REGION) for the footer
  ordering: rows sorted by delta_pp descending; the two period dots labelled once on the top row instead
    of a legend
  color:
    purpose: highlight
    palette_type: neutral-accent
    suggested:
    - '#8c8c8c'
    - '#0072b2'
    - '#d55e00'
    cvd_safe: true
    second_cue: sign printed in the delta label, sorted order, open vs filled dot for the period
  text:
    title: takeaway
    axis_units: true
    direct_labels: true
    annotations:
    - period definition and measure definition in the subtitle
    - delta in percentage points at each row end
    - events per period and median events per region in the footer
    source_line: true
  interaction:
    level: none
    default_state_answers_task: true
    intents: []
  layout:
    small_multiples: false
    facet_by: null
    aspect: tall
  rejected_alternatives:
  - idiom: slope_chart
    reason: 'stored default, but 40 regions whose shares cluster in a 0.5-6.7 % band need 40 direct labels
      at each end: they collide and the lines become spaghetti; the dumbbell gives each region its own
      row'
    rule: EFF-16
  - idiom: bar_chart
    reason: a single bar of delta_pp hides the levels the delta comes from; paired bars per region double
      the marks and hide direction
    rule: EFF-19
  - idiom: bump_chart
    reason: ranks only; the magnitude of the share matters
    rule: EXP-18
  - idiom: heatmap
    reason: two columns of colour cells make a 1-2 pp change invisible; luminance is a weak channel for
      the main task
    rule: EFF-01
  - idiom: pie_chart
    reason: two pies of 40 slices cannot be compared
    rule: IDM-PIE
  - idiom: stacked_bar_graph
    reason: 'two 100 % stacked bars with 40 segments: middle segments have no baseline'
    rule: IDM-STACK
  validation:
    stage3_checks:
    - CMP-01
    - TXT-04
    - EFF-09
    - EXP-13
    - COL-05
    - SCL-06
    - TXT-08
    - DAT-03
    critique_skill: optional
  library_notes:
    altair: mark_rule between the two shares + two mark_point layers; sort y by delta; mark_text for delta
    matplotlib: ax.hlines per row + two scatter calls (open/filled); ax.text for delta; tall figsize
    plotly: go.Scatter lines per row (mode lines) + two marker traces; annotations for delta
rationale: Two periods and forty regions is the shape of rank-change-two-points; the stored slope chart
  (seed rank-change-two-points--slope-chart, REUSE 0.83) was rejected by the stage-3 rule checklist because
  40 end labels in a 6-point band collide (EFF-16). A dumbbell sorted by change gives every region its
  own row, puts the shares on a common zero-based x axis (position, the top channel) and the change on
  segment length and sorted order, so gist, find-extremum and compare are immediate; the concentration
  summary (top-10 share) in the computed title answers whether the overall split changed.
confidence: medium
provenance:
  origin: project
  author: vis-design (autonomous run, assumptions not confirmed)
  sources:
  - seed rank-change-two-points--slope-chart
  - seed distribution-change-over-time--share-shift-slope
  - chart-catalog dumbbell_plot
  created: '2026-11-07'
  updated: '2026-11-07'
  times_used: 1
  last_used: '2026-11-07'
id: p-rank-change-two-points--area-share-shift-by-region-20261107
```

## 6. Supuestos y puntos abiertos
Ejecución autónoma: el usuario estaba ausente y `AskUserQuestion` no está disponible; ninguna pregunta se hizo. Cada pregunta del cuestionario tomó su default:

| id | respuesta asumida | motivo |
|---|---|---|
| S1.reader | `domain-expert` | inferido del prompt: sin pista de lector; regla "otherwise domain-expert" (`stage1-domain.md`) |
| S1.mode | `analysis` | default del perfil `domain-expert` (`profiles/users`) |
| S1.question | "¿Ha cambiado el reparto de AREA_HA entre regiones entre el inicio y el final del periodo?" | texto libre del prompt mapeado con `task-mapping.md` ("reparto" + "entre el inicio y el final" → rank-change-two-points con cuotas; segunda lectura distribution-change-over-time, misma solución almacenada) |
| S1.medium | informe / figura estática (`static-only`) | inferido: el usuario pidió matplotlib; sin otra pista |
| V1.confirm | "Correcto" | asumido, no confirmado |
| S2.task | rank-change-two-points: compare, compute-derived, sort, find-extremum, gist (rate-of-change) | default del arquetipo + gist por la forma de la pregunta ("si ha cambiado") |
| S2.data | clave time (2 periodos) × category REGION (40); valor share de Σ AREA_HA | abstracción del perfil `sum of AREA_HA per EVENT_DATE (year) × REGION`, con el año reducido a dos periodos |
| S2.derive | cuota sobre el total del periodo; periodos = 3 primeros (2015-2017) y 3 últimos (2022-2024) años; 2018-2021 excluidos | catalog/seed default ("first and last n years, stated"); n = 3 elegido porque n = 1 deja ~3 eventos por región; el usuario podría preferir 1, 2 o 5 años, o mitades del periodo |
| V2.confirm | "Correcto" | asumido, no confirmado |
| S3.idiom | `dumbbell_plot` | el default almacenado (`rank-change-two-points--slope-chart`, REUSE 0,83) se rechazó en la lista de reglas de la etapa 3 (EFF-16/TXT-10 con 40 etiquetas apiñadas); se tomó el segundo candidato del catálogo para el arquetipo |
| S3.color | neutral + acento (azul gana / bermellón pierde en \|Δ\| ≥ 2 pp) | default del seed; el umbral de 2 pp es una elección de diseño, no estadística |
| S3.interaction | ninguna | default con `static-only` |
| S4.library | matplotlib | pedido por el usuario; persistido en `project.yaml` |
| S4.host | script (PNG + SVG) | Recommended |
| S4.validate3 | lista de reglas + inspección del render (inspectores del sibling, grises y CVD) | Recommended; `vis-value-critique` completo no ejecutado |
| S4.output | `out/`, registrar la decisión | pedido por el usuario ("Salida en out/"); registro con `--assumed` → status candidate |
| V3.accept | "Aceptar" | asumido, no confirmado |

Puntos abiertos:
1. Definición de los periodos (3 + 3 años). Cambiar `PERIOD_YEARS` en el script recalcula todo; con 1 año (2015 vs 2024) los mayores cambios son otros (Region AL +5,7 pp, Region AC −5,3 pp), señal de que buena parte de los cambios por región es ruido muestral.
2. Incertidumbre (DAT-03): con una mediana de 9 eventos por región y periodo no se ha calculado ningún intervalo; el pie lo avisa. Un bootstrap por región o un test de homogeneidad de la distribución (χ² sobre las sumas de área no es válido; haría falta permutación) sería el siguiente paso si el lector quiere afirmar "ha cambiado" con respaldo estadístico.
3. El resumen de concentración del título (cuota de las 10 primeras: 40 % → 41 %) es una elección; HHI (299 → 313) o el índice de Gini darían el mismo veredicto ("se mantiene") y se podrían añadir al subtítulo.
4. Lector y modo son inferidos; si el destinatario fuera público general o un directivo, el perfil cambiaría la clave de la decisión y convendría reducir a las 7 regiones destacadas más "resto".
5. Validaciones fuertes de Munzner (observar lectores, adopción) no realizadas.
