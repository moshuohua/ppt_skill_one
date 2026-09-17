# Element mapping

| Intended content | PowerPoint object | Editability requirement |
| --- | --- | --- |
| Title, subhead, body, source | Native text box | Text, paragraph, font, color, and position editable |
| Basic geometry or container | Native shape | Fill, border, geometry, size, and position editable |
| Table | Native table | Cell values and formatting editable |
| Data chart | Native chart | Source data, series, labels, axes, and style editable |
| Special chart | Editable vector shapes | Values also retained in an editable table or notes |
| Flow or dependency | Native connector | Endpoints remain attached to named shapes |
| Causal, hierarchy, sequence, or control-point diagram | Native shapes plus connectors | Relationship, labels, order, and endpoints remain editable |
| Icon | SVG where available | Separate, replaceable object |
| Photo or screenshot | Image object | Move, crop, resize, and replace independently |
| Complex illustration | Transparent PNG or SVG slices | Each meaningful visual part remains a separate object |
| Background | Native fill, gradient, or simple shape | Never use the whole flattened page as background |

## Semantic and object editability

Semantic editability means the actual text, data, table values, or connection can change. Require it for all informative elements.

Object editability means a raster asset can move, resize, crop, replace, or change z-order. Accept it only for photos, textures, and genuinely complex illustration pieces.

Never call a flattened region fully editable merely because the bitmap can move.

Use `Microsoft YaHei` for every informative text object, including chart and table text. Build connectors so that nodes and labels visually remain in front of the connector paths.

## Slicing complex assets

- Generate or retain the complete source asset before compositing.
- Use transparent backgrounds.
- Preserve outlines, shadows, glow, and hidden edges.
- Keep at least 2× the final displayed resolution.
- Remove white or page-colored halos.
- Insert each slice as a separately named object.
- Separate all final text, numbers, charts, and connectors from the image.

Do not crop pieces out of the final flattened slide unless no source asset exists and reconstruction is explicitly accepted as a lower-fidelity fallback.
