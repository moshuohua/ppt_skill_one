# QA checklist

## Content

- [ ] PPTX contains exactly one slide.
- [ ] The slide states exactly one core claim.
- [ ] Supporting claims number one to three and jointly prove the core claim.
- [ ] The reasoning follows fact → mechanism → strategic intent → control-point/value-pool shift → company action.
- [ ] At least one credible alternative explanation and one to three observable signals were tested.
- [ ] The claim is non-obvious, causal, strategic, decision-relevant, and testable; at least four of five tests pass.
- [ ] The title is a clear judgment, uses bold 24 pt Microsoft YaHei, contains no manual newline, and renders in at most two natural lines.
- [ ] The title is preferably 50–70 visual characters without filler.
- [ ] The title region is vertically balanced for its natural line count and contains no subtitle or small text.
- [ ] Any list contains no more than three items.
- [ ] Visible body copy is short enough for a 30-second read and never exceeds 220 Chinese characters.
- [ ] Language is direct, concrete, and free of unexplained jargon.
- [ ] The implication fits the cloud, Agent, MaaS, and non-leading-model company context.

## Evidence

- [ ] Every important fact and number has been checked against a current source.
- [ ] Core numbers use a primary source with clear unit, period, scope, and definition.
- [ ] One to three credible global AI media or blog conclusions are used when relevant.
- [ ] Inference is labeled and not presented as fact.
- [ ] Conflicting figures have been reconciled rather than averaged.
- [ ] A visible source footer is used only when useful; if present it is one-line, 10 pt Microsoft YaHei italic gray at the 30 pt left/bottom margins.
- [ ] Full URLs and citations appear in a `[Sources]` speaker-notes block.

## Visual system

- [ ] Slide is 16:9 and all non-background objects respect the 30 pt / 40 px safe margin.
- [ ] Only `#C7000B`, `#000000`, `#8C8C8C`, `#D53C44`, `#F1B4B6`, and `#FFFFFF` appear.
- [ ] Only 24, 18, 14, and 10 pt text appears.
- [ ] Every delivered text run, shape label, chart label, and table cell names Microsoft YaHei.
- [ ] The slide has one visual focus, stable alignment, and useful whitespace.
- [ ] The page is not a grid of small cards or a decorative dashboard.
- [ ] The layout follows the relationship being explained and is not a default left-chart/right-text split.
- [ ] The page contains a high-value chart or semantic diagram whose removal would reduce comprehension.
- [ ] Data is charted when a chart communicates it faster than prose; architecture, causal, combination, hierarchy, or sequence relationships use an appropriate diagram.
- [ ] Every chart makes one conclusion and uses direct labels where practical.
- [ ] No decorative pseudo-chart, stock image, ornamental arrow, or gratuitous icon is used.

## Fidelity and editability

- [ ] Master PNG is 3840×2160 and was exported before the PPTX from the same slide structure.
- [ ] Re-rendered PPTX has been inspected against the master at full size.
- [ ] Both artifact-tool re-import and Office-compatible renders have been inspected; native connectors appear in the Office-compatible render.
- [ ] No unintended overlap, clipping, wrapping, crop drift, or broken connector remains.
- [ ] Key positions and sizes stay within 0.5% of the canvas against the structured specification.
- [ ] Text, shapes, tables, charts, and connectors are native editable objects.
- [ ] Diagram connectors use consistent semantics and remain visually behind nodes and labels.
- [ ] Images and complex illustration pieces are independent, complete, and cleanly cut.
- [ ] No full-slide flattened screenshot is used to fake fidelity.

## Final checks

- [ ] `validate_slide_spec.py` passes.
- [ ] `check_layout.py` passes on the exported layout evidence.
- [ ] `compare_renders.py` passes or every flagged difference is visually resolved.
- [ ] `audit_pptx.py --strict` passes.
- [ ] The Presentations overflow test passes.
- [ ] Final handoff includes only the requested PPTX and master PNG, not scratch files.
