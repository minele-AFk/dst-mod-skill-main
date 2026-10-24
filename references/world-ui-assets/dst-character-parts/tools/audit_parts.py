#!/usr/bin/env python3
"""Audit DST character PNG parts against an SCML-derived plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: install the 'Pillow' package.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parts_root", type=Path, help="Root containing part PNG paths")
    parser.add_argument("--plan", type=Path, required=True, help="JSON from scml_parts_plan.py")
    parser.add_argument("--report", type=Path, required=True, help="Audit JSON output")
    parser.add_argument("--contact-sheet", type=Path, help="Optional PNG preview")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on errors")
    parser.add_argument("--columns", type=int, default=6)
    return parser.parse_args()


def normalize_part_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Every plan file path must be a string")
    normalized = value.replace("\\", "/")
    raw_parts = normalized.split("/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in raw_parts)
        or any(":" in part or "\0" in part for part in raw_parts)
    ):
        raise ValueError(f"Plan file path must be a safe relative path: {value!r}")
    return path.as_posix()


def paths_equal(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def expected_files(plan: dict[str, Any]) -> list[dict[str, Any]]:
    schema_version = plan.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or schema_version != 1
        or not isinstance(plan.get("folders"), list)
    ):
        raise ValueError("Plan must use schema_version 1 and contain a folders list")

    result: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for folder in plan["folders"]:
        if not isinstance(folder, dict) or not isinstance(folder.get("files"), list):
            raise ValueError("Every plan folder must contain a files list")
        for raw_item in folder["files"]:
            if not isinstance(raw_item, dict):
                raise ValueError("Every plan file must be an object")
            item = dict(raw_item)
            item["path"] = normalize_part_path(item.get("path"))
            path_key = item["path"].casefold()
            if path_key in seen_paths:
                raise ValueError(f"Plan contains a duplicate file path: {item['path']}")
            seen_paths.add(path_key)

            for dimension in ("width", "height"):
                value = item.get(dimension)
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    raise ValueError(
                        f"Plan {dimension} must be a positive integer for {item['path']}"
                    )
            allow_empty_alpha = item.get("allow_empty_alpha")
            if allow_empty_alpha is not None and not isinstance(
                allow_empty_alpha, bool
            ):
                raise ValueError(
                    f"Plan allow_empty_alpha must be a boolean for {item['path']}"
                )
            result.append(item)

    declared_folder_count = plan.get("folder_count")
    if declared_folder_count is not None and (
        isinstance(declared_folder_count, bool)
        or not isinstance(declared_folder_count, int)
        or declared_folder_count != len(plan["folders"])
    ):
        raise ValueError("Plan folder_count does not match the folders list")
    declared_file_count = plan.get("file_count")
    if declared_file_count is not None and (
        isinstance(declared_file_count, bool)
        or not isinstance(declared_file_count, int)
        or declared_file_count != len(result)
    ):
        raise ValueError("Plan file_count does not match the files in folders")
    return sorted(result, key=lambda item: item["path"].casefold())


def edge_touches(alpha: Image.Image) -> list[str]:
    width, height = alpha.size
    edges = []
    if alpha.crop((0, 0, width, 1)).getbbox():
        edges.append("top")
    if alpha.crop((0, height - 1, width, height)).getbbox():
        edges.append("bottom")
    if alpha.crop((0, 0, 1, height)).getbbox():
        edges.append("left")
    if alpha.crop((width - 1, 0, width, height)).getbbox():
        edges.append("right")
    return edges


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    image = Image.new("RGBA", size, (46, 46, 46, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(72, 72, 72, 255))
    return image


def make_contact_sheet(items: list[dict[str, Any]], output: Path, columns: int) -> None:
    tile_w, tile_h, label_h = 180, 180, 30
    rows = max(1, math.ceil(len(items) / columns))
    sheet = Image.new("RGB", (columns * tile_w, rows * (tile_h + label_h)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, item in enumerate(items):
        col, row = index % columns, index // columns
        x, y = col * tile_w, row * (tile_h + label_h)
        tile = checkerboard((tile_w, tile_h))
        with Image.open(item["absolute_path"]) as source:
            rgba = source.convert("RGBA")
            preview = ImageOps.contain(rgba, (tile_w - 16, tile_h - 16))
            px = (tile_w - preview.width) // 2
            py = (tile_h - preview.height) // 2
            tile.alpha_composite(preview, (px, py))
        sheet.paste(tile.convert("RGB"), (x, y))
        label = Path(item["path"]).name
        if len(label) > 26:
            label = label[:23] + "..."
        draw.text((x + 5, y + tile_h + 7), label, fill=(235, 235, 235), font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> int:
    args = parse_args()
    root = args.parts_root.resolve()
    plan_path = args.plan.resolve()
    report_path = args.report.resolve()
    contact_sheet_path = args.contact_sheet.resolve() if args.contact_sheet else None
    if not root.is_dir():
        raise ValueError(f"Parts root is not a directory: {root}")
    if report_path.suffix.casefold() != ".json":
        raise ValueError(f"Report path must use a .json extension: {report_path}")
    if paths_equal(report_path, plan_path):
        raise ValueError("Report path must not overwrite the input plan")
    if contact_sheet_path is not None:
        if contact_sheet_path.suffix.casefold() != ".png":
            raise ValueError(
                f"Contact sheet path must use a .png extension: {contact_sheet_path}"
            )
        if paths_equal(contact_sheet_path, plan_path) or paths_equal(
            contact_sheet_path, report_path
        ):
            raise ValueError("Contact sheet path must not overwrite a plan or report")
        if contact_sheet_path.is_relative_to(root):
            raise ValueError("Contact sheet path must be outside the parts root")
    if args.columns <= 0:
        raise ValueError("Contact sheet columns must be a positive integer")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict):
        raise ValueError("Plan root must be a JSON object")
    expected = expected_files(plan)
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.casefold() == ".png"
    }
    actual_by_casefold: dict[str, list[str]] = {}
    for relative in actual_paths:
        actual_by_casefold.setdefault(relative.casefold(), []).append(relative)

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    contact_items: list[dict[str, Any]] = []
    matched_actual_paths: set[str] = set()

    for item in expected:
        relative = item["path"]
        case_matches = sorted(actual_by_casefold.get(relative.casefold(), []))
        if relative not in actual_paths and case_matches:
            result = {
                "path": relative,
                "status": "case_mismatch",
                "actual_paths": case_matches,
            }
            matched_actual_paths.update(case_matches)
            errors.append(
                f"path case mismatch: {relative} != {', '.join(case_matches)}"
            )
            results.append(result)
            continue

        path = root.joinpath(*relative.split("/")).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Part path resolves outside the parts root: {relative}")
        result: dict[str, Any] = {"path": relative, "status": "ok"}
        if not path.is_file():
            result["status"] = "missing"
            errors.append(f"missing: {relative}")
            results.append(result)
            continue

        matched_actual_paths.add(relative)
        try:
            result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            result["absolute_path"] = str(path)
            with Image.open(path) as image:
                image.load()
                result["mode"] = image.mode
                result["width"], result["height"] = image.size
                expected_size = (int(item["width"]), int(item["height"]))
                result["expected_width"], result["expected_height"] = expected_size
                if image.size != expected_size:
                    result["status"] = "size_mismatch"
                    errors.append(
                        f"size mismatch: {relative} {image.size} != {expected_size}"
                    )

                if "A" not in image.getbands():
                    result["status"] = "no_alpha"
                    errors.append(f"no alpha channel: {relative}")
                else:
                    alpha = image.getchannel("A")
                    bbox = alpha.getbbox()
                    result["alpha_bbox"] = list(bbox) if bbox else None
                    result["alpha_extrema"] = list(alpha.getextrema())
                    if bbox is None:
                        if item.get("allow_empty_alpha", False):
                            result["status"] = "template_blank"
                            warnings.append(f"template blank placeholder: {relative}")
                        else:
                            result["status"] = "empty_alpha"
                            errors.append(f"empty alpha: {relative}")
                    elif alpha.getextrema()[0] == 255:
                        result["status"] = "opaque_canvas"
                        errors.append(f"fully opaque canvas: {relative}")
                    touches = edge_touches(alpha)
                    result["edge_touches"] = touches
                    if touches:
                        warnings.append(f"edge touch ({','.join(touches)}): {relative}")
        except (OSError, Image.DecompressionBombError) as exc:
            result["status"] = "invalid_image"
            result["image_error"] = str(exc)
            errors.append(f"invalid image: {relative}: {exc}")
            results.append(result)
            continue

        results.append(result)
        contact_items.append({"path": relative, "absolute_path": str(path)})

    unexpected = sorted(actual_paths - matched_actual_paths, key=str.casefold)
    for relative in unexpected:
        warnings.append(f"unexpected png: {relative}")

    hashes: dict[str, list[str]] = {}
    for item in results:
        if item.get("sha256") and item.get("status") != "template_blank":
            hashes.setdefault(item["sha256"], []).append(item["path"])
    duplicate_groups = [paths for paths in hashes.values() if len(paths) > 1]
    for paths in duplicate_groups:
        warnings.append("duplicate png: " + ", ".join(paths))

    report = {
        "schema_version": 1,
        "parts_root": str(root),
        "plan": str(plan_path),
        "expected_count": len(expected),
        "present_count": len(contact_items),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "duplicate_groups": duplicate_groups,
        "unexpected_pngs": unexpected,
        "files": [{k: v for k, v in item.items() if k != "absolute_path"} for item in results],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if contact_sheet_path is not None:
        make_contact_sheet(contact_items, contact_sheet_path, args.columns)

    print(
        f"expected={len(expected)} present={len(contact_items)} "
        f"errors={len(errors)} warnings={len(warnings)} report={report_path}"
    )
    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
