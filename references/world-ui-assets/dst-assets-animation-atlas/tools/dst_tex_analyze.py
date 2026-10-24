
# KTEX 批次/预览/全量分析（与 ktex_decode.py 同目录协同，import 依赖该文件）
# 用途：ktex_batch 批量统计格式分布+像素统计 / ktex_ascii 无Pillow快速ASCII预览 / dst_tex_analyze 全量研究解码
# 注意：文件内硬编码作者本机路径（ROOT/MODROOT），复用前改为目标目录。暂未在本环境验证运行。
#
# -*- coding: utf-8 -*-
"""KTEX 解码器+分析器 (格式已破解 2026-08-11)
格式: "KTEX"(4) + format u32(4) + N个mip头(每个10B: w u16, h u16, pitch u16, size u32) + 连续数据区
format: 低16位 0x2220族=DXT5, 0x2200族=DXT1; 高16位为标志(未知,不影响解码)
用法: python dst_tex_analyze.py [--png N] [--stat]
"""
import os, sys, struct, collections, zlib, io
from pathlib import Path

ROOT = Path(os.environ.get("MODROOT", r"E:\神秘复苏\饥荒大型mod"))
OUT = Path(os.environ.get("PNGOUT", r"E:\神秘复苏\dist\tex_samples"))
sys.stdout.reconfigure(encoding="utf-8")

def parse_tex(d):
    """返回 (fmt, [(w,h,size,dataoff)]) 或 None"""
    if len(d) < 18 or d[:4] != b"KTEX":
        return None
    fmt = struct.unpack_from("<I", d, 4)[0]
    mips = []
    off = 8
    total = 0
    while off + 10 <= len(d):
        w, h = struct.unpack_from("<HH", d, off)
        size = struct.unpack_from("<I", d, off + 6)[0]
        if not w or not h:
            break
        mips.append((w, h, size))
        total += size
        off += 10
        if 8 + off - 8 + total >= len(d):
            break
    # 数据起点 = 8 + 10*N
    data_start = 8 + 10 * len(mips)
    if data_start + total > len(d):
        return None
    return fmt, mips, data_start

FMT_ID = {0x20: "DXT5", 0x00: "DXT1"}

def fmt_name(fmt):
    return FMT_ID.get(fmt & 0xFF, hex(fmt))

