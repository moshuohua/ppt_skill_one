#!/usr/bin/env python3
"""Set the delivered PPTX's explicit and theme fonts to Microsoft YaHei."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
import zipfile
from pathlib import Path


def patch_xml(data: bytes, font: str, is_theme: bool) -> tuple[bytes, int]:
    font_bytes = font.encode("utf-8")
    changed = 0
    pattern = re.compile(rb'(<(?:[A-Za-z_][\w.-]*:)?(?:latin|ea|cs)\b[^>]*\btypeface=")[^"]*(")')
    data, count = pattern.subn(lambda match: match.group(1) + font_bytes + match.group(2), data)
    changed += count
    if is_theme:
        theme_pattern = re.compile(rb'(<(?:[A-Za-z_][\w.-]*:)?font\b[^>]*\btypeface=")[^"]*(")')
        data, count = theme_pattern.subn(lambda match: match.group(1) + font_bytes + match.group(2), data)
        changed += count
    return data, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--font", default="Microsoft YaHei")
    args = parser.parse_args()

    pptx = args.pptx.resolve()
    if not pptx.is_file():
        parser.error(f"PPTX does not exist: {pptx}")

    fd, temp_name = tempfile.mkstemp(prefix=f".{pptx.stem}-font-", suffix=".pptx", dir=pptx.parent)
    os.close(fd)
    temp = Path(temp_name)
    changed_total = 0
    try:
        with zipfile.ZipFile(pptx, "r") as source, zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.startswith("ppt/") and item.filename.endswith(".xml"):
                    data, changed = patch_xml(data, args.font, item.filename.startswith("ppt/theme/"))
                    changed_total += changed
                target.writestr(item, data)
        os.replace(temp, pptx)
    finally:
        temp.unlink(missing_ok=True)

    print(f"font={args.font}; replacements={changed_total}; file={pptx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
