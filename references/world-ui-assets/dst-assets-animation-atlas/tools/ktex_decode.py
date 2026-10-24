# -*- coding: utf-8 -*-
"""
KTEX (DST) 纹理解码器 + 像素统计。用法: python ktex_decode.py <file.tex> [out.png]

依赖：Pillow（仅用于读取/写出 PNG；若只统计像素可改造成纯标准库）。
用途：与 dst-assets-animation-atlas 的 ktex-format.md 配套，用于读懂 tex 字节布局 ——
      DXT5/DXT1/RGBA8 判别、mip 头解析、数据区统计。
说明：本文件为吸收自外部参考的支撑脚本，当前【暂未在本环境验证可运行】；
      运行验证与依赖配置留待后续工具计划统一处理。仅作格式理解 / 后续迁移底本。
"""
import struct, sys, os
from PIL import Image

def expand_rgb565(c):
    r = (c >> 11) & 0x1F; g = (c >> 5) & 0x3F; b = c & 0x1F
    return (r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)

def decode_bc1(block, w, h):
    """8 bytes -> 4x4 RGB"""
    c0, c1 = struct.unpack('<HH', block[:4])
    col = [expand_rgb565(c0), expand_rgb565(c1)]
    if c0 > c1:
        col += [((col[0][0]*2+col[1][0])//3, (col[0][1]*2+col[1][1])//3, (col[0][2]*2+col[1][2])//3),
                ((col[0][0]+col[1][0]*2)//3, (col[0][1]+col[1][1]*2)//3, (col[0][2]+col[1][2]*2)//3)]
        alpha = [255, 255, 255, 255]
    else:
        col += [((col[0][0]+col[1][0])//2, (col[0][1]+col[1][1])//2, (col[0][2]+col[1][2])//2), (0, 0, 0)]
        alpha = [255, 255, 255, 0]
    idx = int.from_bytes(block[4:8], 'little')
    out = []
    for i in range(h):
        row = []
        for j in range(w):
            code = (idx >> (2 * (i * 4 + j))) & 3
            r, g, b = col[code]
            a = alpha[code]
            # 5:0 通道的 0 透明像素在 DXT1 中 alpha 为 0
            row.append((r, g, b, a))
        out.append(row)
    return out

def decode_bc3(block, w, h):
    """16 bytes -> 4x4 RGBA"""
    a0, a1 = block[0], block[1]
    a_idx_bits = int.from_bytes(block[2:8], 'little')
    alpha = []
    for i in range(16):
        code = (a_idx_bits >> (3 * i)) & 7
        if a0 > a1:
            vals = [a0, a1,
                    (6*a0 + a1)//7, (5*a0 + 2*a1)//7, (4*a0 + 3*a1)//7,
                    (3*a0 + 4*a1)//7, (2*a0 + 5*a1)//7, (a0 + 6*a1)//7]
        else:
            vals = [a0, a1,
                    (4*a0 + a1)//5, (3*a0 + 2*a1)//5, (2*a0 + 3*a1)//5,
                    (a0 + 4*a1)//5, 0, 255]
        alpha.append(vals[code])
    rgb = decode_bc1(block[8:16], 4, 4)
    out = []
    for i in range(h):
        row = []
        for j in range(w):
            r, g, b, _ = rgb[i][j]
            row.append((r, g, b, alpha[i * 4 + j]))
        out.append(row)
    return out

def parse_ktex(data):
    if data[:4] != b'KTEX':
        raise ValueError('not ktex')
    fmt = struct.unpack('<I', data[4:8])[0]
    off = 8
    mips = []
    while off + 10 <= len(data):
        w, h, pitch, size = struct.unpack('<HHHI', data[off:off+10])
        if not (0 < w <= 16384 and 0 < h <= 16384) or size == 0:
            break
        mips.append((w, h, pitch, size))
        off += 10
        if off + size > len(data):
            break
        # 若下一块不像合法头且数据恰好接续，则结束
        if off + 10 <= len(data):
            w2, h2, p2, s2 = struct.unpack('<HHHI', data[off:off+10])
            if not (0 < w2 <= 16384 and 0 < h2 <= 16384 and 0 < s2 <= 1 << 28):
                break
    return fmt, mips, off

def decode_mip(data, fmt, mips, mip_index=0):
    w, h, pitch, size = mips[mip_index]
    off = 8 + 10 * len(mips)
    for i in range(mip_index):
        off += mips[i][3]
    raw = data[off:off+size]
    # 判断格式: 按 size 与 w*h 关系
    if size == w * h * 4:
        img = Image.frombytes('RGBA', (w, h), raw, 'raw', 'RGBA')
        return img
    if size == w * h * 2:
        img = Image.frombytes('RGB', (w, h), raw[:w*h*2], 'raw', 'RGB;16B')
        return img
    if size == w * h * 1:
        # DXT1 -> 需要看颜色是否带 alpha (c0<=c1 且用了透明码)
        bpp = 8
        block_bytes = 8
        bc = decode_bc1
    elif size == w * h // 2:
        bpp = 4
        block_bytes = 8
        bc = decode_bc1
    elif size == w * h * 2:
        bpp = 16
        block_bytes = 16
        bc = decode_bc3
    else:
        # 兜底: 按 size/bw/bh 判断
        bwb = (w + 3) // 4; bhb = (h + 3) // 4
        per_block = size // (bwb * bhb)
        bc = decode_bc3 if per_block == 16 else decode_bc1
    bwb = (w + 3) // 4; bhb = (h + 3) // 4
    block_size = 16 if bc is decode_bc3 else 8
    out = Image.new('RGBA', (w, h))
    px = out.load()
    pos = 0
    for by in range(bhb):
        for bx in range(bwb):
            block = raw[pos:pos + block_size]
            block = block + b'\x00' * (block_size - len(block))
            cells = bc(block, min(4, w - bx*4), min(4, h - by*4))
            for i, row in enumerate(cells):
                for j, pix in enumerate(row):
                    px[bx*4+j, by*4+i] = pix
            pos += block_size
    return out

def stats(img):
    px = img.load()
    w, h = img.size
    n = w * h
    rsum = gsum = bsum = asum = 0
    sat_sum = 0; bright_sum = 0
    hist = {}
    opaque = 0; transparent = 0; semi = 0
    edge_transp = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            rsum += r; gsum += g; bsum += b; asum += a
            mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn) * 255 // (mx or 1)
            sat_sum += sat
            bright_sum += (r + g + b) // 3
            if a >= 250: opaque += 1
            elif a <= 5: transparent += 1
            else: semi += 1
            # 描边检测: 透明像素旁的彩色像素
            if a <= 5:
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        nr, ng, nb, na = px[nx, ny]
                        if na > 5:
                            edge_transp += 1
                            break
            key = (r // 32, g // 32, b // 32)
            hist[key] = hist.get(key, 0) + 1
    top = sorted(hist.items(), key=lambda kv: -kv[1])[:8]
    return {
        'size': f'{w}x{h}', 'n': n,
        'avg_rgb': (round(rsum/n), round(gsum/n), round(bsum/n)),
        'avg_alpha': round(asum/n),
        'opaque%': round(opaque*100/n), 'transparent%': round(transparent*100/n), 'semi%': round(semi*100/n),
        'avg_saturation': round(sat_sum/n),
        'avg_brightness': round(bright_sum/n),
        'edge_transparent_px%': round(edge_transp*100/n, 2),
        'top_colors': [('#%02x%02x%02x' % ((k[0]*32+16)&255, (k[1]*32+16)&255, (k[2]*32+16)&255), round(v*100/n)) for k, v in top],
    }

if __name__ == '__main__':
    src = sys.argv[1]
    data = open(src, 'rb').read()
    fmt, mips, off = parse_ktex(data)
    print(f'format=0x{fmt:08X} mips={len(mips)} mip0={mips[0][0]}x{mips[0][1]} size={mips[0][3]}')
    img = decode_mip(data, fmt, mips, 0)
    print('mip0 decoded:', img.size, img.mode)
    if len(sys.argv) > 2:
        img.save(sys.argv[2])
    s = stats(img)
    for k, v in s.items():
        print(f'  {k}: {v}')
