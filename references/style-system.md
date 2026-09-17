# Style system

## Canvas and safe area

- Slide: 16:9, 1280×720 px authoring canvas.
- Visual master: 3840×2160 PNG.
- Safe margin: 30 PowerPoint pt on every side, equal to 40 px at 96 dpi.
- Keep every non-background object inside `x=40..1240` and `y=40..680`.
- Keep real whitespace inside the safe area; do not fill every available region.

## Colors

Only use black, white, and these colors:

| Use | RGB | HEX |
| --- | --- | --- |
| Title, subhead, text highlight, key graphic | 199 / 0 / 11 | `#C7000B` |
| Main text | 0 / 0 / 0 | `#000000` |
| Supporting graphics, containers, rules | 140 / 140 / 140 | `#8C8C8C` |
| Chart mid red | 213 / 60 / 68 | `#D53C44` |
| Chart light red | 241 / 180 / 182 | `#F1B4B6` |
| Background | 255 / 255 / 255 | `#FFFFFF` |

Use at most three red levels in a chart. Highlight only the series or point that proves the claim. Use white fills and thin gray rules before creating large gray surfaces. Do not add blue, green, orange, or purple for variety.

## Typography

Only use these PowerPoint sizes:

| Role | PowerPoint pt | Artifact-tool px | Default color |
| --- | ---: | ---: | --- |
| Main title | 24 | 32 | `#C7000B` |
| Subhead or chart conclusion | 18 | 24 | `#C7000B` |
| Body | 14 | 18.6667 | `#000000` |
| Sources, axes, legend, labels, notes | 10 | 13.3333 | `#8C8C8C` or `#000000` |

Use `Microsoft YaHei` throughout the delivered PPTX, including text runs, shape text, chart labels, legends, axes, and table cells.

- Make the 24 pt main title bold.
- Do not insert a newline into the title. Let it wrap naturally to at most two lines.
- Vertically center the title inside a line-count-aware title region. A typical `contentTop` is 132 px for one rendered line and 158 px for two rendered lines.
- Let the title box start at `y=40` and end at `meta.contentTop`; use vertical middle alignment and zero insets.
- Place no subtitle or small text between the title and `meta.contentTop`.

Check `Microsoft YaHei` with `scripts/prepare_fontconfig.py` before building. If it is unavailable locally, retain the exact typeface in the PPTX, use the bundled Noto Sans CJK SC only for render QA, set `meta.renderFontFallback`, and keep conservative line-fit headroom. Never silently change the delivered font.

### Optional visible source footer

When present, name it `source-footer` and use:

- frame left `x=40` and bottom `y+h=680`;
- `Microsoft YaHei`, 10 pt, italic, `#8C8C8C`;
- left alignment, one natural line, and no long URL.

## Composition

- Use one main composition, not a dashboard of tiny cards.
- Choose the silhouette from the relationship the page must explain; do not default to a left-chart/right-text split.
- Give the high-value chart or semantic diagram the dominant evidence area.
- Give a data chart the largest evidence area when data is central.
- Keep one obvious reading order and one visual focus.
- Use alignment, spacing, and a restrained rule system instead of decoration.
- Avoid pills, button-like labels, dense card grids, 3D effects, and ornamental icons.
- Use an illustration only when it explains something a chart or native shape cannot.
