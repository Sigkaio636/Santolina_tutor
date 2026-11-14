# User profiles (generated from profiles/users/*.yaml by build_index.py)

Each profile states the reader's capabilities and the cognitive tasks they perform, which the
questionnaire uses to pick defaults and which the matcher uses as part of the decision key.

| id | literacy | time | why | primary tasks | prefers | avoid |
|---|---|---|---|---|---|---|
| `communicator-journalist` | medium | a-minute | present/locate/compare | find-extremum, compare, trend | line, bar, slope, map-choropleth, small-multiples, scatter, dot-plot | pie-over-5, dual-axes, radial, gauge, 3d, word-cloud |
| `data-analyst` | high | sustained | discover/explore/summarize | correlate, cluster, filter, characterize-distribution, find-anomalies | scatter, heatmap, parallel, small-multiples, distribution, line | pie, radial, word-cloud, gauge, proportional-area |
| `domain-expert` | medium | minutes | discover/browse/compare | find-anomalies, compare, retrieve-value, characterize-distribution | heatmap, small-multiples, dot-plot, line, distribution, map-choropleth | pie-over-5, gauge, word-cloud, radial |
| `executive` | medium | a-minute | present/lookup/compare | find-extremum, compute-derived, trend, compare | bar, bullet, slope, line, small-multiples, table | pie-over-5, radar, gauge, word-cloud, dual-axes, parallel, network |
| `general-public` | low | seconds | present/lookup/identify | gist, find-extremum, retrieve-value | bar, line, dot-plot, map-choropleth, pictogram, small-multiples | pie-over-5, dual-axes, log-scale, parallel, network, radar, gauge, word-cloud |
| `operator-monitoring` | medium | seconds | discover/lookup/identify | find-anomalies, retrieve-value, determine-range | line, bullet, bar, heatmap, table | pie, radial, word-cloud, animation, treemap, gauge |
| `scientist-reviewer` | high | minutes | present/locate/compare | characterize-distribution, determine-range, find-anomalies, compare | distribution, scatter, small-multiples, dot-plot, line, heatmap | pie, mean-bars-without-data, dual-axes, radial, word-cloud, 3d |
| `student-learner` | low | minutes | enjoy/browse/identify | retrieve-value, compare, sort, trend | bar, line, scatter, histogram, small-multiples, dot-plot | pie-over-5, dual-axes, parallel, network, radial, word-cloud |

## Communicator or journalist (`communicator-journalist`)

Builds and reads narrative graphics for a broad audience; reads for about a minute and expects annotation, a highlighted series against grey context, honest scales and a story the title states.

- Capabilities: literacy medium, domain medium, statistics low, time a-minute, interaction tolerance medium, working-memory budget 3 chunks.
- Idioms that need no explanation: bar, line, map-choropleth, slope, scatter, small-multiples, stacked-bar, pictogram, table; need explanation: heatmap, parallel, network, distribution.
- Cognitive tasks: primary find-extremum, compare, trend; secondary gist, retrieve-value, find-anomalies; Shneiderman overview, details-on-demand.
- Text: title takeaway, annotations high, units and n required.
- Confidence needs: source, period, definition-of-the-metric, caveats. Default mode: explanatory. Default modifiers: cvd, mobile.
- Typical readers: data journalist, communications officer, NGO report author.

## Data analyst (`data-analyst`)

Explores to find the questions worth asking, for sustained sessions. Expects interaction (filter, brush, reconfigure), linked views and dense multivariate idioms; cares about distributions and outliers, not polish.

- Capabilities: literacy high, domain medium, statistics high, time sustained, interaction tolerance high, working-memory budget 4 chunks.
- Idioms that need no explanation: bar, line, scatter, heatmap, distribution, parallel, small-multiples, network, stacked-bar, grouped-bar, map-choropleth, table; need explanation: none.
- Cognitive tasks: primary correlate, cluster, filter, characterize-distribution, find-anomalies; secondary compute-derived, determine-range, sort, trend; Shneiderman overview, zoom, filter, details-on-demand, relate, history, extract.
- Text: title descriptive, annotations low, units and n required.
- Confidence needs: n, aggregation-method, missing-data, filters-applied. Default mode: exploration. Default modifiers: none.
- Typical readers: data scientist in an exploratory session, BI analyst building a view, researcher cleaning a dataset.

## Domain expert (not a visualization specialist) (`domain-expert`)

Knows the entities, units and categories intimately and wants to confirm or challenge what they already suspect. Tolerates dense charts if the labels are the ones they use daily; reads for minutes.

