# Problem archetypes (generated from profiles/problems/*.yaml by build_index.py)

An archetype is a family of questions with an expected data shape, default tasks and preferred
idioms. Stage 1 maps the user's question to one archetype; the seeds under decisions/seed/ hold
the declared solutions per (archetype, data shape, profile, mode).

| id | question | functions | preferred idioms | seeds |
|---|---|---|---|---|
| `categorical-state-over-time` | Which {category} state occurs when, and for how long? | data-over-time, patterns | heatmap, gantt_chart, timeline, small_multiples, stacked_bar_graph | categorical-state-over-time--binned-state-heatmap |
| `category-breakdown-over-time` | How has the number of {events} by {category} evolved over {time}? | data-over-time, proportions | line_graph, small_multiples, stacked_bar_graph, stacked_area_graph, heatmap | category-breakdown-over-time--lines-few-categories |
| `compare-against-target` | Is {measure} on target for each {category}? | comparisons, range | bullet_graph, bar_chart, dumbbell_plot | compare-against-target--bullet-per-kpi |
| `compare-two-keys` | How does {measure} vary by {category} and {category2}? | comparisons, patterns | multiset_barchart, heatmap, dumbbell_plot, small_multiples, stacked_bar_graph | compare-two-keys--grouped-bars-few-few, compare-two-keys--heatmap-one-key-many |
| `compare-values-across-categories` | How does {measure} compare across {category}? | comparisons | bar_chart, dot_plot, data_table | compare-values-across-categories--dot-plot-small-differences, compare-values-across-categories--sorted-horizontal-bar |
| `correlation-two-quantities` | Is {measure} related to {measure2}? | relationships | scatterplot, bubble_chart, connected_scatterplot, heatmap | correlation-two-quantities--linked-scatter-and-bars, correlation-two-quantities--scatter-with-trend |
| `distribution-change-over-time` | Has the distribution of {measure} changed between periods of {time}? | distribution, data-over-time | ridge_plot, small_multiples, heatmap, histogram | distribution-change-over-time--ridge-by-period |
| `distribution-compare-groups` | How does the distribution of {measure} differ between {category}? | distribution, comparisons | strip_plot, violin_plot, raincloud, beeswarm, box_plot, ridge_plot, wilkinson_dot_plot, small_multiples | distribution-compare-groups--strip-with-summary, distribution-compare-groups--violins-large-n |
| `distribution-single` | How are the values of {measure} distributed? | distribution | histogram, density_plot, strip_plot, wilkinson_dot_plot, stem_and_leaf_plot | distribution-single--histogram |
| `event-timeline-intervals` | When did {events} happen and how long did they last? | data-over-time, processes-and-methods, range | gantt_chart, timeline, span_chart, data_table | event-timeline-intervals--gantt-rows |
| `exact-values-lookup` | What exactly is {measure} for {item}? | reference-tool | data_table, bar_chart, timetable | exact-values-lookup--formatted-table |
| `flow-between-states` | How much {flow} moves from {source} to {target}? | movement-or-flow, how-things-work | sankey_diagram, parallel_sets, heatmap, adjacency_matrix, flow_map, chord_diagram | flow-between-states--sankey |
| `hierarchy-structure` | How is {organisation|taxonomy} structured? | hierarchy, reference-tool | tree_diagram, indented_tree, icicle, dendrogram, treemap, sunburst_diagram, data_table | hierarchy-structure--node-link-tree |
| `matrix-pattern-two-keys` | Where do {measure} concentrate across {category} × {category2}? | patterns, relationships | heatmap, dendrogram, bubble_chart, small_multiples | matrix-pattern-two-keys--reordered-heatmap |
| `multivariate-relationships` | How do items compare across {measures}? | relationships, patterns | parallel_coordinates, scatterplot, bubble_chart, heatmap, small_multiples | multivariate-relationships--heatmap-items-by-measures, multivariate-relationships--parallel-coordinates-analyst |
| `network-relationships` | Which {entities} are connected? | relationships | network_diagram, adjacency_matrix, heatmap, arc_diagram, chord_diagram | network-relationships--node-link-sparse |
| `part-to-whole-hierarchy` | How is {total} split into {level1} and then {level2}? | hierarchy, part-to-a-whole | treemap, sunburst_diagram, circle_packing, bar_chart | part-to-whole-hierarchy--treemap-two-levels |
| `part-to-whole-over-time` | How has the share of each {category} in {total} changed over {time}? | part-to-a-whole, data-over-time | stacked_area_graph, stacked_bar_graph, small_multiples, line_graph, stream_graph | part-to-whole-over-time--stacked-area-few |
| `part-to-whole-single` | What share of {total} does each {category} take? | proportions, part-to-a-whole | bar_chart, stacked_bar_graph, pie_chart, treemap, dot_matrix_chart | part-to-whole-single--pie-three-parts, part-to-whole-single--sorted-bars-with-percent |
| `point-events-on-map` | Where do {events} happen? | location, distribution | dot_map, bubble_map, heatmap | point-events-on-map--dot-map |
| `process-sequence` | What are the steps of {process}? | processes-and-methods, how-things-work, concepts | flow_chart, illustration_diagram, timeline, data_table | process-sequence--flow-chart-plan |
| `range-per-item` | What is the range of {measure} per {category}? | range, comparisons | dumbbell_plot, span_chart, error_bars, box_plot, strip_plot | range-per-item--dumbbell-sorted |
| `rank-change-two-points` | How did {measure} per {category} change between {t0} and {t1}? | comparisons, data-over-time | slope_chart, dumbbell_plot, bar_chart, bump_chart | rank-change-two-points--share-shift-slope, rank-change-two-points--slope-chart |
| `seasonality-cycles` | Is there a seasonal pattern in {measure}? | data-over-time, patterns | heatmap, calendar, line_graph, small_multiples | seasonality-cycles--month-by-year-heatmap |
| `set-overlap` | How many {items} belong to both {setA} and {setB}? | concepts, relationships | upset, venn_diagram, bar_chart, heatmap | set-overlap--intersection-bars, set-overlap--venn-two-or-three |
| `spatial-change-over-time` | How has {measure} per {region} evolved over {time}? | location, data-over-time | small_multiples, heatmap, slope_chart, choropleth, arrow_map, spike_map, tile_cartogram | spatial-change-over-time--heatmap-region-by-year, spatial-change-over-time--small-multiple-maps-few-periods |
| `spatial-distribution` | Where is {measure} highest? | location | choropleth, bubble_map, bar_chart, tile_cartogram, spike_map | spatial-distribution--choropleth-rate, spatial-distribution--map-with-linked-ranking, spatial-distribution--sorted-bars-no-geometry |
| `text-frequency` | Which terms are most frequent in {corpus}? | analysing-text | bar_chart, wordcloud, dumbbell_plot | text-frequency--top-terms-bars |
| `trend-few-series` | How do {category} compare over {time}? | data-over-time, comparisons | line_graph, small_multiples, slope_chart, connected_scatterplot | trend-few-series--lines-direct-labels, trend-few-series--small-multiples-different-units |
| `trend-many-series` | How has {measure} per {category} evolved over {time}? | data-over-time, patterns | heatmap, small_multiples, line_graph, horizon_graph, bump_chart | trend-many-series--heatmap-key-x-time, trend-many-series--small-multiples-public |
| `trend-single-series` | How has {measure} changed over {time}? | data-over-time | line_graph, area_graph, bar_chart | trend-single-series--line, trend-single-series--overview-detail-brush, trend-single-series--yearly-bars-from-zero |
| `uncertainty-of-estimate-or-forecast` | How sure are we about {measure} for each {category}? | range, distribution, data-over-time | gradient_interval, quantile_dotplot, error_bars, ensemble_plot, violin_plot, hypothetical_outcome_plot | uncertainty-of-estimate-or-forecast--gradient-interval-expert, uncertainty-of-estimate-or-forecast--quantile-dotplot-public |

