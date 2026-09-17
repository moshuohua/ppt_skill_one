#!/usr/bin/env python3
"""Compare an i2p-666 master PNG with a re-rendered PPTX slide."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageStat


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("master", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--pixel-threshold", type=int, default=24)
    parser.add_argument("--max-mean-diff", type=float, default=5.0)
    parser.add_argument("--max-changed-ratio", type=float, default=0.05)
    args = parser.parse_args()

    master = Image.open(args.master).convert("RGB")
    candidate = Image.open(args.candidate).convert("RGB")
    resized = candidate.size != master.size
    if resized:
        candidate = candidate.resize(master.size, Image.Resampling.LANCZOS)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    diff = ImageChops.difference(master, candidate)
    stat = ImageStat.Stat(diff)
    mean_diff = sum(stat.mean) / 3.0
    gray = diff.convert("L")
    histogram = gray.histogram()
    total = master.size[0] * master.size[1]
    changed = sum(histogram[args.pixel_threshold + 1 :])
    changed_ratio = changed / total

    heatmap = ImageEnhance.Contrast(diff).enhance(4.0)
    heatmap.save(args.out_dir / "difference.png")
    Image.blend(master, candidate, 0.5).save(args.out_dir / "overlay.png")
    candidate.save(args.out_dir / "candidate-normalized.png")

    passed = mean_diff <= args.max_mean_diff and changed_ratio <= args.max_changed_ratio
    report = {
        "passed": passed,
        "masterSize": list(master.size),
        "candidateWasResized": resized,
        "meanAbsoluteDifference": round(mean_diff, 4),
        "pixelThreshold": args.pixel_threshold,
        "changedPixelRatio": round(changed_ratio, 6),
        "limits": {
            "maxMeanDifference": args.max_mean_diff,
            "maxChangedPixelRatio": args.max_changed_ratio,
        },
    }
    (args.out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
