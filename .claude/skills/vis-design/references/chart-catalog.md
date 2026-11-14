# Chart catalog (generated from data/chart-catalog.json by build_index.py)

Facts (functions, similar charts) come from datavizcatalogue.com; summaries are paraphrases;
the characterization lines (data, tasks, scale, fit, rules) are ours. Entries marked
*supplement* are not on the site.

## Functions

- **Comparisons** (`comparisons`): Charts that let the reader compare magnitudes of several items or groups. Charts: bar_chart, box_plot, bubble_chart, bullet_graph, line_graph, marimekko_chart, multiset_barchart, nightingale_rose_chart, parallel_coordinates, population_pyramid, radar_chart, radial_bar_chart, radial_column_chart, span_chart, stacked_area_graph, stacked_bar_graph, chord_diagram, choropleth, donut_chart, dot_matrix_chart, heatmap, parallel_sets, pictogram, pie_chart, area_chart, tally_chart, treemap, venn_diagram, bump_chart, data_table, dot_plot, dumbbell_plot, ridge_plot, slope_chart, small_multiples, strip_plot, upset, raincloud, beeswarm, difference_view, spike_map, tile_cartogram. Archetypes: compare-values-across-categories, compare-two-keys, compare-against-target, rank-change-two-points, distribution-compare-groups, range-per-item, trend-few-series.
- **Proportions** (`proportions`): Charts whose marks are sized relative to one another or to a whole. Charts: bubble_chart, bubble_map, circle_packing, dot_matrix_chart, nightingale_rose_chart, area_chart, stacked_bar_graph, wordcloud, donut_chart, marimekko_chart, parallel_sets, pie_chart, sankey_diagram, treemap, icicle. Archetypes: part-to-whole-single, part-to-whole-over-time, part-to-whole-hierarchy, category-breakdown-over-time.
- **Relationships** (`relationships`): Charts that show connections between entities or correlations between variables. Charts: heatmap, marimekko_chart, parallel_coordinates, radar_chart, venn_diagram, arc_diagram, brainstorm, chord_diagram, connection_map, network_diagram, non_ribbon_chord_diagram, tree_diagram, bubble_chart, scatterplot, connected_scatterplot, dendrogram, adjacency_matrix, upset. Archetypes: correlation-two-quantities, multivariate-relationships, matrix-pattern-two-keys, network-relationships, set-overlap.
- **Hierarchy** (`hierarchy`): Charts for nested, parent-child structures. Charts: circle_packing, sunburst_diagram, tree_diagram, treemap, dendrogram, indented_tree, icicle. Archetypes: hierarchy-structure, part-to-whole-hierarchy.
- **Concepts** (`concepts`): Diagrams that explain ideas rather than encode measured data. Charts: brainstorm, flow_chart, illustration_diagram, venn_diagram. Archetypes: process-sequence, set-overlap.
- **Location** (`location`): Charts drawn over geography. Charts: bubble_map, choropleth, connection_map, dot_map, flow_map, arrow_map, spike_map, tile_cartogram, streamline_map. Archetypes: spatial-distribution, spatial-change-over-time, point-events-on-map, flow-between-states.
- **Part-to-a-whole** (`part-to-a-whole`): Charts whose parts sum to a meaningful total. Charts: donut_chart, marimekko_chart, pie_chart, stacked_bar_graph, sunburst_diagram, treemap, icicle. Archetypes: part-to-whole-single, part-to-whole-over-time, part-to-whole-hierarchy.
- **Distribution** (`distribution`): Charts that show how values or items are spread. Charts: box_plot, bubble_chart, density_plot, dot_matrix_chart, histogram, multiset_barchart, parallel_sets, pictogram, stem_and_leaf_plot, tally_chart, timeline, violin_plot, dot_map, connection_map, flow_map, population_pyramid, wordcloud, ridge_plot, strip_plot, raincloud, beeswarm, wilkinson_dot_plot, quantile_dotplot, hypothetical_outcome_plot. Archetypes: distribution-single, distribution-compare-groups, distribution-change-over-time, point-events-on-map, uncertainty-of-estimate-or-forecast.
- **How Things Work** (`how-things-work`): Diagrams that explain mechanisms and systems. Charts: flow_chart, illustration_diagram, sankey_diagram. Archetypes: process-sequence, flow-between-states.
- **Processes and Methods** (`processes-and-methods`): Charts for sequences of steps, schedules and procedures. Charts: flow_chart, gantt_chart, illustration_diagram, parallel_sets, sankey_diagram. Archetypes: process-sequence, event-timeline-intervals.
- **Movement or Flow** (`movement-or-flow`): Charts for quantities moving between places or states. Charts: connection_map, flow_map, parallel_sets, sankey_diagram, streamline_map. Archetypes: flow-between-states.
- **Patterns** (`patterns`): Charts in which the reader looks for structure, trends, clusters or anomalies. Charts: arc_diagram, area_graph, bar_chart, box_plot, bubble_chart, candlestick_chart, choropleth, connection_map, density_plot, dot_map, dot_matrix_chart, heatmap, histogram, kagi_chart, line_graph, multiset_barchart, OHLC_chart, parallel_coordinates, point_and_figure_chart, population_pyramid, radar_chart, scatterplot, spiral_plot, stacked_area_graph, stream_graph, timeline, violin_plot, horizon_graph, small_multiples, adjacency_matrix, sparkline, ensemble_plot, overview_detail. Archetypes: trend-many-series, matrix-pattern-two-keys, seasonality-cycles, multivariate-relationships, categorical-state-over-time.
- **Range** (`range`): Charts that show spans between a low and a high value. Charts: box_plot, bullet_graph, candlestick_chart, error_bars, gantt_chart, kagi_chart, OHLC_chart, span_chart, violin_plot, dumbbell_plot, quantile_dotplot, gradient_interval, ensemble_plot, hypothetical_outcome_plot. Archetypes: range-per-item, compare-against-target, event-timeline-intervals, uncertainty-of-estimate-or-forecast.
- **Showing Data Over Time** (`data-over-time`): Charts whose main axis is time. Charts: area_graph, bubble_chart, candlestick_chart, gantt_chart, heatmap, line_graph, nightingale_rose_chart, OHLC_chart, spiral_plot, stacked_area_graph, stream_graph, calendar, timeline, timetable, bump_chart, connected_scatterplot, horizon_graph, ridge_plot, slope_chart, small_multiples, sparkline, gradient_interval, ensemble_plot, overview_detail, arrow_map. Archetypes: trend-single-series, trend-few-series, trend-many-series, category-breakdown-over-time, seasonality-cycles, event-timeline-intervals, rank-change-two-points, distribution-change-over-time, spatial-change-over-time, part-to-whole-over-time, uncertainty-of-estimate-or-forecast, categorical-state-over-time.
- **Analysing Text** (`analysing-text`): Charts built from word frequencies in text. Charts: wordcloud. Archetypes: text-frequency.
- **Reference Tool** (`reference-tool`): Lookup layouts rather than analytic charts. Charts: calendar, gantt_chart, timetable, tree_diagram, stem_and_leaf_plot, data_table, indented_tree. Archetypes: exact-values-lookup, event-timeline-intervals, hierarchy-structure.

## Charts

### Adjacency matrix (`adjacency_matrix`) *(supplement)*

A network drawn as a square grid: every node is both a row and a column and a filled cell marks a link between the pair, shaded by weight. Nothing crosses, so dense graphs stay legible; clusters appear as blocks once rows and columns are reordered.

- Also known as: matrix view of a network, connectivity matrix, node-by-node matrix. Functions: relationships, patterns.
- Anatomy: The same node list on rows and columns, one cell per node pair, cell shade for link weight, a diagonal for self-links, optional cluster brackets.
- Fits: Dense networks where a node-link drawing becomes a hairball; Finding clusters, cliques and hubs as blocks and stripes; Checking whether a specific pair is linked; Showing weighted or directed links without clutter.
- Limits: The ordering decides what is visible; a poor order hides everything; Following a path over several hops is hard; Space grows with the square of the node count; Unfamiliar to general readers; needs a reading guide; Sparse graphs waste most of the grid.
- Data: network; keys categorical (some/many/huge); values quantitative (weight). Mark rect; channels position-x, position-y, color-luminance.
- Tasks: cluster, find-anomalies, retrieve-value, compare. Scale: up to ~1,000 nodes with one pixel per cell; labels readable to ~100. Modes: analysis, exploration. Profiles: data-analyst, scientist-reviewer, domain-expert.
- Rules: CMP-01, IDM-HEATMAP, EFF-17, COL-02. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: network-relationships, matrix-pattern-two-keys, flow-between-states. Similar: heatmap, network_diagram, chord_diagram, arc_diagram. Sibling chart-types.md: Hierarchies and networks.

### Arc Diagram (`arc_diagram`)

Network links drawn as arcs over a single horizontal line of nodes. Arc thickness shows how often two nodes connect, so a reader scans the arcs for pairs that co-occur and for clusters of linked items.

- Also known as: —. Functions: patterns, relationships.
- Anatomy: A straight baseline carrying the nodes, semicircular arcs rising above it as links, and arc stroke width encoding link frequency. Node labels sit along the line.
- Fits: Showing which items co-occur within one sequence; Compact one-dimensional view of a network; Comparing link frequency between pairs of nodes; Spotting clusters of mutual connections.
- Limits: Shows structure less clearly than 2D network diagrams; Too many links make the diagram cluttered; Harder to read as link count grows; Node ordering strongly shapes which patterns appear.
- Data: network; keys categorical (few/some/many); values quantitative (weight). Mark point; channels position-x, connection, size.
- Tasks: cluster, find-anomalies, retrieve-value. Scale: dozens of nodes, ~100 links; order of nodes decides what is visible. Modes: analysis, explanatory. Profiles: data-analyst, domain-expert, communicator-journalist.
- Rules: EFF-16, CMP-01. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: network-relationships. Similar: network_diagram. Sibling chart-types.md: Hierarchies and networks.

### Proportional Area Chart (`area_chart`)

Shapes such as squares or circles are sized so their area, not side length, matches each value, giving an at-a-glance sense of relative magnitude without axes. Readers compare how much space each shape occupies, though precise estimates are hard.

- Also known as: —. Functions: comparisons, proportions.
- Anatomy: A set of shapes, usually circles or squares, each scaled by its enclosed area. No axis or gridlines; relative size is the only cue, so labels usually supply exact values.
- Fits: Quick overview of relative sizes without a scale; Presentation slides where impact outweighs precision; Comparing a few quantities of very different magnitude; Infographics showing shares or counts of items.
- Limits: Sizing by length instead of area exaggerates differences; Values are hard to estimate accurately from area; Better suited to presentation than analytical work; Without labels, exact values remain unclear.
- Data: table; keys categorical (few); values quantitative (amount). Mark area; channels area.
- Tasks: gist, compare. Scale: 2–6 shapes. Modes: explanatory. Profiles: general-public, communicator-journalist.
- Rules: EFF-02, EFF-04, EXP-07. Discouraged (EFF-02): area is read inaccurately (Stevens ≈0.7); bars compare better; use only for impact with printed values. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: compare-values-across-categories. Similar: bubble_chart.

### Area Graph (`area_graph`)

A trend line with the space beneath it filled in, showing how a quantity develops across an interval such as time. Readers judge direction, peaks and overall volume rather than exact values; grouped and stacked variants show several series.

- Also known as: —. Functions: patterns, data-over-time.
- Anatomy: Horizontal interval or time axis, vertical value axis, a connecting line through the data points, and a shaded fill from that line down to the baseline. Multiple fills may overlap or stack.
- Fits: Tracking a quantity's development over time; Emphasising overall volume trends over exact values; Comparing a few series' trajectories side by side; Showing cumulative totals when series are stacked.
- Limits: Exact values are hard to read from the filled shape; Overlapping fills can obscure one another; Stacked layers make lower series harder to compare; Shaded area implies a zero baseline; truncated axes mislead; Not suited to unordered categories.
- Data: table; keys temporal (some/many/huge); values quantitative (amount). Mark area; channels position-x, position-y, length.
- Tasks: trend, find-extremum, gist. Scale: one or two series; hundreds of time points. Modes: explanatory. Profiles: general-public, executive, communicator-journalist.
- Rules: EXP-08, SCL-02, IDM-LINE. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: trend-single-series. Similar: line_graph, stacked_area_graph. Sibling chart-types.md: Time series / Area / stacked area / streamgraph.

### Arrow map (`arrow_map`) *(supplement)*

One arrow per region, anchored at the region, pointing in the direction of change between two periods and as long as the change is large. A glance shows where the shift went one way or the other and where it was strongest.

- Also known as: shift map, change-vector map, swing map. Functions: location, data-over-time.
- Anatomy: A plain base map, one arrow per region with a common origin rule, direction or colour for the sign of change, a legend showing a reference arrow length and direction.
- Fits: Change between exactly two periods across many regions; Showing direction and size of a shift together; Spatial patterns of gain versus loss; Results that swing between two options.
- Limits: Arrows overlap where regions are small and dense; Shows change only; the level before or after is lost; Direction mapping is arbitrary and needs a legend; Long arrows reach into neighbouring regions; Unusable for more than two periods.
- Data: geometry; keys geo-code (some/many/huge); temporal (few); values quantitative (delta). Mark arrow; channels position-x, position-y, orientation, length, color-hue.
- Tasks: compare, cluster, find-extremum, gist. Scale: hundreds of regions; thin out in dense areas. Modes: explanatory, analysis. Profiles: communicator-journalist, general-public, domain-expert, data-analyst.
- Rules: EFF-16, TXT-07, IDM-MAP, CMP-12. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: spatial-change-over-time. Similar: flow_map, choropleth, slope_chart, spike_map, streamline_map. Sibling chart-types.md: Geospatial / Flow / line maps, network maps.

### Bar Chart (`bar_chart`)

Rectangular bars whose lengths are proportional to a value, one bar per discrete category, drawn horizontally or vertically. Readers compare bar lengths against the value scale to see which categories are larger or smaller.

- Also known as: Bar Graph, Column Graph. Functions: comparisons, patterns.
- Anatomy: A category axis listing the groups, a value axis with a numeric scale, and solid bars starting from a common baseline. Bar length encodes magnitude; bars may be horizontal or vertical.
- Fits: Comparing values across named categories; Ranking items from largest to smallest; Showing counts for discrete groups; Displaying one measure across several categories.
- Limits: Not for continuous change over an interval; Easily confused with histograms, which bin continuous data; Bars should start at zero to compare fairly; Too many categories crowd the axis and labels.
- Data: table; keys categorical (few/some/many); values quantitative (amount). Mark line; channels position-x, length.
- Tasks: compare, find-extremum, sort, retrieve-value. Scale: readable to ~40 bars, hundreds with scrolling; one value per category. Modes: explanatory, analysis. Profiles: general-public, executive, domain-expert, student-learner, scientist-reviewer.
- Rules: EXP-08, CMP-01, COL-03, SCL-12, EXP-16. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: compare-values-across-categories, category-breakdown-over-time. Similar: histogram, multiset_barchart, population_pyramid, radial_bar_chart, radial_column_chart, stacked_bar_graph. Sibling chart-types.md: Quantities / Bar chart.

### Beeswarm plot (`beeswarm`) *(supplement)*