## A categorical state sampled over time (`categorical-state-over-time`)

Questions: Which {category} state occurs when, and for how long? · At what times of {time} does each {category} state dominate?
- Data shape: table; keys temporal (many/huge); categorical (few/some); values quantitative (share).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'identify'}; low-level characterize-distribution, find-anomalies, compare, cluster; temporal existence, temporal-location, interval, pattern, sequence.
- Preferred idioms: heatmap, gantt_chart, timeline, small_multiples, stacked_bar_graph.
- Discouraged: line_graph when the state is nominal, so a line through it implies an order and in-between values (EXP-03); scatterplot when raw samples are coloured by a dozen hues (COL-04); stacked_area_graph when more than ~5 states, or individual states must be compared (IDM-STACK); pie_chart when the timing matters, not only the total share (IDM-PIE).
- Related: event-timeline-intervals, seasonality-cycles, part-to-whole-over-time. Sibling chart-types.md sections: Relationships / Heat map, Time series / Calendar heatmap, punch card.
- Disambiguation: The raw record is one nominal label per instant, sampled densely; states are mutually exclusive. Derive before drawing: either bin time and compute the share (or count) of each state per bin → heatmap of time bin × state, or stacked bars per bin when shares must sum visibly; or merge consecutive equal samples into intervals (run-length merging) → gantt/timeline rows, which is event-timeline-intervals once the intervals exist. A repeating daily or weekly rhythm → seasonality-cycles; a few states whose shares over long periods are the point → part-to-whole-over-time.
- Examples: dominant sound class per second over a day, machine status per minute over a shift, sleep stage per 30-second epoch over a night, activity label per sample from a wearable sensor.

## Counts per category over time (`category-breakdown-over-time`)

Questions: How has the number of {events} by {category} evolved over {time}? · Is {category} replacing {category2} over {time}?
- Data shape: table; keys temporal (some/many); categorical (few/some); values quantitative (count).
- Default tasks: why {'goal': 'present', 'search': 'browse', 'query': 'compare'}; low-level trend, compare, compute-derived, gist; temporal pattern, rate-of-change.
- Preferred idioms: line_graph, small_multiples, stacked_bar_graph, stacked_area_graph, heatmap.
- Discouraged: stacked_area_graph when more than 5–6 categories (IDM-STACK); multiset_barchart when time as groups (EXP-04); pie_chart when always (IDM-PIE).
- Related: trend-few-series, trend-many-series, part-to-whole-over-time. Sibling chart-types.md sections: Time series / Area / stacked area / streamgraph, Time series / Line chart, Time series / Small multiples.
- Disambiguation: This is a router: ≤7 categories and individual trends → trend-few-series; shares → part-to-whole-over-time; many categories → trend-many-series.
- Examples: fires by cause per year, tickets by type per week, enrolments by programme per year.

