#!/usr/bin/env python3
"""Validate an i2p-666 one-slide JSON specification."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_COLORS = {"#C7000B", "#000000", "#8C8C8C", "#D53C44", "#F1B4B6", "#FFFFFF"}
ALLOWED_FONT_PT = {10, 14, 18, 24}
ALLOWED_TYPES = {"text", "shape", "line", "connector", "image", "chart", "table"}
REQUIRED_FONT = "Microsoft YaHei"
RELATIONSHIP_TYPES = {
    "comparison", "trend", "causal", "architecture", "combination", "hierarchy",
    "sequence", "control-point-shift", "evidence-chain", "matrix",
}
LAYOUT_FAMILIES = {
    "chart-dominant", "control-point-migration", "causal-chain", "architecture-stack",
    "comparison-matrix", "evidence-to-action", "central-thesis", "sequence-timeline",
}
INDEPENDENT_TYPES = {"media", "blog", "analysis"}
PRIMARY_TYPES = {"official", "paper", "dataset", "filing", "research"}
SOURCE_TYPES = PRIMARY_TYPES | {"consulting"} | INDEPENDENT_TYPES


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("Top-level JSON value must be an object")
    return value


def parse_date(value: object, label: str, errors: list[str]) -> dt.date | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be YYYY-MM-DD")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be YYYY-MM-DD")
        return None


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def visual_units(text: str) -> float:
    units = 0.0
    for char in text:
        if char == "\n":
            continue
        units += 1.0 if unicodedata.east_asian_width(char) in {"W", "F"} else 0.52
    return units


def element_text(element: dict) -> str:
    if element.get("text") is not None:
        return str(element.get("text", ""))
    paragraphs = element.get("paragraphs")
    if not isinstance(paragraphs, list):
        return ""
    pieces: list[str] = []
    for paragraph in paragraphs:
        if not isinstance(paragraph, dict):
            continue
        if paragraph.get("text") is not None:
            pieces.append(str(paragraph.get("text", "")))
            continue
        runs = paragraph.get("runs")
        if isinstance(runs, list):
            run_text: list[str] = []
            for run in runs:
                if isinstance(run, str):
                    run_text.append(run)
                elif isinstance(run, dict):
                    run_text.append(str(run.get("text", "")))
            pieces.append("".join(run_text))
    return "\n".join(pieces)


def count_body_chars(elements: list[dict]) -> int:
    roles = {"subhead", "body", "highlight", "annotation"}
    text = "".join(
        element_text(e)
        for e in elements
        if (e.get("type") == "text" and e.get("role") in roles)
        or (e.get("type") == "shape" and e.get("text") is not None)
    )
    return len(re.sub(r"\s+", "", text))


def colors_in(value: object, trail: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            next_trail = f"{trail}.{key}" if trail else key
            if key.lower() in {"color", "fill", "background"} and isinstance(child, str) and child.startswith("#"):
                found.append((next_trail, child.upper()))
            found.extend(colors_in(child, next_trail))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(colors_in(child, f"{trail}[{index}]"))
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--today", help="Override today's date for deterministic tests")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    try:
        spec = load_json(args.spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    meta = spec.get("meta") if isinstance(spec.get("meta"), dict) else {}
    slide = spec.get("slide") if isinstance(spec.get("slide"), dict) else {}
    sources = spec.get("sources") if isinstance(spec.get("sources"), list) else []
    elements = spec.get("elements") if isinstance(spec.get("elements"), list) else []

    if spec.get("version") != "1.1":
        errors.append("version must be '1.1'")
    if slide.get("width") != 1280 or slide.get("height") != 720:
        errors.append("slide must be 1280x720")
    if slide.get("margin") != 40:
        errors.append("slide.margin must be 40 px (30 pt)")
    if str(slide.get("background", "")).upper() != "#FFFFFF":
        errors.append("slide background must be #FFFFFF")

    claim = str(meta.get("coreClaim", "")).strip()
    if not claim:
        errors.append("meta.coreClaim is required")
    supporting = meta.get("supportingClaims", [])
    if not isinstance(supporting, list) or not 1 <= len(supporting) <= 3:
        errors.append("meta.supportingClaims must contain 1 to 3 items")
    elif any(not str(item).strip() for item in supporting):
        errors.append("supporting claims cannot be blank")

    try:
        content_top = float(meta.get("contentTop"))
        if not 120 <= content_top <= 180:
            errors.append("meta.contentTop must be between 120 and 180 px")
    except (TypeError, ValueError):
        content_top = 0.0
        errors.append("meta.contentTop is required and must be numeric")

    insight = meta.get("insightChain") if isinstance(meta.get("insightChain"), dict) else {}
    for key in ("fact", "mechanism", "strategicIntent", "controlPointShift", "companyAction", "alternativeExplanation"):
        if not str(insight.get(key, "")).strip():
            errors.append(f"meta.insightChain.{key} is required")
    signals = insight.get("observableSignals", [])
    if not isinstance(signals, list) or not 1 <= len(signals) <= 3 or any(not str(item).strip() for item in signals):
        errors.append("meta.insightChain.observableSignals must contain 1 to 3 non-blank signals")

    visual_strategy = meta.get("visualStrategy") if isinstance(meta.get("visualStrategy"), dict) else {}
    if visual_strategy.get("relationshipType") not in RELATIONSHIP_TYPES:
        errors.append("meta.visualStrategy.relationshipType is invalid")
    if visual_strategy.get("layoutFamily") not in LAYOUT_FAMILIES:
        errors.append("meta.visualStrategy.layoutFamily is invalid")
    if not str(visual_strategy.get("message", "")).strip():
        errors.append("meta.visualStrategy.message is required")
    visual_ids = visual_strategy.get("elementIds", [])
    if not isinstance(visual_ids, list) or not visual_ids or any(not str(item).strip() for item in visual_ids):
        errors.append("meta.visualStrategy.elementIds must contain at least one element id")
        visual_ids = []

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    as_of = parse_date(meta.get("asOfDate"), "meta.asOfDate", errors)
    if as_of and abs((today - as_of).days) > 7:
        errors.append(f"meta.asOfDate {as_of} is not within 7 days of {today}")

    if not 2 <= len(sources) <= 6:
        errors.append("sources must contain 2 to 6 verified items")
    source_ids: set[str] = set()
    source_types: set[str] = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        source_id = str(source.get("id", "")).strip()
        if not source_id or source_id in source_ids:
            errors.append(f"{label}.id is missing or duplicated")
        source_ids.add(source_id)
        source_type = str(source.get("type", "")).strip()
        if source_type not in SOURCE_TYPES:
            errors.append(f"{label}.type is invalid")
        source_types.add(source_type)
        for key in ("institution", "title"):
            if not str(source.get(key, "")).strip():
                errors.append(f"{label}.{key} is required")
        parse_date(source.get("publishedDate"), f"{label}.publishedDate", errors)
        accessed = parse_date(source.get("accessedDate"), f"{label}.accessedDate", errors)
        if as_of and accessed and accessed != as_of:
            warnings.append(f"{label}.accessedDate differs from meta.asOfDate")
        if not valid_url(source.get("url")):
            errors.append(f"{label}.url must be an http(s) URL")
        if not isinstance(source.get("supports"), list) or not source.get("supports"):
            errors.append(f"{label}.supports must name at least one claim or element")
    if sources and not (source_types & PRIMARY_TYPES):
        errors.append("at least one primary source is required")
    if sources and not (source_types & INDEPENDENT_TYPES):
        errors.append("at least one independent AI media, blog, or analysis source is required")

    ids: set[str] = set()
    title_elements: list[dict] = []
    source_elements = 0
    subhead_elements = 0
    chart_count = 0
    table_count = 0
    font_families: set[str] = set()
    for index, element in enumerate(elements):
        label = f"elements[{index}]"
        if not isinstance(element, dict):
            errors.append(f"{label} must be an object")
            continue
        element_id = str(element.get("id", "")).strip()
        if not element_id or element_id in ids:
            errors.append(f"{label}.id is missing or duplicated")
        ids.add(element_id)
        if not str(element.get("name", "")).strip():
            errors.append(f"{label}.name is required")
        element_type = element.get("type")
        if element_type not in ALLOWED_TYPES:
            errors.append(f"{label}.type is invalid")
            continue
        if element_type == "chart":
            chart_count += 1
        if element_type == "table":
            table_count += 1
        if element_type != "connector":
            frame = element.get("frame")
            if not isinstance(frame, dict) or any(key not in frame for key in ("x", "y", "w", "h")):
                errors.append(f"{label}.frame must contain x, y, w, h")
            else:
                try:
                    x, y, w, h = (float(frame[key]) for key in ("x", "y", "w", "h"))
                    if w <= 0 or h <= 0:
                        errors.append(f"{label}.frame dimensions must be positive")
                    if x < 40 or y < 40 or x + w > 1240 or y + h > 680:
                        errors.append(f"{label} crosses the 40 px safe margin")
                except (TypeError, ValueError):
                    errors.append(f"{label}.frame values must be numeric")
        if element_type == "text":
            role = element.get("role")
            style = element.get("style") if isinstance(element.get("style"), dict) else {}
            font_pt = style.get("fontPt")
            color = str(style.get("color", "")).upper()
            family = str(style.get("fontFamily", "")).strip()
            if family != REQUIRED_FONT:
                errors.append(f"{label} must use style.fontFamily '{REQUIRED_FONT}'")
            if family:
                font_families.add(family)
            if font_pt not in ALLOWED_FONT_PT:
                errors.append(f"{label} uses disallowed font size {font_pt}")
            if role == "title":
                title_elements.append(element)
                if font_pt != 24 or color != "#C7000B" or style.get("bold") is not True:
                    errors.append("title must be bold 24 pt and #C7000B")
            elif role == "subhead":
                subhead_elements += 1
                if font_pt != 18 or color != "#C7000B":
                    errors.append(f"{label} subhead must be 18 pt and #C7000B")
            elif role == "source":
                source_elements += 1
                frame = element.get("frame") if isinstance(element.get("frame"), dict) else {}
                if element.get("name") != "source-footer":
                    errors.append(f"{label} visible source must be named source-footer")
                if font_pt != 10 or color != "#8C8C8C" or style.get("italic") is not True:
                    errors.append(f"{label} source footer must be 10 pt italic and #8C8C8C")
                if style.get("align", "left") != "left":
                    errors.append(f"{label} source footer must be left aligned")
                try:
                    if abs(float(frame.get("x")) - 40) > 0.5 or abs(float(frame.get("y")) + float(frame.get("h")) - 680) > 0.5:
                        errors.append(f"{label} source footer must be 30 pt from the left and bottom edges")
                except (TypeError, ValueError):
                    errors.append(f"{label} source footer frame is invalid")
            elif role in {"chart-label", "annotation"} and font_pt != 10:
                errors.append(f"{label} {role} must be 10 pt")
            elif role == "diagram-label" and font_pt not in {10, 14}:
                errors.append(f"{label} diagram-label must be 10 or 14 pt")
            elif role in {"body", "highlight"} and font_pt != 14:
                errors.append(f"{label} {role} must be 14 pt")
            text = element_text(element)
            bullet_count = len(re.findall(r"(?m)^\s*[•·\-]\s+", text))
            paragraphs = element.get("paragraphs")
            if isinstance(paragraphs, list):
                bullet_count += sum(1 for paragraph in paragraphs if isinstance(paragraph, dict) and paragraph.get("bullet"))
                for paragraph_index, paragraph in enumerate(paragraphs):
                    runs = paragraph.get("runs", []) if isinstance(paragraph, dict) else []
                    if not isinstance(runs, list):
                        errors.append(f"{label}.paragraphs[{paragraph_index}].runs must be a list")
                        continue
                    for run_index, run in enumerate(runs):
                        if not isinstance(run, dict):
                            continue
                        run_style = run.get("style", {}) if isinstance(run.get("style"), dict) else {}
                        run_font = run_style.get("fontPt", font_pt)
                        if run_font not in ALLOWED_FONT_PT:
                            errors.append(f"{label}.paragraphs[{paragraph_index}].runs[{run_index}] uses a disallowed font size")
                        run_family = str(run_style.get("fontFamily", family)).strip()
                        if run_family != REQUIRED_FONT:
                            errors.append(f"{label}.paragraphs[{paragraph_index}].runs[{run_index}] must use {REQUIRED_FONT}")
            if bullet_count > 3:
                errors.append(f"{label} contains more than 3 list items")
            frame = element.get("frame")
            if isinstance(frame, dict) and font_pt in ALLOWED_FONT_PT:
                frame_width = float(frame.get("w", 0) or 0)
                frame_height = float(frame.get("h", 0) or 0)
                font_px = float(font_pt) * 96.0 / 72.0
                capacity = max(frame_width / font_px * 1.05, 1)
                estimated_lines = max(text.count("\n") + 1, math.ceil(visual_units(text) / capacity))
                line_spacing = float(style.get("lineSpacing", 1.0) or 1.0)
                required_height = estimated_lines * font_px * line_spacing * 1.05
                if frame_height + 0.5 < required_height:
                    errors.append(
                        f"{label} text is estimated to need {required_height:.1f}px height "
                        f"for {estimated_lines} line(s), but frame.h is {frame_height:.1f}px"
                    )
        elif element_type == "shape" and element.get("text") is not None:
            style = element.get("style") if isinstance(element.get("style"), dict) else {}
            font_pt = style.get("fontPt")
            family = str(style.get("fontFamily", "")).strip()
            if family != REQUIRED_FONT:
                errors.append(f"{label} shape text must use style.fontFamily '{REQUIRED_FONT}'")
            if family:
                font_families.add(family)
            if font_pt not in ALLOWED_FONT_PT:
                errors.append(f"{label} shape text uses disallowed font size {font_pt}")
            frame = element.get("frame")
            if isinstance(frame, dict) and font_pt in ALLOWED_FONT_PT:
                text = str(element.get("text", ""))
                font_px = float(font_pt) * 96.0 / 72.0
                capacity = max(float(frame.get("w", 0) or 0) / font_px * 1.05, 1)
                estimated_lines = max(text.count("\n") + 1, math.ceil(visual_units(text) / capacity))
                required_height = estimated_lines * font_px * float(style.get("lineSpacing", 1.0) or 1.0) * 1.05
                if float(frame.get("h", 0) or 0) + 0.5 < required_height:
                    errors.append(f"{label} shape text is estimated to overflow its frame")
        refs = element.get("sourceIds", [])
        if refs and (not isinstance(refs, list) or any(ref not in source_ids for ref in refs)):
            errors.append(f"{label}.sourceIds contains an unknown source")
        if element_type == "chart" and not refs:
            errors.append(f"{label} chart requires sourceIds")
        if element_type == "table" and not refs:
            errors.append(f"{label} table requires sourceIds")
        if element_type == "chart":
            options = element.get("options", {}) if isinstance(element.get("options"), dict) else {}
            if str(options.get("fontFamily", "")).strip() != REQUIRED_FONT:
                errors.append(f"{label} chart options.fontFamily must be '{REQUIRED_FONT}'")
            categories = element.get("categories", [])
            series = element.get("series", [])
            chart_type = element.get("chartType")
            if chart_type != "scatter" and (not isinstance(categories, list) or not categories):
                errors.append(f"{label} chart requires categories")
            if not isinstance(series, list) or not series:
                errors.append(f"{label} chart requires at least one series")
            elif isinstance(categories, list):
                for series_index, series_item in enumerate(series):
                    values = series_item.get("values", []) if isinstance(series_item, dict) else []
                    if chart_type == "scatter":
                        x_values = series_item.get("xValues", []) if isinstance(series_item, dict) else []
                        if not isinstance(values, list) or not values or not isinstance(x_values, list) or len(values) != len(x_values):
                            errors.append(f"{label}.series[{series_index}] scatter xValues and values must have equal non-zero length")
                    elif not isinstance(values, list) or len(values) != len(categories):
                        errors.append(f"{label}.series[{series_index}] values must match category count")
        if element_type == "table":
            if str(element.get("fontFamily", "")).strip() != REQUIRED_FONT:
                errors.append(f"{label} table fontFamily must be '{REQUIRED_FONT}'")
            values = element.get("values", [])
            if not isinstance(values, list) or not values or not all(isinstance(row, list) and row for row in values):
                errors.append(f"{label} table requires a non-empty rectangular values matrix")
            elif len({len(row) for row in values}) != 1:
                errors.append(f"{label} table rows must have equal column counts")
            if element.get("fontPt", 10) not in ALLOWED_FONT_PT:
                errors.append(f"{label} table uses a disallowed font size")
        if element_type == "image":
            image_path = element.get("path")
            if not isinstance(image_path, str) or not (args.spec.parent / image_path).exists():
                errors.append(f"{label}.path does not exist relative to the spec")

    for index, element in enumerate(elements):
        if isinstance(element, dict) and element.get("type") == "connector":
            if element.get("fromId") not in ids or element.get("toId") not in ids:
                errors.append(f"elements[{index}] connector endpoints are missing")

    missing_visual_ids = [element_id for element_id in visual_ids if element_id not in ids]
    if missing_visual_ids:
        errors.append(f"meta.visualStrategy.elementIds contains unknown ids: {missing_visual_ids}")
    visual_non_text = [
        element for element in elements
        if isinstance(element, dict)
        and element.get("id") in visual_ids
        and element.get("type") in {"shape", "line", "connector", "chart", "table"}
    ]
    if visual_ids and not visual_non_text:
        errors.append("the core semantic visual must contain at least one non-text element")

    if len(title_elements) != 1:
        errors.append("exactly one title text element is required")
    else:
        title = title_elements[0]
        text = element_text(title)
        if "\n" in text or "\r" in text:
            errors.append("title must not contain a manual line break")
        explicit_lines = 1
        frame_width = float(title.get("frame", {}).get("w", 0) or 0)
        capacity = max(frame_width / 32.0 * 1.05, 1)
        estimated_lines = max(explicit_lines, math.ceil(visual_units(text) / capacity))
        if estimated_lines > 2:
            errors.append(f"title is estimated to occupy {estimated_lines} lines at 24 pt")
        title_units = visual_units(text)
        if title_units < 50 or title_units > 70:
            warnings.append(f"title has {title_units:.1f} visual units; preferred range is 50–70")
        frame = title.get("frame", {}) if isinstance(title.get("frame"), dict) else {}
        try:
            if abs(float(frame.get("x")) - 40) > 0.5 or abs(float(frame.get("y")) - 40) > 0.5:
                errors.append("title frame must start at the 40 px top-left safe margin")
            if abs(float(frame.get("w")) - 1200) > 0.5 or abs(float(frame.get("h")) - (content_top - 40)) > 0.5:
                errors.append("title frame must extend from y=40 to meta.contentTop across the 1200 px content width")
        except (TypeError, ValueError):
            errors.append("title frame is invalid")
        if str(meta.get("title", "")).strip() != text.strip():
            warnings.append("meta.title differs from the title element")
    if source_elements > 1:
        errors.append("at most one visible source footer is allowed")

    for index, element in enumerate(elements):
        if not isinstance(element, dict) or element.get("type") != "text" or element.get("role") == "title":
            continue
        frame = element.get("frame") if isinstance(element.get("frame"), dict) else {}
        try:
            if float(frame.get("y")) < content_top - 0.5:
                errors.append(f"elements[{index}] places non-title text inside the title region")
        except (TypeError, ValueError):
            pass
    if subhead_elements > 3:
        errors.append(f"found {subhead_elements} subheads; maximum is 3")
    if len(font_families) > 1:
        errors.append(f"multiple font families are used: {sorted(font_families)}")
    body_chars = count_body_chars(elements)
    if body_chars > 220:
        errors.append(f"visible body copy is {body_chars} characters; maximum is 220")
    elif body_chars < 140:
        warnings.append(f"visible body copy is {body_chars} characters; recommended range is 140–200 unless the visual carries the evidence")
    elif body_chars > 200:
        warnings.append(f"visible body copy is {body_chars} characters; recommended range is 140–200")
    if bool(meta.get("dataHeavy")) and chart_count + table_count == 0:
        errors.append("meta.dataHeavy is true but no chart or table exists")

    for trail, color in colors_in(spec):
        if color not in ALLOWED_COLORS:
            errors.append(f"{trail} uses disallowed color {color}")

    report = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "elements": len(elements),
            "sources": len(sources),
            "bodyCharacters": body_chars,
            "charts": chart_count,
            "tables": table_count,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