Every observation is a dot on a quantitative axis, pushed sideways just far enough that no two dots overlap. The packing is deterministic and the swarm widens where values are frequent, so it shows each point and the rough shape at once.

- Also known as: swarm plot, bee swarm. Functions: distribution, comparisons.
- Anatomy: One swarm per group along a quantitative axis, non-overlapping dots, sideways spread without meaning, optional median marker.
- Fits: Small to medium samples where every point should be visible; Showing ties and clusters that a strip would overplot; Reproducible alternative to random jitter; Colouring individual points by a second attribute.
- Limits: Packing shifts dots slightly off their true value; Swarm width depends on dot size, not only on density; Breaks down beyond a few hundred points per group; Sideways position carries no data; Layout algorithms differ between tools.
- Data: table; keys categorical (one/few/some); values quantitative (amount). Mark point; channels position-x, position-y.
- Tasks: characterize-distribution, compare, find-anomalies, determine-range. Scale: ≤ ~300 points per group, ≤ ~8 groups. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert, communicator-journalist.
- Rules: EXP-21, EFF-19, EXP-16. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: distribution-compare-groups, distribution-single. Similar: strip_plot, wilkinson_dot_plot, violin_plot, raincloud. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Box and Whisker Plot (`box_plot`)

A box covers the middle half of the values with a line inside marking the central value; whiskers stretch toward the extremes and isolated points flag outliers. Readers compare spread, symmetry and skew across groups.

- Also known as: —. Functions: distribution, range, comparisons, patterns.
- Anatomy: A central box spanning the inner quartiles, a median line within it, whiskers extending outward, and individual dots beyond the whisker ends for outliers. Drawn vertically or horizontally.
- Fits: Comparing distributions across many groups compactly; Spotting outliers in a dataset; Checking whether values are symmetric or skewed; Judging how tightly values cluster.
- Limits: Hides the detailed shape within the box; Less informative than histograms or density plots; Can make multimodal data look ordinary; Whisker rules differ between software packages.
- Data: table; keys categorical (one/few/some); values quantitative (amount). Mark glyph; channels position-x, position-y, length.
- Tasks: characterize-distribution, compare, find-anomalies, determine-range. Scale: dozens of groups; any n per group. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: EXP-16, DAT-03. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: distribution-compare-groups. Similar: span_chart, violin_plot, raincloud. Sibling chart-types.md: Distributions / Box plot.

### Brainstorm (`brainstorm`)

A central topic sits in the middle with main categories radiating outward and smaller branches splitting off them. Readers follow branches from the centre to see how ideas nest and relate; no numeric scale is involved.

- Also known as: Mind-map. Functions: concepts, relationships.
- Anatomy: A central node holding the main topic, labelled primary branches leaving it, and nested sub-branches off those. Layout is radial and free-form rather than axis-based.
- Fits: Capturing ideas at the start of a project; Organising notes into hierarchical categories; Supporting group brainstorming sessions; Mapping associations between related concepts; Visualising the structure of a topic.
- Limits: Encodes no quantitative values; Becomes cluttered as branches multiply; Relationships are informal and loosely defined; Structure depends on the author's manual choices.
- Data: tree; keys categorical (few/some); values none. Mark point; channels connection, containment.
- Tasks: gist. Scale: dozens of nodes. Modes: explanatory. Profiles: general-public, student-learner.
- Rules: PUR-10. Discouraged (PUR-10): encodes no data; a concept diagram, not a data visualization. Libraries: altair none, matplotlib none, plotly none.
- Archetypes: process-sequence. Similar: —.

### Bubble Chart (`bubble_chart`)

Labelled circles positioned on two numeric axes, with circle area encoding a third variable and colour often distinguishing categories. Readers compare positions and sizes to spot relationships, correlations and groups.

- Also known as: —. Functions: comparisons, data-over-time, distribution, patterns, proportions, relationships.
- Anatomy: Two numeric axes forming a Cartesian grid, circles whose area represents a value, colour fills for categories, and labels or a legend identifying each bubble. Time may appear as an axis or animation.
- Fits: Showing three numeric variables in one view; Comparing labelled categories on two measures and size; Revealing correlations across many entities; Animating how entities change over time.
- Limits: Crowded plots become hard to read; Sizing by radius rather than area misleads; Human judgement of circle area is imprecise; Interactivity often needed when bubbles are numerous.
- Data: table; keys categorical (few/some/many); values quantitative; quantitative; quantitative (amount). Mark point; channels position-x, position-y, area, color-hue.
- Tasks: correlate, find-anomalies, cluster, compare. Scale: dozens to a few hundred bubbles; size for ≤ 1 order of magnitude. Modes: analysis, explanatory, exploration. Profiles: data-analyst, domain-expert, communicator-journalist.
- Rules: EFF-02, EFF-04, EFF-16, SCL-05. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: multivariate-relationships, correlation-two-quantities. Similar: area_chart, scatterplot. Sibling chart-types.md: Relationships / Bubble chart.

### Bubble Map (`bubble_map`)

Circles placed over locations on a geographic map, each sized by its area in proportion to a value. Readers compare bubble sizes to see where a quantity concentrates, avoiding the area bias that large shaded regions create.

- Also known as: —. Functions: location, proportions.
- Anatomy: A base map with geographic regions, circles centred on locations, circle area encoding each value, and overlap between neighbouring bubbles. A size key helps readers interpret the scale.
- Fits: Comparing totals across countries or cities; Avoiding the area bias of shaded regions; Showing point-located values on a map; Revealing where a quantity concentrates geographically.
- Limits: Large bubbles overlap neighbouring bubbles and regions; Overlap can hide smaller values beneath larger ones; Area-based sizes are hard to judge precisely; Needs a size legend to be read accurately.
- Data: geometry; keys geo-code (some/many/huge); values quantitative (amount). Mark point; channels position-x, position-y, area.
- Tasks: find-extremum, compare, cluster. Scale: dozens to hundreds of places; overlap grows with density. Modes: explanatory, analysis. Profiles: general-public, domain-expert, communicator-journalist.
- Rules: EFF-04, EFF-02, IDM-MAP. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: spatial-distribution. Similar: dot_map, area_chart, spike_map. Sibling chart-types.md: Geospatial / Graduated / proportional symbol map.

### Bullet Graph (`bullet_graph`)

A compact bar showing a main measure, crossed by a short perpendicular marker for a target, and set over shaded bands for qualitative ranges. Readers check whether the bar passes the marker and which band it reaches.

- Also known as: —. Functions: comparisons, range.
- Anatomy: A thick central bar for the main value, a perpendicular target line, grey or coloured background bands for performance ranges, and a linear value scale along the length.
- Fits: Tracking actual performance against a target; Compact KPI displays on dashboards; Showing poor, average and good performance bands; Replacing gauges and meters on dashboards.
- Limits: Works best with no more than about five ranges; Overused bands clutter the display; Shade differences must remain distinguishable; Unfamiliar readers may need explanation.
- Data: table; keys categorical (one/few); values quantitative (amount); quantitative (amount). Mark line; channels length, position-x.
- Tasks: compare, retrieve-value, determine-range. Scale: a few KPIs per panel. Modes: explanatory. Profiles: executive, operator-monitoring.
- Rules: EXP-08, IDM-RADAR/GAUGE. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: compare-against-target. Similar: bar_chart. Sibling chart-types.md: Quantities / Gauge vs bullet chart.

### Bump chart (`bump_chart`) *(supplement)*

A line chart of ranks rather than values: each item is a line through its rank at each period, so overtakes appear as crossings. The value itself is not shown.

- Also known as: rank chart. Functions: data-over-time, comparisons.
- Anatomy: A time axis, a rank axis (1 at the top), one line per item with direct labels at the ends, a highlighted item.
- Fits: Rank changes over several periods; Replacing an animated bar chart race; Leaderboards over time.
- Limits: Hides magnitudes; a rank change of one may be a large or tiny value change; Many items tangle; Ties need a rule.
- Data: table; keys temporal (few/some); categorical (few/some); values quantitative (position). Mark line; channels position-x, position-y, connection, color-hue.
- Tasks: sort, trend, compare. Scale: ≤ ~15 items × ≤ ~12 periods. Modes: explanatory, analysis. Profiles: communicator-journalist, executive, general-public.
- Rules: EXP-18, TXT-04. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: rank-change-two-points, trend-many-series. Similar: line_graph, slope_chart. Sibling chart-types.md: Time series / Animation / bar chart race.

### Calendar (`calendar`)

A grid of day cells arranged into weekday columns and week rows, usually one month per grid, so dates follow chronological order. Readers locate specific days or events and see how time units sequence across the period.

- Also known as: —. Functions: data-over-time, reference-tool.
- Anatomy: Cells each representing one date, column headers for weekdays, rows for weeks, and month or year divisions. Events or colour fills can be placed inside individual cells.
- Fits: Planning schedules and recurring events; Showing a sequence of dates across months; Displaying daily values across a year; Familiar reference layout for dates.
- Limits: Shows time units rather than continuous magnitudes; Calendar layouts vary across cultures and systems; Long spans require many grids, reducing overview; Dense entries crowd individual cells.
- Data: table; keys temporal (many/huge); values quantitative (amount). Mark rect; channels position-x, position-y, color-luminance.
- Tasks: find-anomalies, trend, retrieve-value. Scale: one value per day over months or years. Modes: analysis, explanatory. Profiles: domain-expert, data-analyst, operator-monitoring.
- Rules: COL-02, IDM-HEATMAP. Libraries: altair native, matplotlib workaround, plotly workaround.
- Archetypes: seasonality-cycles. Similar: timetable. Sibling chart-types.md: Time series / Calendar heatmap, punch card.

### Candlestick Chart (`candlestick_chart`)

A financial price chart with one symbol per time period. Each symbol's wide body spans the opening and closing prices, thin wicks reach the period's high and low, and colour indicates whether price rose or fell.

- Also known as: Japanese Candlestick Chart. Functions: data-over-time, patterns, range.
- Anatomy: Time along the horizontal axis, price on the vertical axis, and candle symbols made of a rectangular real body plus upper and lower shadows. Body colour marks bullish or bearish direction.
- Fits: Analysing price movement of traded securities; Viewing open, high, low and close per period; Spotting reversal or continuation patterns; Reading daily trading sentiment at a glance.
- Limits: Does not show movement within each period; Easily confused with box plots; Named patterns' predictive value is disputed; Colour conventions differ between markets.
- Data: table; keys temporal (some/many/huge); values quantitative (amount); quantitative (amount); quantitative (amount); quantitative (amount). Mark glyph; channels position-x, position-y, length, color-hue.
- Tasks: trend, determine-range, find-anomalies. Scale: hundreds of periods. Modes: analysis. Profiles: domain-expert, data-analyst.
- Rules: COL-05, TXT-07. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: range-per-item, trend-single-series. Similar: kagi_chart, OHLC_chart.

### Chord Diagram (`chord_diagram`)

Entities arranged around a circle, joined by arcs or curved ribbons whose width reflects each connection's value. Readers follow the links to see which entities share things in common and how strongly they connect.

- Also known as: —. Functions: comparisons, relationships.
- Anatomy: A ring of labelled segments around the circumference, curved connections between segments, connection width proportional to value, and colour grouping categories.
- Fits: Comparing similarity within a dataset; Showing flows between groups of entities; Revealing which groups share most in common; Presenting mutual relationships in a circular layout.
- Limits: Clutters quickly when many connections appear; Ribbon ends are hard to trace precisely; Direction of flows can be ambiguous; Exact values need labels or interactivity.
- Data: network; keys categorical (few/some); values quantitative (weight). Mark area; channels angle, connection, size, color-hue.
- Tasks: compare, cluster, gist. Scale: ≤ ~12 nodes before ribbons tangle. Modes: explanatory, analysis. Profiles: communicator-journalist, domain-expert.
- Rules: EFF-16, EFF-11. Libraries: altair none, matplotlib workaround, plotly workaround.
- Archetypes: flow-between-states, network-relationships. Similar: non_ribbon_chord_diagram, adjacency_matrix. Sibling chart-types.md: Hierarchies and networks.

### Choropleth Map (`choropleth`)

A map whose geographic regions are shaded according to a data value on a colour progression. Readers scan the shading to see regional variation and spatial clusters, though exact figures are difficult to recover from colour.

- Also known as: —. Functions: comparisons, location, patterns.
- Anatomy: Region boundaries forming the base map, a fill colour or pattern per region, and a colour scale legend linking shades to value ranges. Labels may name the regions.
- Fits: Showing rates or normalised values across regions; Comparing regional variation on one measure; Spotting spatial clusters or regional gradients; Presenting results by administrative area.
- Limits: Large regions look more important than small ones; Colour makes exact values hard to read; Raw counts mislead unless normalised; Colour scale choice can distort perceived differences.
- Data: geometry; keys geo-code (some/many/huge); values quantitative (rate). Mark geoshape; channels color-luminance.
- Tasks: cluster, find-extremum, compare, gist. Scale: dozens to thousands of regions; ~5–7 color classes. Modes: explanatory, analysis. Profiles: general-public, domain-expert, communicator-journalist, executive.
- Rules: EXP-12, COL-02, EXP-17, IDM-MAP. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: spatial-distribution, spatial-change-over-time. Similar: tile_cartogram, spike_map. Sibling chart-types.md: Geospatial / Choropleth.

### Circle Packing (`circle_packing`)

Nested circles where containment expresses hierarchy: each branch is a circle holding its sub-branches as smaller circles. Circle area can carry an extra quantity. Readers read depth from nesting and size from area.

- Also known as: Circular Treemap. Functions: hierarchy, proportions.
- Anatomy: Outer enclosing circles for top-level branches, smaller circles nested inside for sub-branches, circle area encoding a numeric value, and optional colour shades for categories.
- Fits: Showing nested groups with a size attribute; Revealing hierarchical structure clearly; Displaying file or folder sizes in a tree; Visualising budgets split into nested categories.
- Limits: Wastes space with gaps between circles; Less space-efficient than a treemap; Small nested circles are hard to compare; Area judgements can be imprecise.
- Data: tree; keys categorical (some/many/huge); values quantitative (amount). Mark area; channels containment, area, color-hue.
- Tasks: gist, find-extremum, cluster. Scale: hundreds of leaves; depth ≤ 3. Modes: explanatory. Profiles: general-public, communicator-journalist.
- Rules: EFF-02, CLT-03. Libraries: altair none, matplotlib workaround, plotly workaround.
- Archetypes: part-to-whole-hierarchy, hierarchy-structure. Similar: treemap. Sibling chart-types.md: Proportions / Treemap.

### Connected scatterplot (`connected_scatterplot`) *(supplement)*

A scatterplot of two measures where the points of one entity are joined in time order, so the path shows how the two measures co-evolved. Direct year labels on the path replace a time axis.

- Also known as: —. Functions: relationships, data-over-time.
- Anatomy: Two quantitative axes, one polyline per entity through its points in time order, arrowheads or labels for direction, a highlighted entity.
- Fits: Co-evolution of two quantities over time; Trajectories of a few entities; Showing both the relation and the change.
- Limits: Hard to read without direction cues; More than a few entities tangle; Unfamiliar to general readers.
- Data: table; keys temporal (few/some); categorical (one/few); values quantitative; quantitative. Mark point; channels position-x, position-y, connection, text.
- Tasks: correlate, trend, compare. Scale: ≤ 5 entities × dozens of points. Modes: explanatory, analysis. Profiles: communicator-journalist, domain-expert, data-analyst.
- Rules: EFF-17, TXT-04. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: correlation-two-quantities, trend-few-series. Similar: scatterplot, line_graph. Sibling chart-types.md: Relationships / Connected scatterplot / dumbbell / range plot.