## Compare actual values against a target or reference (`compare-against-target`)

Questions: Is {measure} on target for each {category}? · How far is {measure} from the {reference}?
- Data shape: table; keys categorical (one/few/some); values quantitative (amount); quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'compare'}; low-level compare, retrieve-value, compute-derived, find-anomalies.
- Preferred idioms: bullet_graph, bar_chart, dumbbell_plot.
- Discouraged: radar_chart when always: axis order is arbitrary (IDM-RADAR/GAUGE); pie_chart when always (IDM-PIE).
- Related: compare-values-across-categories, range-per-item. Sibling chart-types.md sections: Quantities / Gauge vs bullet chart.
- Disambiguation: A reference can be a target, a previous period, a mean or a threshold; if the reference is itself a full series over time, use trend-few-series with a reference line.
- Examples: KPI vs plan per department, temperature vs threshold per sensor, vaccination rate vs goal per district.

## Compare a measure across two categorical keys (`compare-two-keys`)

Questions: How does {measure} vary by {category} and {category2}? · Within each {category}, which {category2} is largest?
- Data shape: table; keys categorical (few/some); categorical (few/some/many); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'compare'}; low-level compare, find-extremum, cluster, retrieve-value.
- Preferred idioms: multiset_barchart, heatmap, dumbbell_plot, small_multiples, stacked_bar_graph.
- Discouraged: stacked_bar_graph when comparison within or across groups is the task (IDM-STACK); multiset_barchart when one key is time (EXP-04); marimekko_chart when precise comparison needed (EFF-02).
- Related: compare-values-across-categories, matrix-pattern-two-keys, trend-many-series. Sibling chart-types.md sections: Quantities / Grouped / paired bar chart, Quantities / Stacked bar chart, Relationships / Heat map.
- Disambiguation: If one key is time, use trend-few-series / trend-many-series. If both keys have many levels, use matrix-pattern-two-keys.
- Examples: sales by region and product, incidents by cause and severity, grades by course and cohort.

## Compare one measure across categories (`compare-values-across-categories`)

Questions: How does {measure} compare across {category}? · Which {category} has the highest {measure}? · How is {measure} distributed among {category}?
- Data shape: table; keys categorical (few/some/many); values quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'compare'}; low-level compare, find-extremum, sort, retrieve-value.
- Preferred idioms: bar_chart, dot_plot, data_table.
- Discouraged: pie_chart when more than 5 categories or the task is comparison (IDM-PIE); radial_bar_chart when always: geometry lies (EXP-07); area_chart when precise comparison needed (EFF-02).
- Related: part-to-whole-single, compare-two-keys, exact-values-lookup. Sibling chart-types.md sections: Quantities / Bar chart, Quantities / Dot plot / lollipop.
- Disambiguation: If the measure is a share of one total and there are ≤5 parts, part-to-whole-single may apply; if the user says 'distribution among categories' they usually mean this archetype, not distribution-single (which is the spread of a numeric variable).
- Examples: burned area per region, revenue per product line, students per degree programme.

## Relation between two measures (`correlation-two-quantities`)

Questions: Is {measure} related to {measure2}? · Which items are outliers in {measure} vs {measure2}?
- Data shape: table; keys none; values quantitative; quantitative.
- Default tasks: why {'goal': 'discover', 'search': 'explore', 'query': 'compare'}; low-level correlate, find-anomalies, cluster, characterize-distribution.
- Preferred idioms: scatterplot, bubble_chart, connected_scatterplot, heatmap.
- Discouraged: line_graph when x is not ordered (EXP-03); bar_chart when two measures per item is not a ranking (EFF-01).
- Related: multivariate-relationships, compare-two-keys. Sibling chart-types.md sections: Relationships / Scatterplot.
- Disambiguation: Add a third attribute as color (categorical, ≤7) or size (quantitative, with legend); thousands of points → opacity or 2-D binning.
- Examples: income vs life expectancy, area burned vs number of fires, price vs rating.

## How a distribution shifts across periods (`distribution-change-over-time`)

Questions: Has the distribution of {measure} changed between periods of {time}? · Did {measure} per {category} become more concentrated over {time}?
- Data shape: table; keys temporal (few/some); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'compare'}; low-level characterize-distribution, compare, trend, find-anomalies; temporal pattern, rate-of-change.
- Preferred idioms: ridge_plot, small_multiples, heatmap, histogram.
- Discouraged: stacked_area_graph when distribution, not composition (EXP-06); bar_chart when bars of means (EXP-16); slope_chart when shares of categories belong to rank-change-two-points (PUR-01).
- Related: distribution-single, rank-change-two-points, trend-many-series. Sibling chart-types.md sections: Distributions / Histogram, Time series / Small multiples, Relationships / Heat map.
- Disambiguation: This archetype is the spread of a numeric variable per item across periods (ridges, faceted histograms). If the question is 'share of each category at start vs end', it is rank-change-two-points with value semantics share (seed rank-change-two-points--share-shift-slope).
- Examples: fire sizes in the first vs last decade, age distribution of customers per year, delay distribution by quarter.