# ---------- DXT 解码 ----------
def dxt1_block(b):
    c0, c1 = struct.unpack_from("<HH", b, 0)
    r0, g0, b0 = ((c0 >> 11) & 31) << 3, ((c0 >> 5) & 63) << 2, (c0 & 31) << 3
    r1, g1, b1 = ((c1 >> 11) & 31) << 3, ((c1 >> 5) & 63) << 2, (c1 & 31) << 3
    pal = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
    if c0 > c1:
        pal += [((2*r0+r1)//3, (2*g0+g1)//3, (2*b0+b1)//3, 255),
                ((r0+2*r1)//3, (g0+2*g1)//3, (b0+2*b1)//3, 255)]
    else:
        pal += [((r0+r1)//2, (g0+g1)//2, (b0+b1)//2, 255), (0, 0, 0, 0)]
    idx = int.from_bytes(b[4:8], "little")
    return [pal[(idx >> (2*i)) & 3] for i in range(16)]

def dxt5_block(b):
    a0, a1 = b[0], b[1]
    al = [a0, a1]
    if a0 > a1:
        al += [(6*a0+a1)//7, (5*a0+2*a1)//7, (4*a0+3*a1)//7,
               (3*a0+4*a1)//7, (2*a0+5*a1)//7, (a0+6*a1)//7]
    else:
        al += [(4*a0+a1)//5, (3*a0+2*a1)//5, (2*a0+3*a1)//5,
               (a0+4*a1)//5, 0, 255]
    ai = int.from_bytes(b[2:8], "little")
    c0, c1 = struct.unpack_from("<HH", b, 8)
    r0, g0, b0 = ((c0 >> 11) & 31) << 3, ((c0 >> 5) & 63) << 2, (c0 & 31) << 3
    r1, g1, b1 = ((c1 >> 11) & 31) << 3, ((c1 >> 5) & 63) << 2, (c1 & 31) << 3
    if c0 > c1:
        rgb = [(r0, g0, b0), (r1, g1, b1),
               ((2*r0+r1)//3, (2*g0+g1)//3, (2*b0+b1)//3),
               ((r0+2*r1)//3, (g0+2*g1)//3, (b0+2*b1)//3)]
    else:
        rgb = [(r0, g0, b0), (r1, g1, b1),
               ((r0+r1)//2, (g0+g1)//2, (b0+b1)//2), (0, 0, 0)]
    idx = int.from_bytes(b[12:16], "little")
    out = []
    for i in range(16):
        r, g, b = rgb[(idx >> (2*i)) & 3]
        out.append((r, g, b, al[(ai >> (3*i)) & 7]))
    return out

def decode_mip(data, w, h, fmt):
    if fmt & 0xFF == 0x20:  # DXT5
        n, dec = 16, dxt5_block
    elif fmt & 0xFF == 0x00:  # DXT1
        n, dec = 8, dxt1_block
    else:
        return None
    bw, bh = (w + 3) // 4, (h + 3) // 4
    out = bytearray(w * h * 4)
    for by in range(bh):
        for bx in range(bw):
            chunk = data[(by * bw + bx) * n:(by * bw + bx + 1) * n]
            if len(chunk) < n:
                return None
            px = dec(chunk)
            for j in range(4):
                for i in range(4):
                    x, y = bx * 4 + i, by * 4 + j
                    if x < w and y < h:
                        o = (y * w + x) * 4
                        out[o:o + 4] = bytes(px[j * 4 + i])
    return bytes(out)

def save_png(w, h, rgba, p):
    raw = b"".join(b"\x00" + bytes(rgba[y*w*4:(y+1)*w*4]) for y in range(h))
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c))
    with open(p, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))

# ---------- 统计 ----------
fmt_count = collections.Counter()
size_bucket = collections.Counter()
mip_count = collections.Counter()
non_pow2 = []
samples = []
total = 0
for path in ROOT.rglob("*.tex"):
    try:
        parsed = parse_tex(path.read_bytes())
    except Exception:
        continue
    if parsed is None:
        continue
    fmt, mips, dstart = parsed
    total += 1
    fmt_count[fmt_name(fmt)] += 1
    mip_count[len(mips)] += 1
    w, h = mips[0][0], mips[0][1]
    b = ">=2048" if max(w, h) >= 2048 else ">=1024" if max(w, h) >= 1024 else ">=512" if max(w, h) >= 512 else ">=256" if max(w, h) >= 256 else ">=128" if max(w, h) >= 128 else ">=64" if max(w, h) >= 64 else "<64"
    size_bucket[b] += 1
    if (w & (w - 1)) or (h & (h - 1)):
        non_pow2.append((str(path), w, h))
    samples.append((path, fmt, mips, dstart))

print(f"TOTAL {total}  FORMAT {dict(fmt_count)}  MIPS {dict(sorted(mip_count.items()))}")
print("SIZES", dict(sorted(size_bucket.items(), key=lambda kv: -int(kv[0].strip(">=<")))))
print("NON_POW2", len(non_pow2), non_pow2[:6])

if "--stat" in sys.argv:
    sys.exit(0)

# ---------- 抽样解码 ----------
# 每mod每类取1-3张: turf类(文件名含turf/ground/tile), 建筑(含building/home/house/station/machine), 生物(含monster/creature/boss/animal), 植物, UI, 图标(64x64以下)
CATS = {
    "turf": lambda p: any(k in p.lower() for k in ("turf", "ground", "tile", "road", "terrain", "floor", "soil", "dirt")),
    "building": lambda p: any(k in p.lower() for k in ("building", "house", "home", "station", "machine", "temple", "palace", "furniture", "altar", "structure")),
    "creature": lambda p: any(k in p.lower() for k in ("monster", "creature", "boss", "animal", "bird", "deer", "pig", "spider", "dragon", "god", "beast", "head")),
    "plant": lambda p: any(k in p.lower() for k in ("plant", "tree", "crop", "flower", "grass", "mushroom", "crop")),
    "ui": lambda p: any(k in p.lower() for k in ("icon", "button", "ui", "hud", "menu", "badge", "slot")),
}
import re
def cat_of(p):
    pl = p.lower()
    for c, fn in CATS.items():
        if fn(pl):
            return c
    return "other"

per_mod = collections.defaultdict(collections.Counter)
for path, fmt, mips, dstart in samples:
    per_mod[str(path).split(os.sep)[-2]][cat_of(str(path))] += 1

print("PER_MOD_CAT:")
for m, c in per_mod.items():
    print(" ", m, dict(c))

# 解码: 每mod每类最多2张, 全局限60张
OUT.mkdir(parents=True, exist_ok=True)
picked = collections.Counter()
n = 0
for path, fmt, mips, dstart in samples:
    mod = str(path).split(os.sep)[-2]
    cat = cat_of(str(path))
    if picked[(mod, cat)] >= 2 or n >= 60:
        continue
    if cat == "other" and picked[(mod, cat)] >= 1:
        continue
    d = path.read_bytes()
    w, h, size = mips[0]
    data_start = dstart
    payload = d[data_start:]
    dec = decode_mip(payload, w, h, fmt)
    if dec is None:
        continue
    png = OUT / f"{mod[:10]}_{cat}_{w}x{h}_{fmt_name(fmt)}_{n}.png"
    save_png(w, h, dec, png)
    picked[(mod, cat)] += 1
    n += 1
print(f"DECODED {n} -> {OUT}")
