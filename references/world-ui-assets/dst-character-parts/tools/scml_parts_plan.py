#!/usr/bin/env python3
"""Extract a deterministic part plan from a Spriter SCML file."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import sys
import xml.etree.ElementTree as ET

try:
    from PIL import Image
except ImportError:  # The plan still works; source alpha metadata is optional.
    Image = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scml", type=Path, help="Input Spriter .scml file")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON plan")
    return parser.parse_args()


def number(value: str | None, default: float = 0.0) -> int | float:
    if value is None:
        return default
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"SCML numeric values must be finite: {value!r}")
    return int(parsed) if parsed.is_integer() else parsed


def positive_integer(value: str | None, field: str, part_path: str) -> int:
    parsed = number(value, 0)
    if not isinstance(parsed, int) or parsed <= 0:
        raise ValueError(
            f"SCML {field} must be a positive integer for {part_path}: {value!r}"
        )
    return parsed


def nonnegative_integer(value: str | None, field: str) -> int:
    if value is None:
        raise ValueError(f"SCML {field} is required")
    cleaned = value.strip()
    if not cleaned or any(character not in "0123456789" for character in cleaned):
        raise ValueError(f"SCML {field} must be a nonnegative integer: {value!r}")
    return int(cleaned)


def normalize_part_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    raw_parts = normalized.split("/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in raw_parts)
        or any(":" in part or "\0" in part for part in raw_parts)
    ):
        raise ValueError(f"SCML file path must be a safe relative path: {value!r}")
    return path.as_posix()


def main() -> int:
    args = parse_args()
    scml = args.scml.resolve()
    output = args.output.resolve()
    if output.suffix.casefold() != ".json":
        raise ValueError(f"Output path must use a .json extension: {output}")
    if output == scml:
        raise ValueError("Output path must not overwrite the input SCML file")

    source_root = scml.parent
    root = ET.parse(scml).getroot()
    if root.tag != "spriter_data":
        raise ValueError(f"SCML root element must be spriter_data: {root.tag!r}")
    actual_source_paths = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file() and path.suffix.casefold() == ".png"
    }
    actual_sources_by_casefold: dict[str, list[str]] = {}
    for relative in actual_source_paths:
        actual_sources_by_casefold.setdefault(relative.casefold(), []).append(relative)

    folders = []
    seen_folder_ids: set[int] = set()
    seen_paths: set[str] = set()
    total_files = 0

    folder_nodes: list[tuple[int, ET.Element]] = []
    for folder in root.findall("folder"):
        folder_id = nonnegative_integer(folder.get("id"), "folder id")
        if folder_id in seen_folder_ids:
            raise ValueError(f"SCML contains a duplicate folder id: {folder_id}")
        seen_folder_ids.add(folder_id)
        folder_nodes.append((folder_id, folder))

    for folder_id, folder in sorted(folder_nodes, key=lambda item: item[0]):
        files = []
        seen_file_ids: set[int] = set()
        file_nodes: list[tuple[int, ET.Element]] = []
        for file_node in folder.findall("file"):
            file_id = nonnegative_integer(
                file_node.get("id"), f"file id in folder {folder_id}"
            )
            if file_id in seen_file_ids:
                raise ValueError(
                    f"SCML folder {folder_id} contains a duplicate file id: {file_id}"
                )
            seen_file_ids.add(file_id)
            file_nodes.append((file_id, file_node))

        for file_id, file_node in sorted(file_nodes, key=lambda item: item[0]):
            name = normalize_part_path(file_node.get("name") or "")
            path_key = name.casefold()
            if path_key in seen_paths:
                raise ValueError(f"SCML contains a duplicate file path: {name}")
            seen_paths.add(path_key)

            width = positive_integer(file_node.get("width"), "width", name)
            height = positive_integer(file_node.get("height"), "height", name)

            file_data = {
                "id": file_id,
                "path": name,
                "width": width,
                "height": height,
                "pivot_x": number(file_node.get("pivot_x"), 0.0),
                "pivot_y": number(file_node.get("pivot_y"), 1.0),
            }
            source_png = source_root.joinpath(*name.split("/")).resolve()
            if not source_png.is_relative_to(source_root):
                raise ValueError(f"SCML file resolves outside its source directory: {name}")
            case_matches = sorted(actual_sources_by_casefold.get(name.casefold(), []))
            if name not in actual_source_paths and case_matches:
                file_data["source_path_case_mismatch"] = case_matches
            elif Image is not None and source_png.is_file():
                try:
                    with Image.open(source_png) as source_image:
                        source_image.load()
                        file_data["source_mode"] = source_image.mode
                        if "A" in source_image.getbands():
                            source_bbox = source_image.getchannel("A").getbbox()
                            file_data["source_alpha_bbox"] = (
                                list(source_bbox) if source_bbox else None
                            )
                            file_data["allow_empty_alpha"] = source_bbox is None
                except (OSError, Image.DecompressionBombError) as exc:
                    file_data["source_image_error"] = type(exc).__name__
            files.append(file_data)
        total_files += len(files)
        folders.append(
            {
                "id": folder_id,
                "name": folder.get("name") or "",
                "files": files,
            }
        )

    payload = {
        "schema_version": 1,
        "source_scml": scml.name,
        "source_sha256": hashlib.sha256(scml.read_bytes()).hexdigest(),
        "folder_count": len(folders),
        "file_count": total_files,
        "folders": folders,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"folders={len(folders)} files={total_files} output={output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