## Distributions compared across groups (`distribution-compare-groups`)

Questions: How does the distribution of {measure} differ between {category}? · Do {category} groups overlap on {measure}?
- Data shape: table; keys categorical (few/some); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'compare'}; low-level characterize-distribution, compare, find-anomalies, determine-range.
- Preferred idioms: strip_plot, violin_plot, raincloud, beeswarm, box_plot, ridge_plot, wilkinson_dot_plot, small_multiples.
- Discouraged: bar_chart when bars of means hide the distribution (EXP-16); box_plot when multimodality matters (EXP-16); raincloud when built from a density, randomly jittered points and a box plot with undefined whiskers (IDM-RAINCLOUD); beeswarm when more than a few hundred points per group (EFF-19); density_plot when values are discrete, rounded or bounded and the curve spills past the possible range (EXP-22).
- Related: distribution-single, compare-values-across-categories, range-per-item. Sibling chart-types.md sections: Distributions / Box plot, Distributions / Violin / strip / beeswarm / ridge / raincloud.
- Disambiguation: Never summarise with bars of means (Wilmer & Kerns); show the points when n is small and a density when n is large; state n per group. Points go at their true value (ticks, translucent or hollow marks); where they must be spread use a beeswarm, stacked dots or a seeded documented offset, never an unseeded random one, which redraws differently each time (EXP-21). A raincloud earns its layers only when each covers another's weakness (density + strip + median with a labelled interval; Correll 2023).
- Examples: treatment outcome by group, salary by department, fire size by cause.

## Shape of one numeric variable (`distribution-single`)

Questions: How are the values of {measure} distributed? · Are there outliers or several modes in {measure}?
- Data shape: table; keys none; values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'summarize'}; low-level characterize-distribution, find-anomalies, determine-range.
- Preferred idioms: histogram, density_plot, strip_plot, wilkinson_dot_plot, stem_and_leaf_plot.
- Discouraged: pie_chart when always (IDM-PIE); bar_chart when values are continuous, not categories (EXP-15).
- Related: distribution-compare-groups, distribution-change-over-time, compare-values-across-categories. Sibling chart-types.md sections: Distributions / Histogram.
- Disambiguation: 'Distribution of X across categories' means compare-values-across-categories; this archetype is the spread of one numeric variable over items. Explore several bin widths. Small samples or readers who count better than they read densities → stacked dots (Wilkinson dot plot).
- Examples: size of individual fires in hectares, response times of a service, exam scores.

## Events and intervals in time (`event-timeline-intervals`)

Questions: When did {events} happen and how long did they last? · Which {tasks} overlap?
- Data shape: table; keys categorical (few/some/many); values temporal (position); temporal (position).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level determine-range, sort, retrieve-value; temporal existence, temporal-location, interval, sequence, synchronization.
- Preferred idioms: gantt_chart, timeline, span_chart, data_table.
- Discouraged: line_graph when events are not a continuous measure (EXP-03).
- Related: trend-single-series, exact-values-lookup. Sibling chart-types.md sections: none.
- Disambiguation: Instants only → timeline; intervals → gantt/span rows sorted by start; many events → aggregate to counts per period (trend-single-series).
- Examples: project tasks, reigns and governments, outages per service.

## Precise values and heterogeneous attributes (`exact-values-lookup`)

Questions: What exactly is {measure} for {item}? · Give me the numbers for {items}.
- Data shape: table; keys categorical (few/some); values quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level retrieve-value, sort, compare.
- Preferred idioms: data_table, bar_chart, timetable.
- Discouraged: pie_chart when always (IDM-PIE).
- Related: compare-values-across-categories. Sibling chart-types.md sections: Tables and text.
- Disambiguation: When the reader will quote numbers, or there are ≤5 values, or attributes mix text and numbers, a table beats a chart (Munzner / Few). Add inline bars only if ranking matters.
- Examples: league table, budget lines, schedule.

## Quantities moving between categories (`flow-between-states`)

Questions: How much {flow} moves from {source} to {target}? · Where does {total} go?
- Data shape: network; keys categorical (few/some); categorical (few/some); values quantitative (weight).
- Default tasks: why {'goal': 'present', 'search': 'browse', 'query': 'compare'}; low-level find-extremum, compare, gist, compute-derived.
- Preferred idioms: sankey_diagram, parallel_sets, heatmap, adjacency_matrix, flow_map, chord_diagram.
- Discouraged: chord_diagram when more than ~12 nodes (EFF-16); sankey_diagram when exact values needed without labels (EFF-02); sankey_diagram when too many links, heavy crossings or nodes in no meaningful order (IDM-SANKEY).
- Related: network-relationships, matrix-pattern-two-keys. Sibling chart-types.md sections: Geospatial / Flow / line maps, network maps.
- Disambiguation: Source × target with many levels → a matrix (heatmap) beats a Sankey; geographic endpoints → flow map.
- Examples: energy balance, migration between regions, customer journey stages.

