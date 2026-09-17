# Slide specification schema

Use one JSON file as the source for the visual master and PPTX.

## Contents

- Top level
- Sources
- Common element fields
- Text
- Shape and line
- Connector
- Image
- Chart
- Table
- Ordering and relationships

## Top level

```json
{
  "version": "1.1",
  "meta": {
    "title": "A viewpoint title",
    "coreClaim": "One claim only",
    "supportingClaims": ["Up to three"],
    "companyImplication": "Optional decision implication",
    "asOfDate": "YYYY-MM-DD",
    "dataHeavy": true,
    "contentTop": 158,
    "renderFontFallback": "Optional glyph-complete local font used only for preview and layout QA",
    "insightChain": {
      "fact": "Verified external change",
      "mechanism": "Why the fact changes economics or capability",
      "strategicIntent": "What the actor is trying to control or achieve",
      "controlPointShift": "Where power, value, or the bottleneck moves",
      "companyAction": "What the company should do differently",
      "alternativeExplanation": "One credible competing explanation",
      "observableSignals": ["One to three signals that can confirm or weaken the inference"]
    },
    "visualStrategy": {
      "relationshipType": "control-point-shift",
      "layoutFamily": "control-point-migration",
      "message": "The relationship the reader must see",
      "elementIds": ["node-model", "connector-up", "node-runtime"]
    }
  },
  "slide": {
    "width": 1280,
    "height": 720,
    "margin": 40,
    "background": "#FFFFFF"
  },
  "sources": [],
  "elements": []
}
```

`meta.contentTop` marks the start of the body region. Use approximately `132` for a one-line natural title and `158` for a two-line natural title. The title box starts at `y=40`, ends at `contentTop`, and vertically centers the title. Do not place any other text before `contentTop`.

Use `meta.renderFontFallback` only when the local renderer lacks Microsoft YaHei glyphs. Keep every element's delivered `fontFamily` as `Microsoft YaHei`; the builder applies the fallback only to the master and layout-evidence render, while the final PPTX font pass restores Microsoft YaHei throughout.

Allowed `relationshipType` values: `comparison`, `trend`, `causal`, `architecture`, `combination`, `hierarchy`, `sequence`, `control-point-shift`, `evidence-chain`, `matrix`.

Allowed `layoutFamily` values: `chart-dominant`, `control-point-migration`, `causal-chain`, `architecture-stack`, `comparison-matrix`, `evidence-to-action`, `central-thesis`, `sequence-timeline`.

`visualStrategy.elementIds` identifies the native chart, table, shapes, lines, connectors, and labels that jointly form the core semantic visual. The visual must encode the relationship rather than decorate the page.

## Sources

```json
{
  "id": "src-official-1",
  "institution": "Company or author",
  "title": "Source title",
  "publishedDate": "YYYY-MM-DD",
  "accessedDate": "YYYY-MM-DD",
  "url": "https://...",
  "type": "official",
  "supports": ["core-claim", "chart-main"],
  "metric": {
    "definition": "What the number measures",
    "unit": "Unit",
    "period": "Time window",
    "scope": "Geography or sample"
  }
}
```

Allowed source types: `official`, `paper`, `dataset`, `filing`, `research`, `consulting`, `media`, `blog`, `analysis`.

## Common element fields

Every element has:

```json
{
  "id": "unique-id",
  "name": "clear-object-name",
  "type": "text",
  "z": 10,
  "frame": { "x": 40, "y": 40, "w": 1200, "h": 64 },
  "sourceIds": ["src-official-1"]
}
```

`frame` uses 1280×720 pixel coordinates. All non-background elements stay inside the 40 px margin.

## Text

```json
{
  "id": "title",
  "name": "main-title",
  "type": "text",
  "role": "title",
  "z": 20,
  "frame": { "x": 40, "y": 40, "w": 1200, "h": 78 },
  "text": "Clear conclusion",
  "style": {
    "fontPt": 24,
    "fontFamily": "Microsoft YaHei",
    "bold": true,
    "color": "#C7000B",
    "align": "left",
    "valign": "middle",
    "lineSpacing": 1.05,
    "insets": { "top": 0, "right": 0, "bottom": 0, "left": 0 }
  }
}
```

