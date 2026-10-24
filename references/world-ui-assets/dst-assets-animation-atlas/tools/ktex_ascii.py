
# KTEX 批次/预览/全量分析（与 ktex_decode.py 同目录协同，import 依赖该文件）
# 用途：ktex_batch 批量统计格式分布+像素统计 / ktex_ascii 无Pillow快速ASCII预览 / dst_tex_analyze 全量研究解码
# 注意：文件内硬编码作者本机路径（ROOT/MODROOT），复用前改为目标目录。暂未在本环境验证运行。
#
# -*- coding: utf-8 -*-
"""KTEX ASCII 色块预览: 解码 tex -> 缩略字符画(色相+亮度) -> 网格分区统计。
用法: python ktex_ascii.py <tex路径> [--xml xxx.xml] [--element name] [--cols 80] [--rows 36]"""
import sys, os, struct
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ktex_decode import parse_ktex, decode_mip

# 色相 -> 字符 (RGB 主色)
HUE_CHARS = {
    'R': 'R', 'G': 'G', 'B': 'B',
    'C': 'c', 'M': 'm', 'Y': 'y',   # 青/品红/黄
    'K': 'K', 'W': 'W',             # 黑/白
}
BRIGHT_CHARS = ' .:-=+*#%@'  # 低到高

def rgb_to_hue_char(r, g, b, a):
    if a < 40:
        return ' '
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 24:  # 灰
        v = (r + g + b) / 3
        if v < 40: return 'K'
        if v > 210: return 'W'
        return BRIGHT_CHARS[min(9, int(v / 26))]
    sat = (mx - mn) / mx
    if sat < 0.25:
        return BRIGHT_CHARS[min(9, int((r+g+b)/3 / 26))]
    if r == mx and g >= b: return 'R' if g < 128 else 'y'
    if r == mx and b > g: return 'm'
    if g == mx and r >= b: return 'G'
    if g == mx and b > r: return 'c'
    if b == mx: return 'B'
    return '?'

def ascii_preview(img, cols=72, rows=34):
    w, h = img.size
    img2 = img.resize((cols, rows), Image.LANCZOS)
    px = img2.load()
    out = []
    for y in range(rows):
        line = []
        for x in range(cols):
            r, g, b, a = px[x, y]
            line.append(rgb_to_hue_char(r, g, b, a))
        out.append(''.join(line))
    return out

def grid_stats(img, grid=4):
    w, h = img.size
    cw, ch = w // grid, h // grid
    lines = []
    for gy in range(grid):
        row = []
        for gx in range(grid):
            region = img.crop((gx*cw, gy*ch, (gx+1)*cw, (gy+1)*ch)).resize((1,1), Image.LANCZOS)
            r, g, b, a = region.getpixel((0,0))
            row.append(f'{rgb_to_hue_char(r,g,b,a)}{int((r+g+b)/3):03d}')
        lines.append(' '.join(row))
    return lines

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = {}
    for i, a in enumerate(sys.argv[1:]):
        if a.startswith('--') and i+2 <= len(sys.argv):
            opts[a[2:]] = sys.argv[i+2]
    tex = args[0]
    cols = int(opts.get('cols', 72))
    rows = int(opts.get('rows', 34))

    data = open(tex, 'rb').read()
    fmt, mips, off = parse_ktex(data)
    img = decode_mip(data, fmt, mips, 0)

    # 如果给了 xml + element，裁剪元素区域
    if opts.get('xml') and opts.get('element'):
        import re
        xml = open(opts['xml'], encoding='utf-8', errors='ignore').read()
        m = re.search(r'<Element name="%s" u1="([\d.]+)" u2="([\d.]+)" v1="([\d.]+)" v2="([\d.]+)"' % re.escape(opts['element']), xml)
        if m:
            u1, u2, v1, v2 = [float(x) for x in m.groups()]
            bw, bh = img.size
            box = (int(u1*bw), int((1-v2)*bh), int(u2*bw), int((1-v1)*bh))
            if box[2] > box[0] and box[3] > box[1]:
                img = img.crop(box)

    print(f'== {os.path.basename(tex)} fmt=0x{fmt:08X} mip0={mips[0][0]}x{mips[0][1]} (预览 {cols}x{rows}) ==')
    for line in ascii_preview(img, cols, rows):
        print(line)
    print('-- 4x4 网格 (字符=色相 R红G绿B蓝c青m品y黄K黑W白.灰, 数字=亮度) --')
    for line in grid_stats(img, 4):
        print('  ' + line)
    # 整体统计
    from ktex_decode import stats
    s = stats(img)
    print(f'-- avg_rgb={s["avg_rgb"]} alpha={s["avg_alpha"]} 不透明{s["opaque%"]}% 透明{s["transparent%"]}% 饱和{s["avg_saturation"]} 亮度{s["avg_brightness"]} 描边像素{s["edge_transparent_px%"]}%')
    print(f'-- 主色: {s["top_colors"][:6]}')

if __name__ == '__main__':
    main()