## Structure of a tree (`hierarchy-structure`)

Questions: How is {organisation|taxonomy} structured? · Which node is the parent of {item}?
- Data shape: tree; keys categorical (some/many); values none.
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level retrieve-value, cluster, gist.
- Preferred idioms: tree_diagram, indented_tree, icicle, dendrogram, treemap, sunburst_diagram, data_table.
- Discouraged: treemap when structure matters more than size (EFF-02); circle_packing when space matters (CLT-03).
- Related: part-to-whole-hierarchy. Sibling chart-types.md sections: Hierarchies and networks.
- Disambiguation: If each node carries a size that matters, use part-to-whole-hierarchy. Node-link tree: the shape of a small hierarchy for any reader. Indented tree: looking up names, long labels or attribute columns beside each node, at the cost of vertical space and overview. Icicle: structure plus a size on aligned lengths. Dendrogram: only when the tree comes from clustering and the merge distance matters.
- Examples: org chart, file system, taxonomy of species.

## Pattern across two keys with many levels (`matrix-pattern-two-keys`)

Questions: Where do {measure} concentrate across {category} × {category2}? · Which combinations are unusual?
- Data shape: table; keys categorical (some/many/huge); categorical (some/many/huge); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'identify'}; low-level cluster, find-anomalies, compare, find-extremum.
- Preferred idioms: heatmap, dendrogram, bubble_chart, small_multiples.
- Discouraged: multiset_barchart when more than ~12 groups (EFF-19); stacked_bar_graph when many categories (IDM-STACK).
- Related: compare-two-keys, trend-many-series, network-relationships. Sibling chart-types.md sections: Relationships / Heat map.
- Disambiguation: Order rows and columns by totals or clustering; a categorical palette for values is wrong (sequential or diverging). A dendrogram is a companion on the margin of a cluster-ordered heatmap, showing why the rows sit where they do; it is not a replacement for the matrix.
- Examples: product × region sales, origin × destination trips, gene × sample expression.

## Three or more measures per item (`multivariate-relationships`)

Questions: How do items compare across {measures}? · Are there groups of items with similar profiles?
- Data shape: table; keys categorical (some/many); values quantitative; quantitative; quantitative.
- Default tasks: why {'goal': 'discover', 'search': 'explore', 'query': 'summarize'}; low-level correlate, cluster, find-anomalies, compare.
- Preferred idioms: parallel_coordinates, scatterplot, bubble_chart, heatmap, small_multiples.
- Discouraged: radar_chart when axis order is arbitrary and polygons mislead (IDM-RADAR/GAUGE); bubble_chart when more than 3 measures (EFF-11).
- Related: correlation-two-quantities, compare-two-keys. Sibling chart-types.md sections: Relationships / Scatterplot matrix (SPLOM), Relationships / Parallel coordinates, Relationships / Bubble chart.
- Disambiguation: Analysts: parallel coordinates or SPLOM with brushing; general readers: pick the two measures that answer the question (correlation-two-quantities) or a heatmap of items × measures (normalised).
- Examples: car specs, country indicators, player statistics.

## Nodes and links (`network-relationships`)

Questions: Which {entities} are connected? · Are there communities or hubs among {entities}?
- Data shape: network; keys categorical (some/many/huge); values quantitative (weight).
- Default tasks: why {'goal': 'discover', 'search': 'explore', 'query': 'identify'}; low-level cluster, find-anomalies, retrieve-value.
- Preferred idioms: network_diagram, adjacency_matrix, heatmap, arc_diagram, chord_diagram.
- Discouraged: network_diagram when more than a few hundred nodes (hairball) (EFF-16); chord_diagram when more than ~12 nodes (EFF-16); adjacency_matrix when rows and columns are left in arbitrary order (CMP-01).
- Related: matrix-pattern-two-keys, flow-between-states. Sibling chart-types.md sections: Hierarchies and networks.
- Disambiguation: Dense graphs → adjacency_matrix with rows and columns reordered (seriation) so clusters form blocks; sparse graphs or path-following tasks → node-link; weighted flows between few categories → flow-between-states. A matrix has no edge crossings but paths are hard to trace.
- Examples: collaboration network, trade links, citations.

## Nested composition (`part-to-whole-hierarchy`)

Questions: How is {total} split into {level1} and then {level2}? · Which branches of the hierarchy dominate {measure}?
- Data shape: tree; keys categorical (some/many/huge); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'identify'}; low-level find-extremum, gist, retrieve-value.
- Preferred idioms: treemap, sunburst_diagram, circle_packing, bar_chart.
- Discouraged: sunburst_diagram when more than 3 levels or labels needed (TXT-10); circle_packing when space matters (CLT-03).
- Related: part-to-whole-single, hierarchy-structure. Sibling chart-types.md sections: Proportions / Treemap.
- Disambiguation: If only one level matters, flatten it and use part-to-whole-single; if structure matters more than size, use hierarchy-structure.
- Examples: disk usage by folder, budget by ministry and programme, species by family and genus.

