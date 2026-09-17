---
name: i2p-666
description: Create exactly one executive-ready, insight-led, editable PowerPoint slide from a user's AI, agent, MaaS, model, or cloud-computing viewpoint and evidence. Use for single-slide leadership briefings, strategy insights, data-driven AI trend slides, image-first editable PowerPoint reconstruction, or requests mentioning i2p-666, I2P, 单页洞察PPT, 领导汇报PPT, 图片母版转可编辑PPT, or high-fidelity editable PPT. The slide must be current, fact-checked, conclusion-first, causally deep, supported by a high-value semantic visual, and generated master-image-first from the same structured specification as the PPTX.
---

# i2p-666

Create one 16:9 insight slide for rapid executive reading. Build a 4K visual master first, then export the editable PPTX from the same in-memory slide structure. Never reverse-engineer editable objects from a flattened screenshot.

## Required companion skills

- Load and follow `Presentations` before any PowerPoint work. Its artifact-tool, rendering, notes, overlap, and delivery rules remain mandatory. User-specified typography in this skill overrides its default font sizes.
- Load `imagegen` only when a photo, complex illustration, texture, or transparent raster cutout materially improves the page. Do not use image generation for final text, charts, tables, numbers, axes, or connectors.

Before running scripts, set `I2P_SKILL_DIR` to the absolute directory containing this file and `PRESENTATIONS_SKILL_DIR` to the absolute directory of the loaded `Presentations` skill. Keep the `Presentations` runtime variables exactly as that skill defines them.

## Non-negotiable output

- Produce exactly one slide and one core claim.
- Use at most three supporting claims. They must jointly prove the core claim.
- Keep the slide suitable for a cloud-computing company leadership team.
- Prioritize insight depth, then evidence reliability, semantic visualization, and visual polish in that order.
- Use `Microsoft YaHei` for every delivered PowerPoint text run, chart label, and table cell.
- Use a bold 24 pt title with no manual line break. Let it wrap naturally to at most two lines and place no subtitle, date, caveat, or explanatory small text beneath it.
- Include one high-value chart or semantic diagram that materially improves comprehension. Never add a decorative pseudo-chart or ornamental illustration.
- Deliver an editable `.pptx` and the corresponding 3840×2160 master `.png` when the user asks for the standard i2p-666 output.
- Keep full source details in a `[Sources]` block in speaker notes. A visible source footer is optional.
- Do not use a full-slide screenshot as the final slide.

## Read the references

Read these files before building:

1. `references/company-context.md`
2. `references/content-rules.md`
3. `references/source-policy.md`
4. `references/style-system.md`
5. `references/chart-guidelines.md`
6. `references/layout-strategy.md`
7. `references/slide-spec-schema.md`
8. `references/element-mapping.md`
9. `references/qa-checklist.md`

## Workflow

### 1. Frame the communication job

Write one internal sentence:

> By the end, the leadership team should understand or decide **X** because **Y**.

Identify the single claim the slide must prove. If the user provides several unrelated claims, select the one most useful to the stated decision or ask which one matters most. Do not create extra slides.

### 2. Research and verify

Browse for every time-sensitive or non-trivial claim. Use the source mix in `references/source-policy.md`:

- primary evidence for facts and numbers;
- credible global AI media or author-led blogs for interpretation;
- transparent research or consulting data when it adds a useful comparison.

Record publication date, access date, metric definition, time period, unit, and URL. Resolve conflicting figures before writing. Clearly label inference. Delete claims that cannot be verified.

### 3. Develop the insight before designing

Build the complete reasoning chain before writing visible copy:

> verified fact → causal mechanism → strategic intent → control-point or value-pool shift → company action

Test at least one credible alternative explanation and identify one to three observable signals that would confirm or weaken the conclusion. Distinguish fact, external interpretation, and author inference. Rework the claim unless it is non-obvious, causal, strategic, decision-relevant, and testable.

Do not mistake more text for more depth. Perform the full analysis, then compress only the decisive reasoning into the slide.

### 4. Write the answer first

Create:

- one viewpoint title at 24 pt, bold, preferably 50–70 visual characters, with no explicit newline and at most two natural rendered lines;
- one to three viewpoint subheads;
- only the evidence needed to support them;
- a clear implication for the company when it improves the decision.

Keep visible body copy normally within 140–200 Chinese characters and never above 220. A diagram may carry part of this information through short labels. Any list may contain at most three items. Use short, direct sentences and plain language. Place no small text between the title and the body region.

### 5. Choose evidence, relationship, and visual form

Identify the relationship the reader must see: comparison, trend, causality, architecture, combination, hierarchy, sequence, control-point migration, evidence chain, or decision matrix. Use a chart whenever comparable numeric evidence exists. Otherwise use an editable semantic diagram. Give one visual one message and one obvious focal point. Choose the layout dynamically from `references/layout-strategy.md`; do not default to left-chart/right-text.

### 6. Create one `slide_spec`

Use `references/slide-spec-schema.md` and `assets/style-tokens.json`. Work on a 1280×720 canvas. Thirty PowerPoint points equal 40 canvas pixels, so all non-background content must remain inside the 40 px safe area.

