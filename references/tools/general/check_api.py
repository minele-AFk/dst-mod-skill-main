#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check direct DST Component, Replica and EntityScript calls against Lua source.

Usage: python check_api.py <file.lua|directory> [...] [--scripts-dir DIR]
       python check_api.py <file.lua> --zip scripts.zip
       python check_api.py <file.lua> --dst <game-install-root>

DIR may be the unpacked scripts directory or its parent. Without an explicit
source, use DST_SCRIPTS_DIR, then dst_zip_tool's scripts.zip discovery.
Exit codes: 0 = direct declarations matched, 1 = missing component declaration,
2 = input/source error, 3 = manual review required (including zero checked calls).
This is a lexical check, not a Lua type checker or a game-runtime test. It does
not prove signatures, execution authority, lifecycle or dynamic method validity.
Requires Python 3.9+. No third-party dependencies.
"""

import argparse
from dataclasses import dataclass, field
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dst_zip_tool as zt

ZIP_REL = Path("data") / "databundles" / "scripts.zip"


def resolve_scripts_source(args):
    if args.scripts_dir:
        return "dir", Path(args.scripts_dir).expanduser()
    if args.zip:
        return "zip", Path(args.zip).expanduser()
    if args.dst:
        dst = Path(args.dst).expanduser()
        if (dst / ZIP_REL).is_file():
            return "zip", dst / ZIP_REL
        for candidate in (dst, dst / "data" / "scripts", dst / "scripts"):
            if (candidate / "components").is_dir():
                return "dir", candidate
        raise ValueError("no scripts.zip or unpacked components under --dst: %s" % dst)
    if os.environ.get("DST_SCRIPTS_DIR"):
        return "dir", Path(os.environ["DST_SCRIPTS_DIR"]).expanduser()
    return "zip", Path(zt.resolve_zip_path(None))


class ScriptsReader:
    """Use scripts/... entry names for ZIP and unpacked directory layouts."""

    def __init__(self, kind, root):
        self.kind = kind
        self.root = Path(root)
        self._zf = None
        if kind == "dir":
            if not (self.root / "components").is_dir():
                self.root = self.root / "scripts"
            if not (self.root / "components").is_dir():
                raise ValueError("components directory not found: %s" % root)
            if not (self.root / "entityscript.lua").is_file():
                raise ValueError("entityscript.lua not found: %s" % self.root)
        else:
            self._zf = zipfile.ZipFile(self.root)
            names = set(self._zf.namelist())
            self._zip_prefix = "scripts/" if "scripts/entityscript.lua" in names else ""
            if self._zip_prefix + "entityscript.lua" not in names:
                self.close()
                raise ValueError("ZIP has no entityscript.lua: %s" % root)

    def close(self):
        if self._zf is not None:
            self._zf.close()

    def _entry(self, entry):
        return entry.removeprefix("scripts/")

    def exists(self, entry):
        relative = self._entry(entry)
        if self.kind == "dir":
            return (self.root / relative).is_file()
        return self._zip_prefix + relative in self._zf.namelist()

    def read_text(self, entry):
        relative = self._entry(entry)
        if self.kind == "dir":
            return (self.root / relative).read_text(encoding="utf-8-sig")
        return self._zf.read(self._zip_prefix + relative).decode("utf-8-sig")

    def listdir_prefix(self, prefix):
        relative = self._entry(prefix)
        if self.kind == "dir":
            base = self.root / relative
            for path in sorted(base.rglob("*.lua")):
                yield "scripts/" + path.relative_to(self.root).as_posix()
        else:
            for info in self._zf.infolist():
                name = info.filename
                if not info.is_dir() and name.startswith(self._zip_prefix + relative):
                    yield "scripts/" + name.removeprefix(self._zip_prefix)


def mask_lua_noncode(src):
    """Mask comments and strings, preserving offsets and line numbers."""
    chars = list(src)
    i = 0
    while i < len(src):
        start = i
        comment = src.startswith("--", i)
        offset = i + 2 if comment else i
        long_open = re.match(r"\[(=*)\[", src[offset:]) if src[offset:offset + 1] == "[" else None
        if long_open:
            closing = "]" + long_open.group(1) + "]"
            end = src.find(closing, offset + long_open.end())
            i = len(src) if end < 0 else end + len(closing)
        elif comment:
            end = src.find("\n", i)
            i = len(src) if end < 0 else end
        elif src[i] in ("'", '"'):
            quote = src[i]
            i += 1
            while i < len(src):
                if src[i] == "\\":
                    i += 2
                elif src[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
        else:
            i += 1
            continue
        for j in range(start, min(i, len(src))):
            if chars[j] not in "\r\n":
                chars[j] = " "
    return "".join(chars)


def declared_members(text):
    code = mask_lua_noncode(text)
    methods = set(re.findall(r"function\s+[\w.]+\s*[:.]\s*(\w+)\s*\(", code))
    methods.update(re.findall(r"(?:self|[A-Z]\w*)\.(\w+)\s*=\s*function\s*\(", code))
    fields = set(re.findall(r"self\.(\w+)\s*=(?!=)", code)) - methods
    return methods, fields


def collect_component_members(reader, replica=False):
    methods, fields = {}, {}
    for entry in reader.listdir_prefix("scripts/components/"):
        if not entry.endswith(".lua"):
            continue
        name = entry.rsplit("/", 1)[-1][:-4]
        if name.endswith("_replica") != replica:
            continue
        if replica:
            name = name[:-8]
        methods[name], fields[name] = declared_members(reader.read_text(entry))
    return methods, fields


def collect_component_methods(reader):
    return collect_component_members(reader)[0]


def collect_entityscript_methods(reader):
    methods = set()
    for entry in ("scripts/entityscript.lua", "scripts/entityreplica.lua"):
        if reader.exists(entry):
            methods.update(declared_members(reader.read_text(entry))[0])
    return methods


def lua_files_from_args(paths):
    files = set()
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            raise ValueError("input path does not exist: %s" % path)
        if path.is_dir():
            found = [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() == ".lua"]
            if not found:
                raise ValueError("no Lua files under input directory: %s" % path)
            files.update(p.resolve() for p in found)
        elif path.suffix.lower() == ".lua":
            files.add(path.resolve())
        else:
            raise ValueError("input is not a Lua file: %s" % path)
    return sorted(files)


@dataclass
class CheckResult:
    verified: int = 0
    examined: int = 0
    problems: list = field(default_factory=list)
    reviews: list = field(default_factory=list)


def check_file(path, comp_methods, es_methods, quiet=False, *, replica_methods=None,
               component_fields=None, replica_fields=None):
    code = mask_lua_noncode(Path(path).read_text(encoding="utf-8-sig"))
    result = CheckResult()
    catalogs = {"components": comp_methods, "replica": replica_methods or {}}
    fields = {"components": component_fields or {}, "replica": replica_fields or {}}
    direct = re.compile(r"\b(components|replica)\s*\.\s*(\w+)\s*[:.]\s*(\w+)\s*\(")

    def location(match):
        return "%s:%d" % (path, code.count("\n", 0, match.start()) + 1)

    for match in direct.finditer(code):
        side, component, method = match.groups()
        label = "%s %s.%s:%s()" % (location(match), side, component, method)
        known = catalogs[side].get(component)
        result.examined += 1
        if known is None:
            result.reviews.append(label + " -- source not found (custom or dynamic component)")
        elif method in known:
            result.verified += 1
            if not quiet:
                print("  [ok] " + label)
        elif method in fields[side].get(component, set()):
            result.reviews.append(label + " -- field exists, callability is not established")
        else:
            result.problems.append(label + " -- method declaration NOT FOUND on this side")

    for match in re.finditer(r"(?<![\w.])inst\s*:\s*(\w+)\s*\(", code):
        method = match.group(1)
        result.examined += 1
        if method in es_methods:
            result.verified += 1
        else:
            result.reviews.append("%s inst:%s() -- engine/prefab/dynamic method needs verification"
                                  % (location(match), method))

    # Alias scope, reassignment and shadowing require Lua type analysis.
    # Flag these calls for review rather than silently declaring them verified.
    aliases = set(re.findall(r"\b(\w+)\s*=(?!=)\s*[\w.]+\.(?:components|replica)\.\w+\b", code))
    for alias in sorted(aliases):
        for match in re.finditer(r"(?<![\w.])" + re.escape(alias) + r"\s*[:.]\s*(\w+)\s*\(", code):
            result.reviews.append("%s %s:%s() -- component alias needs scope/type review"
                                  % (location(match), alias, match.group(1)))

    for match in re.finditer(r"\b(?:components|replica)\s*\[|\b(?:components|replica)\.\w+\s*\[", code):
        result.reviews.append(location(match) + " -- computed component/member access needs review")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--dst")
    source.add_argument("--zip")
    source.add_argument("--scripts-dir")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    reader = None
    try:
        files = lua_files_from_args(args.files)
        kind, root = resolve_scripts_source(args)
        reader = ScriptsReader(kind, root)
        components, component_fields = collect_component_members(reader)
        replicas, replica_fields = collect_component_members(reader, replica=True)
        entity_methods = collect_entityscript_methods(reader)
        if not components or not entity_methods:
            raise ValueError("source index is empty/incomplete: %s" % root)
        if not args.quiet:
            print("[check_api] source: %s (%s); components=%d, replicas=%d"
                  % (reader.root, kind, len(components), len(replicas)))
        total = CheckResult()
        for path in files:
            checked = check_file(path, components, entity_methods, args.quiet,
                                 replica_methods=replicas, component_fields=component_fields,
                                 replica_fields=replica_fields)
            total.verified += checked.verified
            total.examined += checked.examined
            total.problems.extend(checked.problems)
            total.reviews.extend(checked.reviews)
        for issue in total.problems:
            print("[X] " + issue)
        for issue in total.reviews:
            print("[?] " + issue)
        counts = "%d file(s), %d matched direct declaration(s), %d examined direct call(s)" % (
            len(files), total.verified, total.examined)
        if total.problems:
            print("check_api: FAIL -- %s; %d missing declaration(s), %d review item(s)"
                  % (counts, len(total.problems), len(total.reviews)))
            return 1
        if total.reviews or not total.examined:
            print("check_api: REVIEW -- %s; %d review item(s); no runtime guarantee"
                  % (counts, len(total.reviews)))
            return 3
        print("check_api: MATCHED -- %s; static declaration check only" % counts)
        return 0
    except (OSError, ValueError, KeyError, UnicodeError, zipfile.BadZipFile) as exc:
        print("check_api: ERROR -- %s" % exc, file=sys.stderr)
        return 2
    finally:
        if reader is not None:
            reader.close()


if __name__ == "__main__":
    sys.exit(main())
