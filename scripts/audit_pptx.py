#!/usr/bin/env python3
"""Audit structural i2p-666 constraints in an exported PPTX."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
}
ALLOWED_FONT_SIZES = {1000, 1400, 1800, 2400}
ALLOWED_COLORS = {"C7000B", "000000", "8C8C8C", "D53C44", "F1B4B6", "FFFFFF"}
REQUIRED_FONT = "Microsoft YaHei"
EMU_PER_PX = 9525


def xml_root(archive: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(archive.read(name))


def slide_size(archive: zipfile.ZipFile) -> tuple[int, int]:
    root = xml_root(archive, "ppt/presentation.xml")
    node = root.find("p:sldSz", NS)
    if node is None:
        raise ValueError("presentation.xml has no slide size")
    return int(node.attrib["cx"]), int(node.attrib["cy"])


def picture_frames(root: ET.Element) -> list[tuple[int, int, int, int]]:
    frames = []
    for picture in root.findall(".//p:pic", NS):
        xfrm = picture.find("p:spPr/a:xfrm", NS)
        if xfrm is None:
            continue
        off = xfrm.find("a:off", NS)
        ext = xfrm.find("a:ext", NS)
        if off is not None and ext is not None:
            frames.append((int(off.attrib.get("x", 0)), int(off.attrib.get("y", 0)), int(ext.attrib.get("cx", 0)), int(ext.attrib.get("cy", 0))))
    return frames


def shape_name(shape: ET.Element) -> str:
    node = shape.find("p:nvSpPr/p:cNvPr", NS)
    return node.attrib.get("name", "") if node is not None else ""


def shape_frame(shape: ET.Element) -> tuple[int, int, int, int] | None:
    xfrm = shape.find("p:spPr/a:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return int(off.attrib.get("x", 0)), int(off.attrib.get("y", 0)), int(ext.attrib.get("cx", 0)), int(ext.attrib.get("cy", 0))


def run_properties(shape: ET.Element) -> list[ET.Element]:
    props = list(shape.findall(".//a:r/a:rPr", NS))
    if props:
        return props
    return list(shape.findall(".//a:pPr/a:defRPr", NS))


def property_color(prop: ET.Element) -> str:
    node = prop.find("a:solidFill/a:srgbClr", NS)
    return node.attrib.get("val", "").upper() if node is not None else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    with zipfile.ZipFile(args.pptx) as archive:
        names = archive.namelist()
        slides = sorted(name for name in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
        if len(slides) != 1:
            errors.append(f"expected exactly one slide, found {len(slides)}")
        width, height = slide_size(archive)
        full_slide_images = 0
        font_sizes: set[int] = set()
        colors: set[str] = set()
        font_names: set[str] = set()
        text_boxes = 0
        image_count = 0
        connector_count = 0
        title_count = 0
        source_footer_count = 0
        for slide_name in slides:
            root = xml_root(archive, slide_name)
            text_boxes += len(root.findall(".//p:sp/p:txBody", NS))
            connectors = root.findall(".//p:cxnSp", NS)
            connector_count += len(connectors)
            for connector in connectors:
                start = connector.find("p:nvCxnSpPr/p:cNvCxnSpPr/a:stCxn", NS)
                end = connector.find("p:nvCxnSpPr/p:cNvCxnSpPr/a:endCxn", NS)
                if start is None or end is None:
                    errors.append("found a connector without attached start and end shapes")
            frames = picture_frames(root)
            image_count += len(frames)
            for _, _, cx, cy in frames:
                if cx >= width * 0.95 and cy >= height * 0.95:
                    full_slide_images += 1
            for shape in root.findall(".//p:sp", NS):
                name = shape_name(shape)
                if name == "main-title":
                    title_count += 1
                    paragraphs = shape.findall("p:txBody/a:p", NS)
                    if len(paragraphs) != 1 or shape.findall(".//a:br", NS):
                        errors.append("main-title contains a manual line or paragraph break")
                    props = run_properties(shape)
                    if not props or any(
                        prop.attrib.get("b") != "1"
                        or prop.attrib.get("sz") != "2400"
                        or property_color(prop) != "C7000B"
                        for prop in props
                    ):
                        errors.append("main-title must be bold 24 pt and #C7000B in every text run")
                if name == "source-footer":
                    source_footer_count += 1
                    frame = shape_frame(shape)
                    if frame is None:
                        errors.append("source-footer has no valid frame")
                    else:
                        x, y, _, cy = frame
                        if abs(x - 40 * EMU_PER_PX) > EMU_PER_PX // 2 or abs(y + cy - 680 * EMU_PER_PX) > EMU_PER_PX // 2:
                            errors.append("source-footer is not 30 pt from the left and bottom edges")
                    paragraphs = shape.findall("p:txBody/a:p", NS)
                    if len(paragraphs) != 1 or shape.findall(".//a:br", NS):
                        errors.append("source-footer must occupy one natural line")
                    props = run_properties(shape)
                    if not props or any(
                        prop.attrib.get("i") != "1"
                        or prop.attrib.get("sz") != "1000"
                        or property_color(prop) != "8C8C8C"
                        for prop in props
                    ):
                        errors.append("source-footer must be italic 10 pt and #8C8C8C")
                    ppr = shape.find("p:txBody/a:p/a:pPr", NS)
                    if ppr is None or ppr.attrib.get("algn") != "l":
                        errors.append("source-footer must be left aligned")
        if full_slide_images:
            errors.append(f"found {full_slide_images} near-full-slide image(s)")
        if title_count != 1:
            errors.append(f"expected one main-title, found {title_count}")
        if source_footer_count > 1:
            errors.append(f"expected at most one source-footer, found {source_footer_count}")

        chart_pattern = r"ppt/(?:slides/)?charts/chart\d+\.xml"
        charts = sorted(name for name in names if re.fullmatch(chart_pattern, name))
        inspected_xml = slides + charts
        for name in inspected_xml:
            root = xml_root(archive, name)
            for node in root.findall(".//*[@sz]"):
                try:
                    font_sizes.add(int(node.attrib["sz"]))
                except ValueError:
                    pass
            for node in root.findall(".//a:srgbClr", NS):
                value = node.attrib.get("val", "").upper()
                if value:
                    colors.add(value)

        for name in (item for item in names if item.startswith("ppt/") and item.endswith(".xml")):
            try:
                root = xml_root(archive, name)
            except ET.ParseError:
                continue
            for local_name in ("latin", "ea", "cs"):
                for node in root.findall(f".//a:{local_name}", NS):
                    value = node.attrib.get("typeface", "")
                    if value:
                        font_names.add(value)
            if name.startswith("ppt/theme/"):
                for node in root.findall(".//a:font", NS):
                    value = node.attrib.get("typeface", "")
                    if value:
                        font_names.add(value)
        bad_sizes = sorted(size for size in font_sizes if size not in ALLOWED_FONT_SIZES)
        if bad_sizes:
            errors.append(f"found disallowed explicit font sizes (hundredths of a point): {bad_sizes}")
        bad_colors = sorted(color for color in colors if color not in ALLOWED_COLORS)
        if bad_colors:
            errors.append(f"found disallowed explicit colors: {bad_colors}")
        bad_fonts = sorted(font for font in font_names if font != REQUIRED_FONT)
        if bad_fonts:
            errors.append(f"found non-{REQUIRED_FONT} typefaces: {bad_fonts}")
        if REQUIRED_FONT not in font_names:
            errors.append(f"no explicit {REQUIRED_FONT} typeface was found")

        notes = [name for name in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)]
        notes_text = ""
        for name in notes:
            root = xml_root(archive, name)
            notes_text += "\n".join(node.text or "" for node in root.findall(".//a:t", NS))
        if "[Sources]" not in notes_text:
            errors.append("speaker notes do not contain a [Sources] block")
        if "http://" not in notes_text and "https://" not in notes_text:
            errors.append("speaker notes contain no source URL")

        for chart_name in charts:
            chart_root = xml_root(archive, chart_name)
            has_values = bool(chart_root.findall(".//c:numLit", NS) or chart_root.findall(".//c:numRef", NS))
            if not has_values:
                errors.append(f"native chart {chart_name} contains no numeric data")
        if text_boxes == 0:
            errors.append("no native text boxes were detected")

    report = {
        "passed": not errors and (not args.strict or not warnings),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "slides": len(slides),
            "textBoxes": text_boxes,
            "images": image_count,
            "charts": len(charts),
            "connectors": connector_count,
            "fontSizesHundredthsPt": sorted(font_sizes),
            "fontNames": sorted(font_names),
            "explicitColors": sorted(colors),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