### Connection Map (`connection_map`)

Points placed on a geographic map, joined by straight or curved lines representing connections between places. Readers trace lines to follow routes or single chains, and dense bundles reveal where links concentrate spatially.

- Also known as: Link Map, Ray Map. Functions: distribution, location, movement-or-flow, patterns, relationships.
- Anatomy: A base map with plotted location points, straight or arced lines joining pairs of points, and line styling that may vary by strength or direction.
- Fits: Showing flight or shipping routes between places; Revealing hubs and concentrated link patterns; Mapping a chain of linked locations; Displaying geographic relationships between many sites.
- Limits: Dense lines create visual clutter quickly; Curved arcs can distort apparent distances; Individual link strength is hard to judge; Overlapping routes hide one another.
- Data: geometry; keys geo-code (some/many); geo-code (some/many); values quantitative (weight). Mark line; channels position-x, position-y, connection.
- Tasks: cluster, find-extremum, gist. Scale: dozens to hundreds of links before clutter. Modes: explanatory, analysis. Profiles: communicator-journalist, domain-expert.
- Rules: EFF-16, IDM-MAP. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: flow-between-states. Similar: flow_map. Sibling chart-types.md: Geospatial / Flow / line maps, network maps.

### Table (`data_table`) *(supplement)*

Rows and columns of values with aligned numbers, light row separation and sorted order. The right answer when precision, heterogeneous attributes or a handful of numbers matter more than shape.

- Also known as: data table, formatted table. Functions: reference-tool, comparisons.
- Anatomy: Header row, one row per item, text left-aligned, numbers right-aligned with equal decimals, optional inline bars or shading, sorted by the key column.
- Fits: Exact values that will be quoted; Mixed numeric and text attributes; Few values where a chart would be decoration.
- Limits: No overview of shape or trend; Scanning many rows is slow; Unsorted tables hide ranking.
- Data: table; keys categorical (few/some); values quantitative (amount). Mark text; channels position-x, position-y.
- Tasks: retrieve-value, sort, compare. Scale: dozens of rows on one screen. Modes: explanatory, analysis. Profiles: executive, domain-expert, scientist-reviewer, data-analyst, general-public, student-learner, operator-monitoring, communicator-journalist.
- Rules: IDM-TABLE, TXT-13, PUR-02. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: exact-values-lookup, compare-values-across-categories. Similar: timetable, stem_and_leaf_plot. Sibling chart-types.md: Tables and text.

### Dendrogram (`dendrogram`) *(supplement)*

A tree produced by hierarchical clustering. Every leaf sits on the same baseline and two branches join at a height equal to the distance at which their clusters merge, so the reader sees which items group early (similar) and which only join near the top.

- Also known as: cluster tree, linkage tree, clustering tree. Functions: hierarchy, relationships.
- Anatomy: Leaves aligned on one level with labels, right-angled branches, a quantitative merge-distance axis, optional cut line that defines the clusters.
- Fits: Showing how items group at successive similarity levels; Choosing a number of clusters by cutting at a height; Ordering the rows or columns of a heatmap; Comparing two clusterings side by side.
- Limits: Leaf order is partly arbitrary: branches can flip freely; Neighbouring leaves are not necessarily similar; Result depends on the distance and linkage chosen; state them; Hundreds of leaves make labels unreadable.
- Data: tree; keys categorical (some/many); values quantitative (amount). Mark line; channels connection, position-x, position-y, length.
- Tasks: cluster, compare, find-anomalies. Scale: up to a few hundred leaves; labels readable to ~60. Modes: analysis, exploration. Profiles: data-analyst, scientist-reviewer, domain-expert.
- Rules: CMP-01, TXT-07, EFF-17. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: hierarchy-structure, matrix-pattern-two-keys. Similar: tree_diagram, heatmap, indented_tree. Sibling chart-types.md: Hierarchies and networks.

### Density Plot (`density_plot`)

A smoothed curve over a continuous variable whose height shows how concentrated values are at each point. Readers look for peaks, valleys, skew and the number of modes to understand a distribution's shape.

- Also known as: Kernel Density Plot, Density Trace Graph. Functions: distribution, patterns.
- Anatomy: Horizontal axis of the variable's values, vertical density axis, one smoothed line sometimes filled beneath, and peaks marking concentration. Several curves may be overlaid for comparison.
- Fits: Judging the shape of a numeric distribution; Spotting multiple peaks within data; Comparing smoothed distributions across groups; Avoiding histogram bin-count sensitivity.
- Limits: Smoothing bandwidth can change apparent shape; Smoothing may blur genuine small features; Curve can extend beyond the data's actual range; Densities are not raw counts, confusing lay readers.
- Data: table; keys categorical (one/few); values quantitative (amount). Mark area; channels position-x, position-y.
- Tasks: characterize-distribution, compare, find-anomalies. Scale: a few overlaid groups; n ≥ ~50 per group. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: EXP-15, COL-10. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: distribution-single, distribution-compare-groups, distribution-change-over-time. Similar: histogram, raincloud. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Difference view (`difference_view`) *(supplement)*

The difference between two states is computed and drawn as its own mark: diverging bars or a diverging heatmap of B minus A around a zero line, often placed next to the two originals. The reader sees the change directly instead of subtracting by eye.

- Also known as: explicit difference chart, delta chart, change view. Functions: comparisons.
- Anatomy: A zero reference line or neutral colour, marks for B minus A in two directions, sorted items, optional side panels with the original values.
- Fits: Before versus after, plan versus actual, model versus observed; Small changes that side-by-side charts would hide; Ranking items by how much they changed; Matrices compared cell by cell.
- Limits: Hides the absolute level unless the originals stay visible; Absolute and relative change tell different stories; name the one used; Only compares two states at a time; Differences of noisy values need their own uncertainty.
- Data: table; keys categorical (few/some/many); categorical (few); values quantitative (delta). Mark line; channels position-x, position-y, length, color-hue.
- Tasks: compare, sort, find-extremum, find-anomalies, compute-derived. Scale: dozens of items as bars; hundreds × hundreds of cells as a heatmap. Modes: analysis, explanatory, exploration. Profiles: data-analyst, domain-expert, executive, scientist-reviewer, communicator-journalist.
- Rules: CMP-12, CMP-13, CMP-01, COL-02. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: rank-change-two-points, compare-against-target, compare-two-keys. Similar: dumbbell_plot, slope_chart, bar_chart, heatmap, small_multiples.

### Donut Chart (`donut_chart`)

A ring-shaped variant of the pie in which arcs stand for parts of a whole. Readers mainly judge arc length rather than slice area, so the hollow centre can hold a headline figure. Suits a few shares; comparing several rings is easier than comparing several pies.

- Also known as: —. Functions: comparisons, part-to-a-whole, proportions.
- Anatomy: A circular ring split into coloured arcs, one per category. Arc length carries the value. The empty centre often holds a total or label, and a legend or direct labels identify each arc.
- Fits: Showing a few shares of one whole; Highlighting a single headline total in the centre; Tracking how shares shift across several rings; Compact dashboard summaries with few categories.
- Limits: Many small arcs become hard to tell apart; Arc lengths are still tricky to estimate precisely; Misleading when categories do not sum to a whole; Inherits pie criticism about weak comparisons between slices.
- Data: table; keys categorical (few); values quantitative (share). Mark arc; channels angle, color-hue.
- Tasks: gist, retrieve-value. Scale: 2–5 parts. Modes: explanatory. Profiles: general-public, executive.
- Rules: IDM-PIE, EXP-05, EFF-02, CMP-01. Discouraged (IDM-PIE): angle is a weak channel; only for ≤5 parts of a whole with simple fractions. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: part-to-whole-single. Similar: pie_chart, sunburst_diagram. Sibling chart-types.md: Proportions / Pie / donut.

### Dot Map (`dot_map`)

Identical dots are placed over a geographic base map, each dot marking one item or a fixed number of items. Dense clusters reveal where things concentrate and empty areas show sparseness. It gives an overview of spatial spread rather than exact figures.

- Also known as: Point Map, Dot Distribution Map, Dot Density Map. Functions: distribution, location, patterns.
- Anatomy: A base map of a region, uniform point markers, and an optional key stating whether one dot equals one unit or several. Spatial clustering is the main visual signal.
- Fits: Seeing where events or objects concentrate geographically; Spotting clusters across a region; Giving an overview of spatial distribution; Counting objects where one dot stands for a unit.
- Limits: Exact values are not readable from dot positions; Overlapping dots hide density in crowded areas; Unit size is unclear unless the key is explicit; One-to-many dots make small counts hard to see.
- Data: geometry; keys geo-code (many/huge); values none. Mark point; channels position-x, position-y.
- Tasks: cluster, gist, find-anomalies. Scale: thousands of points; overplotting in dense areas. Modes: analysis, explanatory. Profiles: domain-expert, data-analyst, communicator-journalist.
- Rules: EFF-16, IDM-MAP. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: point-events-on-map. Similar: bubble_map. Sibling chart-types.md: Geospatial / Dot map / pixel map.

### Dot Matrix Chart (`dot_matrix_chart`)

A grid of evenly spaced dots, each coloured by category, showing how many items fall into each group. Counting coloured dots gives a quick feel for composition, and several grids can be compared to spot patterns. With one colour it mainly conveys a proportion.

- Also known as: icon array, waffle chart. Functions: comparisons, distribution, patterns, proportions.
- Anatomy: A rectangular lattice of identical dots. Colour codes the category, a legend maps colours to groups, and each dot represents one counted unit.
- Fits: Quick overview of category shares in a dataset; Comparing composition across several groups; Showing discrete counts in an approachable pictogram style; Showing a single share with one colour; Communicating a risk as a frequency, such as 3 in 10.
- Limits: Exact values are hard to read by counting dots; Many colours make categories hard to distinguish; Dot totals need a key to match real quantities; Less useful for very large or continuous data.
- Data: table; keys categorical (few); values quantitative (count). Mark point; channels color-hue, position-x, position-y.
- Tasks: gist, compare. Scale: ≤ a few hundred dots, ≤ 5 categories. Modes: explanatory. Profiles: general-public, communicator-journalist, student-learner.
- Rules: COL-04, EFF-02, PUR-14. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: part-to-whole-single, uncertainty-of-estimate-or-forecast. Similar: pictogram, quantile_dotplot.

### Dot plot (`dot_plot`) *(supplement)*

One point per category placed on a quantitative axis, categories sorted by value. Position carries the value, so the axis need not start at zero and small differences stay visible.

- Also known as: Cleveland dot plot, lollipop chart. Functions: comparisons.
- Anatomy: A category axis with one row per item, a quantitative axis, a dot per item, optional thin stems (lollipop) and value labels.
- Fits: Comparing values across categories when differences are small; Ranking dozens of items; Showing values whose scale is far from zero.
- Limits: Must be sorted by value or it becomes hard to read; No zero baseline, so readers must check the axis start; Stems add ink without information.
- Data: table; keys categorical (few/some/many); values quantitative (amount). Mark point; channels position-x, position-y.
- Tasks: compare, sort, find-extremum, retrieve-value. Scale: dozens of rows, more with scrolling. Modes: explanatory, analysis. Profiles: executive, domain-expert, scientist-reviewer, data-analyst, general-public.
- Rules: CMP-01, SCL-02, EFF-05. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: compare-values-across-categories. Similar: bar_chart, slope_chart. Sibling chart-types.md: Quantities / Dot plot / lollipop.

### Dumbbell plot (`dumbbell_plot`) *(supplement)*

Each item is a row with two dots joined by a segment, one per state or period; the segment length is the change or gap. Rows are sorted by one of the values or by the gap.

- Also known as: connected dot plot, range plot with two values. Functions: comparisons, range.
- Anatomy: A category axis with one row per item, a quantitative axis, two dots of distinct hue per row joined by a line, direct labels.
- Fits: Gap between two groups per item; Change between two periods with a common scale; Before/after per category.
- Limits: Only two values per item; Sign of the change needs a cue (arrow or color) when dots cross; Many rows need sorting and space.
- Data: table; keys categorical (few/some/many); categorical (few); values quantitative (amount). Mark point; channels position-x, position-y, connection, color-hue.
- Tasks: compare, sort, compute-derived, find-extremum. Scale: dozens of rows. Modes: explanatory, analysis. Profiles: executive, domain-expert, scientist-reviewer, general-public.
- Rules: CMP-01, TXT-04. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: rank-change-two-points, compare-two-keys, range-per-item. Similar: slope_chart, span_chart, difference_view. Sibling chart-types.md: Relationships / Connected scatterplot / dumbbell / range plot.

### Ensemble plot (`ensemble_plot`) *(supplement)*

One line or path per model run, simulation or posterior draw, overlaid in a thin translucent stroke. Agreement shows as a tight bundle and uncertainty as spread; a contour boxplot summarises the same members into a median path and bands.

- Also known as: spaghetti plot, ensemble display, contour boxplot. Functions: data-over-time, range, patterns.
- Anatomy: Many thin semi-transparent lines sharing both axes, an optional highlighted mean or median member, a note on how many members and from which run.
- Fits: Showing forecast spread without assuming a distribution shape; Revealing distinct scenarios that a band would average away; Trajectories or paths from a simulation ensemble; Expert readers who know the models behind the members.
- Limits: Members from different models or dates are not comparable; Line density reflects member count, not only probability; Dozens of lines tangle; individual members cannot be followed; One odd member attracts more attention than it deserves; Readers may take each line as an equally likely outcome.
- Data: table; keys temporal (some/many/huge); categorical (some/many); values quantitative (amount). Mark line; channels position-x, position-y, color-luminance.
- Tasks: determine-range, trend, cluster, find-anomalies. Scale: ~10–100 members; summarise beyond. Modes: analysis, exploration, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: DAT-12, EFF-16, DAT-03, COL-10. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: uncertainty-of-estimate-or-forecast. Similar: line_graph, gradient_interval, hypothetical_outcome_plot, small_multiples.

### Error Bars (`error_bars`)

A graphical overlay on a Cartesian plot that draws capped lines from a data point to show uncertainty or spread, such as standard error, confidence intervals, or min-max range. Short bars mean values cluster tightly around the plotted point; long bars mean the estimate is less certain.

- Also known as: —. Functions: range.
- Anatomy: Cap-tipped line segments attached to points or bar edges. They run parallel to a quantitative axis, vertically or horizontally, and may be balanced or unbalanced on each side. The underlying chart supplies the marks.
- Fits: Showing uncertainty around averages in scientific plots; Adding confidence intervals to bar or line charts; Comparing precision across several estimates; Displaying min and max ranges for each category.
- Limits: Not a standalone chart; needs an underlying plot; Readers may not know which statistic is shown; Symmetric-looking bars can hide skewed data; Mixing standard deviation and standard error causes confusion.
- Data: table; keys categorical (few/some); values quantitative (amount); quantitative (amount); quantitative (amount). Mark line; channels length, position-y.
- Tasks: determine-range, compare. Scale: overlay on any point/bar chart. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst.
- Rules: DAT-03, EXP-16. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: range-per-item, uncertainty-of-estimate-or-forecast. Similar: gradient_interval, quantile_dotplot.