For a title, set its frame to `{ "x": 40, "y": 40, "w": 1200, "h": meta.contentTop - 40 }`, use vertical middle alignment and zero insets. Do not include `\n` in title text. Prefer 50–70 visual characters and allow at most two natural rendered lines.

Roles: `title`, `subhead`, `body`, `highlight`, `chart-label`, `diagram-label`, `annotation`, `source`. Use `diagram-label` for concise labels inside a semantic visual; it may be 10 or 14 pt and does not replace explanatory body copy.

The `source` role is optional. If used, name the element `source-footer`, keep it to one natural line, set `x=40` and `y+h=680`, and use 10 pt `Microsoft YaHei`, italic, `#8C8C8C`, left aligned. Never use a source-role text box beneath the title.

For editable lists, paragraph spacing, mixed emphasis, and links, replace `text` with structured paragraphs:

```json
"paragraphs": [
  {
    "bullet": true,
    "bulletCharacter": "•",
    "marginLeft": 20,
    "indent": -10,
    "spaceAfter": 6,
    "runs": [
      { "text": "判断：", "style": { "fontPt": 14, "bold": true, "color": "#C7000B" } },
      { "text": "用一句短证据支持判断。", "style": { "fontPt": 14, "color": "#000000" } }
    ]
  }
]
```

Use at most three bullet paragraphs. A run may include `url` for an external hyperlink. Keep every run within the four allowed font sizes and the approved palette.

## Shape and line

```json
{
  "id": "evidence-frame",
  "name": "evidence-frame",
  "type": "shape",
  "geometry": "roundRect",
  "frame": { "x": 640, "y": 150, "w": 600, "h": 430 },
  "fill": "#FFFFFF",
  "line": { "color": "#8C8C8C", "width": 1, "style": "solid" },
  "radius": 10,
  "z": 1
}
```

Use `type: "line"` with the same `frame`; `x,y` are the start and `x+w,y+h` the end.

## Connector

```json
{
  "id": "flow-1",
  "name": "flow-1",
  "type": "connector",
  "fromId": "node-a",
  "toId": "node-b",
  "fromSide": "right",
  "toSide": "left",
  "kind": "elbow",
  "line": { "color": "#8C8C8C", "width": 2, "style": "solid" },
  "endArrow": "arrow"
}
```

Use `endArrow` for an arrow pointing toward `toId` and `startArrow` for an arrow at `fromId`. The builder maps these clear names to the underlying Office connector ends.

## Image

```json
{
  "id": "illustration",
  "name": "illustration",
  "type": "image",
  "path": "assets/illustration.png",
  "alt": "Plain description",
  "fit": "contain",
  "frame": { "x": 760, "y": 160, "w": 420, "h": 360 },
  "crop": { "left": 0, "top": 0, "right": 0, "bottom": 0 },
  "rotation": 0,
  "z": 5
}
```

Keep generated illustrations free of final text and data.

## Chart

```json
{
  "id": "chart-main",
  "name": "chart-main",
  "type": "chart",
  "chartType": "bar",
  "frame": { "x": 520, "y": 180, "w": 720, "h": 400 },
  "categories": ["A", "B", "C"],
  "series": [
    { "name": "Value", "values": [10, 20, 30], "color": "#C7000B" }
  ],
  "options": {
    "direction": "bar",
    "grouping": "clustered",
    "gapWidth": 45,
    "legend": false,
    "showValues": true,
    "numberFormat": "0",
    "xAxisVisible": false,
    "yAxisVisible": true
  },
  "sourceIds": ["src-official-1"],
  "z": 5
}
```

## Table

```json
{
  "id": "table-main",
  "name": "table-main",
  "type": "table",
  "frame": { "x": 420, "y": 180, "w": 820, "h": 360 },
  "values": [["Item", "Value"], ["A", "10"]],
  "header": true,
  "fontPt": 10,
  "sourceIds": ["src-official-1"],
  "z": 5
}
```

## Ordering and relationships

Use low `z` for backgrounds and containers, then charts or images, then text. Name every object clearly. Keep connectors attached through `fromId` and `toId`; do not store them as arbitrary pixel lines.

Keep diagram connectors visually behind their nodes and labels. Retain the raw values for editable vector charts in an editable table or in the `[Sources]` notes record.
