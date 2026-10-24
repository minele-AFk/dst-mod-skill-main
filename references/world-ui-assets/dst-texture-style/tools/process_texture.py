#!/usr/bin/env python3
"""
DST 贴图后处理流水线：生成/编辑图 → 游戏可用透明 PNG。

默认保留 RGBA；trim+fit、64 图标 / 256 画布、原尺寸 REVIEW 拼板。
纯色抠底与旧擦角算法只在显式启用时运行，使用后必须检查是否误伤主体。

用法示例：
  python process_texture.py input.png --name qiankun_bag --out .tmp/.output/tex
  python process_texture.py input.png --name item --out out --icon 64 --body 256 --content-ratio 0.55
  python process_texture.py input.png --name item --out out --key-background
  python process_texture.py input.png --name item --out out --review
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError as exc:
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


def key_background(im: Image.Image, strength: float = 55.0) -> Image.Image:
    """抠除四角采样底色 + 品红/洋红生成底。保留半透明边缘，避免白晕。"""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    x0, y0 = min(2, w - 1), min(2, h - 1)
    x1, y1 = max(0, w - 3), max(0, h - 3)
    samples = [px[x0, y0], px[x1, y0], px[x0, y1], px[x1, y1]]
    br = sum(s[0] for s in samples) / len(samples)
    bg = sum(s[1] for s in samples) / len(samples)
    bb = sum(s[2] for s in samples) / len(samples)

    def is_bg(r: int, g: int, b: int) -> bool:
        if abs(r - br) < strength and abs(g - bg) < strength and abs(b - bb) < strength:
            return True
        # magenta / pink generation backdrops
        if r > 180 and b > 180 and g < 100:
            return True
        if r > 150 and g < 90 and b > 70 and (r - g) > 100 and (b - g) > 40:
            return True
        return False

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10:
                continue
            if is_bg(r, g, b):
                px[x, y] = (0, 0, 0, 0)
    return im


def clear_watermark(im: Image.Image, corner_ratio: float = 0.12) -> Image.Image:
    """去掉右下角常见亮色水印（生成工具残留）。"""
    im = im.convert("RGBA")
    w, h = im.size
    x0 = int(w * (1 - corner_ratio - 0.10))
    y0 = int(h * (1 - corner_ratio))
    for y in range(y0, h):
        for x in range(x0, w):
            r, g, b, a = im.getpixel((x, y))
            if a > 0 and (r + g + b) > 280:
                im.putpixel((x, y), (0, 0, 0, 0))
    return im


def trim_and_fit(
    im: Image.Image,
    target: tuple[int, int],
    content_ratio: float = 0.80,
    resample=Image.Resampling.LANCZOS,
) -> Image.Image:
    """按 alpha bbox 裁切后，把主体缩放到目标画布并居中。

    content_ratio 是**面积占比**（bbox 面积 / 画布面积），与原版实测口径一致：
    - 工具/武器图标约 0.50–0.70（斧 0.56）
    - 偏满装备图标可到 0.85–0.95（木甲 0.97）
    - 256 母版常用 0.70–0.85
    """
    im = im.convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    tw, th = target
    if im.width <= 0 or im.height <= 0:
        return Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    canvas_area = float(tw * th)
    target_bbox_area = max(1.0, content_ratio * canvas_area)
    # uniform scale so bbox area matches target
    src_area = float(im.width * im.height)
    scale = (target_bbox_area / src_area) ** 0.5
    nw = max(1, int(im.width * scale))
    nh = max(1, int(im.height * scale))
    # clamp if exceeds canvas
    if nw > tw or nh > th:
        fit = min(tw / nw, th / nh)
        nw = max(1, int(nw * fit))
        nh = max(1, int(nh * fit))
    im = im.resize((nw, nh), resample)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    # Copy RGBA directly: using im as a mask multiplies alpha a second time.
    canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def checker(size: tuple[int, int], cell: int = 12) -> Image.Image:
    im = Image.new("RGBA", size, (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(215, 215, 215, 255))
    return im


def fill_stats(im: Image.Image) -> tuple[int, int, float]:
    bbox = im.convert("RGBA").getchannel("A").getbbox()
    if not bbox:
        return 0, 0, 0.0
    cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
    return cw, ch, round((cw * ch) / max(1, im.size[0] * im.size[1]), 3)


def write_review(
    out_dir: Path,
    name: str,
    master: Image.Image,
    body: Image.Image,
    icon: Image.Image,
) -> Path:
    # Each native preview is copied at 1:1. Zoom is explicitly a separate aid.
    zoom = icon.resize((icon.width * 4, icon.height * 4), Image.Resampling.NEAREST)
    gap, top = 20, 40
    row_h = max(body.height, icon.height, zoom.height) + 50
    width = body.width + icon.width + zoom.width + gap * 4
    sheet = Image.new("RGBA", (width, top + row_h * 3), (235, 235, 235, 255))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 10), f"source {master.width}x{master.height}; native / native / 4x zoom", fill=(20, 20, 20))
    for row, (label, background) in enumerate([
        ("light", (255, 255, 255, 255)),
        ("dark", (30, 30, 35, 255)),
        ("checker", None),
    ]):
        x, y = gap, top + row * row_h
        for asset, caption in [
            (body, f"{label}: body {body.width}x{body.height} 1x"),
            (icon, "icon 1x"),
            (zoom, "icon 4x NEAREST (inspection only)"),
        ]:
            panel = checker(asset.size) if background is None else Image.new("RGBA", asset.size, background)
            panel.alpha_composite(asset)
            sheet.alpha_composite(panel, (x, y + 25))
            d.text((x, y), caption, fill=(20, 20, 20))
            x += asset.width + gap
    path = out_dir / f"REVIEW_{name}.png"
    sheet.convert("RGB").save(path)
    return path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DST texture post-process pipeline")
    p.add_argument("input", type=Path, help="Source PNG (generated/edited)")
    p.add_argument("--name", default=None, help="Output base name (default: input stem)")
    p.add_argument("--out", type=Path, default=Path(".tmp/.output/process_texture"))
    p.add_argument("--icon", type=int, default=64, help="Icon canvas (default 64)")
    p.add_argument("--body", type=int, default=256, help="Body/master canvas (default 256)")
    p.add_argument(
        "--content-ratio",
        type=float,
        default=0.72,
        help="Body content AREA fill (bbox/canvas), default 0.72; tools icons ~0.56, full armor ~0.95",
    )
    p.add_argument("--icon-ratio", type=float, default=None, help="Icon content AREA fill (default: same as content-ratio)")
    p.add_argument("--key-strength", type=float, default=55.0, help="Background key tolerance")
    key = p.add_mutually_exclusive_group()
    key.add_argument("--key-background", action="store_true", help="Opt in to color keying; may erase matching subject colors")
    key.add_argument("--no-key", action="store_true", help="Compatibility flag: keying is off by default")
    watermark = p.add_mutually_exclusive_group()
    watermark.add_argument("--clear-watermark", action="store_true", help="Opt in to legacy bright-corner erase; may damage subject")
    watermark.add_argument("--no-watermark", action="store_true", help="Compatibility flag: corner erase is off by default")
    p.add_argument("--review", action="store_true", help="Write REVIEW_*.png sheet")
    args = p.parse_args()
    if args.body < 1 or args.icon < 1:
        p.error("--body and --icon must be positive")
    if not 0 < args.content_ratio <= 1 or (args.icon_ratio is not None and not 0 < args.icon_ratio <= 1):
        p.error("content area ratios must be in (0, 1]")
    return args


def main() -> int:
    args = parse_args()
    src_path = args.input
    if not src_path.exists():
        raise SystemExit(f"input not found: {src_path}")
    name = args.name or src_path.stem
    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    im = Image.open(src_path).convert("RGBA")
    if args.key_background:
        im = key_background(im, strength=args.key_strength)
    if args.clear_watermark:
        im = clear_watermark(im)

    master_path = out_dir / f"{name}_master.png"
    im.save(master_path)

    body_ratio = args.content_ratio
    icon_ratio = args.icon_ratio if args.icon_ratio is not None else max(0.45, min(0.95, body_ratio))
    body = trim_and_fit(im, (args.body, args.body), body_ratio)
    icon = trim_and_fit(im, (args.icon, args.icon), icon_ratio, resample=Image.Resampling.LANCZOS)
    body_path = out_dir / f"{name}_body_{args.body}.png"
    icon_path = out_dir / f"{name}_icon_{args.icon}.png"
    body.save(body_path)
    icon.save(icon_path)

    print(f"master: {master_path} {im.size}")
    print(f"body:   {body_path} fill={fill_stats(body)[2]} ratio={body_ratio}")
    print(f"icon:   {icon_path} fill={fill_stats(icon)[2]} ratio={icon_ratio}")

    if args.review:
        review = write_review(out_dir, name, im, body, icon)
        print(f"review: {review}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