### Flow Chart (`flow_chart`)

A diagram of a process drawn as connected symbols joined by arrows that show the order of steps. Rounded terminators bracket the sequence, rectangles hold actions and diamonds mark decisions with branching paths. Read it by following the arrows from start to finish.

- Also known as: Flow Diagram, Flow Process Chart, Process Chart, Process Map, Process Model, Work Flow Diagram. Functions: concepts, how-things-work, processes-and-methods.
- Anatomy: Standardised symbols: rounded terminators for start and end, rectangles for steps, diamonds for decisions. Labels sit inside shapes, connecting lines or arrows show direction, and the layout runs horizontally or vertically.
- Fits: Documenting a multistep procedure or workflow; Explaining an algorithm or system to non-experts; Planning or redesigning an existing process; Showing decision points and alternative branches.
- Limits: Reader must know the symbol conventions; Large processes become tangled and hard to follow; Shows sequence, not timing or durations; Symbol sets vary between tools and organisations.
- Data: network; keys categorical (few/some); values none. Mark glyph; channels connection, shape.
- Tasks: gist. Scale: dozens of steps. Modes: explanatory. Profiles: general-public, student-learner, domain-expert.
- Rules: PUR-10. Discouraged (PUR-10): a process diagram, not a data visualization; use only to explain a method. Libraries: altair none, matplotlib none, plotly none.
- Archetypes: process-sequence. Similar: —.

### Flow Map (`flow_map`)

A geographic map where lines run between places to show the movement of people, goods, or other items, with line thickness scaled to volume. Arrowheads show direction, while plain lines can suggest two-way exchange. Merged or bundled lines reduce clutter.

- Also known as: —. Functions: distribution, location, movement-or-flow.
- Anatomy: A base map with origin points, flow lines whose width encodes magnitude, optional arrowheads for direction, and bundled lines where routes overlap.
- Fits: Migration or commuting flows between regions; Trade volumes between countries or ports; Showing where goods or animals travel from and to; Comparing relative size of several routes.
- Limits: Many crossing lines create visual clutter; Line thickness alone makes exact volumes hard to judge; Lines without arrows hide the direction of movement; Bundling can merge distinct routes into one line.
- Data: geometry; keys geo-code (few/some); geo-code (few/some/many); values quantitative (weight). Mark line; channels position-x, position-y, size, connection.
- Tasks: find-extremum, compare, gist. Scale: dozens of flows; bundle beyond. Modes: explanatory, analysis. Profiles: communicator-journalist, domain-expert, general-public.
- Rules: EFF-16, EFF-02. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: flow-between-states. Similar: connection_map, sankey_diagram, streamline_map, arrow_map. Sibling chart-types.md: Geospatial / Flow / line maps, network maps.

### Gantt Chart (`gantt_chart`)

A timeline laid out as a table, where each row is a task and a horizontal bar spans the period it runs. Bar position and length show start, end, duration, and overlap. Dependencies, progress fills, milestones, and a current-date line add detail; it is mainly used to plan and track projects.

- Also known as: —. Functions: data-over-time, processes-and-methods, range, reference-tool.
- Anatomy: Task labels down the left, a time scale across the top, horizontal bars placed by start and end, optional arrows for dependencies, partial fills for completion, milestone symbols, and a vertical today-line.
- Fits: Scheduling and tracking project tasks over time; Seeing which activities run in parallel; Comparing progress against planned durations; Identifying dependencies and the critical path.
- Limits: Becomes unreadable with very many tasks; Does not show cost or resource load by default; Progress fills can be misread without a clear legend; Needs start dates and durations for every task.
- Data: table; keys categorical (few/some/many); values temporal (position); temporal (position). Mark line; channels position-x, position-y, length.
- Tasks: determine-range, sort, retrieve-value. Scale: dozens of rows. Modes: explanatory, analysis. Profiles: executive, domain-expert, operator-monitoring.
- Rules: CMP-01, TXT-03. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: event-timeline-intervals, categorical-state-over-time. Similar: span_chart.

### Gradient interval plot (`gradient_interval`) *(supplement)*

An estimate drawn with its uncertainty as nested or fading bands: a central line or point, darker ink where values are more probable, lighter towards the tails. Along time it becomes a fan that widens with the forecast horizon.

- Also known as: gradient plot, fan chart, confidence band, interval band, probability density and interval plot. Functions: range, data-over-time.
- Anatomy: A central estimate line or point, one or more shaded bands for named probability levels, fading opacity outward, a legend stating each level.
- Fits: Forecasts whose uncertainty grows over time; Estimates per category with a stated interval; Avoiding the false cliff of a single hard-edged interval; Expert readers comparing estimates and their precision.
- Limits: Band edges get read as limits the value cannot cross; On maps or paths the band looks like a physical area; Probability levels must be labelled or the bands mean nothing; Opacity steps are hard to compare precisely; Overlapping bands of several series blend together.
- Data: table; keys categorical (one/few/some/many/huge); values quantitative (amount); quantitative (amount); quantitative (amount). Mark area; channels position-x, position-y, length, color-luminance.
- Tasks: determine-range, trend, compare, retrieve-value. Scale: 1–4 series over time, or dozens of estimates as rows; ≤ 3–4 bands. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert, communicator-journalist, executive.
- Rules: DAT-03, DAT-11, PUR-14, DAT-13. Libraries: altair native, matplotlib native, plotly workaround.
- Archetypes: uncertainty-of-estimate-or-forecast, range-per-item. Similar: error_bars, quantile_dotplot, ensemble_plot, area_graph, violin_plot.

### Heatmap (Matrix) (`heatmap`)

A grid where rows and columns list two sets of categories and each cell's colour encodes a value, categorical or numeric. Shade differences reveal patterns, similarities, and correlations across the matrix. A colour legend is essential for decoding the cells.

- Also known as: —. Functions: comparisons, data-over-time, patterns, relationships.
- Anatomy: Row and column labels along the edges, coloured cells at their intersections, a legend mapping colours to categories or a gradient scale, and optionally numbers printed inside cells.
- Fits: Spotting patterns across two category dimensions; Showing variation across many variables at once; Revealing correlations between variables; Tracking values across time periods and locations.
- Limits: Colour shades are hard to compare precisely; Exact values are hard to extract without cell labels; Meaningless without a legend to decode colours; Colour scales can exaggerate small differences.
- Data: table; keys categorical (few/some/many/huge); categorical (few/some/many/huge); values quantitative (amount). Mark rect; channels position-x, position-y, color-luminance.
- Tasks: cluster, find-anomalies, compare, characterize-distribution. Scale: hundreds × hundreds of cells; ~10 color levels. Modes: analysis, exploration, explanatory. Profiles: domain-expert, data-analyst, scientist-reviewer.
- Rules: IDM-HEATMAP, COL-02, CMP-01, COL-04. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: trend-many-series, matrix-pattern-two-keys, compare-two-keys, seasonality-cycles, categorical-state-over-time. Similar: adjacency_matrix, dendrogram. Sibling chart-types.md: Relationships / Heat map.

### Histogram (`histogram`)

A column chart of one numeric variable's distribution: the horizontal axis is cut into continuous intervals called bins, and each bar's height counts the values in its bin. The overall shape shows where values concentrate, where the extremes lie, and whether gaps or unusual values appear.

- Also known as: —. Functions: distribution, patterns.
- Anatomy: Touching bars on a continuous horizontal axis, bar height equal to frequency per bin, a vertical count or density axis, and labelled interval ranges. Bin width is a visible design choice.
- Fits: Checking the shape of a numeric variable; Finding outliers, gaps, or skew in a dataset; Estimating where most observations concentrate; Giving a rough view of a probability distribution.
- Limits: Bin width choice can change the apparent shape; Uneven bin widths mislead unless scaled as density; Not suited to categorical data; Individual values inside each bin are hidden.
- Data: table; keys none; values quantitative (amount). Mark line; channels position-x, length.
- Tasks: characterize-distribution, find-anomalies, determine-range. Scale: any n; 10–50 bins. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert, student-learner.
- Rules: EXP-15, EXP-08. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: distribution-single, distribution-change-over-time. Similar: bar_chart, density_plot, population_pyramid, wilkinson_dot_plot. Sibling chart-types.md: Distributions / Histogram.

### Horizon graph (`horizon_graph`) *(supplement)*

An area chart folded into bands and mirrored for negative values, each band darker the further from the baseline, so many series fit in little vertical space.

- Also known as: —. Functions: data-over-time, patterns.
- Anatomy: One narrow row per series, a shared time axis, overlapping bands of increasing darkness, two hues for positive and negative.
- Fits: Dozens of time series in a small space; Spotting extremes across many series; Monitoring panels.
- Limits: Needs learning; Exact values unreadable; Only for readers who will see it repeatedly.
- Data: table; keys temporal (many/huge); categorical (some/many); values quantitative (delta). Mark area; channels position-x, color-luminance, length.
- Tasks: find-anomalies, trend, compare. Scale: dozens of series × hundreds of points. Modes: analysis. Profiles: data-analyst, operator-monitoring, domain-expert.
- Rules: EFF-17. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: trend-many-series. Similar: small_multiples, heatmap, sparkline. Sibling chart-types.md: Time series / Horizon graph.

### Hypothetical outcome plot (`hypothetical_outcome_plot`) *(supplement)*

An animation in which each frame is one plausible outcome drawn from the distribution, shown with the same marks as an ordinary chart. Watching the frames change lets readers feel how often one outcome beats another instead of decoding an interval.

- Also known as: HOP, animated draws. Functions: range, distribution.
- Anatomy: An ordinary chart whose marks jump between sampled outcomes several times a second, an optional frame counter, a caption saying each frame is one draw.
- Fits: Lay readers judging how reliable a difference is; Uncertainty in orderings, trends or other joint outcomes; Interactive media where animation is available; Building intuition that estimates could have been otherwise.
- Limits: Needs animation; unusable in print or static reports; Readers cannot compare frames no longer on screen; Probabilities are estimated by watching, hence slow and imprecise; Frame rate and number of draws change what is perceived; Motion draws attention away from everything else.
- Data: table; keys categorical (few/some); categorical (some/many/huge); values quantitative (amount). Mark point; channels position-x, position-y.
- Tasks: compare, determine-range, gist. Scale: a handful of marks per frame; 50+ draws at ~2–3 frames per second. Modes: explanatory. Profiles: general-public, communicator-journalist, student-learner.
- Rules: PUR-14, CMP-08, EXP-18, DAT-03. Libraries: altair none, matplotlib workaround, plotly native.
- Archetypes: uncertainty-of-estimate-or-forecast. Similar: quantile_dotplot, ensemble_plot, gradient_interval, error_bars. Sibling chart-types.md: Time series / Animation / bar chart race.

### Icicle plot (`icicle`) *(supplement)*

A space-filling hierarchy in rectangular coordinates: each level is a band, each node a rectangle placed directly under its parent, and the node's length along the band is proportional to its value. Depth and size are read on two separate straight axes.

- Also known as: adjacency diagram, partition layout, flame graph, icicle tree. Functions: hierarchy, part-to-a-whole, proportions.
- Anatomy: Stacked bands, one per level; rectangles whose length encodes value; children aligned beneath their parent; labels inside the rectangles; root band spanning the full extent.
- Fits: Seeing structure and size together with aligned lengths; Comparing sizes within one level along a common axis; Profiling call stacks or nested costs (flame graph); Hierarchies of moderate depth with labelled nodes.
- Limits: Deep levels shrink to slivers too thin to label; Every level costs a full band of space; Sizes in different levels are not on a common baseline; Sibling order must be meaningful or sorted by size.
- Data: tree; keys categorical (some/many); values quantitative (amount). Mark rect; channels length, position-x, position-y, containment.
- Tasks: compare, find-extremum, retrieve-value, gist. Scale: hundreds of nodes; depth ≤ ~6 bands. Modes: analysis, exploration, explanatory. Profiles: data-analyst, domain-expert, scientist-reviewer.
- Rules: EFF-19, TXT-10, CMP-01. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: hierarchy-structure, part-to-whole-hierarchy. Similar: treemap, sunburst_diagram, tree_diagram. Sibling chart-types.md: Hierarchies and networks.

### Illustration Diagram (`illustration_diagram`)

A picture, which may be a drawing, sketch, wireframe, or photograph, annotated with labels, notes, or a legend. It explains a concept, describes an object or place, or shows how something works or changes. Cutaways and enlargements add depth where needed.

- Also known as: —. Functions: concepts, how-things-work, processes-and-methods.
- Anatomy: A central image carrying the content, callout labels or leader lines, notes or a legend, and optional enlargements or cross-sections. Imagery can be symbolic, pictorial, or realistic.
- Fits: Explaining how an object or mechanism is built; Describing a place or object with annotations; Teaching a concept through a labelled picture; Showing internal workings with cross-section views.
- Limits: Labels and notes can crowd the image; Accuracy depends on how faithfully the image is drawn; Not data-driven; values are not encoded; Interpretation depends on the annotator's choices.
- Data: text; keys none; values none. Mark glyph; channels .
- Tasks: gist. Scale: n/a. Modes: explanatory. Profiles: general-public, student-learner.
- Rules: PUR-10. Discouraged (PUR-10): an annotated picture, not a data visualization. Libraries: altair none, matplotlib none, plotly none.
- Archetypes: process-sequence. Similar: —.

### Indented tree (`indented_tree`) *(supplement)*

A hierarchy written as a vertical list, one node per line, with horizontal indentation showing depth. Labels all start on a readable line, so scanning for a name is fast, and columns of attributes can sit beside each row.

- Also known as: outline view, tree list, file-explorer tree, indented outline. Functions: hierarchy, reference-tool.
- Anatomy: One text row per node, indentation steps for depth, optional expand/collapse markers and guide lines, optional aligned attribute columns or inline bars.
- Fits: Looking up a node by name in a deep hierarchy; Showing attributes of every node in aligned columns; Hierarchies with long labels; Interactive drill-down by expanding branches.
- Limits: Uses one line per node, so tall trees scroll far; Overall shape and breadth of the tree are hard to see; Siblings far apart vertically are hard to relate; Poor at showing several scales at once.
- Data: tree; keys categorical (some/many/huge); values none. Mark text; channels position-y, position-x, text.
- Tasks: retrieve-value, sort, filter. Scale: thousands of nodes with collapsing; ~50 rows visible at once. Modes: analysis, exploration, explanatory. Profiles: data-analyst, domain-expert, operator-monitoring, executive, student-learner.
- Rules: CLT-03, CMP-01. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: hierarchy-structure, exact-values-lookup. Similar: tree_diagram, data_table, icicle. Sibling chart-types.md: Hierarchies and networks.

### Kagi Chart (`kagi_chart`)

A time-independent price chart drawn from vertical lines that reverse direction once price moves past a set reversal amount, with short horizontal joints marking each turn. Thick or green lines indicate rising demand and thin or red lines falling supply; shifts between them are read as trading signals.

