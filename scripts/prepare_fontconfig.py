#!/usr/bin/env python3
"""Create an isolated fontconfig file for reliable i2p-666 CJK rendering."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


def system_match(family: str) -> str:
    result = subprocess.run(
        ["fc-match", "--format", "%{family}", family],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.split(",", 1)[0].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--delivery-font", default="Microsoft YaHei")
    parser.add_argument("--fallback-font", default="Noto Sans CJK SC")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    font_dir = skill_dir / "assets" / "fonts"
    required_files = [font_dir / "NotoSansCJKsc-Regular.otf", font_dir / "NotoSansCJKsc-Bold.otf"]
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        parser.error(f"missing bundled fallback font assets: {missing}")

    matched = system_match(args.delivery_font)
    fallback_active = matched.casefold() != args.delivery_font.casefold()
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cache_dir = out.parent / "font-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    alias = ""
    if fallback_active:
        alias = f"""
  <match target="pattern">
    <test name="family" qual="any"><string>{escape(args.delivery_font)}</string></test>
    <edit name="family" mode="prepend" binding="strong"><string>{escape(args.fallback_font)}</string></edit>
  </match>"""
    config = f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>{escape(str(font_dir))}</dir>
  <cachedir>{escape(str(cache_dir))}</cachedir>{alias}
</fontconfig>
"""
    out.write_text(config, encoding="utf-8")
    print(json.dumps({
        "fontconfig": str(out),
        "deliveryFont": args.delivery_font,
        "systemMatch": matched,
        "fallbackActive": fallback_active,
        "renderFontFallback": args.fallback_font if fallback_active else None,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