## Composition changing over time (`part-to-whole-over-time`)

Questions: How has the share of each {category} in {total} changed over {time}?
- Data shape: table; keys temporal (some/many); categorical (few); values quantitative (share).
- Default tasks: why {'goal': 'present', 'search': 'browse', 'query': 'compare'}; low-level trend, compare, gist, compute-derived; temporal pattern, rate-of-change.
- Preferred idioms: stacked_area_graph, stacked_bar_graph, small_multiples, line_graph, stream_graph.
- Discouraged: stream_graph when exact values or few time steps (EXP-06); stacked_area_graph when more than 5–6 categories or non-additive values (IDM-STACK); pie_chart when always (IDM-PIE).
- Related: category-breakdown-over-time, trend-few-series, part-to-whole-single. Sibling chart-types.md sections: Time series / Area / stacked area / streamgraph, Quantities / Normalized (100 %) stacked bar.
- Disambiguation: If the reader must compare individual categories rather than the composition, use small multiples or lines (category-breakdown-over-time).
- Examples: energy mix per year, share of each cause in annual incidents, device share of web traffic by month.

## Composition of one whole at one moment (`part-to-whole-single`)

Questions: What share of {total} does each {category} take? · How is {total} split among {category}?
- Data shape: table; keys categorical (few); values quantitative (share).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level gist, retrieve-value, compare.
- Preferred idioms: bar_chart, stacked_bar_graph, pie_chart, treemap, dot_matrix_chart.
- Discouraged: pie_chart when more than 5 parts or similar sizes (IDM-PIE); donut_chart when more than 5 parts (IDM-PIE); sunburst_diagram when single level (EFF-02).
- Related: compare-values-across-categories, part-to-whole-hierarchy, part-to-whole-over-time. Sibling chart-types.md sections: Proportions / Pie / donut, Quantities / Normalized (100 %) stacked bar.
- Disambiguation: Parts must sum to a meaningful whole; otherwise it is compare-values-across-categories. Sorted bars with percentages beat the pie whenever parts are more than 3 or similar in size.
- Examples: budget by cost centre, energy mix by source, survey answers by option.

## Individual events with coordinates (`point-events-on-map`)

Questions: Where do {events} happen? · Do {events} cluster in space?
- Data shape: geometry; keys geo-code (many/huge); values none.
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'identify'}; low-level cluster, gist, find-anomalies.
- Preferred idioms: dot_map, bubble_map, heatmap.
- Discouraged: choropleth when events are points, not rates (EXP-12).
- Related: spatial-distribution. Sibling chart-types.md sections: Geospatial / Dot map / pixel map.
- Disambiguation: Thousands of points overplot: bin them (hex/grid heatmap) or aggregate to regions (spatial-distribution).
- Examples: locations of ignition points, store locations, GPS traces of deliveries.

## Steps of a process or how something works (`process-sequence`)

Questions: What are the steps of {process}? · Where are the decision points?
- Data shape: network; keys categorical (few/some); values none.
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level gist, retrieve-value; temporal sequence.
- Preferred idioms: flow_chart, illustration_diagram, timeline, data_table.
- Discouraged: sankey_diagram when no quantities flow (EXP-10).
- Related: event-timeline-intervals, flow-between-states. Sibling chart-types.md sections: none.
- Disambiguation: Not a data visualization: no measured attribute. The skill produces a diagram plan, not a chart; if quantities per step exist, use flow-between-states.
- Examples: onboarding workflow, how a bill becomes law, data pipeline.

## A low and a high value per item (`range-per-item`)

Questions: What is the range of {measure} per {category}? · How uncertain is {measure} per {category}?
- Data shape: table; keys categorical (few/some/many); values quantitative (lower); quantitative (upper).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'compare'}; low-level determine-range, compare, sort, find-anomalies.
- Preferred idioms: dumbbell_plot, span_chart, error_bars, box_plot, strip_plot.
- Discouraged: bar_chart when range has no zero baseline meaning (EXP-08); span_chart when the inside of the range matters (EXP-16).
- Related: distribution-compare-groups, compare-against-target, uncertainty-of-estimate-or-forecast. Sibling chart-types.md sections: Relationships / Connected scatterplot / dumbbell / range plot.
- Disambiguation: If raw observations exist, show them (distribution-compare-groups); intervals must state what they are (SD, CI, min–max). Inferential or predictive intervals → uncertainty-of-estimate-or-forecast.
- Examples: temperature min–max per city, price range per product, confidence interval per estimate.

## Change of many items between two moments (`rank-change-two-points`)

Questions: How did {measure} per {category} change between {t0} and {t1}? · Which {category} gained or lost the most?
- Data shape: table; keys temporal (few); categorical (few/some/many); values quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'locate', 'query': 'compare'}; low-level compare, sort, compute-derived, find-extremum; temporal rate-of-change, sequence.
- Preferred idioms: slope_chart, dumbbell_plot, bar_chart, bump_chart.
- Discouraged: multiset_barchart when more than ~8 items (EFF-19); pie_chart when always (IDM-PIE); slope_chart when more than ~25 items with close values: end labels collide; use a sorted dumbbell (EFF-16).
- Related: trend-few-series, distribution-change-over-time, compare-two-keys. Sibling chart-types.md sections: Relationships / Slope chart, Relationships / Connected scatterplot / dumbbell / range plot.
- Disambiguation: Exactly two moments → this archetype, for amounts and for shares of a whole (value semantics share); three or more → trend-few-series or trend-many-series; if the question is the spread of a numeric variable per item, use distribution-change-over-time.
- Examples: unemployment per region 2015 vs 2025, market share per brand before and after a launch, scores per school in two exams.

