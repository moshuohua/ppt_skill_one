#!/usr/bin/env python3
"""Check artifact-tool layout evidence for text fit, margins, and overlap."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ALLOWED_FONT_PX = (13.3333, 18.6667, 24.0, 32.0)
ALLOWED_COLORS = {"#C7000B", "#000000", "#8C8C8C", "#D53C44", "#F1B4B6", "#FFFFFF"}


def close_to_allowed(value: float) -> bool:
    return any(abs(value - allowed) <= 0.08 for allowed in ALLOWED_FONT_PX)


def rect_overlap(a: list[float], b: list[float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    width = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    height = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    return width * height


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("layout", type=Path)
    parser.add_argument("--margin", type=float, default=40.0)
    parser.add_argument("--expected-font", default="Microsoft YaHei")
    args = parser.parse_args()

    data = json.loads(args.layout.read_text(encoding="utf-8"))
    slide_frame = data.get("slide", {}).get("frame", {})
    slide_w = float(slide_frame.get("width", 1280))
    slide_h = float(slide_frame.get("height", 720))
    elements = data.get("elements", [])
    errors: list[str] = []
    warnings: list[str] = []
    text_elements: list[dict] = []

    for element in elements:
        name = element.get("name") or element.get("aid") or "unnamed"
        bbox = element.get("bbox")
        if isinstance(bbox, list) and len(bbox) == 4:
            x, y, w, h = map(float, bbox)
            if x < args.margin - 0.5 or y < args.margin - 0.5 or x + w > slide_w - args.margin + 0.5 or y + h > slide_h - args.margin + 0.5:
                errors.append(f"{name} crosses the {args.margin:g}px safe margin")
        if element.get("kind") != "shape" or not element.get("text"):
            continue
        text_elements.append(element)
        font_px = float(element.get("resolvedFontSize", 0) or 0)
        if not close_to_allowed(font_px):
            errors.append(f"{name} uses disallowed resolved font size {font_px:g}px")
        color = str(element.get("resolvedTextStyle", {}).get("color", "")).upper()
        if color and color not in ALLOWED_COLORS:
            errors.append(f"{name} uses disallowed resolved color {color}")
        typeface = str(element.get("resolvedTextStyle", {}).get("typeface", ""))
        if typeface != args.expected_font:
            errors.append(f"{name} uses typeface {typeface!r}; expected render font is {args.expected_font!r}")
        line_count = int(element.get("textLayout", {}).get("lineCount", 1) or 1)
        if name == "main-title":
            if line_count > 2:
                errors.append(f"main-title renders in {line_count} lines; maximum is 2")
            if "\n" in str(element.get("text", "")) or "\r" in str(element.get("text", "")):
                errors.append("main-title contains a manual line break")
            if element.get("resolvedTextStyle", {}).get("bold") is not True:
                errors.append("main-title is not bold")
        if name == "source-footer":
            if line_count != 1:
                errors.append(f"source-footer renders in {line_count} lines; it must stay on one line")
            if element.get("resolvedTextStyle", {}).get("italic") is not True:
                errors.append("source-footer is not italic")
            if isinstance(bbox, list) and len(bbox) == 4:
                x, y, _, h = map(float, bbox)
                if abs(x - 40) > 0.5 or abs(y + h - 680) > 0.5:
                    errors.append("source-footer is not 30 pt from the left and bottom edges")
        if isinstance(bbox, list) and len(bbox) == 4 and font_px > 0:
            line_spacing = 1.0
            paragraphs = element.get("paragraphs", [])
            if paragraphs:
                line_spacing = float(paragraphs[0].get("resolvedTextStyle", {}).get("lineSpacing", 1.0) or 1.0)
            insets = element.get("resolvedTextStyle", {}).get("insets", {})
            vertical_insets = float(insets.get("top", 0) or 0) + float(insets.get("bottom", 0) or 0)
            required = line_count * font_px * line_spacing * 1.03 + vertical_insets
            if float(bbox[3]) + 0.5 < required:
                errors.append(f"{name} needs about {required:.1f}px for {line_count} line(s), but its box is {float(bbox[3]):.1f}px high")

    for index, first in enumerate(text_elements):
        for second in text_elements[index + 1 :]:
            a = first.get("bbox")
            b = second.get("bbox")
            if not (isinstance(a, list) and isinstance(b, list) and len(a) == len(b) == 4):
                continue
            area = rect_overlap(list(map(float, a)), list(map(float, b)))
            if area > 1.0:
                first_name = first.get("name") or first.get("aid")
                second_name = second.get("name") or second.get("aid")
                errors.append(f"text boxes overlap: {first_name} and {second_name} ({area:.1f}px²)")

    report = {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {"elements": len(elements), "textElements": len(text_elements)},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
