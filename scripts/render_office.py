#!/usr/bin/env python3
"""Render a PPTX through an Office-compatible engine for visual QA."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_executable(name: str, runtime_bin: Path | None) -> str:
    if runtime_bin:
        candidate = runtime_bin / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    resolved = shutil.which(name)
    if not resolved:
        raise FileNotFoundError(f"Required executable not found: {name}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=288, help="288 DPI yields 3840x2160 for a standard 16:9 slide")
    args = parser.parse_args()

    pptx = args.pptx.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    runtime_value = os.environ.get("RUNTIME_BIN_DIR")
    runtime_bin = Path(runtime_value) if runtime_value else None
    try:
        soffice = resolve_executable("soffice", runtime_bin)
        pdftoppm = resolve_executable("pdftoppm", runtime_bin)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 2

    work_dir = Path(tempfile.mkdtemp(prefix="i2p-office-render-", dir=args.out_dir))
    profile_dir = work_dir / "profile"
    cache_dir = work_dir / "cache"
    profile_dir.mkdir()
    cache_dir.mkdir()
    env = os.environ.copy()
    env["XDG_CACHE_HOME"] = str(cache_dir)
    profile_uri = profile_dir.resolve().as_uri()
    try:
        conversion = subprocess.run(
            [
                soffice,
                f"-env:UserInstallation={profile_uri}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(work_dir),
                str(pptx),
            ],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if conversion.returncode != 0:
            print(conversion.stdout)
            print(conversion.stderr, file=sys.stderr)
            return conversion.returncode or 1
        pdf = work_dir / f"{pptx.stem}.pdf"
        if not pdf.exists():
            print("ERROR: Office-compatible renderer produced no PDF")
            return 1
        raster = subprocess.run(
            [pdftoppm, "-png", "-r", str(args.dpi), str(pdf), str(args.out_dir / "slide")],
            text=True,
            capture_output=True,
            check=False,
        )
        if raster.returncode != 0:
            print(raster.stdout)
            print(raster.stderr, file=sys.stderr)
            return raster.returncode or 1
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    outputs = sorted(args.out_dir.glob("slide-*.png"))
    if not outputs:
        print("ERROR: no rendered slide PNG was produced")
        return 1
    for output in outputs:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