## Periodic patterns in time (`seasonality-cycles`)

Questions: Is there a seasonal pattern in {measure}? · Which {weekday|month|hour} concentrates {events}?
- Data shape: table; keys temporal (many/huge); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'identify'}; low-level find-anomalies, trend, compare, characterize-distribution; temporal pattern, temporal-location.
- Preferred idioms: heatmap, calendar, line_graph, small_multiples.
- Discouraged: spiral_plot when unfamiliar readers (EFF-17); radial_column_chart when precise reading (EFF-02); nightingale_rose_chart when always (EXP-07).
- Related: trend-single-series, trend-many-series. Sibling chart-types.md sections: Time series / Calendar heatmap, punch card.
- Disambiguation: Two temporal grains (e.g. month × year, hour × weekday) → heatmap; one grain over several cycles → overlaid lines per cycle or small multiples.
- Examples: fires per month across years, visits per hour and weekday, sales per week across years.

## Membership overlap between sets (`set-overlap`)

Questions: How many {items} belong to both {setA} and {setB}? · How do the sets overlap?
- Data shape: table; keys categorical (few); values quantitative (count).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'identify'}; low-level retrieve-value, compare, gist.
- Preferred idioms: upset, venn_diagram, bar_chart, heatmap.
- Discouraged: venn_diagram when more than 3 sets (IDM-VENN); venn_diagram when areas must be proportional to the counts (EXP-07).
- Related: part-to-whole-single. Sibling chart-types.md sections: none.
- Disambiguation: Two or three sets for a general reader → Venn. Four or more sets, or exact intersection sizes → upset (sorted bars of intersection sizes over a membership matrix); plain sorted bars of the combinations when the matrix would need explaining.
- Examples: customers using products A and B, genes in two conditions, skills shared by teams.

## A measure per region across periods (`spatial-change-over-time`)

Questions: How has {measure} per {region} evolved over {time}? · Which regions changed most?
- Data shape: geometry; keys temporal (few/some); geo-code (some/many); values quantitative (rate).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'compare'}; low-level compare, trend, find-anomalies, find-extremum; temporal pattern, rate-of-change, synchronization.
- Preferred idioms: small_multiples, heatmap, slope_chart, choropleth, arrow_map, spike_map, tile_cartogram.
- Discouraged: choropleth when more than ~6 periods as separate maps (CMP-08); line_graph when more than ~7 regions (IDM-LINE); arrow_map when more than two periods, or small dense regions where arrows overlap (EFF-16).
- Related: trend-many-series, spatial-distribution, rank-change-two-points. Sibling chart-types.md sections: Time series / Small multiples, Geospatial / Choropleth, Relationships / Heat map.
- Disambiguation: Few periods → small multiple maps or a slope chart of regions; many periods → region × time heatmap (regions as rows), which is trend-many-series with a geographic key. Exactly two periods → map the difference itself, one arrow per region (direction and length of the shift) or spikes of the change in totals, instead of two maps to subtract by eye; a tile cartogram can hold a small trend chart per region.
- Examples: fires per county per year, rainfall per station per month, votes per district across elections.

## A measure per region on a map (`spatial-distribution`)

Questions: Where is {measure} highest? · How does {measure} vary across {region}?
- Data shape: geometry; keys geo-code (some/many/huge); values quantitative (rate).
- Default tasks: why {'goal': 'present', 'search': 'locate', 'query': 'identify'}; low-level find-extremum, cluster, compare, gist.
- Preferred idioms: choropleth, bubble_map, bar_chart, tile_cartogram, spike_map.
- Discouraged: choropleth when raw counts without normalisation (EXP-12); bubble_map when overlapping dense regions (EFF-16).
- Related: spatial-change-over-time, point-events-on-map, compare-values-across-categories. Sibling chart-types.md sections: Geospatial / Choropleth, Geospatial / Graduated / proportional symbol map.
- Disambiguation: A map needs a geometry file for the regions; without one, a sorted bar chart of regions answers the comparison task better. Choropleths need rates, symbol maps can show totals. When regions count equally and small ones vanish at true scale → tile cartogram (equal tiles, needs only a layout table). Totals in dense areas where bubbles overlap → spike map (height instead of area).
- Examples: unemployment rate by province, burned hectares per county, cases per 100k by district.

## Term frequencies in text (`text-frequency`)

Questions: Which terms are most frequent in {corpus}? · How do two texts differ in vocabulary?
- Data shape: text; keys categorical (many/huge); values quantitative (count).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'summarize'}; low-level find-extremum, sort, compare.
- Preferred idioms: bar_chart, wordcloud, dumbbell_plot.
- Discouraged: wordcloud when comparison or exact ranking needed (IDM-WORDCLOUD).
- Related: compare-values-across-categories. Sibling chart-types.md sections: Text.
- Disambiguation: A sorted bar chart of the top-N terms is the analytic answer; a word cloud is at most a teaser.
- Examples: survey free-text answers, tweets about a topic, exam answers.

