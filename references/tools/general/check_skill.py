#!/usr/bin/env python3
"""
Lightweight integrity checks for the DST mod development skill.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path


def _find_repo_root() -> Path:
    # 本文件位于 references/tools/general/ 下，向上回溯到含 SKILL.md 的目录，
    # 避免目录层级调整后 REPO_ROOT 指向错误位置。
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "SKILL.md").is_file():
            return current
        current = current.parent
    raise SystemExit("check_skill.py: 未找到包含 SKILL.md 的仓库根目录")


REPO_ROOT = _find_repo_root()
REFERENCES_ROOT = REPO_ROOT / "references"
COMPONENT_REFERENCES_ROOT = REFERENCES_ROOT / "components"
# mod-notes 为外部 mod 分析的原始笔记归档，引用的外部脚本/文件不保证随仓库发布，不做链接校验。
MOD_NOTES_ROOT = REFERENCES_ROOT / "mod-notes"
FROZEN_KB_ROOT = REFERENCES_ROOT / "knowledge" / "dst-engineering-kb"
DOC_FILES = [
    REPO_ROOT / "SKILL.md",
]
SCRIPT_FILES: list[Path] = []
REFERENCE_FILES: list[Path] = []
COMPONENT_REFERENCE_FILES: list[Path] = []
SKILL_FILES: list[Path] = []
METADATA_FILES: list[Path] = []
# 在 os.walk 进入目录之前剪枝；导入模块不触发扫描。
SKIP_DIRECTORIES = {
    ".git", "mod-notes", "dst-engineering-kb", ".codex", ".tmp", ".cache",
    "__pycache__", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}


def is_link(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def iter_skill_files(root: Path):
    def fail(error):
        raise error

    for base, directories, filenames in os.walk(root, topdown=True, followlinks=False, onerror=fail):
        parent = Path(base)
        directories[:] = sorted(
            name for name in directories
            if name not in SKIP_DIRECTORIES and not is_link(parent / name)
        )
        for name in sorted(filenames):
            path = parent / name
            if not is_link(path):
                yield path


def load_inventory() -> None:
    global SCRIPT_FILES, REFERENCE_FILES, COMPONENT_REFERENCE_FILES, SKILL_FILES, METADATA_FILES
    files = list(iter_skill_files(REPO_ROOT))
    refs = [p for p in files if REFERENCES_ROOT in p.parents]
    SCRIPT_FILES = [p for p in refs if p.suffix == ".py" and (
        "tools" in p.relative_to(REFERENCES_ROOT).parts or p.name.startswith("test_")
    )]
    REFERENCE_FILES = [p for p in refs if p.suffix == ".md" and COMPONENT_REFERENCES_ROOT not in p.parents]
    COMPONENT_REFERENCE_FILES = [p for p in refs if p.suffix == ".md" and COMPONENT_REFERENCES_ROOT in p.parents]
    SKILL_FILES = [p for p in files if p.name == "SKILL.md"]
    METADATA_FILES = [p for p in files if p.name == "openai.yaml" and p.parent.name == "agents"]
OFFICIAL_REFERENCE_DOCS = [
    REFERENCES_ROOT / "official-files.md",
    REFERENCES_ROOT / "official-examples.md",
]
CRITICAL_PATHS = [
    REPO_ROOT / "SKILL.md",
    REFERENCES_ROOT / "tools" / "general" / "dst_zip_tool.py",
    REFERENCES_ROOT / "tools" / "general" / "dst_zip_cache.py",
    REFERENCES_ROOT / "tools" / "general" / "init_dst_mod.py",
    REFERENCES_ROOT / "tools" / "general" / "bundle_release.py",
    REFERENCES_ROOT / "tools" / "general" / "tex_atlas_tool.py",
    REFERENCES_ROOT / "tools" / "general" / "resize_png.py",
    REFERENCES_ROOT / "task-playbook.md",
    REFERENCES_ROOT / "official-files.md",
    REFERENCES_ROOT / "patterns.md",
    REFERENCES_ROOT / "component-patterns.md",
    REFERENCES_ROOT / "feature-recipes.md",
    REFERENCES_ROOT / "patterns" / "startup" / "modinfo-patterns.md",
    REFERENCES_ROOT / "patterns" / "startup" / "modmain-patterns.md",
    REFERENCES_ROOT / "patterns" / "asset" / "texture-patterns.md",
]

PATH_PATTERN = re.compile(r"((?:[A-Za-z0-9_./-]+/)?(?:references|scripts)/[A-Za-z0-9_./-]+\.(?:md|py))")
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
OFFICIAL_SCRIPT_PATTERN = re.compile(r"`(scripts/[^`]+)`")
SKILL_INVOCATION_PATTERN = re.compile(r"\$dst-[a-z0-9-]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight integrity checks for this skill.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat soft warnings such as low doc counts as failures.",
    )
    return parser.parse_args()


def to_repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def check_exists(errors: list[str]) -> None:
    for path in CRITICAL_PATHS:
        if not path.exists():
            errors.append(f"missing critical path: {to_repo_relative(path)}")


def normalize_markdown_link_target(target: str) -> str | None:
    value = target.strip()
    if not value:
        return None
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")].strip()
    else:
        value = re.split(r"\s+[\"']", value, maxsplit=1)[0]
    if not value:
        return None
    if value.startswith(("http://", "https://", "mailto:", "#", "file://")):
        return None
    value = value.split("#", 1)[0].strip()
    if not value:
        return None
    return value


def resolve_markdown_target(doc: Path, target: str) -> Path:
    # Markdown 链接必须相对文档解析，不能用其他目录碰巧存在的文件掩盖坏链接。
    return (doc.parent / Path(target)).resolve(strict=False)


def check_markdown_references(errors: list[str]) -> None:
    markdown_files = sorted({*DOC_FILES, *REFERENCE_FILES, *COMPONENT_REFERENCE_FILES})
    for doc in markdown_files:
        text = doc.read_text(encoding="utf-8")
        seen_repo_refs: set[str] = set()
        reference_text = re.sub(r"https?://[^\s)]+", "", text)
        for match in PATH_PATTERN.findall(reference_text):
            if match in seen_repo_refs:
                continue
            seen_repo_refs.add(match)
            # 同一路径可能相对文档自身目录、上级 skill 目录或仓库根，任一存在即视为有效。
            if any(
                (base / Path(match)).exists()
                for base in (doc.parent, doc.parent.parent, REPO_ROOT)
            ):
                continue
            errors.append(
                f"broken reference in {to_repo_relative(doc)}: {match}"
            )
        seen_links: set[str] = set()
        # Lua 表索引/调用与代码示例不是 Markdown 链接。
        link_text = re.sub(r"```[\s\S]*?```|~~~[\s\S]*?~~~", "", text)
        link_text = re.sub(r"`[^`\n]*`", "", link_text)
        for raw_target in MARKDOWN_LINK_PATTERN.findall(link_text):
            target_ref = normalize_markdown_link_target(raw_target)
            if target_ref is None or target_ref in seen_links:
                continue
            seen_links.add(target_ref)
            target = resolve_markdown_target(doc, target_ref)
            try:
                target.relative_to(REPO_ROOT)
            except ValueError:
                errors.append(
                    f"out-of-repo markdown link in {to_repo_relative(doc)}: {target_ref}"
                )
                continue
            if not target.exists():
                errors.append(
                    f"broken markdown link in {to_repo_relative(doc)}: {target_ref}"
                )


def check_py_compile(errors: list[str]) -> None:
    for script in SCRIPT_FILES:
        try:
            compile(script.read_bytes(), str(script), "exec")
        except (SyntaxError, UnicodeError, OSError) as exc:
            errors.append(f"Python syntax check failed for {to_repo_relative(script)}: {exc}")


def check_skill_frontmatter(errors: list[str]) -> None:
    expected = REPO_ROOT / "SKILL.md"
    if expected not in SKILL_FILES:
        errors.append("missing root SKILL.md")
    for doc in SKILL_FILES:
        if doc != expected:
            errors.append(f"unexpected callable skill entry: {to_repo_relative(doc)}; use GUIDE.md")
            continue
        text = doc.read_text(encoding="utf-8-sig")
        header = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
        if header is None:
            errors.append(f"missing skill frontmatter: {to_repo_relative(doc)}")
            continue
        name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", header.group(1), re.MULTILINE)
        description = re.search(r"^description:\s*\S.*$", header.group(1), re.MULTILINE)
        if name is None or description is None:
            errors.append(f"invalid skill name/description: {to_repo_relative(doc)}")
        elif name.group(1) != "dst-mod-skill-main":
            errors.append(f"unexpected root skill name: {name.group(1)}")


def check_skill_invocations(errors: list[str]) -> None:
    for doc in sorted({*DOC_FILES, *REFERENCE_FILES, *COMPONENT_REFERENCE_FILES, *METADATA_FILES}):
        text = doc.read_text(encoding="utf-8-sig")
        for invocation in sorted(set(SKILL_INVOCATION_PATTERN.findall(text)) - {"$dst-mod-skill-main"}):
            errors.append(f"retired skill invocation in {to_repo_relative(doc)}: {invocation}")
        if doc in METADATA_FILES:
            prompt = re.search(r"^\s+default_prompt:\s*(.+)$", text, re.MULTILINE)
            if prompt is None or "$dst-mod-skill-main" not in prompt.group(1):
                errors.append(f"metadata must route to $dst-mod-skill-main: {to_repo_relative(doc)}")
            if doc.parent.parent != REPO_ROOT and not (doc.parent.parent / "GUIDE.md").is_file():
                errors.append(f"metadata has no topic GUIDE.md: {to_repo_relative(doc)}")


def normalize_official_script_ref(ref: str) -> str:
    return ref.strip()


def validate_official_script_ref(
    ref: str,
    entry_names: set[str],
    all_entries: list[str],
) -> bool:
    if "*" in ref:
        return any(fnmatch.fnmatch(name, ref) for name in all_entries)
    if ref.endswith("/"):
        return any(name.startswith(ref) for name in all_entries)
    return ref in entry_names


def check_official_script_references(errors: list[str], warnings: list[str]) -> None:
    try:
        from dst_zip_tool import resolve_zip_path
    except Exception as exc:  # pragma: no cover - defensive import fallback
        warnings.append(f"skipped official script reference validation: {exc}")
        return

    try:
        zip_path = resolve_zip_path(None)
    except Exception as exc:
        warnings.append(f"skipped official script reference validation: {exc}")
        return

    with zipfile.ZipFile(zip_path) as zf:
        all_entries = sorted(
            info.filename for info in zf.infolist() if not info.is_dir()
        )
        entry_names = set(all_entries)

    for doc in OFFICIAL_REFERENCE_DOCS:
        text = doc.read_text(encoding="utf-8")
        refs = {
            normalize_official_script_ref(ref)
            for ref in OFFICIAL_SCRIPT_PATTERN.findall(text)
        }
        for ref in sorted(refs):
            if ref.endswith(".py"):
                continue
            if not validate_official_script_ref(ref, entry_names, all_entries):
                errors.append(
                    f"broken official script reference in {to_repo_relative(doc)}: {ref}"
                )


def check_counts(warnings: list[str]) -> None:
    if len(REFERENCE_FILES) < 20:
        warnings.append(f"reference doc count looks low: {len(REFERENCE_FILES)}")
    if len(COMPONENT_REFERENCE_FILES) < 4:
        warnings.append(
            f"component detail doc count looks low: {len(COMPONENT_REFERENCE_FILES)}"
        )
    if len(SCRIPT_FILES) < 5:
        warnings.append(f"helper script count looks low: {len(SCRIPT_FILES)}")


def check_document_routes(errors: list[str]) -> None:
    """Keep every legacy pattern attached to a real primary topic."""
    registry = REFERENCES_ROOT / "knowledge" / "document-routes.json"
    if not registry.is_file() or is_link(registry):
        errors.append("missing or linked document route registry")
        return
    try:
        data = json.loads(registry.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(f"invalid document route registry: {exc}")
        return
    routes = data.get("supporting_documents") if isinstance(data, dict) else None
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(routes, dict):
        errors.append("unsupported document route registry")
        return
    known = {to_repo_relative(path) for path in (*REFERENCE_FILES, *COMPONENT_REFERENCE_FILES)}
    guides = {path for path in known if path.endswith("/GUIDE.md")}
    patterns = {path for path in known if path.startswith("references/patterns/")}
    engineering_details = {
        path for path in known
        if path.startswith("references/engineering/dst-mod-engineering/")
        and path.endswith(".md")
        and not path.endswith("/README.md")
        and path not in {
            "references/engineering/dst-mod-engineering/kb-retrieval.md",
            "references/engineering/dst-mod-engineering/knowledge-integration.md",
            "references/engineering/dst-mod-engineering/sources-and-corrections.md",
            "references/engineering/dst-mod-engineering/upstream-validation.md",
        }
    }
    for path in sorted(patterns - routes.keys()):
        errors.append(f"legacy pattern has no primary topic: {path}")
    for path in sorted(engineering_details - routes.keys()):
        errors.append(f"engineering detail has no primary topic: {path}")
    for support, owners in routes.items():
        if support not in known or support in guides or not isinstance(owners, list) or not owners:
            errors.append(f"invalid supporting document route: {support}")
            continue
        for owner in owners:
            if not isinstance(owner, str) or f"references/{owner}/GUIDE.md" not in guides:
                errors.append(f"missing primary topic for {support}: {owner}")


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        load_inventory()
    except OSError as exc:
        print(f"inventory failed: {exc}", file=sys.stderr)
        return 1
    check_exists(errors)
    check_skill_frontmatter(errors)
    check_skill_invocations(errors)
    check_markdown_references(errors)
    check_py_compile(errors)
    check_official_script_references(errors, warnings)
    check_document_routes(errors)
    check_counts(warnings)

    print(f"repo: {REPO_ROOT}")
    print(f"references: {len(REFERENCE_FILES)}")
    print(f"component_references: {len(COMPONENT_REFERENCE_FILES)}")
    print(f"scripts: {len(SCRIPT_FILES)}")

    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.strict and warnings:
        return 1

    print("check_skill: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
