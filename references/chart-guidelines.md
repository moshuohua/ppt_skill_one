# Chart and semantic-visual guidelines

Use a consulting-style visual: one conclusion, direct labels, little decoration, and a clear source. Every page should contain a core chart or semantic diagram that materially improves understanding.

## Choose the relationship before the graphic

| Relationship to explain | Preferred form |
| --- | --- |
| Numeric comparison | Bar, column, dot plot, or slope chart |
| Trend or inflection | Line, stage evolution, or timeline |
| Causality or logical dependency | Causal chain, driver tree, or restrained flywheel |
| Architecture or capability boundary | Layered architecture or capability stack |
| Combination or ecosystem | Nested composition, value chain, or clustered relationship |
| Hierarchy or priority | Tree, pyramid, or priority matrix |
| Sequence or migration | Process, path, before-after, or control-point migration |
| Evidence leading to action | Evidence chain ending in one decision implication |

Delete a visual if removing it does not reduce comprehension. Do not use stock photography, decorative arrows, ornamental icons, or a pseudo-chart merely to fill space.

## Choose the simplest truthful chart

| Question | Preferred form |
| --- | --- |
| Compare categories | Bar or column |
| Show a time trend | Line |
| Show before and after | Slope chart |
| Show composition | Stacked bar |
| Explain additions and subtractions | Waterfall |
| Show two-variable relationship | Scatter |
| Show a few exact values | Small table or direct numbers |

Avoid 3D charts, ornamental gauges, crowded pies, radar charts, unnecessary dual axes, heavy gridlines, and legends that force eye movement.

## Build the message into the chart

- Write a conclusion as the chart title, not a topic label.
- Use `#C7000B` for the decisive series or data point.
- Use `#D53C44`, `#F1B4B6`, or gray only for context.
- Label important values directly.
- Remove borders and gridlines that do not improve reading.
- Show the unit, period, scope, and source.
- Keep categories and series few enough to read in one glance.

## Data integrity

- Preserve the original values in the native chart data.
- Match the chart axis and number format to the source definition.
- Do not truncate an axis in a way that exaggerates the difference.
- Do not combine series with incompatible units without a clear explanation.
- Link every chart to one or more `sourceIds` in `slide_spec`.
- If reliable data does not exist, do not create a decorative pseudo-chart.

## Editable implementation

Prefer a native PowerPoint chart. Use editable vector shapes only for forms the native chart API cannot express clearly. Keep labels as real text, connectors as real connectors, and the underlying numbers in an editable chart or table.

For semantic diagrams:

- use native PowerPoint shapes and connectors;
- keep nodes few enough to read in one glance and avoid more than five horizontally;
- make connector direction and meaning consistent;
- place connectors behind nodes and labels;
- use size, position, and the approved red hierarchy to encode meaning rather than decoration;
- retain every informative label as editable text.