## Two to seven series over time (`trend-few-series`)

Questions: How do {category} compare over {time}? · Which {category} grows fastest?
- Data shape: table; keys temporal (some/many/huge); categorical (few); values quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'browse', 'query': 'compare'}; low-level trend, compare, find-extremum, find-anomalies; temporal pattern, rate-of-change, synchronization.
- Preferred idioms: line_graph, small_multiples, slope_chart, connected_scatterplot.
- Discouraged: multiset_barchart when one key is time (EXP-04); stacked_area_graph when comparison of individual series (IDM-STACK); line_graph when dual y axes for different units (EXP-11).
- Related: trend-single-series, trend-many-series, part-to-whole-over-time. Sibling chart-types.md sections: Time series / Line chart.
- Disambiguation: Different units → small multiples with their own y, never dual axes; same units → one panel with direct labels.
- Examples: sales of three products per month, temperature in two cities, cases per age group per week.

## Eight or more series over time (`trend-many-series`)

Questions: How has {measure} per {category} evolved over {time}? · Which {category} deviate from the common pattern?
- Data shape: table; keys temporal (few/some/many); categorical (some/many); values quantitative (amount).
- Default tasks: why {'goal': 'discover', 'search': 'browse', 'query': 'compare'}; low-level compare, find-anomalies, find-extremum, characterize-distribution; temporal pattern, rate-of-change, synchronization.
- Preferred idioms: heatmap, small_multiples, line_graph, horizon_graph, bump_chart.
- Discouraged: line_graph when more than ~12 series, or more than ~7 told apart only by hue without direct labels or a highlight-on-grey design (IDM-LINE); stacked_area_graph when comparison of individual series (IDM-STACK); multiset_barchart when always with time (EXP-04).
- Related: trend-few-series, compare-two-keys, spatial-change-over-time. Sibling chart-types.md sections: Time series / Small multiples, Relationships / Heat map, Time series / Horizon graph.
- Disambiguation: ≤7 series → trend-few-series. If shares of a whole are the point → part-to-whole-over-time. Rows of the heatmap sorted by total or by trajectory similarity.
- Examples: incidents per region per year, sales per store per month, sensor readings per machine per hour.

## One measure over time (`trend-single-series`)

Questions: How has {measure} changed over {time}? · When did {measure} peak?
- Data shape: table; keys temporal (some/many/huge); values quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'browse', 'query': 'identify'}; low-level trend, find-extremum, find-anomalies, retrieve-value; temporal pattern, rate-of-change, temporal-location.
- Preferred idioms: line_graph, area_graph, bar_chart.
- Discouraged: bar_chart when more than ~12 periods or the task is trend (EXP-04); area_graph when axis not from zero (EXP-08); pie_chart when always (IDM-PIE).
- Related: trend-few-series, seasonality-cycles. Sibling chart-types.md sections: Time series / Line chart.
- Disambiguation: Few discrete totals (yearly) where amounts matter can be bars from zero; otherwise a line. Annotate events that explain spikes.
- Examples: monthly revenue, annual number of incidents, daily temperature.

## Uncertainty of an estimate or forecast (`uncertainty-of-estimate-or-forecast`)

Questions: How sure are we about {measure} for each {category}? · What range of outcomes should we expect for {measure} over {time}? · How likely is {measure} to pass {threshold}?
- Data shape: table; keys categorical (one/few/some/many); values quantitative (amount); quantitative (amount); quantitative (amount).
- Default tasks: why {'goal': 'present', 'search': 'lookup', 'query': 'compare'}; low-level determine-range, compare, retrieve-value, characterize-distribution; temporal rate-of-change.
- Preferred idioms: gradient_interval, quantile_dotplot, error_bars, ensemble_plot, violin_plot, hypothetical_outcome_plot.
- Discouraged: bar_chart when only point estimates are drawn and the uncertainty is left out (DAT-03); error_bars when the interval is not defined on the chart, or the reader is a lay audience (PUR-14); ensemble_plot when members come from different models, dates or resolutions, or are stale (DAT-12); gradient_interval when the band can be read as a physical area or a hard limit (DAT-11); hypothetical_outcome_plot when the output is static or printed (CMP-08).
- Related: range-per-item, distribution-compare-groups, trend-single-series. Sibling chart-types.md sections: none.
- Disambiguation: range-per-item shows observed extremes (a measured min and max); this archetype shows inferential or predictive uncertainty (standard error, confidence, credible or prediction interval, posterior draws, model runs). Name the interval and its level and make it match the analysis. Expert readers: gradient bands or intervals; lay readers: countable frequencies (quantile dots, icon grids) with one sentence of explanation. The key may be a category (one estimate each) or time (a forecast path); with raw observations only, use distribution-compare-groups.
- Examples: forecast demand per week with a prediction interval, estimated effect per treatment with a credible interval, arrival-time prediction for a bus, projected temperature path from several model runs.
