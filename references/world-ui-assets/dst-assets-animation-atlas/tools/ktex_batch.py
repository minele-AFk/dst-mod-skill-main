
# KTEX 批次/预览/全量分析（与 ktex_decode.py 同目录协同，import 依赖该文件）
# 用途：ktex_batch 批量统计格式分布+像素统计 / ktex_ascii 无Pillow快速ASCII预览 / dst_tex_analyze 全量研究解码
# 注意：文件内硬编码作者本机路径（ROOT/MODROOT），复用前改为目标目录。暂未在本环境验证运行。
#
# -*- coding: utf-8 -*-
"""批量分析 KTEX: 统计全部 tex 的格式分布 + 每类代表性样本的像素统计"""
import struct, sys, os, glob, json
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ktex_decode import parse_ktex, decode_mip, stats

ROOT = r"C:\Users\22308\Desktop\new\3544387985"

def probe(path):
    try:
        data = open(path, 'rb').read()
        if data[:4] != b'KTEX':
            return None
        fmt, mips, off = parse_ktex(data)
        return fmt, mips
    except Exception:
        return None

# ---- 1. 全量格式分布 ----
fmt_stats = defaultdict(lambda: [0, 0, 0, 0])  # fmt -> [count, total_w*h, max_w, max_h]
sizes = defaultdict(int)
total = 0
by_dir = defaultdict(lambda: [0, 0, 0])  # dir -> [count, dxt_count, rgba_count]

all_tex = glob.glob(os.path.join(ROOT, '**', '*.tex'), recursive=True)
for p in all_tex:
    total += 1
    r = probe(p)
    if r is None:
        continue
    fmt, mips = r
    w, h = mips[0][0], mips[0][1]
    key = 'RGBA8' if fmt & 0xFFF0 == 0x2240 else ('DXT1' if fmt & 0xFFF0 == 0x6220 else ('DXT5' if fmt & 0xFFF0 == 0x8220 else 'other'))
    # 用块大小确认
    m0 = mips[0]
    per_block = m0[3] // (((m0[0]+3)//4) * ((m0[1]+3)//4)) if m0[3] < m0[0]*m0[1]*2 else None
    if m0[3] == m0[0]*m0[1]*4:
        key = 'RGBA8'
    elif per_block == 16:
        key = 'DXT5'
    elif per_block == 8:
        key = 'DXT1'
    fmt_stats[key][0] += 1
    fmt_stats[key][1] += w * h
    fmt_stats[key][2] = max(fmt_stats[key][2], w)
    fmt_stats[key][3] = max(fmt_stats[key][3], h)
    sizes[m0[3]] += 1
    d = os.path.basename(os.path.dirname(p))
    by_dir[d][0] += 1
    by_dir[d][1 if key != 'RGBA8' else 2] += 1

print('===== 全量 tex 统计 =====')
print('tex 文件总数:', total)
for k, v in sorted(fmt_stats.items()):
    print(f'  {k}: {v[0]} 个, 总像素 {v[1]:,}, 最大 {v[2]}x{v[3]}')
print('按目录:')
for d, v in sorted(by_dir.items(), key=lambda kv: -kv[1][0])[:20]:
    print(f'  {d}: {v[0]} (DXT {v[1]}, RGBA {v[2]})')

# ---- 2. 代表性样本像素统计 ----
samples = [
    (r"modicon.tex", "modicon"),
    (r"atbooks2\images\tbat_ui.tex", "atbooks2_ui"),
    (r"atbooks2\images\tbat_inventoryimages.tex", "atbooks2_inv"),
    (r"atbooks2\images\tbat_hud.tex", "atbooks2_hud"),
    (r"atbooks2\images\tbat_crafting_menu_icons.tex", "atbooks2_craft"),
    (r"atbooks2\minimap\tbat_minimap.tex", "atbooks2_minimap"),
    (r"atbooks1\levels\textures\tbat_milkyway_cloud.tex", "turf_milkyway_cloud"),
    (r"atbooks1\levels\textures\tbat_turf_fallen_cherry_blossoms.tex", "turf_cherry"),
    (r"atbooks1\levels\textures\tbat_turf_lavender_dusk.tex", "turf_lavender"),
    (r"atbooks1\levels\textures\tbat_turf_emerald_feather_leaves.tex", "turf_emerald"),
    (r"atbooks1\levels\textures\tbat_turf_fake_ocean_shallow.tex", "turf_fakeocean"),
    (r"atbooks1\levels\textures\tbat_turf_checkerfloor_pink.tex", "turf_checker_pink"),
    (r"atbooks1\levels\textures\tbat_miragewood_floor_purple.tex", "turf_mirage_purple"),
    (r"atbooks1\levels\textures\tbat_redautumn_maplepath.tex", "turf_maplepath"),
]

print('\n===== 代表性样本 =====')
results = {}
for rel, name in samples:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print(f'{name}: MISSING')
        continue
    try:
        data = open(p, 'rb').read()
        fmt, mips, off = parse_ktex(data)
        img = decode_mip(data, fmt, mips, 0)
        s = stats(img)
        results[name] = s
        print(f'[{name}] {s["size"]} fmt=0x{fmt:08X} avg_rgb={s["avg_rgb"]} alpha={s["avg_alpha"]} '
              f'opaque={s["opaque%"]}% trans={s["transparent%"]}% sat={s["avg_saturation"]} '
              f'bright={s["avg_brightness"]} edge={s["edge_transparent_px%"]}% top={s["top_colors"][:4]}')
    except Exception as e:
        print(f'[{name}] ERROR {e}')

# ---- 3. 地皮纹理合集统计 ----
print('\n===== levels/textures 全部 =====')
turf_tex = glob.glob(os.path.join(ROOT, 'atbooks1', 'levels', 'textures', '*.tex'))
turf_tex = [t for t in turf_tex if '_mini' not in os.path.basename(t)]
turf_stats = []
for p in turf_tex:
    try:
        data = open(p, 'rb').read()
        fmt, mips, off = parse_ktex(data)
        img = decode_mip(data, fmt, mips, 0)
        s = stats(img)
        turf_stats.append((os.path.basename(p), s))
    except Exception:
        pass
avg_sat = sum(s['avg_saturation'] for _, s in turf_stats) // max(1, len(turf_stats))
avg_bri = sum(s['avg_brightness'] for _, s in turf_stats) // max(1, len(turf_stats))
print(f'地皮纹理 {len(turf_stats)} 个, 平均饱和 {avg_sat}, 平均亮度 {avg_bri}')
for n, s in sorted(turf_stats, key=lambda x: x[1]['avg_saturation']):
    print(f'  {n}: {s["size"]} rgb={s["avg_rgb"]} sat={s["avg_saturation"]} bri={s["avg_brightness"]}')
