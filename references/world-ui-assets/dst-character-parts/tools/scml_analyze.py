#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 说明：吸收自外部参考的支撑脚本，当前【暂未在本环境验证可运行】；运行验证留待后续工具计划。
# 依赖：纯 Python 标准库（stdlib）。配套 official-esctemplate-spec.md 用于导出官方 20 部位规范表。
"""SCML 分析器：解析 BrashMonkey Spriter 工程 → 部位规范表。

用途：
  - 生成 references/character-esc.md 的 20 部位规范表（Markdown 表格）
  - 输出 JSON（--json），供 char_sheet_gen.py 取 pivot/z 顺序程序化生成人物

用法：
  python scml_analyze.py <file.scml> [-j out.json] [--json-only]

输出：
  - folder 表：id / 名称 / 文件数 / 每文件尺寸+pivot
  - timeline 统计：总数 / z-index 区间 / 按 folder 分组符号数
  - 动画表：名称 / 时长(ms) / 帧数(40fps) / 帧率
  - timeline 全清单（编译符号名 = <folder>_<file>_<timelineID>）

纯 Python 标准库，无第三方依赖。
"""
import sys
import json
import xml.etree.ElementTree as ET
from collections import defaultdict

# Windows 控制台 UTF-8 输出
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


def sdbm(s):
    """sdbm 哈希（小写），与 DST anim.bin 编译符号一致。"""
    h = 0
    for c in s.lower():
        h = (h * 65599 + ord(c)) & 0xFFFFFFFF
    return h


def parse(scml_path):
    tree = ET.parse(scml_path)
    root = tree.getroot()

    folders = []
    for f in root.findall("folder"):
        files = []
        for img in f.findall("file"):
            files.append({
                "id": int(img.get("id")),
                "name": img.get("name"),
                "width": int(img.get("width", 0)),
                "height": int(img.get("height", 0)),
                "pivot_x": float(img.get("pivot_x", 0)),
                "pivot_y": float(img.get("pivot_y", 0)),
            })
        folders.append({"id": int(f.get("id")), "name": f.get("name"), "files": files})

    animations = []
    entities = root.findall("entity") or [root]
    for ent in entities:
        for a in ent.findall("animation"):
            anim = {
                "id": int(a.get("id")),
                "name": a.get("name"),
                "entity": ent.get("name", ""),
                "length": int(a.get("length", 0)),
                "fps": float(a.get("fps", 40)),
                "mainline_keys": len(a.findall("mainline/key")),
                "timeline_count": len(a.findall("timeline")),
            }
            animations.append(anim)

    # timeline 按动画收集（编译符号名 = <folder>_<file>_<timelineID>；
    # z_index 来自 mainline 的 object_ref，timeline 顺序即 z 顺序）
    timelines = defaultdict(list)
    for ent in entities:
        for a in ent.findall("animation"):
            refs = {}
            for ref in a.findall("mainline/key/object_ref"):
                t = ref.get("timeline")
                if t is not None:
                    refs[t] = max(refs.get(t, -1), int(ref.get("z_index", 0)))
            for tl in a.findall("timeline"):
                tid = tl.get("id")
                objs = tl.findall("key/object")
                if not objs:
                    continue
                obj = objs[0]
                z = refs.get(tid, 0)
                fid = int(obj.get("folder"))
                fname = folders[fid]["name"] if fid < len(folders) else f"?{fid}"
                fidx = obj.get("file")
                timelines[fname].append({
                    "timeline_id": int(tid),
                    "symbol": f"{fname}_{fidx}_{tid}",
                    "z_index": z,
                    "folder": fid,
                "file": int(fidx) if fidx else -1,
                "x": float(obj.get("x", 0)),
                "y": float(obj.get("y", 0)),
            })

    return {"folders": folders, "animations": animations, "timelines": timelines}


def md_table(folders):
    out = ["| folder id | 部位名 | 帧数 | 尺寸 | pivot |", "|---|---|---|---|---|"]
    for f in folders:
        if not f["files"]:
            continue
        dims = set()
        pivots = set()
        for img in f["files"]:
            dims.add(f"{img['width']}x{img['height']}")
            pivots.add(f"({img['pivot_x']:.3f},{img['pivot_y']:.3f})")
        out.append(f"| {f['id']} | {f['name']} | {len(f['files'])} | "
                   f"{' / '.join(sorted(dims))} | {' / '.join(sorted(pivots))} |")
    return "\n".join(out)


def report(data):
    lines = []
    folders = data["folders"]
    total_files = sum(len(f["files"]) for f in folders)
    lines.append(f"## folder 总数: {len(folders)}，文件(帧)总数: {total_files}")
    lines.append("")
    lines.append(md_table(folders))
    lines.append("")
    for a in data["animations"]:
        frames = round(a["length"] / 1000 * a["fps"]) if a["fps"] else 0
        lines.append(f"## 动画: {a['name']} (id={a['id']}, length={a['length']}ms, "
                     f"{frames}帧@{a['fps']:g}fps, mainline keys={a['mainline_keys']}, "
                     f"timelines={a['timeline_count']})")
        lines.append("")
        for fname in sorted(data["timelines"]):
            tls = data["timelines"][fname]
            zs = sorted(t["z_index"] for t in tls)
            lines.append(f"- **{fname}**（{len(tls)} 条 timeline，z: {zs[0]}~{zs[-1]}）: "
                         f"{', '.join(t['symbol'] for t in sorted(tls, key=lambda t: t['z_index']))}")
        lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    scml_path = sys.argv[1]
    out_json = None
    json_only = False
    for i, a in enumerate(sys.argv[2:], start=2):
        if a == "-j" and i + 1 < len(sys.argv):
            out_json = sys.argv[i + 1]
        elif a == "--json-only":
            json_only = True

    data = parse(scml_path)
    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)
        print(f"JSON -> {out_json}")
    if not json_only:
        print(report(data))
    # sdbm 校验表（帮助核对 anim.bin 符号）
    print("\n## sdbm 哈希抽查（小写，DST anim.bin 用）")
    for name in ["template", "build_player", "hair", "headbase", "torso_pelvis", "esctemplate"]:
        print(f"- {name}: 0x{sdbm(name):08X}")


if __name__ == "__main__":
    main()