- Capabilities: literacy medium, domain high, statistics medium, time minutes, interaction tolerance medium, working-memory budget 4 chunks.
- Idioms that need no explanation: bar, line, scatter, heatmap, map-choropleth, distribution, table, grouped-bar, stacked-bar; need explanation: parallel, network, stacked-area, radial.
- Cognitive tasks: primary find-anomalies, compare, retrieve-value, characterize-distribution; secondary find-extremum, sort, determine-range, trend; Shneiderman overview, zoom, filter, details-on-demand.
- Text: title descriptive, annotations medium, units and n required.
- Confidence needs: source, n, aggregation-method, period, normalization. Default mode: analysis. Default modifiers: none.
- Typical readers: epidemiologist, forest engineer, sales operations lead, clinician.

## Executive or manager (`executive`)

Decides with the chart in under a minute. Wants the number, the comparison to a target or to last period, and the direction of change; will not decode encodings or scan a legend.

- Capabilities: literacy medium, domain medium, statistics low, time a-minute, interaction tolerance low, working-memory budget 3 chunks.
- Idioms that need no explanation: bar, line, bullet, slope, table, pie; need explanation: heatmap, distribution, parallel, network, stacked-area.
- Cognitive tasks: primary find-extremum, compute-derived, trend, compare; secondary retrieve-value, sort; Shneiderman overview, details-on-demand.
- Text: title takeaway, annotations medium, units and n required.
- Confidence needs: source, period, definition-of-the-metric, target. Default mode: explanatory. Default modifiers: none.
- Typical readers: department head reading a KPI page, board member, product manager.

## General public (`general-public`)

Reads charts in news, reports or slides for seconds, with no training and no prior knowledge of the data. Wants one clear message and the numbers behind it; gives up on anything that needs a legend lookup or an unfamiliar idiom.

- Capabilities: literacy low, domain low, statistics low, time seconds, interaction tolerance none, working-memory budget 2 chunks.
- Idioms that need no explanation: bar, line, pie, map-choropleth, pictogram, table; need explanation: heatmap, scatter, distribution, parallel, network, stacked-area, treemap, slope.
- Cognitive tasks: primary gist, find-extremum, retrieve-value; secondary compare, trend; Shneiderman overview.
- Text: title takeaway, annotations high, units and n required.
- Confidence needs: source, period, what-the-numbers-mean. Default mode: explanatory. Default modifiers: cvd.
- Typical readers: newspaper reader, citizen reading a public-health report, audience of a public talk.

## Operator monitoring a system (`operator-monitoring`)

Glances at the same display many times a day to spot anomalies and current levels. Needs stable layout, thresholds and reference lines, alert color only for alerts, and values readable in a second.

- Capabilities: literacy medium, domain high, statistics medium, time seconds, interaction tolerance low, working-memory budget 3 chunks.
- Idioms that need no explanation: line, bar, bullet, table, heatmap; need explanation: parallel, network, scatter, treemap.
- Cognitive tasks: primary find-anomalies, retrieve-value, determine-range; secondary trend, compare; Shneiderman overview, details-on-demand, filter.
- Text: title minimal, annotations low, units and n required.
- Confidence needs: threshold-definition, time-of-last-update, units. Default mode: analysis. Default modifiers: projector.
- Typical readers: network operations engineer, plant supervisor, on-call analyst watching a dashboard.

## Scientist or reviewer (`scientist-reviewer`)

Reads figures in papers and technical reports with high statistical literacy and scepticism. Wants distributions rather than means, uncertainty and sample sizes stated, honest axes, and figures that survive grayscale printing.

- Capabilities: literacy high, domain high, statistics high, time minutes, interaction tolerance low, working-memory budget 4 chunks.
- Idioms that need no explanation: bar, line, scatter, distribution, heatmap, small-multiples, slope, table, histogram; need explanation: network, parallel, stacked-area.
- Cognitive tasks: primary characterize-distribution, determine-range, find-anomalies, compare; secondary correlate, retrieve-value, trend; Shneiderman overview, details-on-demand.
- Text: title descriptive, annotations medium, units and n required.
- Confidence needs: n, uncertainty-definition, source, method, units. Default mode: analysis. Default modifiers: print-grayscale.
- Typical readers: peer reviewer, thesis committee member, lab colleague reading a results figure.

## Student or learner (`student-learner`)

Is learning the domain or the chart type at the same time. Reads for minutes, benefits from canonical idioms, explicit encoding explanations, annotations and one idea per chart.

- Capabilities: literacy low, domain low, statistics low, time minutes, interaction tolerance low, working-memory budget 3 chunks.
- Idioms that need no explanation: bar, line, pie, scatter, histogram, table, map-choropleth; need explanation: heatmap, distribution, parallel, network, stacked-area, slope, treemap.
- Cognitive tasks: primary retrieve-value, compare, sort, trend; secondary find-extremum, gist, characterize-distribution; Shneiderman overview, details-on-demand.
- Text: title takeaway, annotations high, units and n required.
- Confidence needs: source, what-the-numbers-mean, units. Default mode: explanatory. Default modifiers: none.
- Typical readers: undergraduate reading course material, newcomer to a team's metrics, textbook reader.
