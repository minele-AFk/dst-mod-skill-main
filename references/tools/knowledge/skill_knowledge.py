"""Read-only discovery of local skill references plus the existing evidence KB."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import stat

from dst_kb.config import KBError
from dst_kb.service import MODE_TYPES, Service, tokens


SKILL_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = Path(__file__).with_name("config.json")
SKIP_DIRECTORIES = {
    "mod-notes", "dst-engineering-kb", "assets", "agents", "tests", "history",
    ".git", ".codex", ".cache", ".tmp", ".venv", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
NAME_TABLE = "references/prefabs/物品名字.txt"
DOCUMENT_ROUTES = "references/knowledge/document-routes.json"
STOP_WORDS = {"如何", "需要", "一个", "我的", "这个", "实现", "相关", "当前", "任务"}
# Navigation aliases only; they do not assert game API behavior.
DOMAIN_ALIASES = (
    "联网 联机 网络 同步 rpc replica netvar networking",
    "生命周期 清理 取消 listener lifecycle",
    "存档 保存 读档 persistence save load",
    "贴图 纹理 图集 texture atlas alpha tex",
    "动画 骨骼 scml spriter openspine animation",
    "料理 食谱 烹饪 调味 seasoning cooker cooking spice",
    "角色 人物 character player",
    "战斗 伤害 武器 护甲 combat damage weapon armor",
    "界面 控件 widget hud screen ui",
    "世界生成 worldgen room taskset layout",
    "音频 音效 声音 fmod audio sound",
    "能量 魔力 法力 mana energy",
    "温度 恒温 体温 temperature",
    "皮肤 外观 造型 skin appearance build symbol override",
    "状态机 动作状态 预测 stategraph state sg",
    "钩子 补丁 hook postinit wrapper compatibility",
    "工具 安装 环境 发现 tool setup bootstrap dmt ktech krane",
)


def is_link(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def allowed_relative(value: str) -> PurePosixPath:
    value = value.replace("\\", "/")
    path = PurePosixPath(value)
    if path.is_absolute() or re.match(r"^[a-zA-Z]:", value) or ".." in path.parts:
        raise ValueError("Use a skill-relative reference path without parent traversal.")
    if any(":" in part or part.rstrip(" .") != part for part in path.parts):
        raise ValueError("Windows stream and trailing-dot/space path aliases are not allowed.")
    if path.as_posix() == "SKILL.md":
        return path
    if not path.parts or path.parts[0].casefold() != "references":
        raise ValueError("Only SKILL.md and permitted references are readable here.")
    if any(part.casefold() in SKIP_DIRECTORIES for part in path.parts[1:-1]):
        raise ValueError("This path is excluded from ordinary knowledge retrieval.")
    if path.suffix.lower() != ".md" and path.as_posix().casefold() != NAME_TABLE.casefold():
        raise ValueError("Only Markdown references and the prefab name table are readable here.")
    return path


def safe_path(root: Path, value: str) -> Path:
    relative = allowed_relative(value)
    current = root
    for part in relative.parts:
        current = current / part
        if is_link(current):
            raise ValueError("Linked files and directories are excluded from knowledge retrieval.")
    if not current.is_file():
        raise ValueError("Reference is not a file: " + relative.as_posix())
    return current


def document_paths(root: Path):
    root_entry = root / "SKILL.md"
    if root_entry.is_file() and not is_link(root_entry):
        yield root_entry
    references = root / "references"
    if is_link(references):
        raise ValueError("The references directory must not be a link.")

    def fail(error):
        raise error

    for base, directories, filenames in os.walk(references, topdown=True, followlinks=False, onerror=fail):
        parent = Path(base)
        # Prune before os.walk enters a directory; do not enumerate restricted notes/assets.
        directories[:] = sorted(name for name in directories
                                if name.casefold() not in SKIP_DIRECTORIES and not is_link(parent / name))
        for name in sorted(filenames):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if (path.suffix.lower() == ".md" or relative == NAME_TABLE) and not is_link(path):
                yield path


def load_review_registry(root: Path) -> dict:
    """Read optional maintenance data without following linked directories."""
    path = Path(root)
    try:
        for part in ("references", "knowledge", "review-status.json"):
            path = path / part
            if is_link(path):
                raise ValueError("Linked maintenance registry is excluded.")
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if (data.get("schema_version") != 1 or not isinstance(data.get("documents"), dict)
                or not isinstance(data.get("source_snapshot", {}), dict)):
            raise ValueError("Unsupported maintenance registry.")
        return {"status": "available", "data": data}
    except FileNotFoundError:
        return {"status": "missing", "data": {}}
    except (OSError, ValueError, UnicodeError, AttributeError) as exc:
        return {"status": "unavailable", "data": {}, "reason": str(exc)}


def review_status(registry: dict, relative: str, sha256: str) -> dict:
    """Content hash matching is a maintenance fact, never a game verdict."""
    if registry["status"] == "unavailable":
        return {"status": "unavailable", "reason": registry["reason"]}
    data = registry["data"]
    record = data.get("documents", {}).get(relative)
    if not isinstance(record, dict):
        return {"status": "unrecorded"}
    if record.get("sha256") != sha256:
        return {"status": "stale", "notice": "Content changed after the recorded review."}
    depth = record.get("depth")
    if depth not in {"structure_screened", "content_curated", "source_signatures"}:
        return {"status": "unrecorded"}
    return {"status": "record_current", "depth": depth,
            "reviewed_on": record.get("reviewed_on", data.get("reviewed_on")),
            "source_snapshot_sha256": record.get("source_snapshot_sha256", data.get("source_snapshot", {}).get("sha256")),
            "runtime_validation": "not_established_by_this_review",
            "notice": "Hash matches the maintenance record; source version and task applicability still require checking."}


def word_set(text: str) -> set[str]:
    return set(tokens(text)) - STOP_WORDS


def identifiers(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))


def expand_query(query: str) -> tuple[set[str], set[str]]:
    """Expand navigation aliases without treating them as direct evidence."""
    original = word_set(query)
    expanded = set(original)
    for group in DOMAIN_ALIASES:
        # Latin aliases match tokens: "ui" inside "build" is not an UI request.
        if any(term.casefold() in original if term.isascii() else term in query
               for term in group.split()):
            expanded.update(word_set(group))
    return original, expanded


@dataclass
class Document:
    path: str
    lines: list[str]
    title: str
    sha256: str
    fields: list[tuple[set[str], float]]
    kind: str
    description: str
    identifiers: set[str]


class Corpus:
    def __init__(self, root: Path = SKILL_ROOT):
        self.root = Path(root).resolve()
        self.review_registry = load_review_registry(self.root)
        self.documents: list[Document] = []
        self.errors: list[dict] = []
        for path in document_paths(self.root):
            relative = path.relative_to(self.root).as_posix()
            try:
                data = path.read_bytes()
                text = data.decode("utf-8-sig")
            except (OSError, UnicodeError) as exc:
                self.errors.append({"path": relative, "error": str(exc)})
                continue
            # A guide may link to restricted notes; do not rank or quote that route as retrieved knowledge.
            lines = ["" if "mod-notes/" in line.replace("\\", "/").casefold() else line
                     for line in text.splitlines()]
            searchable_text = "\n".join(lines)
            title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
            description = next((line.partition(":")[2].strip() for line in lines
                                if line.startswith("description:")), "")
            headings = " ".join(line.lstrip("# ") for line in lines if line.startswith("#"))
            kind = "topic_guide" if path.name == "GUIDE.md" else "reference"
            if relative == NAME_TABLE:
                title, kind = "物品代码名表", "prefab_names"
            elif path.name in {"topic-index.md", "patterns.md", "signatures.md", "pitfalls.md"}:
                kind = "navigation"
            self.documents.append(Document(relative, lines, title, hashlib.sha256(data).hexdigest(), [
                (word_set(title), 6.0), (word_set(description), 3.0),
                (word_set(headings), 2.0),
                (word_set(re.sub(r"[/_-]", " ", relative)), 1.5),
                (word_set(searchable_text), 0.5),
            ], kind, description, {symbol.casefold() for symbol in identifiers(searchable_text)}))
        self.frequency = Counter(term for doc in self.documents for term in doc.fields[-1][0])
        self.document_routes = self._load_document_routes()

    def _load_document_routes(self) -> dict:
        """Curated navigation links; never evidence claims or document replacements."""
        path = self.root / DOCUMENT_ROUTES
        try:
            if any(is_link(parent) for parent in (self.root / "references", self.root / "references/knowledge", path)):
                raise ValueError("Linked document route registry is excluded.")
            if not path.exists():
                return {"status": "missing", "routes": {}}
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            routes = data.get("supporting_documents")
            if data.get("schema_version") != 1 or not isinstance(routes, dict):
                raise ValueError("Unsupported document route registry.")
            known = {doc.path for doc in self.documents}
            topics = {doc.path for doc in self.documents if doc.kind == "topic_guide"}
            for support, owners in routes.items():
                if (support not in known or support.endswith("/GUIDE.md")
                        or not isinstance(owners, list) or not owners):
                    raise ValueError("Invalid supporting document route: " + str(support))
                if any(not isinstance(owner, str) or f"references/{owner}/GUIDE.md" not in topics
                       for owner in owners):
                    raise ValueError("Missing primary topic for: " + support)
            return {"status": "available", "routes": routes}
        except (OSError, UnicodeError, ValueError, AttributeError) as exc:
            return {"status": "unavailable", "routes": {}, "reason": str(exc)}

    def route_for(self, doc: Document) -> dict:
        if doc.kind == "topic_guide":
            return {"role": "primary_topic", "primary_topics": [doc.path]}
        owners = self.document_routes["routes"].get(doc.path, [])
        return {"role": "supporting_detail" if owners else "reference",
                "primary_topics": [f"references/{owner}/GUIDE.md" for owner in owners]}

    def topics(self, query: str = "", limit: int = 10) -> dict:
        """Search current guide routes with the same navigation aliases as docs."""
        if not 0 <= limit <= 50:
            raise ValueError("limit must be 0..50")
        original, expanded = expand_query(query) if query.strip() else (set(), set())
        by_path = {doc.path: doc for doc in self.documents}
        supports = {}
        for support, owners in self.document_routes["routes"].items():
            for owner in owners:
                supports.setdefault(f"references/{owner}/GUIDE.md", []).append(support)
        rows = []
        for doc in self.documents:
            if doc.kind != "topic_guide":
                continue
            details = sorted(supports.get(doc.path, []))
            score = 0.0
            if expanded:
                direct_terms = original - STOP_WORDS
                direct_match = False
                for field, weight in doc.fields:
                    direct_match = direct_match or bool(direct_terms & field)
                    score += sum(weight * (1.0 if term in original else 0.18)
                                 for term in expanded & field)
                for detail in details:
                    detail_doc = by_path.get(detail)
                    if detail_doc is not None:
                        for field, weight in detail_doc.fields:
                            direct_match = direct_match or bool(direct_terms & field)
                            score += sum(weight * 0.5 * (1.0 if term in original else 0.18)
                                         for term in expanded & field)
                if not direct_match:
                    continue
            rows.append({"path": doc.path, "title": doc.title, "description": doc.description,
                         "supporting_documents": details, "source": "current_local_guide",
                         "score": round(score, 4),
                         "evidence_grade": "not_assigned",
                         "notice": "Navigation metadata only; read the guide and check current source before use."})
        if expanded:
            rows.sort(key=lambda row: (-row["score"], row["path"]))
        matched = len(rows)
        return {"topics": rows[:limit], "matched": matched,
                "total": sum(doc.kind == "topic_guide" for doc in self.documents),
                "routes_status": self.document_routes["status"]}

    def scope(self) -> dict:
        return {"root": str(self.root), "documents": len(self.documents),
                "kinds": dict(Counter(doc.kind for doc in self.documents)),
                "topic_catalog": {"primary_topics": sum(doc.kind == "topic_guide" for doc in self.documents),
                                  "routed_supporting_documents": len(self.document_routes["routes"]),
                                  "status": self.document_routes["status"],
                                  "reason": self.document_routes.get("reason"),
                                  "nature": "navigation_metadata_not_evidence_claims"},
                "excluded_directories": sorted(SKIP_DIRECTORIES),
                "read_errors": self.errors,
                "status": "partial" if self.errors or self.document_routes["status"] == "unavailable" else "ready",
                "review_registry": {"status": self.review_registry["status"],
                                    "counts": dict(Counter(review_status(self.review_registry, doc.path, doc.sha256)["status"]
                                                           for doc in self.documents))},
                "source_policy": "Local references are guidance; no automatic evidence grade or runtime validation."}

    def search(self, query: str, limit: int = 5) -> dict:
        if not query.strip() or len(query) > 4000:
            raise ValueError("query must contain 1..4000 characters")
        if not 1 <= limit <= 10:
            raise ValueError("limit must be 1..10")
        original, expanded = expand_query(query)
        # Keep full API identifiers ahead of incidental matches on split Get/Set words.
        query_symbols = {symbol.casefold() for symbol in identifiers(query)
                         if "_" in symbol or re.search(r"[a-z][A-Z]", symbol)}
        exact_hits = {}
        by_path = {doc.path: doc for doc in self.documents}
        rows = []
        for doc in self.documents:
            matched = expanded & doc.fields[-1][0]
            # A synonym-only hit is allowed, but is explicitly marked and ranks below direct matches.
            all_fields = set().union(*(field for field, _ in doc.fields))
            exact_hits[doc.path] = len(query_symbols & doc.identifiers)
            if not expanded & all_fields and not exact_hits[doc.path]:
                continue
            score = 0.0
            for field, weight in doc.fields:
                for term in expanded & field:
                    inverse = 1 + math.log((len(self.documents) + 1) / (self.frequency[term] + 1))
                    score += weight * inverse * (1.0 if term in original else 0.18)
            score *= {"navigation": 0.3, "topic_guide": 1.15}.get(doc.kind, 1.0)
            best_line, best_value, heading = 1, (-1, -1.0), doc.title
            best_heading = heading
            for number, line in enumerate(doc.lines, 1):
                if line.startswith("#"):
                    heading = line.lstrip("# ")
                overlap = word_set(line) & expanded
                line_symbols = {symbol.casefold() for symbol in identifiers(line)} if query_symbols else set()
                value = (len(query_symbols & line_symbols),
                         sum(1.0 if term in original else 0.18 for term in overlap))
                if value > best_value:
                    best_line, best_value, best_heading = number, value, heading
            snippet = " ".join(doc.lines[best_line - 1:best_line + 1]).strip()[:360]
            rows.append({"path": doc.path, "title": doc.title, "kind": doc.kind,
                         **self.route_for(doc),
                         "line": best_line, "heading": best_heading, "snippet": snippet,
                         "sha256": doc.sha256, "score": round(score, 4),
                         "exact_symbol_matches": sorted(query_symbols & doc.identifiers),
                         "matched_terms": sorted(matched | (query_symbols & doc.identifiers))[:16],
                         "direct_match": bool(original & all_fields) or bool(exact_hits[doc.path]),
                         "maintenance": review_status(self.review_registry, doc.path, doc.sha256)})
        rows.sort(key=lambda row: (-exact_hits[row["path"]], -row["score"], row["path"]))
        selected = rows[:limit]
        selected_paths = {row["path"] for row in selected}
        primary_paths = []
        for row in selected:
            for primary in row["primary_topics"]:
                if primary not in primary_paths:
                    primary_paths.append(primary)
        primary_candidates = []
        for path in primary_paths:
            if path in selected_paths:
                continue
            doc = by_path.get(path)
            if doc is not None:
                primary_candidates.append({
                    "path": doc.path, "title": doc.title, "description": doc.description,
                    "role": "primary_topic", "reason": "navigates_from_selected_supporting_detail",
                    "maintenance": review_status(self.review_registry, doc.path, doc.sha256)})
        return {"results": selected, "primary_topic_candidates": primary_candidates,
                "total_matches": len(rows), "knowledge_gap": not rows,
                "scope": self.scope(),
                "notice": "Candidate locations only. Read any primary_topic_candidates first, then the relevant supporting detail; check source/version limits."}


def read_reference(root: Path, relative: str, start: int = 1, count: int = 120) -> dict:
    if start < 1 or not 1 <= count <= 200:
        raise ValueError("start must be positive and count must be 1..200")
    path = safe_path(Path(root).resolve(), relative)
    data = path.read_bytes()
    lines = data.decode("utf-8-sig").splitlines()
    if start > max(1, len(lines)):
        raise ValueError("start is past the end of the reference")
    return {"path": path.relative_to(Path(root).resolve()).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "total_lines": len(lines),
            "maintenance": review_status(load_review_registry(Path(root).resolve()),
                                         path.relative_to(Path(root).resolve()).as_posix(),
                                         hashlib.sha256(data).hexdigest()),
            "lines": [{"number": index + 1, "text": line}
                      for index, line in enumerate(lines[start - 1:start - 1 + count], start - 1)]}


def lookup(query: str, mode: str = "research", limit: int = 5,
           config: Path = DEFAULT_CONFIG, root: Path = SKILL_ROOT) -> dict:
    if mode not in MODE_TYPES:
        raise ValueError("Unknown knowledge query mode")
    documents = Corpus(root).search(query, limit)
    service = None
    try:
        service = Service(config)
        evidence = {"status": "ready", **service.search_kb(query, top_k=limit, mode=mode)}
    except (KBError, OSError, ValueError, sqlite3.DatabaseError) as exc:
        evidence = {"status": "unavailable", "results": [],
                    "error": {"code": getattr(exc, "code", "KB_UNAVAILABLE"), "message": str(exc)}}
    finally:
        if service:
            service.close()
    return {"query": query, "mode": mode, "documents": documents, "engineering_kb": evidence,
            "status": "partial" if evidence["status"] != "ready" or documents["scope"]["status"] != "ready" else "ready",
            "notice": "Local documents and structured evidence have different scopes. Use read/get_entry for full context; no game tests implied."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="On-demand, read-only local skill and evidence lookup.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("lookup", "docs"):
        command = commands.add_parser(name)
        command.add_argument("query")
        command.add_argument("--limit", type=int, default=5)
        if name == "lookup":
            command.add_argument("--mode", choices=sorted(MODE_TYPES), default="research")
    read = commands.add_parser("read")
    read.add_argument("path")
    read.add_argument("--start", type=int, default=1)
    read.add_argument("--count", type=int, default=120)
    commands.add_parser("catalog")
    topics = commands.add_parser("topics")
    topics.add_argument("--query", default="")
    topics.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        if args.command == "lookup":
            result = lookup(args.query, args.mode, args.limit, args.config)
        elif args.command == "docs":
            result = Corpus().search(args.query, args.limit)
        elif args.command == "read":
            result = read_reference(SKILL_ROOT, args.path, args.start, args.count)
        elif args.command == "topics":
            result = Corpus().topics(args.query, args.limit)
        else:
            result = Corpus().scope()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({"error": {"code": "DOCUMENT_QUERY_ERROR", "message": str(exc)}}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
