#!/usr/bin/env python3
"""Measure visual properties of transparent PNG textures."""

from __future__ import annotations

import argparse
import colorsys
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment-specific guidance
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


def iter_png(paths: Iterable[Path], max_files: int) -> tuple[list[Path], int]:
    found: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".png":
            found.add(path.resolve())
        elif path.is_dir():
            found.update(p.resolve() for p in path.rglob("*.png"))
    ordered = sorted(found, key=lambda p: str(p).lower())
    return ordered[:max_files], len(ordered)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    return values[round((len(values) - 1) * fraction)]


def analyze(path: Path, sample_size: int) -> dict[str, object]:
    with Image.open(path) as source:
        image = source.convert("RGBA")
    width, height = image.size
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if max(width, height) > sample_size:
        scale = sample_size / max(width, height)
        sampled = image.resize(
            (max(1, round(width * scale)), max(1, round(height * scale))),
            Image.Resampling.BILINEAR,
        )
    else:
        sampled = image

    get_pixels = getattr(sampled, "get_flattened_data", sampled.getdata)
    pixels = list(get_pixels())
    visible = [(r, g, b, a) for r, g, b, a in pixels if a > 8]
    total = max(1, len(pixels))
    opaque = sum(1 for *_, a in pixels if a >= 250)
    partial = sum(1 for *_, a in pixels if 8 < a < 250)
    luminances: list[float] = []
    saturations: list[float] = []
    alpha_weights: list[float] = []
    bucketed: Counter[tuple[int, int, int]] = Counter()
    for r, g, b, a in visible:
        rn, gn, bn = r / 255.0, g / 255.0, b / 255.0
        luminances.append(0.2126 * rn + 0.7152 * gn + 0.0722 * bn)
        saturations.append(colorsys.rgb_to_hsv(rn, gn, bn)[1])
        alpha_weights.append(a / 255.0)
        bucketed[(r // 16 * 16, g // 16 * 16, b // 16 * 16)] += 1

    total_alpha = sum(alpha_weights)
    mean_luminance = (
        sum(value * weight for value, weight in zip(luminances, alpha_weights)) / total_alpha
        if total_alpha
        else 0.0
    )
    mean_saturation = (
        sum(value * weight for value, weight in zip(saturations, alpha_weights)) / total_alpha
        if total_alpha
        else 0.0
    )
    dark_fraction = (
        sum(weight for value, weight in zip(luminances, alpha_weights) if value < 0.18)
        / total_alpha
        if total_alpha
        else 0.0
    )

    if bbox:
        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        bbox_occupancy = bbox_area / (width * height)
        bbox_list: list[int] | None = list(bbox)
    else:
        bbox_occupancy = 0.0
        bbox_list = None

    return {
        "path": str(path),
        "blank": not visible,
        "width": width,
        "height": height,
        "bbox": bbox_list,
        "bbox_occupancy": round(bbox_occupancy, 4),
        "visible_fraction": round(len(visible) / total, 4),
        "opaque_fraction": round(opaque / total, 4),
        "partial_alpha_fraction": round(partial / total, 4),
        "luminance_p10": round(percentile(luminances, 0.10), 4),
        "luminance_median": round(percentile(luminances, 0.50), 4),
        "luminance_p90": round(percentile(luminances, 0.90), 4),
        "mean_luminance": round(mean_luminance, 4),
        "mean_saturation": round(mean_saturation, 4),
        "dark_pixel_fraction": round(dark_fraction, 4),
        "top_bucketed_colors": [
            {"rgb": list(color), "count": count} for color, count in bucketed.most_common(8)
        ],
    }


def summarize(files: list[Path], files_found: int, sample_size: int) -> dict[str, object]:
    reports: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    for path in files:
        try:
            reports.append(analyze(path, sample_size))
        except (OSError, ValueError) as exc:
            errors.append({"path": str(path), "error": str(exc)})

    nonblank = [report for report in reports if not report["blank"]]

    def med(key: str) -> float:
        values = [float(report[key]) for report in nonblank]
        return round(statistics.median(values), 4) if values else 0.0

    return {
        "files_found": files_found,
        "files_parsed": len(reports),
        "blank_files": len(reports) - len(nonblank),
        "errors": errors,
        "median_width": med("width"),
        "median_height": med("height"),
        "median_bbox_occupancy": med("bbox_occupancy"),
        "median_visible_fraction": med("visible_fraction"),
        "median_partial_alpha_fraction": med("partial_alpha_fraction"),
        "median_mean_luminance": med("mean_luminance"),
        "median_saturation": med("mean_saturation"),
        "median_dark_pixel_fraction": med("dark_pixel_fraction"),
        "textures": reports,
    }


def render_markdown(summary: dict[str, object], include_files: bool) -> str:
    lines = [
        "# Texture audit",
        "",
        f"- Files: {summary['files_parsed']} parsed / {summary['files_found']} found",
        f"- Blank/effectively transparent files (alpha <= 8): {summary['blank_files']}",
        f"- Median dimensions: {summary['median_width']} x {summary['median_height']}",
        f"- Median alpha-bbox occupancy: {summary['median_bbox_occupancy']}",
        f"- Median visible-pixel fraction: {summary['median_visible_fraction']}",
        f"- Median partial-alpha fraction: {summary['median_partial_alpha_fraction']}",
        f"- Median alpha-weighted mean luminance: {summary['median_mean_luminance']}",
        f"- Median alpha-weighted saturation: {summary['median_saturation']}",
        f"- Median dark-pixel fraction: {summary['median_dark_pixel_fraction']}",
    ]
    if include_files:
        lines.extend(["", "## Files", ""])
        for item in summary["textures"]:
            lines.append(
                f"- `{item['path']}`: {item['width']}x{item['height']}, "
                f"bbox={item['bbox_occupancy']}, visible={item['visible_fraction']}, "
                f"partial-alpha={item['partial_alpha_fraction']}, dark={item['dark_pixel_fraction']}"
            )
    if summary["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- `{item['path']}`: {item['error']}" for item in summary["errors"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="PNG files or directories")
    parser.add_argument("--max-files", type=int, default=500, help="maximum files to inspect")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=256,
        help="maximum dimension used for color statistics",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="omit per-file rows from Markdown output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_files < 1 or args.sample_size < 1:
        print("--max-files and --sample-size must be positive", file=sys.stderr)
        return 2
    files, files_found = iter_png(args.paths, args.max_files)
    if not files:
        print("No PNG files found.", file=sys.stderr)
        return 2
    summary = summarize(files, files_found, args.sample_size)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary, include_files=not args.summary_only), end="")
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