- Also known as: —. Functions: patterns, range.
- Anatomy: Vertical line segments, short horizontal shoulders and waists at reversals, line thickness or colour for trend state, a price scale on the right, and date markers on the horizontal axis that are not a true timescale.
- Fits: Filtering noise from financial price movements; Viewing shifts in supply and demand for an asset; Showing reversal patterns independent of time; Technical analysis of price action.
- Limits: Horizontal date markers are not a real timescale; Reversal amount choice changes the pattern shown; Buy and sell signals are a convention, not guarantees; Time spent between moves is not visible.
- Data: table; keys temporal (many/huge); values quantitative (amount). Mark line; channels position-y, size, color-hue.
- Tasks: trend, find-anomalies. Scale: hundreds of reversals. Modes: analysis. Profiles: domain-expert.
- Rules: EFF-17, SCL-07. Discouraged (EFF-17): specialist financial idiom; readers need training and the x axis is not time. Libraries: altair none, matplotlib workaround, plotly none.
- Archetypes: trend-single-series. Similar: candlestick_chart, OHLC_chart, point_and_figure_chart.

### Line Graph (`line_graph`)

Plots values on a Cartesian grid and joins them with straight segments, usually with time or an ordered sequence on the horizontal axis and a quantity on the vertical. Rising and falling slopes show increases and decreases, so trends and turning points stand out. Several lines can be compared together.

- Also known as: —. Functions: patterns, data-over-time, comparisons.
- Anatomy: A horizontal axis of time or ordered intervals, a vertical quantitative axis, plotted points joined by line segments, values below the baseline for negatives, and separate series distinguished by colour or label.
- Fits: Showing how a value changes over time; Revealing trends and turning points; Comparing a few series over the same period; Displaying continuous measurements across an interval.
- Limits: Cluttered once more than three or four lines appear; Lines can imply continuity between sparse points; Baseline and axis scaling can exaggerate trends; Small multiples work better for many series.
- Data: table; keys temporal (some/many/huge); categorical (one/few); values quantitative (amount). Mark line; channels position-x, position-y, color-hue.
- Tasks: trend, compare, find-extremum, find-anomalies. Scale: ≤ 5–7 series; hundreds of time points. Modes: explanatory, analysis, exploration. Profiles: general-public, executive, domain-expert, data-analyst, scientist-reviewer, student-learner, communicator-journalist, operator-monitoring.
- Rules: IDM-LINE, EXP-03, SCL-02, SCL-04, TXT-04. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: trend-single-series, trend-few-series, category-breakdown-over-time. Similar: area_graph, stacked_area_graph, sparkline. Sibling chart-types.md: Time series / Line chart.

### Marimekko Chart (`marimekko_chart`)

A variable-width grid in which both the width and height of each block are percentages. Each column's width shows a category's share, and its stacked segments show subcategory shares, so block area reflects joint share. It reveals how two categorical variables relate, acting as a two-way 100% stacked bar.

- Also known as: Mosaic Plot. Functions: comparisons, part-to-a-whole, proportions, relationships.
- Anatomy: Columns of differing widths along one axis, stacked segments of varying height within each column, percentage scales on both axes, and category labels on the axes or inside blocks.
- Fits: Comparing market share across two categorical dimensions; Showing how segments divide within each column; General overview of category relationships; Contribution to totals by brand and region.
- Limits: Hard to read with many segments; Segments lack a common baseline, complicating comparisons; Narrow columns make labels and values cramped; Best for overview rather than precise comparison.
- Data: table; keys categorical (few); categorical (few); values quantitative (share). Mark rect; channels length, area, color-hue.
- Tasks: gist, compare. Scale: ≤ ~6 × 6 blocks. Modes: explanatory. Profiles: executive, domain-expert.
- Rules: EFF-02, EFF-06, IDM-STACK. Discouraged (EFF-02): areas without a common baseline; use for an overview of two shares only. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: compare-two-keys, part-to-whole-single. Similar: stacked_bar_graph, treemap. Sibling chart-types.md: Quantities / Stacked bar chart.

### Multi-set Bar Chart (`multiset_barchart`)

A bar chart in which two or more series share one value axis and sit side by side inside parent-category groups. Bar length gives discrete values and colour tells series apart. It suits comparing matching subcategories across groups, comparing mini histograms, or showing change over time within clusters.

- Also known as: Grouped Bar Chart, Clustered Bar Chart. Functions: comparisons, distribution, patterns, relationships.
- Anatomy: Clusters of adjacent bars on a common value axis, one colour per series, group labels beneath each cluster, a legend naming the series, and visible gaps separating the groups.
- Fits: Comparing subcategories across parent categories; Showing several series side by side; Comparing mini histograms across groups; Tracking yearly change within each cluster.
- Limits: Harder to read as bars per group increase; Needs a legend when many colours are used; Keep the number of bars per group small; Crowded when there are many groups.
- Data: table; keys categorical (few/some); categorical (few); values quantitative (amount). Mark line; channels position-x, length, color-hue.
- Tasks: compare, find-extremum, retrieve-value. Scale: ≤ ~12 groups × ≤ 5 bars. Modes: explanatory, analysis. Profiles: general-public, executive, domain-expert, student-learner.
- Rules: EXP-08, EXP-04, COL-04, EFF-19. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: compare-two-keys. Similar: bar_chart, histogram, stacked_bar_graph. Sibling chart-types.md: Quantities / Grouped / paired bar chart.

### Network Diagram (`network_diagram`)

Nodes drawn as dots or icons are joined by link lines that show which entities connect and how. Node size or line weight can encode extra values, and small arrows can mark one-way or two-way ties. Readers look for clusters, connection density, and overall layout structure.

- Also known as: Network Graph, Network Map, Node-Link Diagram. Functions: relationships.
- Anatomy: Nodes as circles or icons, links as lines between them, optional arrowheads for direction, variable node sizes or stroke widths for extra values, and the spatial arrangement that reveals clusters.
- Fits: Mapping relationships among people or organisations; Spotting clusters and densely linked groups; Showing directed influence between entities; Exploring the structure of connected systems.
- Limits: Becomes a hairball with many nodes; Layout algorithm choice shapes apparent clustering; Limited capacity for detailed data per node; Exact paths are hard to follow in dense networks.
- Data: network; keys categorical (some/many/huge); values quantitative (weight). Mark point; channels connection, position-x, position-y, size, color-hue.
- Tasks: cluster, find-anomalies, retrieve-value. Scale: dozens to a few hundred nodes; hairball beyond. Modes: exploration, analysis, explanatory. Profiles: data-analyst, domain-expert.
- Rules: EFF-16, EFF-17. Libraries: altair none, matplotlib workaround, plotly workaround.
- Archetypes: network-relationships. Similar: arc_diagram, brainstorm, non_ribbon_chord_diagram, connection_map, tree_diagram, adjacency_matrix. Sibling chart-types.md: Hierarchies and networks.

### Nightingale Rose Chart (`nightingale_rose_chart`)

Segments of a circle, each assigned to a category or time interval, extend outward by different distances from a central point; the radial distance encodes the value. Readers compare how far each wedge reaches from the center, usually along the rings used as a scale.

- Also known as: Coxcomb Chart, Polar Area Diagram. Functions: comparisons, data-over-time, proportions.
- Anatomy: Polar grid of concentric rings acting as the value scale, equal-angle wedges per category, and wedge length from the centre as the encoded mark. Readers should judge radius rather than wedge area.
- Fits: Showing category values across a full cycle or set of intervals; Presentational displays of values for a general audience; Historical or stylised reports where visual impact matters; Proportions or values over time in a radial layout.
- Limits: Outer wedges look larger, exaggerating value increases; Wedge area perception makes precise comparisons difficult; Readers must decode a polar grid, which takes effort; Radial scale is harder to read than a straight axis.
- Data: table; keys ordinal (few/some); values quantitative (amount). Mark arc; channels length, angle, color-hue.
- Tasks: gist, compare. Scale: ≤ 12 wedges. Modes: explanatory. Profiles: communicator-journalist, general-public.
- Rules: EFF-02, IDM-RADAR/GAUGE, EXP-07. Discouraged (EFF-02): radius/area encoding exaggerates outer values; a bar or line is more accurate. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: seasonality-cycles, compare-values-across-categories. Similar: pie_chart, radial_column_chart. Sibling chart-types.md: Proportions / Polar area / stacked polar.

### Non-ribbon Chord Diagram (`non_ribbon_chord_diagram`)

Nodes arranged around a circle are joined by connector lines, with no filled bands between them. Readers trace which entities link to which, focusing on the web of connections rather than the size of each link.

- Also known as: —. Functions: relationships.
- Anatomy: Nodes placed around a ring, with lines drawn across the interior between linked nodes. No ribbon fills appear; the lines alone carry the connections.
- Fits: Revealing which entities in a network connect to each other; Emphasising the overall web of connections in the data; Cleaner alternative when ribbon fills would clutter the view; Showing relationships between a modest set of categories.
- Limits: Link thickness or flow size is not conveyed without ribbons; Dense networks make individual connection lines hard to follow; Unsuited where exact link quantities must be read; Circular layout order strongly affects how readable it is.
- Data: network; keys categorical (few/some); values none. Mark point; channels angle, connection.
- Tasks: cluster, gist. Scale: ≤ ~30 nodes. Modes: explanatory, analysis. Profiles: domain-expert, communicator-journalist.
- Rules: EFF-16, CMP-01. Libraries: altair none, matplotlib workaround, plotly workaround.
- Archetypes: network-relationships. Similar: chord_diagram. Sibling chart-types.md: Hierarchies and networks.

### Open-High-Low-Close Chart (`OHLC_chart`)

Each time period is drawn as a vertical bar spanning the highest to lowest price, with small ticks on the left and right for opening and closing values. Readers judge each period's sentiment and look for recurring formations across the timeline.

- Also known as: OHLC Chart, Price Chart, Bar Chart. Functions: data-over-time, patterns, range.
- Anatomy: Vertical price scale and horizontal time axis. Each mark has a central line for the high-low span, a left tick for the open, a right tick for the close, with hue marking rising or falling periods.
- Fits: Tracking daily price movements of stocks or currencies; Spotting trend reversals through repeated price formations; Showing the price range and open-to-close change per period; Comparing market sentiment across consecutive trading periods.
- Limits: Does not show trading volume unless paired with another chart; Small ticks are hard to read when the series is dense; Colour coding for bullish or bearish needs an explicit key; Past price patterns do not reliably predict future moves.
- Data: table; keys temporal (some/many/huge); values quantitative (amount); quantitative (amount); quantitative (amount); quantitative (amount). Mark glyph; channels position-x, position-y, length, color-hue.
- Tasks: trend, determine-range, find-anomalies. Scale: hundreds of periods. Modes: analysis. Profiles: domain-expert, data-analyst.
- Rules: COL-05, TXT-07. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: range-per-item, trend-single-series. Similar: candlestick_chart, kagi_chart.

### Overview + detail (`overview_detail`) *(supplement)*

Two linked views of one dataset: a small overview of everything and a larger detail view of the range the reader brushes in the overview. The detail may use another idiom. The overview keeps the reader oriented while they zoom.

- Also known as: overview and detail, context and focus views, brush and zoom, range selector. Functions: data-over-time, patterns.
- Anatomy: A compact overview with a draggable selection rectangle, a larger detail view bound to that selection, shared scale direction, the selected extent shown in text.
- Fits: Long time series where local shape matters; Large scatterplots or maps explored region by region; Readers who must zoom without losing their place; Detail in a different idiom, such as a table of selected items.
- Limits: Requires interaction; a static export shows only one selection; The reader must mentally connect two separate views; A selection that drives nothing is a broken promise; Costs screen space that a single chart would not; The default selection must already answer the main question.
- Data: table; keys temporal (many/huge); categorical (one/few); values quantitative (amount). Mark line; channels position-x, position-y, position-common-scale.
- Tasks: filter, find-anomalies, trend, retrieve-value. Scale: tens of thousands of points in the overview; detail window as small as needed. Modes: exploration, analysis. Profiles: data-analyst, domain-expert, operator-monitoring, scientist-reviewer.
- Rules: INT-04, INT-09, CMP-13, INT-02, DAT-14. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: trend-single-series, trend-few-series, categorical-state-over-time. Similar: small_multiples, line_graph, horizon_graph, scatterplot.

### Parallel Coordinates Plot (`parallel_coordinates`)

Many variables are drawn as vertical axes side by side, and each record becomes a line crossing every axis at its value. Readers follow individual lines or bundles to compare items across attributes and to spot correlations between neighbouring axes.

- Also known as: —. Functions: comparisons, relationships, patterns.
- Anatomy: Vertical axes, one per variable, stand side by side and may share or differ in scale. Polylines connect a record's value on every axis. Axis order affects how easily adjacent relationships are read.
- Fits: Comparing many products sharing the same attribute set; Exploring multivariate numeric data for correlations; Comparing specs such as cars or computers across models; Interactive exploration where highlighting isolates lines of interest.
- Limits: Dense datasets become illegible without interactive filtering; Reordering axes changes which patterns appear obvious; Non-adjacent axes are harder to relate than neighbouring ones; Mixed units need per-axis scales or normalisation to compare.
- Data: table; keys categorical (some/many); values quantitative; quantitative; quantitative. Mark line; channels position-y, connection, color-hue.
- Tasks: correlate, cluster, find-anomalies, compare. Scale: ≤ ~12 axes; hundreds of items, thousands with opacity. Modes: exploration, analysis. Profiles: data-analyst, domain-expert.
- Rules: EFF-17, EFF-16, EFF-19. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: multivariate-relationships. Similar: parallel_sets, radar_chart. Sibling chart-types.md: Relationships / Parallel coordinates.

### Parallel Sets (`parallel_sets`)

Categorical dimensions appear as stacked vertical bands, with flows drawn between them as ribbons whose widths reflect each category's share. Readers follow a ribbon from one dimension to the next to see how groups split and recombine, and can colour flows to compare categories.

- Also known as: —. Functions: comparisons, distribution, movement-or-flow, processes-and-methods, proportions.
- Anatomy: Vertical bands, one per categorical dimension, split into labelled segments. Ribbons link segments across adjacent bands, and their width tracks each category's share.
- Fits: Showing how categorical groups distribute across several attributes; Following respondents through multiple classification questions; Comparing category composition between linked dimensions; Interactive exploration of categorical data in analysis; Flows without direction, where arrows would imply a sequence.
- Limits: Often confused with Sankey and alluvial diagrams; No arrows, so direction of movement is not implied; Many ribbons crossing bands become tangled and hard to trace; Ribbon widths judged by eye, so exact values need labels.
- Data: table; keys categorical (few); categorical (few); categorical (few); values quantitative (count). Mark area; channels position-y, size, connection, color-hue.
- Tasks: compare, gist, cluster. Scale: 2–4 dimensions of ≤ 6 levels. Modes: analysis, explanatory. Profiles: data-analyst, domain-expert.
- Rules: EFF-17, EFF-16. Libraries: altair none, matplotlib workaround, plotly native.
- Archetypes: flow-between-states, compare-two-keys. Similar: sankey_diagram, parallel_coordinates.

### Pictogram Chart (`pictogram`)

Rows or columns of repeated icons stand for counts across a small set of discrete categories, each icon representing one unit or a fixed multiple of one. Readers count icons and compare row or column lengths side by side.

