#!/usr/bin/env python3
"""Summarize and audit Spriter SCML files used by Don't Starve Together."""

from __future__ import annotations

import argparse
import json
import statistics
import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable


@dataclass
class FileReport:
    path: str
    entities: int = 0
    animations: int = 0
    image_files: int = 0
    missing_images: int = 0
    dimension_mismatches: int = 0
    mainline_keys: int = 0
    timeline_keys: int = 0
    object_refs: int = 0
    bone_refs: int = 0
    instant_keys: int = 0
    non_instant_keys: int = 0
    transformed_objects: int = 0
    negative_scale_objects: int = 0
    alpha_objects: int = 0
    broken_references: int = 0
    off_grid_keys: int = 0
    schema_mismatches: int = 0
    unsafe_image_paths: int = 0
    invalid_image_dimensions: int = 0
    invalid_or_duplicate_ids: int = 0
    invalid_animation_timing: int = 0
    unkeyed_mainline_slots: int = 0
    mismatched_ref_times: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def complexity(self) -> int:
        return self.timeline_keys + self.object_refs + self.bone_refs * 2


def iter_scml(paths: Iterable[Path]) -> list[Path]:
    found: set[Path] = set()
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".scml":
            found.add(path.resolve())
        elif path.is_dir():
            found.update(p.resolve() for p in path.rglob("*.scml"))
    return sorted(found, key=lambda p: str(p).lower())