Use specification version `1.1`. Store the insight chain, visual strategy, title-aware `contentTop`, and every object's id, type, frame, z-order, content, style, source ids, and relationships. Treat this specification as the single source of truth for both the image master and PPTX.

Validate it before rendering:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/validate_slide_spec.py" "$TMP_DIR/slide-spec.json"
```

### 7. Build master first, then PPTX

Follow the runtime setup in `Presentations`. Copy the reusable builder into the writable build directory so its bare package import resolves through the required runtime symlink:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/prepare_fontconfig.py" \
  --out "$TMP_DIR/i2p-fonts.conf"
export FONTCONFIG_FILE="$TMP_DIR/i2p-fonts.conf"

cp "$I2P_SKILL_DIR/scripts/build_i2p.mjs" "$TMP_DIR/build_i2p.mjs"
ln -s "$RUNTIME_NODE_MODULES" "$TMP_DIR/node_modules"
"$RUNTIME_NODE" "$TMP_DIR/build_i2p.mjs" \
  "$TMP_DIR/slide-spec.json" "$TMP_DIR/output" "i2p-slide"

"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/enforce_pptx_font.py" \
  "$TMP_DIR/output/i2p-slide.pptx" --font "Microsoft YaHei"
```

Inspect the font-preparation JSON. If `fallbackActive` is true, set `meta.renderFontFallback` in the specification to the returned family before running the builder. Keep all delivered element font families as Microsoft YaHei.

The builder creates the editable objects, exports the 3840×2160 master PNG first, records layout evidence, and only then exports the PPTX. The font pass makes theme-driven chart, table, and notes text resolve to Microsoft YaHei without changing editability. For unsupported element behavior, write a focused artifact-tool builder in `$TMP_DIR` rather than flattening the slide.

Check the exported layout evidence before re-rendering. If `meta.renderFontFallback` is set, pass that exact family with `--expected-font`; otherwise omit the option:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/check_layout.py" \
  "$TMP_DIR/output/i2p-slide-layout.json" \
  --expected-font "<meta.renderFontFallback or Microsoft YaHei>"
```

This check must pass. It catches actual text wrapping, text boxes that are too short, safe-area violations, and overlapping text frames that a basic canvas-overflow test may miss.

### 8. Re-render and compare

Render the exported PPTX with the `Presentations` helper, then compare it with the master:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" \
  "$PRESENTATIONS_SKILL_DIR/container_tools/render_slides.py" \
  "$TMP_DIR/output/i2p-slide.pptx"

RUNTIME_BIN_DIR="$RUNTIME_BIN_DIR" "$CODEX_PRIMARY_RUNTIME_PYTHON" \
  "$I2P_SKILL_DIR/scripts/render_office.py" \
  "$TMP_DIR/output/i2p-slide.pptx" \
  --out-dir "$TMP_DIR/output/office-render"

"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/compare_renders.py" \
  "$TMP_DIR/output/i2p-slide-master.png" \
  "$TMP_DIR/output/office-render/slide-1.png" \
  --out-dir "$TMP_DIR/output/visual-diff"
```

Inspect the master, both rendered PPTX images, the overlay, and the difference map at full size. The artifact-tool re-import render checks structural round-tripping; the Office-compatible render is the final fidelity comparison because some import renderers omit valid native connectors. Treat font substitution, wrapping, crop drift, clipping, and broken connectors as failures to fix.

When a declared render fallback is active, use the same `FONTCONFIG_FILE` for every render. Font engines may still produce small glyph-spacing differences; after full-size visual inspection, allow at most `--max-mean-diff 12 --max-changed-ratio 0.08`. Do not use this tolerance for structural drift, changed wrapping, clipping, missing glyphs, or broken connectors.

### 9. Audit the final PPTX

Run both checks:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" "$I2P_SKILL_DIR/scripts/audit_pptx.py" \
  "$TMP_DIR/output/i2p-slide.pptx" --strict

"$CODEX_PRIMARY_RUNTIME_PYTHON" \
  "$PRESENTATIONS_SKILL_DIR/container_tools/slides_test.py" \
  "$TMP_DIR/output/i2p-slide.pptx"
```

Fix all errors and re-run the complete render-and-check loop. Do not hide a mismatch by adding a full-slide image.

### 10. Deliver

Return the final `.pptx` and standard master `.png`. Briefly state the slide's core conclusion and that claims were checked against current sources. Do not attach scratch specifications, diff images, builder files, or QA logs unless requested.

## Failure rules

- If a critical fact cannot be verified, remove it or state the uncertainty plainly.
- If content does not fit, cut content or change the layout; never add a slide or shrink below the four allowed font sizes.
- If a chart cannot remain native, rebuild it with editable vector shapes and retain the data in notes or an editable table. Do not rasterize informative content.
- If a complex illustration cannot be semantically edited, keep it as a separate transparent asset and disclose object-level editability. Never describe movable pixels as fully editable content.
- If `Microsoft YaHei` is unavailable to the local renderer, retain `Microsoft YaHei` in the delivered PPTX, render with a glyph-complete local substitute for QA, and leave conservative wrapping headroom. Do not silently change the delivered typeface or approve tofu glyphs.

## Completion gate

Use every item in `references/qa-checklist.md`. The task is complete only when the slide passes content, evidence, visual, structural, editability, and source checks.