- Also known as: Pictograph Chart, Pictorial Chart, Pictorial Unit Chart, Picture Graph. Functions: comparisons, distribution.
- Anatomy: Rows or columns of identical icons, one row per category. A key states the value each icon stands for. Partial icons are best avoided, since they confuse the count.
- Fits: Small sets of discrete counts for a general audience; Audiences where language, culture or education varies; Countable subjects such as people, cars or animals; Presentations where icons add visual engagement.
- Limits: Large data sets make icons too numerous to count; Partial icons confuse what each symbol represents; Unit value must be stated clearly on the chart; Icons may not map cleanly onto abstract categories.
- Data: table; keys categorical (few); values quantitative (count). Mark glyph; channels length, position-x.
- Tasks: compare, gist, retrieve-value. Scale: ≤ 6 categories, ≤ ~50 icons per row. Modes: explanatory. Profiles: general-public, communicator-journalist, student-learner.
- Rules: EXP-07, EFF-04. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: compare-values-across-categories. Similar: dot_matrix_chart.

### Pie Chart (`pie_chart`)

A circle is split into wedges whose arc lengths or angles represent each category's share of the total, which equals the full circle. Readers estimate each slice's proportion, and judging one slice against the whole is more dependable than comparing slices across several pies.

- Also known as: —. Functions: comparisons, part-to-a-whole, proportions.
- Anatomy: Circle divided into wedges, each wedge a category; the full circle equals the total. A legend or direct labels identify slices, and arc length or angle encodes the proportion.
- Fits: Showing a few categories as shares of one total; Quick proportional overview for presentations or offices; Highlighting one segment against the whole; Two to five categories with clearly different sizes.
- Limits: Too many slices become thin and unreadable; Comparing slices across several pies is difficult; Uses more space than a 100% stacked bar chart; Usually needs a legend, adding visual overhead.
- Data: table; keys categorical (few); values quantitative (share). Mark arc; channels angle, area, color-hue.
- Tasks: gist, retrieve-value. Scale: 2–5 parts with distinct sizes. Modes: explanatory. Profiles: general-public, executive.
- Rules: IDM-PIE, EXP-05, EFF-02, CMP-01, COL-04. Discouraged (IDM-PIE): angle is a weak channel; only for ≤5 parts of a whole with simple fractions; sorted bars compare better. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: part-to-whole-single. Similar: donut_chart, nightingale_rose_chart, sunburst_diagram. Sibling chart-types.md: Proportions / Pie / donut.

### Point & Figure Chart (`point_and_figure_chart`)

Stacked Xs and Os form columns that plot filtered price moves: X marks rising prices, O marks falling ones, and a new column begins only after a set reversal. Horizontal spacing is not elapsed time; readers look for breakouts and support or resistance levels.

- Also known as: P&F Chart. Functions: patterns.
- Anatomy: Vertical value scale for price. Each column holds only X or only O symbols, and columns advance left to right. Occasional month markers use 1-9 for January to September and A, B, C for October to December.
- Fits: Filtering minor price noise to reveal supply-demand shifts; Spotting support, resistance and trend lines in prices; Analysing asset prices without volume or elapsed-time scaling; Studying breakout patterns in securities or commodities.
- Limits: Ignores trading volume and does not plot elapsed time; Box size and reversal amount strongly change the appearance; Date markers on the x-axis are not a true timescale; Results depend on the chosen price basis and settings.
- Data: table; keys temporal (many/huge); values quantitative (amount). Mark glyph; channels position-x, position-y.
- Tasks: trend, find-anomalies. Scale: hundreds of moves. Modes: analysis. Profiles: domain-expert.
- Rules: EFF-17, SCL-07. Discouraged (EFF-17): specialist financial idiom without a time axis. Libraries: altair none, matplotlib workaround, plotly none.
- Archetypes: trend-single-series. Similar: kagi_chart.

### Population Pyramid (`population_pyramid`)

Two back-to-back sets of horizontal bars, one for each sex, extend from a central axis to show population counts within each age band. Readers judge the overall silhouette to infer demographic structure and compare the two sexes within each age group.

- Also known as: Age & Sex Pyramid. Functions: comparisons, distribution, patterns.
- Anatomy: Central vertical axis listing age groups; horizontal bars extend left and right, one side per sex; horizontal axis carries population counts. Bar lengths on the two sides reveal sex balance.
- Fits: Showing the age and sex makeup of a national population; Comparing demographic structure across countries or regions; Tracking population change across successive census years; Teaching ageing and fertility trends in sociology or ecology.
- Limits: Shape-based readings of future trends are speculative; Only age and sex appear, so other factors stay hidden; Mirrored bars make precise cross-side comparison harder; Raw counts need normalising to compare different-sized populations.
- Data: table; keys ordinal (some); categorical (few); values quantitative (count). Mark line; channels position-y, length, color-hue.
- Tasks: characterize-distribution, compare, gist. Scale: 10–20 age bands × 2 groups. Modes: explanatory, analysis. Profiles: general-public, domain-expert, student-learner.
- Rules: EXP-08, DAT-02, COL-13. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: distribution-compare-groups. Similar: bar_chart, histogram. Sibling chart-types.md: Quantities / Bar chart.

### Quantile dot plot (`quantile_dotplot`) *(supplement)*

A predictive or posterior distribution drawn as a few dozen stacked dots, each standing for an equal slice of probability. Readers count dots on either side of a threshold to get a chance such as 3 in 20, without reading a density or an interval.

- Also known as: quantile dotplot, frequency-framed dot plot. Functions: distribution, range.
- Anatomy: A quantitative axis, 20 to 100 equal dots stacked in columns, an optional threshold line, a caption stating what one dot is worth.
- Fits: Forecasts for lay readers who must judge a risk; Decisions against a threshold, such as arriving late; Skewed or multimodal predictive distributions; Replacing an interval that readers take as a hard range.
- Limits: Mistaken for raw observations when shown beside data dots; The dot count sets the resolution of probabilities; Needs a sentence explaining the value of one dot; Takes more space than an interval per estimate.
- Data: table; keys categorical (one/few); values quantitative (amount). Mark point; channels position-x, length.
- Tasks: characterize-distribution, determine-range, retrieve-value, compare. Scale: 1–6 estimates; 20–100 dots each. Modes: explanatory, analysis. Profiles: general-public, communicator-journalist, executive, domain-expert, student-learner.
- Rules: PUR-14, DAT-03, TXT-07. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: uncertainty-of-estimate-or-forecast. Similar: wilkinson_dot_plot, error_bars, gradient_interval, density_plot, hypothetical_outcome_plot.

### Radar Chart (`radar_chart`)

Several variables radiate from a central point, each on its own equally spaced axis, and one series' values join into a closed polygon. Readers compare overall profile shape and spot which variables score high or low, mostly for a few series at a time.

- Also known as: Spider Chart, Web Chart, Polar Chart, Star Plots. Functions: comparisons, patterns, relationships.
- Anatomy: Spokes radiate from a centre, one per variable, all sharing one scale. Grid webs or rings guide the eye. Each series appears as a polygon joining its values on the spokes.
- Fits: Comparing performance profiles across several attributes; Showing which variables run high or low for one item; Spotting outliers among a handful of variables; Visualising player or athlete statistics side by side.
- Limits: Overlapping polygons become cluttered as series increase; Filled shapes hide series drawn beneath them; Many spokes overwhelm readers; Values are hard to compare directly across axes.
- Data: table; keys categorical (one/few); values quantitative; quantitative; quantitative. Mark line; channels position-y, angle, connection, color-hue.
- Tasks: gist, compare. Scale: ≤ 3 profiles × ≤ 8 axes. Modes: explanatory. Profiles: executive, general-public.
- Rules: IDM-RADAR/GAUGE, EFF-02, EFF-17. Discouraged (IDM-RADAR/GAUGE): polygon shape depends on arbitrary axis order; bars or parallel coordinates compare better. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: multivariate-relationships, compare-against-target. Similar: parallel_coordinates. Sibling chart-types.md: Quantities / Radar / spider chart.

### Radial Bar Chart (`radial_bar_chart`)

Bars laid out on a circular frame extend outward from a shared centre, each at its own radius. Readers compare bar extents around the ring, remembering that outer bars can look longer even at equal values.

- Also known as: —. Functions: comparisons.
- Anatomy: Bars radiate from a central origin, each placed at its own radius; the reader must account for radius when judging length.
- Fits: Aesthetic circular displays where looks matter more than precision; Ranking a small set of categories in a radial layout; Circular dashboards or infographics with a ring theme; Decorative charts meant to stand out on a page.
- Limits: Bar lengths mislead, since outer bars appear longer; Linear bar charts are better for accurate comparison; Mainly justified by aesthetics rather than analysis.
- Data: table; keys categorical (few/some); values quantitative (amount). Mark arc; channels length, angle.
- Tasks: gist. Scale: ≤ 12 bars. Modes: explanatory. Profiles: communicator-journalist.
- Rules: EXP-07, EFF-02. Discouraged (EXP-07): outer bars are longer for the same value: the geometry lies; use a bar chart. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: compare-values-across-categories. Similar: —.

### Radial Column Chart (`radial_column_chart`)

Columns are plotted on a polar grid, with concentric rings forming the value scale and radial spokes separating categories. Each column rises outward from the centre by its value, so readers match each column to its spoke and read height against the rings.

- Also known as: Circular Column Graph, Star Graph. Functions: comparisons.
- Anatomy: Rings mark the value scale; radial dividers separate categories; column bars extend outward from the centre. Placing zero on an outer ring lets inner rings hold negatives.
- Fits: Categories arranged around a circle with clear value rings; Showing values that include negatives on one scale; Compact circular comparisons of several categories; Star-shaped displays for presentations or dashboards.
- Limits: Reading column height against curved rings is harder; Circular scales make precise value reading harder; Negative-value layouts need careful ring labelling; Ring spacing must be labelled to be interpreted.
- Data: table; keys categorical (few/some); values quantitative (amount). Mark arc; channels length, angle.
- Tasks: gist, compare. Scale: ≤ 12 columns. Modes: explanatory. Profiles: communicator-journalist.
- Rules: EFF-02, IDM-RADAR/GAUGE. Discouraged (EFF-02): curved scale reads worse than a straight bar chart; cyclic data only. Libraries: altair native, matplotlib workaround, plotly native.
- Archetypes: seasonality-cycles, compare-values-across-categories. Similar: bar_chart, radial_bar_chart.

### Raincloud plot (`raincloud`) *(supplement)*

A combined view of one distribution per group: a half density for shape, the individual values for sample size and gaps, and a summary mark for the centre. Each part should compensate for what another part hides, otherwise it only adds ink.

- Also known as: half-violin with raw data, density-plus-points plot. Functions: distribution, comparisons.
- Anatomy: A half density curve, a strip of ticks or points at their true values beneath it, a median marker with a labelled quantile interval, one row per group.
- Fits: Reporting group differences with raw data and summary together; Small to medium samples where shape and n both matter; Readers who need a summary but must check the data; Replacing bars of means in scientific figures.
- Limits: Density plus random jitter plus box plot repeats the same weaknesses; Smoothing invents mass for discrete or bounded data; Three layers per group need generous row height; The interval shown must be named; Bandwidth choice changes the apparent shape.
- Data: table; keys categorical (one/few/some); values quantitative (amount). Mark area; channels position-x, position-y, length.
- Tasks: characterize-distribution, compare, find-anomalies, determine-range. Scale: ≤ ~10 groups; tens to a few thousand points per group. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: IDM-RAINCLOUD, RAIN-1, EXP-21, EXP-22, DAT-10. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: distribution-compare-groups, distribution-single. Similar: violin_plot, strip_plot, density_plot, box_plot, ridge_plot, wilkinson_dot_plot. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Ridge plot (`ridge_plot`) *(supplement)*

Stacked, slightly overlapping density curves, one per group or period, sharing one value axis, so shifts in location and shape across the groups read as a landscape.

- Also known as: joyplot, ridgeline. Functions: distribution, comparisons, data-over-time.
- Anatomy: A shared quantitative axis, one row per group in a meaningful order, filled density curves that may overlap the row above, direct row labels.
- Fits: How a distribution shifts across many periods or groups; Dozens of distributions in one panel; Ordered groups (months, years, latitude bands).
- Limits: No exact values; Overlap hides the tails of the row behind; Needs an order; unordered groups are better as violins.
- Data: table; keys ordinal (few/some/many); values quantitative (amount). Mark area; channels position-x, position-y, length.
- Tasks: characterize-distribution, compare, trend. Scale: ≤ ~40 rows. Modes: explanatory, analysis. Profiles: scientist-reviewer, data-analyst, domain-expert, communicator-journalist.
- Rules: EXP-15, CMP-01. Libraries: altair native, matplotlib workaround, plotly workaround.
- Archetypes: distribution-change-over-time, distribution-compare-groups. Similar: density_plot, violin_plot. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Sankey Diagram (`sankey_diagram`)

Bands whose thickness matches quantity trace energy, material, money or any process flow, branching or merging at each stage. Readers follow the widest paths to see where most of the flow goes, with colour often marking categories or stages.

- Also known as: —. Functions: how-things-work, movement-or-flow, processes-and-methods, proportions.
- Anatomy: Nodes or stages joined by flow bands, each band's width proportional to its quantity. Bands split and combine at nodes, with hue distinguishing categories or a change of state.
- Fits: Energy transfer or material flows through a system; Money moving through budgets, revenues or costs; Multi-stage processes with losses or transfers between stages; Comparing alternative routes through a process.
- Limits: Easily mistaken for alluvial diagrams or parallel sets; Crossing bands in dense diagrams become hard to trace; Node ordering strongly affects how readable the flows are; Band widths judged by eye, so exact values need labels.
- Data: network; keys categorical (few/some); categorical (few/some); values quantitative (weight). Mark area; channels size, connection, position-x, color-hue.
- Tasks: find-extremum, compare, gist. Scale: ≤ ~30 nodes, ≤ ~60 flows. Modes: explanatory, analysis. Profiles: executive, domain-expert, communicator-journalist, general-public.
- Rules: EFF-02, EFF-16, CMP-01, IDM-SANKEY. Libraries: altair none, matplotlib workaround, plotly native.
- Archetypes: flow-between-states. Similar: flow_map, parallel_sets.

### Scatterplot (`scatterplot`)

Each record appears as a point placed by two numeric variables along horizontal and vertical axes. Readers look at how the cloud rises, falls, bends or stays flat to judge correlation direction, shape, strength and any outliers.

- Also known as: Scatter Graph, Point Graph, X-Y Plot, Scatter Chart, Scattergram. Functions: patterns, relationships.
- Anatomy: Two numeric axes meeting at an origin; each point is one paired observation. An optional trend line overlays the cloud, and isolated points far from the cluster are outliers.
- Fits: Testing whether two numeric variables move together; Spotting outliers in paired measurements; Estimating values with a fitted trend line; Checking non-linear shapes such as U-shaped relationships; Exploring relationships before building predictive models.
- Limits: Correlation does not imply causation; hidden variables may drive results; Overlapping points hide density when many observations exist; Trend lines can suggest precision the data lacks; Needs paired numerical data for both axes.
- Data: table; keys none; values quantitative; quantitative. Mark point; channels position-x, position-y.
- Tasks: correlate, find-anomalies, cluster, characterize-distribution. Scale: hundreds opaque, thousands with opacity/binning. Modes: analysis, exploration, explanatory. Profiles: data-analyst, scientist-reviewer, domain-expert, student-learner.
- Rules: EFF-16, SCL-05, IDM-SCATTER. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: correlation-two-quantities, multivariate-relationships. Similar: bubble_chart. Sibling chart-types.md: Relationships / Scatterplot.