def read_png_size(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def as_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def count_invalid_or_duplicate_ids(elements: Iterable[ET.Element]) -> int:
    seen: set[str] = set()
    invalid = 0
    for element in elements:
        element_id = element.get("id")
        if not element_id or element_id in seen:
            invalid += 1
        else:
            seen.add(element_id)
    return invalid


def is_unsafe_image_path(name: str) -> bool:
    if not name or chr(92) in name:
        return True
    posix_path = PurePosixPath(name)
    windows_path = PureWindowsPath(name)
    return posix_path.is_absolute() or windows_path.is_absolute() or ".." in posix_path.parts


def analyze_file(path: Path, check_images: bool) -> tuple[FileReport, dict[str, object]]:
    report = FileReport(path=str(path))
    root = ET.parse(path).getroot()
    if root.tag != "spriter_data" or root.get("scml_version") != "1.0":
        report.schema_mismatches += 1
    report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(root.findall("folder"))
    report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(root.findall("entity"))
    report.entities = len(root.findall("entity"))

    image_map: dict[tuple[str, str], ET.Element] = {}
    pivots_outside = 0
    for folder in root.findall("folder"):
        folder_id = folder.get("id", "")
        images = folder.findall("file")
        report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(images)
        for image in images:
            report.image_files += 1
            image_map[(folder_id, image.get("id", ""))] = image
            image_name = image.get("name", "")
            unsafe_image_path = is_unsafe_image_path(image_name)
            if unsafe_image_path:
                report.unsafe_image_paths += 1
            declared = (
                int(as_float(image.get("width"), -1)),
                int(as_float(image.get("height"), -1)),
            )
            if declared[0] <= 0 or declared[1] <= 0:
                report.invalid_image_dimensions += 1
            px = as_float(image.get("pivot_x"), 0.0)
            py = as_float(image.get("pivot_y"), 1.0)
            if not (0.0 <= px <= 1.0 and 0.0 <= py <= 1.0):
                pivots_outside += 1
            if check_images and not unsafe_image_path:
                image_path = path.parent / Path(image_name)
                actual = read_png_size(image_path)
                if actual is None:
                    report.missing_images += 1
                    report.warnings.append(f"{image_name}: missing or invalid PNG")
                else:
                    if actual != declared:
                        report.dimension_mismatches += 1
                        report.warnings.append(
                            f"{image_name}: declared {declared[0]}x{declared[1]}, "
                            f"actual {actual[0]}x{actual[1]}"
                        )

    animation_names: list[str] = []
    intervals: list[int] = []
    lengths: list[int] = []
    loop_values: Counter[str] = Counter()
    curve_types: Counter[str] = Counter()

    for entity in root.findall("entity"):
        report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(
            entity.findall("animation")
        )

    for animation in root.findall("entity/animation"):
        report.animations += 1
        animation_names.append(animation.get("name", ""))
        length = int(as_float(animation.get("length"), 0))
        interval = int(as_float(animation.get("interval"), 0))
        lengths.append(length)
        intervals.append(interval)
        loop_values[animation.get("looping", "implicit")] += 1
        if interval <= 0 or length < 0:
            report.invalid_animation_timing += 1
        if interval <= 0:
            report.warnings.append(f"{animation.get('name', '<unnamed>')}: interval <= 0")
        elif length % interval not in (0, 1, interval - 1):
            report.warnings.append(
                f"{animation.get('name', '<unnamed>')}: length {length} is off the {interval} ms grid"
            )

        timeline_elements = animation.findall("timeline")
        report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(timeline_elements)
        timelines = {timeline.get("id", ""): timeline for timeline in timeline_elements}
        timeline_keys: dict[str, dict[str, int]] = {}
        for timeline_id, timeline in timelines.items():
            keys = timeline.findall("key")
            report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(keys)
            timeline_keys[timeline_id] = {
                key.get("id", ""): int(as_float(key.get("time"), 0)) for key in keys
            }
        mainline_keys = animation.findall("mainline/key")
        report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(mainline_keys)
        report.mainline_keys += len(mainline_keys)
        mainline_times: set[int] = set()
        for key in mainline_keys:
            key_time = int(as_float(key.get("time"), 0))
            mainline_times.add(key_time)
            if key_time > length:
                report.broken_references += 1
            if interval > 0 and key_time % interval != 0:
                report.off_grid_keys += 1
            object_refs = key.findall("object_ref")
            bone_refs = key.findall("bone_ref")
            refs = [*object_refs, *bone_refs]
            report.invalid_or_duplicate_ids += count_invalid_or_duplicate_ids(refs)
            report.object_refs += len(object_refs)
            report.bone_refs += len(bone_refs)
            for ref in refs:
                timeline_id = ref.get("timeline", "")
                key_id = ref.get("key", "")
                if timeline_id not in timeline_keys or key_id not in timeline_keys[timeline_id]:
                    report.broken_references += 1
                elif timeline_keys[timeline_id][key_id] != key_time:
                    report.mismatched_ref_times += 1

        if interval > 0 and length >= 0:
            expected_times = set(range(0, length + 1, interval))
            report.unkeyed_mainline_slots += len(expected_times - mainline_times)

        for key in animation.findall("timeline/key"):
            report.timeline_keys += 1
            key_time = int(as_float(key.get("time"), 0))
            if key_time > length:
                report.broken_references += 1
            if interval > 0 and key_time % interval != 0:
                report.off_grid_keys += 1
            curve = key.get("curve_type", "linear")
            curve_types[curve] += 1
            if curve == "instant":
                report.instant_keys += 1
            else:
                report.non_instant_keys += 1
            obj = key.find("object")
            if obj is None:
                report.schema_mismatches += 1
                continue
            if (obj.get("folder", ""), obj.get("file", "")) not in image_map:
                report.broken_references += 1
            sx = as_float(obj.get("scale_x"), 1.0)
            sy = as_float(obj.get("scale_y"), 1.0)
            angle = as_float(obj.get("angle"), 0.0)
            alpha = as_float(obj.get("a"), 1.0)
            if sx < 0 or sy < 0:
                report.negative_scale_objects += 1
            if alpha != 1.0:
                report.alpha_objects += 1
            if sx != 1.0 or sy != 1.0 or angle != 0.0:
                report.transformed_objects += 1

    if report.missing_images:
        report.warnings.append(f"{report.missing_images} referenced PNG files are missing or invalid")
    if report.dimension_mismatches:
        report.warnings.append(f"{report.dimension_mismatches} PNG dimensions differ from SCML declarations")
    if report.broken_references:
        report.warnings.append(f"{report.broken_references} SCML references are broken")
    if report.off_grid_keys:
        report.warnings.append(f"{report.off_grid_keys} keys are off the animation interval grid")
    for field_name, label in (
        ("schema_mismatches", "schema mismatches"),
        ("unsafe_image_paths", "unsafe PNG paths"),
        ("invalid_image_dimensions", "invalid PNG dimension declarations"),
        ("invalid_or_duplicate_ids", "missing or duplicate IDs"),
        ("invalid_animation_timing", "invalid animation timing declarations"),
        ("mismatched_ref_times", "object references with mismatched times"),
        ("non_instant_keys", "non-instant timeline keys"),
    ):
        count = getattr(report, field_name)
        if count:
            report.warnings.append(f"{count} {label}")

    details: dict[str, object] = {
        "generator": root.get("generator", "unknown"),
        "generator_version": root.get("generator_version", "unknown"),
        "animation_names": animation_names,
        "intervals": intervals,
        "lengths": lengths,
        "loop_values": loop_values,
        "curve_types": curve_types,
        "pivots_outside": pivots_outside,
    }
    return report, details


def median(values: list[int]) -> float:
    return statistics.median(values) if values else 0.0


def summarize(files: list[Path], check_images: bool) -> dict[str, object]:
    reports: list[FileReport] = []
    errors: list[dict[str, str]] = []
    animation_names: Counter[str] = Counter()
    intervals: Counter[int] = Counter()
    lengths: list[int] = []
    generators: Counter[str] = Counter()
    loop_values: Counter[str] = Counter()
    curve_types: Counter[str] = Counter()
    pivots_outside = 0

    for path in files:
        try:
            report, details = analyze_file(path, check_images)
        except (ET.ParseError, OSError, ValueError) as exc:
            errors.append({"path": str(path), "error": str(exc)})
            continue
        reports.append(report)
        animation_names.update(details["animation_names"])
        intervals.update(details["intervals"])
        lengths.extend(details["lengths"])
        generators[f"{details['generator']} {details['generator_version']}"] += 1
        loop_values.update(details["loop_values"])
        curve_types.update(details["curve_types"])
        pivots_outside += int(details["pivots_outside"])

    totals = {
        key: sum(getattr(report, key) for report in reports)
        for key in (
            "entities",
            "animations",
            "image_files",
            "missing_images",
            "dimension_mismatches",
            "mainline_keys",
            "timeline_keys",
            "object_refs",
            "bone_refs",
            "instant_keys",
            "non_instant_keys",
            "transformed_objects",
            "negative_scale_objects",
            "alpha_objects",
            "broken_references",
            "off_grid_keys",
            "schema_mismatches",
            "unsafe_image_paths",
            "invalid_image_dimensions",
            "invalid_or_duplicate_ids",
            "invalid_animation_timing",
            "unkeyed_mainline_slots",
            "mismatched_ref_times",
        )
    }
    totals["pivots_outside"] = pivots_outside
    totals["validation_issues"] = sum(
        totals[key]
        for key in (
            "missing_images",
            "dimension_mismatches",
            "broken_references",
            "off_grid_keys",
            "schema_mismatches",
            "unsafe_image_paths",
            "invalid_image_dimensions",
            "invalid_or_duplicate_ids",
            "invalid_animation_timing",
            "mismatched_ref_times",
            "non_instant_keys",
        )
    )
    return {
        "image_checks": check_images,
        "files_found": len(files),
        "files_parsed": len(reports),
        "parse_errors": errors,
        "totals": totals,
        "median_animation_length_ms": median(lengths),
        "top_intervals_ms": intervals.most_common(12),
        "top_animation_names": animation_names.most_common(30),
        "generators": generators.most_common(),
        "looping_values": loop_values.most_common(),
        "curve_types": curve_types.most_common(),
        "most_complex": [
            asdict(report)
            for report in sorted(reports, key=lambda item: item.complexity, reverse=True)[:10]
        ],
        "files_with_warnings": [asdict(report) for report in reports if report.warnings][:50],
    }


def render_markdown(summary: dict[str, object]) -> str:
    totals = summary["totals"]
    assert isinstance(totals, dict)
    lines = [
        "# SCML audit",
        "",
        f"- Files: {summary['files_parsed']} parsed / {summary['files_found']} found",
        f"- Entities: {totals['entities']}",
        f"- Animations: {totals['animations']}",
        f"- Declared PNGs: {totals['image_files']}",
        f"- Mainline/timeline keys: {totals['mainline_keys']} / {totals['timeline_keys']}",
        f"- Object/bone refs: {totals['object_refs']} / {totals['bone_refs']}",
        f"- Instant timeline keys: {totals['instant_keys']}",
        f"- Non-instant timeline keys: {totals['non_instant_keys']}",
        f"- Negative-scale objects: {totals['negative_scale_objects']}",
        f"- Non-opaque object keys: {totals['alpha_objects']}",
        f"- Broken SCML references: {totals['broken_references']}",
        f"- Off-grid keys: {totals['off_grid_keys']}",
        f"- Schema mismatches: {totals['schema_mismatches']}",
        f"- Unsafe PNG paths: {totals['unsafe_image_paths']}",
        f"- Invalid PNG dimensions: {totals['invalid_image_dimensions']}",
        f"- Missing/duplicate IDs: {totals['invalid_or_duplicate_ids']}",
        f"- Invalid animation timing: {totals['invalid_animation_timing']}",
        f"- Unkeyed mainline grid slots: {totals['unkeyed_mainline_slots']}",
        f"- Ref/key time mismatches: {totals['mismatched_ref_times']}",
        f"- Validation issues: {totals['validation_issues']}",
        f"- Pivots outside 0..1: {totals['pivots_outside']}",
        f"- Median animation length: {summary['median_animation_length_ms']} ms",
        "",
        "## Common intervals",
        "",
    ]
    if summary["image_checks"]:
        lines[-4:-4] = [
            f"- Missing PNGs: {totals['missing_images']}",
            f"- PNG dimension mismatches: {totals['dimension_mismatches']}",
        ]
    else:
        lines[-4:-4] = ["- PNG checks: skipped"]
    lines.extend(f"- {value} ms: {count}" for value, count in summary["top_intervals_ms"])
    lines.extend(["", "## Common animation names", ""])
    lines.extend(f"- `{name}`: {count}" for name, count in summary["top_animation_names"])
    lines.extend(["", "## Generator, looping, and curves", ""])
    lines.extend(f"- Generator `{name}`: {count}" for name, count in summary["generators"])
    lines.extend(f"- Looping `{name}`: {count}" for name, count in summary["looping_values"])
    lines.extend(f"- Curve `{name}`: {count}" for name, count in summary["curve_types"])
    lines.extend(["", "## Most complex files", ""])
    for item in summary["most_complex"]:
        lines.append(
            f"- `{item['path']}`: {item['animations']} animations, "
            f"{item['timeline_keys']} timeline keys, {item['bone_refs']} bone refs"
        )
    if summary["files_with_warnings"]:
        lines.extend(["", "## Files with warnings", ""])
        for item in summary["files_with_warnings"]:
            lines.append(f"- `{item['path']}`: {'; '.join(item['warnings'])}")
    if summary["parse_errors"]:
        lines.extend(["", "## Parse errors", ""])
        lines.extend(f"- `{item['path']}`: {item['error']}" for item in summary["parse_errors"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="SCML files or directories")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument(
        "--skip-image-checks",
        action="store_true",
        help="skip PNG existence and dimension checks for faster corpus summaries",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = iter_scml(args.paths)
    if not files:
        print("No SCML files found.", file=sys.stderr)
        return 2
    summary = summarize(files, check_images=not args.skip_image_checks)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary), end="")
    totals = summary["totals"]
    assert isinstance(totals, dict)
    return 1 if summary["parse_errors"] or totals["validation_issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