### Slope chart (`slope_chart`) *(supplement)*

Two vertical axes for two moments; each item is a line joining its value at each moment. Slope direction and steepness show change; crossing lines show rank changes.

- Also known as: slopegraph. Functions: comparisons, data-over-time.
- Anatomy: Two labelled vertical axes, one line per item with direct labels at both ends, and a highlighted line for the item of interest.
- Fits: Change of many items between two periods; Rank changes between two moments; Before/after comparisons.
- Limits: Only two time points; Dozens of lines need a highlight-and-grey design; Needs a wide enough panel to read slopes.
- Data: table; keys temporal (few); categorical (few/some/many); values quantitative (amount). Mark line; channels position-y, connection, color-hue.
- Tasks: compare, trend, sort, find-anomalies. Scale: dozens of items. Modes: explanatory, analysis. Profiles: executive, communicator-journalist, domain-expert, scientist-reviewer.
- Rules: TXT-04, EFF-09, SCL-13. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: rank-change-two-points, distribution-change-over-time. Similar: line_graph, dot_plot, difference_view. Sibling chart-types.md: Relationships / Slope chart.

### Small multiples (`small_multiples`) *(supplement)*

The same chart repeated once per category in a grid with shared axes, so the reader compares shapes across panels instead of untangling overlaid series.

- Also known as: trellis, facet grid, panel chart. Functions: comparisons, data-over-time, patterns.
- Anatomy: A grid of equally sized panels, one per category, identical axes and scales, a shared legend, panel titles, logical panel order.
- Fits: Many series over time; Comparing a pattern across groups; Replacing animation with side-by-side frames.
- Limits: Panels get small when there are many categories; Shared scales flatten small series; independent scales break comparison; Needs space.
- Data: table; keys temporal (some/many/huge); categorical (few/some); values quantitative (amount). Mark line; channels position-x, position-y, position-common-scale.
- Tasks: compare, trend, find-anomalies, characterize-distribution. Scale: ≤ ~30 panels. Modes: explanatory, analysis, exploration. Profiles: domain-expert, data-analyst, scientist-reviewer, executive, communicator-journalist, general-public.
- Rules: SCL-08, CMP-05, CMP-08. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: trend-many-series, distribution-change-over-time, spatial-change-over-time, category-breakdown-over-time, distribution-compare-groups, categorical-state-over-time. Similar: line_graph, heatmap, overview_detail. Sibling chart-types.md: Time series / Small multiples.

### Span Chart (`span_chart`)

Each category gets a bar that floats between its lowest and highest value, so readers compare where ranges start and stop and how wide they are across groups.

- Also known as: Range Bar/Column Graph, Floating Bar Graph, Difference Graph, High-Low Graph. Functions: comparisons, range.
- Anatomy: A category axis, a value axis, and one floating bar per category whose bottom and top edges mark the minimum and maximum. Bar length shows the spread.
- Fits: Comparing value ranges across several categories; Showing minimum and maximum values per group; Displaying durations of events on a timeline; Visualising low-to-high spreads such as price or temperature.
- Limits: Shows only the extremes, not averages or distribution; Gives no information between minimum and maximum values.
- Data: table; keys categorical (few/some/many); values quantitative (amount); quantitative (amount). Mark line; channels position-x, length, position-y.
- Tasks: determine-range, compare, sort. Scale: dozens of items. Modes: explanatory, analysis. Profiles: executive, domain-expert, scientist-reviewer.
- Rules: CMP-01, EXP-08. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: range-per-item, event-timeline-intervals. Similar: box_plot, candlestick_chart, gantt_chart. Sibling chart-types.md: Relationships / Connected scatterplot / dumbbell / range plot.

### Sparkline (`sparkline`) *(supplement)*

A line chart shrunk to the size of a word and stripped of axes, placed inside a table cell, a dashboard tile or a sentence. It shows the shape of recent history next to the current number, not exact values.

- Also known as: word-sized graphic, microchart, inline chart. Functions: data-over-time, patterns.
- Anatomy: A short unframed line, optional dot on the last or extreme point, optional shaded normal band, the current value printed beside it.
- Fits: Adding trend context to a number in a table; Dozens of series scanned row by row; Dashboards with little room per indicator; Showing shape when exact values are printed elsewhere.
- Limits: No axis: magnitudes cannot be read or compared across rows; Each row usually has its own scale; say so; Aspect ratio exaggerates or flattens slopes; Too small for annotation or more than one series.
- Data: table; keys temporal (some/many/huge); categorical (one/few/some/many); values quantitative (amount). Mark line; channels position-x, position-y.
- Tasks: trend, find-anomalies, gist. Scale: dozens of rows × ~50–200 points each. Modes: explanatory, analysis. Profiles: executive, operator-monitoring, data-analyst, domain-expert, communicator-journalist.
- Rules: SCL-08, SCL-13, TXT-07. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: trend-many-series, exact-values-lookup, trend-single-series. Similar: line_graph, horizon_graph, small_multiples, data_table. Sibling chart-types.md: Time series / Line chart.

### Spike map (`spike_map`) *(supplement)*

A thin vertical spike rises from each location with a height proportional to its value. Length is judged more accurately than circle area or colour, large regions get no extra weight, and spikes cover far less of the map than bubbles.

- Also known as: spike plot map, prism spikes. Functions: location, comparisons.
- Anatomy: A muted base map, a narrow triangle or line anchored at each location, a height legend with reference values, taller spikes drawn over shorter ones.
- Fits: Totals per place, where a choropleth would mislead; Dense cities next to empty regions; Counts that span several orders of magnitude; Keeping the base map visible under the symbols.
- Limits: Tall spikes cross their neighbours and seem to belong elsewhere; Heights are compared without a common baseline; Looks three-dimensional although it is not; Needs a height legend; values are not readable otherwise; Short spikes vanish beside very tall ones.
- Data: geometry; keys geo-code (some/many/huge); values quantitative (count). Mark line; channels position-x, position-y, length.
- Tasks: find-extremum, compare, cluster, gist. Scale: hundreds to a few thousand locations. Modes: explanatory, analysis. Profiles: communicator-journalist, general-public, domain-expert, data-analyst.
- Rules: EFF-06, EFF-16, IDM-MAP, TXT-07. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: spatial-distribution, spatial-change-over-time, point-events-on-map. Similar: bubble_map, choropleth, dot_map, arrow_map. Sibling chart-types.md: Geospatial / Graduated / proportional symbol map.

### Spiral Plot (`spiral_plot`)

Time-based values are drawn along a path that winds outward from a central start point, so repeating cycles appear as loops lined up around the spiral. Colour can mark each period.

- Also known as: Time Series Spiral. Functions: data-over-time, patterns.
- Anatomy: A start point at the centre, a continuous outward-winding path, and marks (bars, lines or dots) placed along that path, with optional colour bands per period.
- Fits: Very large time series spanning long periods; Revealing periodic or seasonal patterns; Comparing successive cycles using colour per period; Showing daily, monthly or yearly rhythms in one view.
- Limits: Reading exact values is harder than on straight axes; Less familiar to general audiences, so needs explaining; Outer loops are longer, which distorts length comparison.
- Data: table; keys temporal (many/huge); values quantitative (amount). Mark line; channels angle, color-luminance, length.
- Tasks: find-anomalies, trend. Scale: thousands of time points. Modes: analysis. Profiles: domain-expert, data-analyst.
- Rules: EFF-17, EXP-07. Discouraged (EFF-17): unfamiliar and outer loops distort lengths; a calendar heatmap shows cycles with less learning. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: seasonality-cycles. Similar: —.

### Stacked Area Graph (`stacked_area_graph`)

Several series are layered so each one rests on the top edge of the previous; the top boundary is the running total. Readers compare band thickness and overall height over time.

- Also known as: —. Functions: comparisons, data-over-time, patterns.
- Anatomy: A time axis along the bottom, a value axis rising from zero, coloured bands stacked upward with a boundary line each, and a legend naming each series.
- Fits: Showing how several parts add up over time; Tracking each category's contribution across periods; Displaying overall totals alongside component trends; Comparing multiple variables changing in the same period.
- Limits: Values must be non-negative, since areas convey whole quantities; Middle bands are hard to read off a shifting baseline; Only the bottom series sits on a common baseline.
- Data: table; keys temporal (some/many/huge); categorical (few); values quantitative (amount). Mark area; channels position-x, length, color-hue.
- Tasks: trend, gist, compute-derived. Scale: ≤ 5–6 categories; hundreds of time points. Modes: explanatory. Profiles: general-public, executive, communicator-journalist.
- Rules: IDM-STACK, EXP-06, EFF-06. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: part-to-whole-over-time, category-breakdown-over-time. Similar: area_graph, line_graph, stream_graph. Sibling chart-types.md: Time series / Area / stacked area / streamgraph.

### Stacked Bar Graph (`stacked_bar_graph`)

Bars are divided into stacked segments, so each bar's total length shows the whole and each segment shows a part. The 100% variant rescales bars so segments read as shares.

- Also known as: —. Functions: comparisons, proportions, part-to-a-whole.
- Anatomy: Categories along one axis, bars subdivided into coloured segments, a value axis (raw or 0-100%), and a legend matching colours to subcategories.
- Fits: Showing totals split into subcategories per group; Comparing overall totals between a few groups; Part-of-a-whole shares across categories in the 100% version; Seeing how composition differs between bars.
- Limits: Gets harder to read as the number of segments rises; Segments lack a common baseline, so middle ones are hard to compare; The 100% version hides absolute totals.
- Data: table; keys categorical (few/some); categorical (few); values quantitative (amount). Mark line; channels position-x, length, color-hue.
- Tasks: compute-derived, gist, compare. Scale: ≤ ~12 bars × ≤ 5–6 segments. Modes: explanatory, analysis. Profiles: general-public, executive, domain-expert, student-learner.
- Rules: IDM-STACK, EXP-06, EXP-08, EFF-06. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: compare-two-keys, part-to-whole-single, part-to-whole-over-time, category-breakdown-over-time, categorical-state-over-time. Similar: bar_chart, multiset_barchart. Sibling chart-types.md: Quantities / Stacked bar chart.

### Stem and Leaf Plot (`stem_and_leaf_plot`)

Each value is split into a stem (leading digits) and a leaf (final digit); leaves hang beside their stems in ascending order, so the shape of the data shows while raw values stay visible.

- Also known as: Stemplot, Stem & Leaf Display. Functions: distribution, reference-tool.
- Anatomy: A vertical column of stem values in ascending order, with each row's leaves listed sideways from it. Back-to-back layouts place two datasets on either side of the stems.
- Fits: Small datasets where raw values should stay visible; Spotting outliers and the mode quickly; Comparing two small datasets back to back; Reference listings such as transport schedules.
- Limits: Too few values make the plot pointless; Too many values clutter the display and reduce readability; Practical size limit on the datasets it can handle.
- Data: table; keys none; values quantitative (amount). Mark text; channels position-y, length.
- Tasks: characterize-distribution, retrieve-value, find-anomalies. Scale: ≤ ~100 values. Modes: analysis. Profiles: student-learner, scientist-reviewer.
- Rules: TXT-13. Libraries: altair none, matplotlib workaround, plotly none.
- Archetypes: distribution-single, exact-values-lookup. Similar: tally_chart. Sibling chart-types.md: Tables and text.

### Stream Graph (`stream_graph`)

Stacked bands wiggle around a moving central baseline, forming a flowing, river-like shape. Band thickness along the time axis shows each category's value, favouring overall trends over exact figures.

- Also known as: ThemeRiver. Functions: data-over-time, patterns.
- Anatomy: A horizontal time axis through the middle, coloured organic bands stacked around a shifting centre, and a colour legend. No value axis is drawn.
- Fits: Overviewing many categories across long periods; Spotting seasonal peaks and recurring patterns; Showing volatility across a large group of assets; Engaging presentation or interactive pieces for general audiences.
- Limits: Small categories get drowned out by large ones; No value axis, so exact values cannot be read; Cluttered with large datasets, which hurts legibility; Works best as an interactive piece rather than static.
- Data: table; keys temporal (many/huge); categorical (some/many); values quantitative (count). Mark area; channels position-x, length, color-hue.
- Tasks: gist, trend, find-extremum. Scale: hundreds of time steps; dozens of categories. Modes: explanatory. Profiles: communicator-journalist, general-public.
- Rules: EXP-06, IDM-STACK, EFF-06. Libraries: altair native, matplotlib native, plotly workaround.
- Archetypes: part-to-whole-over-time, category-breakdown-over-time. Similar: stacked_area_graph. Sibling chart-types.md: Time series / Area / stacked area / streamgraph.

### Streamline map (`streamline_map`) *(supplement)*

A vector field such as wind or ocean current drawn over a map as curves that follow the local direction, or as a grid of small arrows. Speed goes to colour, stroke weight or, in animated versions, the pace of moving particles, where motion itself encodes the data.

- Also known as: vector field map, flow field, wind map, quiver map. Functions: location, movement-or-flow.
- Anatomy: A base map, streamlines or arrow glyphs tangent to the flow, arrowheads or fading tails for direction, a speed legend.
- Fits: Wind, currents or other continuous directional fields; Finding vortices, fronts and converging zones; Public weather graphics, animated; Showing direction and speed together.
- Limits: Seeding density decides which features appear; Arrow grids clutter and alias with the sampling grid; Speed is read only roughly from colour or motion; A static frame hides how the field changes over time; Not for flows between discrete places.
- Data: field; keys geo-code (huge); values quantitative (amount); quantitative (amount). Mark line; channels position-x, position-y, orientation, color-luminance.
- Tasks: cluster, find-anomalies, find-extremum, gist. Scale: any grid size; seed density tuned to the display. Modes: explanatory, analysis, exploration. Profiles: domain-expert, scientist-reviewer, general-public, communicator-journalist.
- Rules: EFF-16, COL-02, EXP-18, TXT-07. Libraries: altair workaround, matplotlib native, plotly workaround.
- Archetypes: spatial-distribution. Similar: flow_map, arrow_map, connection_map, heatmap. Sibling chart-types.md: Geospatial / Flow / line maps, network maps.

### Strip plot (`strip_plot`) *(supplement)*

Every observation is drawn at its true position on a quantitative axis, one strip per group, as thin ticks or translucent or hollow points, so darker stretches mean more values. The reader sees the raw spread, gaps and outliers, usually with a median mark overlaid.

- Also known as: jitter plot, sina plot, rug plot, barcode plot. Functions: distribution, comparisons.
- Anatomy: A category axis with one strip per group, a quantitative axis, one tick or translucent point per observation at its exact value, optional median marker and labelled interval.
- Fits: Comparing groups on a measured variable with the raw data visible; Small to medium n per group; Replacing bars of means; A raw-data layer under a density or summary.
- Limits: Thousands of points per group overplot; switch to violin or density; Ties hide behind each other without opacity or hollow marks; Random jitter changes on every render; seed it or use a beeswarm; Any sideways offset adds no information.
- Data: table; keys categorical (one/few/some); values quantitative (amount). Mark point; channels position-x, position-y, color-luminance.
- Tasks: characterize-distribution, compare, find-anomalies, determine-range. Scale: ≤ ~500 points per group. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: EXP-16, DAT-03, EXP-21. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: distribution-compare-groups, distribution-single. Similar: box_plot, violin_plot, beeswarm, wilkinson_dot_plot, raincloud. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Sunburst Diagram (`sunburst_diagram`)

Concentric rings show levels of a hierarchy, with the root at the centre and child categories sliced outward; each slice's angle is equal or proportional to a value. Readers trace paths from the centre outward.

- Also known as: Sunburst Chart, Ring Chart, Multi-level Pie Chart, Belt Chart, Radial Treemap. Functions: hierarchy, part-to-a-whole.
- Anatomy: A central root circle, concentric rings for each hierarchy level, wedge slices nested under their parent slices, and colour grouping related categories.
- Fits: Showing nested hierarchies across a few levels; Part-to-whole breakdowns with multiple levels; Highlighting groupings with colour; Displaying multi-level proportions in a compact form.
- Limits: Angles on outer rings are hard to compare; Outer levels get cramped and hard to label; Deep hierarchies quickly become cluttered.
- Data: tree; keys categorical (some/many); values quantitative (amount). Mark arc; channels angle, containment, color-hue.
- Tasks: gist, find-extremum. Scale: depth ≤ 3–4; dozens of leaves. Modes: explanatory. Profiles: general-public, executive.
- Rules: EFF-02, TXT-10. Libraries: altair none, matplotlib workaround, plotly native.
- Archetypes: part-to-whole-hierarchy, hierarchy-structure. Similar: donut_chart, pie_chart, treemap, icicle. Sibling chart-types.md: Proportions / Treemap.

### Tally Chart (`tally_chart`)

Each occurrence of a category adds one mark in its row or column, and totals are counted at the end. The finished tally resembles a histogram and shows the frequency of each category.

- Also known as: —. Functions: comparisons, distribution.
- Anatomy: Category labels down one side, columns or rows of tally marks beside them, and a total column counted at the end.
- Fits: Recording frequencies while counting live; Quick manual counts with no software; Building a frequency table before drawing a histogram; Simple observations or surveys of categories.
- Limits: Manual counting makes errors likely in large datasets; Only suits counting discrete categories or intervals; Result is a table of counts rather than a visual chart.
- Data: table; keys categorical (few/some); values quantitative (count). Mark glyph; channels length.
- Tasks: retrieve-value, compare. Scale: small counts. Modes: analysis. Profiles: student-learner.
- Rules: PUR-02. Discouraged (PUR-02): a counting aid; a sorted bar chart or a table serves the reader better. Libraries: altair none, matplotlib none, plotly none.
- Archetypes: compare-values-across-categories. Similar: —. Sibling chart-types.md: Tables and text.

### Tile cartogram (`tile_cartogram`) *(supplement)*

Every region becomes a tile of identical size, a square or hexagon, arranged to echo the real geography. Each unit receives the same ink, so small but populous regions are no longer drowned out by large empty ones, and tiles can hold a colour, a label or a tiny chart.

- Also known as: tile grid map, hex map, cartogram (non-contiguous), grid map. Functions: location, comparisons.
- Anatomy: A grid of equal tiles in rough geographic position, a short code on each tile, colour for the value, a classed legend.
- Fits: Regions that count equally, such as seats or states; Maps where small regions vanish at true scale; Placing a mini chart per region in a geographic layout; Needs only a tile layout table, not region outlines.
- Limits: True shapes, sizes and distances are gone; Neighbours on the grid are not always neighbours in reality; Readers must already know roughly where regions lie; No standard layout exists for most territories; Equal tiles misstate anything tied to land area.
- Data: geometry; keys geo-code (some/many); values quantitative (rate). Mark rect; channels position-x, position-y, color-luminance.
- Tasks: compare, find-extremum, cluster, retrieve-value, gist. Scale: ~10–200 regions. Modes: explanatory, analysis. Profiles: general-public, communicator-journalist, executive, domain-expert.
- Rules: EXP-12, COL-02, EXP-17, IDM-MAP. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: spatial-distribution, spatial-change-over-time. Similar: choropleth, heatmap, small_multiples, bubble_map. Sibling chart-types.md: Geospatial / Choropleth.

### Timeline (`timeline`)

Events are placed in chronological order along a line, either on a true time scale where spacing reflects real intervals or simply in sequence. Readers use position and spacing to judge timing.

- Also known as: —. Functions: data-over-time, distribution, patterns.
- Anatomy: A linear axis or line, markers or labels at event positions, optional date scale ticks, and descriptive text or cards attached to each event.
- Fits: Narrating historical or project events in order; Showing gaps and intervals between events on a scale; Pairing with bars to show event durations; Revealing when events cluster or spread out.
- Limits: Unscaled timelines hide real time intervals; Crowded events overlap and become hard to read; Shows event timing, not quantities.
- Data: table; keys temporal (few/some/many); values text (label). Mark point; channels position-x, text.
- Tasks: sort, determine-range, retrieve-value. Scale: dozens of events. Modes: explanatory. Profiles: general-public, communicator-journalist, student-learner.
- Rules: SCL-07, TXT-05. Libraries: altair native, matplotlib native, plotly native.
- Archetypes: event-timeline-intervals, categorical-state-over-time. Similar: —.

### Timetable (`timetable`)

A grid of scheduled events, tasks or departures, ordered by time or name so readers can look up an entry quickly. Readers locate a row and column to find a specific time.

- Also known as: —. Functions: data-over-time, reference-tool.
- Anatomy: Rows and columns forming a grid, headers for times or categories, entries in the cells, and a consistent sort order running through the table.
- Fits: Transport arrival and departure schedules; Organising scheduled tasks or actions; Quick reference lists sorted by time or name.
- Limits: Dense grids are hard to scan at a glance; Does not visually show durations or overlaps; Static tables must be updated when schedules change.
- Data: table; keys temporal (some/many); categorical (few/some); values text (label). Mark text; channels position-x, position-y.
- Tasks: retrieve-value. Scale: hundreds of cells. Modes: explanatory. Profiles: general-public, operator-monitoring.
- Rules: TXT-13, IDM-TABLE. Libraries: altair none, matplotlib none, plotly native.
- Archetypes: exact-values-lookup, event-timeline-intervals. Similar: calendar. Sibling chart-types.md: Tables and text.

### Tree Diagram (`tree_diagram`)

A branching structure with a root at the top, nodes linked by branches, and leaf nodes at the ends; it shows parent-child relationships and levels of hierarchy. Readers follow branches to find ancestors or descendants.

- Also known as: Organisational chart, Linkage Tree. Functions: hierarchy, reference-tool, relationships.
- Anatomy: A root node, internal nodes, connecting branch lines between parents and children, and leaf end-nodes that have no children.
- Fits: Family trees and descent relationships; Biological classification and taxonomy; Evolutionary history of species; Organisational and management reporting structures.
- Limits: Large trees become wide and hard to navigate; Shows structure and relationships, not quantities.
- Data: tree; keys categorical (some/many); values none. Mark point; channels connection, position-y, position-x.
- Tasks: retrieve-value, cluster, gist. Scale: dozens to a few hundred nodes; depth ≤ 6. Modes: explanatory, analysis. Profiles: general-public, domain-expert, student-learner.
- Rules: EFF-16, CLT-03. Libraries: altair none, matplotlib workaround, plotly workaround.
- Archetypes: hierarchy-structure. Similar: dendrogram, indented_tree, icicle. Sibling chart-types.md: Hierarchies and networks.

### Treemap (`treemap`)

Nested rectangles where each category's area is proportional to its value, with subcategories sitting inside their parent. Readers compare rectangle sizes to judge shares of the total.

- Also known as: —. Functions: comparisons, hierarchy, part-to-a-whole, proportions.
- Anatomy: Outer rectangles for top-level groups, smaller rectangles nested inside for subcategories, area encoding the value, and colour for groups or variables.
- Fits: Showing shares of a total across many categories; Compact display of a large hierarchy; Overviewing file or directory sizes; Comparing proportions between categories by area.
- Limits: Hierarchy levels are less clear than in tree or sunburst charts; Tiling algorithm changes rectangle shapes and ordering; Hard to compare very similar or thin rectangles.
- Data: tree; keys categorical (some/many/huge); values quantitative (amount). Mark area; channels area, containment, color-hue.
- Tasks: find-extremum, gist, compare. Scale: hundreds to thousands of leaves; depth ≤ 3. Modes: explanatory, analysis. Profiles: executive, domain-expert, general-public, data-analyst.
- Rules: EFF-02, TXT-10, COL-04. Libraries: altair workaround, matplotlib workaround, plotly native.
- Archetypes: part-to-whole-hierarchy, part-to-whole-single. Similar: circle_packing, marimekko_chart, sunburst_diagram, icicle. Sibling chart-types.md: Proportions / Treemap.

### UpSet plot (`upset`) *(supplement)*

Bars give the size of every combination of sets, and a dot matrix under the bars shows which sets each combination contains. Bar length makes intersection sizes exactly comparable, and the layout keeps working well past the three sets a Venn diagram can hold.

- Also known as: intersection bar chart, set intersection matrix, UpSet. Functions: relationships, comparisons.
- Anatomy: Sorted bars of intersection size, a matrix with one row per set and filled connected dots marking membership, side bars for total set sizes.
- Fits: Four or more overlapping sets; Ranking the largest or emptiest combinations; Exact comparison of intersection sizes; Filtering combinations by degree or minimum size.
- Limits: Readers must learn the matrix before the bars make sense; Combinations double with every added set; truncate and say so; Containment is less intuitive than overlapping circles; Sort order changes the story; state it.
- Data: table; keys categorical (few/some); values quantitative (count). Mark line; channels length, position-x, position-y, connection.
- Tasks: compare, sort, find-extremum, retrieve-value, filter. Scale: up to ~20 sets; show the top ~40 combinations. Modes: analysis, exploration, explanatory. Profiles: data-analyst, scientist-reviewer, domain-expert.
- Rules: CMP-01, EFF-17, TXT-07. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: set-overlap. Similar: venn_diagram, bar_chart, heatmap.

### Venn Diagram (`venn_diagram`)

Overlapping shapes, usually circles, each stand for a set; items in an overlap belong to every set covering that region. Readers check which regions hold shared membership.

- Also known as: Set Diagram. Functions: comparisons, concepts, relationships.
- Anatomy: Circles representing sets, overlapping intersection zones where shared items sit, and labels naming each set.
- Fits: Showing shared membership between two or three groups; Explaining logical intersections and set relationships; Comparing overlap between categories or concepts.
- Limits: Geometry gets complex beyond three or four sets; Circle overlap areas do not encode exact quantities; Hard to draw cleanly when many sets are involved.
- Data: table; keys categorical (few); values quantitative (count). Mark area; channels containment, area.
- Tasks: gist, retrieve-value. Scale: 2–3 sets. Modes: explanatory. Profiles: general-public, student-learner.
- Rules: EXP-07, EFF-02, IDM-VENN. Libraries: altair none, matplotlib workaround, plotly none.
- Archetypes: set-overlap. Similar: upset.

### Violin Plot (`violin_plot`)

Mirrored density curves form a shape around a central box-like marker; the width at each height shows how many values fall there. Readers read shape for modes and skew, and median and spread from the centre.

- Also known as: —. Functions: distribution, patterns, range.
- Anatomy: A symmetric density outline mirrored around a vertical axis, a white median dot, a thick central bar for the interquartile range, and a thin line for min and max values.
- Fits: Comparing distribution shapes across several groups; Spotting bimodal or multimodal distributions; Showing median and spread together in one view.
- Limits: Visually noisier than a plain box plot; Marker can be clipped at the ends of the thin line; Density smoothing can hide or invent features in small samples.
- Data: table; keys categorical (few/some); values quantitative (amount). Mark area; channels position-x, position-y, length.
- Tasks: characterize-distribution, compare, find-anomalies. Scale: ≤ ~20 groups; n ≥ ~30 per group. Modes: analysis, explanatory. Profiles: scientist-reviewer, data-analyst, domain-expert.
- Rules: EXP-16, DAT-03. Libraries: altair workaround, matplotlib native, plotly native.
- Archetypes: distribution-compare-groups, uncertainty-of-estimate-or-forecast. Similar: box_plot, raincloud. Sibling chart-types.md: Distributions / Violin / strip / beeswarm / ridge / raincloud.

### Wilkinson dot plot (`wilkinson_dot_plot`) *(supplement)*

Observations are binned along the axis and drawn as dots stacked in columns, one dot per observation. It reads like a histogram whose bars can be counted, which suits small samples and audiences who prefer counts to densities.

- Also known as: dot histogram, stacked dot plot, wheat plot. Functions: distribution.
- Anatomy: A quantitative axis, columns of equally sized dots stacked from a baseline, one dot per observation, bin width equal to dot diameter.
- Fits: Small samples where each observation should be countable; Teaching distributions without a density scale; Discrete or rounded measurements; Showing gaps and repeated values honestly.
- Limits: Binning moves values to the column position; Bin width and dot size are tied; changing one changes the picture; Stacks outgrow the plot beyond a few hundred points; Easily confused with a Cleveland dot plot of categories.
- Data: table; keys categorical (one/few); values quantitative (amount). Mark point; channels position-x, length.
- Tasks: characterize-distribution, retrieve-value, find-anomalies, determine-range. Scale: ≤ ~200 observations per group. Modes: explanatory, analysis. Profiles: student-learner, general-public, scientist-reviewer, data-analyst, communicator-journalist.
- Rules: EXP-15, EFF-19. Libraries: altair workaround, matplotlib workaround, plotly workaround.
- Archetypes: distribution-single, distribution-compare-groups. Similar: histogram, strip_plot, beeswarm, quantile_dotplot, stem_and_leaf_plot. Sibling chart-types.md: Distributions / Histogram.

### Word Cloud (`wordcloud`)

Words are sized by how often they occur in a text, then arranged into a cluster; colour is usually decorative. The eye goes to the largest words as the most frequent terms.

- Also known as: Tag Cloud. Functions: analysing-text, distribution, proportions.
- Anatomy: Words as text labels, font size encoding frequency or an attached value, arrangement in a cluster or shape, and optional colour categories.
- Fits: Quick overview of frequent keywords or tags; Website or blog tag usage display; Rough comparison of two bodies of text; Decorative summary of a topic or text.
- Limits: Long words look bigger than short ones; Letter shapes with ascenders receive extra attention; Poor for analytical accuracy; mostly aesthetic.
- Data: text; keys categorical (many/huge); values quantitative (count). Mark text; channels size, color-hue.
- Tasks: gist. Scale: ≤ ~100 words. Modes: explanatory. Profiles: general-public, communicator-journalist.
- Rules: IDM-WORDCLOUD, EXP-10. Discouraged (IDM-WORDCLOUD): area depends on word length; a sorted bar chart of top terms compares better. Libraries: altair none, matplotlib workaround, plotly none.
- Archetypes: text-frequency. Similar: —. Sibling chart-types.md: Text.

