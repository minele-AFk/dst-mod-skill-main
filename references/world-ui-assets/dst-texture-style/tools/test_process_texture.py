"""Offline regression tests for alpha preservation and native-size previews."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import process_texture as pipeline


class TexturePipelineTests(unittest.TestCase):
    def test_fit_preserves_semitransparent_alpha(self):
        source = Image.new("RGBA", (8, 8), (75, 125, 230, 128))
        result = pipeline.trim_and_fit(source, (8, 8), 1.0)
        self.assertEqual(result.tobytes(), source.tobytes())

    def test_default_cli_keeps_rgba_and_bright_corner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            source.putpixel((15, 15), (240, 20, 210, 128))
            source.putpixel((31, 31), (255, 255, 255, 255))
            source.save(root / "source.png")
            command = [sys.executable, "-B", str(Path(pipeline.__file__)), str(root / "source.png"),
                       "--name", "test", "--out", str(root / "out"), "--review"]
            subprocess.run(command, check=True, capture_output=True)
            with Image.open(root / "out/test_master.png") as saved:
                self.assertEqual(saved.tobytes(), source.tobytes())
            for suffix, size in [("body_256", 256), ("icon_64", 64)]:
                with Image.open(root / f"out/test_{suffix}.png") as saved:
                    self.assertEqual(saved.size, (size, size))
            subprocess.run(command + ["--no-key", "--no-watermark"], check=True, capture_output=True)

    def test_review_contains_unscaled_native_pixels_on_three_backgrounds(self):
        body = Image.new("RGBA", (256, 256), (25, 80, 210, 128))
        body.putpixel((255, 255), (240, 30, 50, 255))
        icon = Image.new("RGBA", (64, 64), (200, 130, 20, 255))
        icon.putpixel((63, 63), (10, 30, 220, 255))
        with tempfile.TemporaryDirectory() as temporary:
            path = pipeline.write_review(Path(temporary), "test", body, body, icon)
            with Image.open(path) as sheet:
                for row, color in enumerate([(255, 255, 255, 255), (30, 30, 35, 255), None]):
                    y = 65 + row * 306
                    for asset, x in [(body, 20), (icon, 296)]:
                        expected = pipeline.checker(asset.size) if color is None else Image.new("RGBA", asset.size, color)
                        expected.alpha_composite(asset)
                        actual = sheet.crop((x, y, x + asset.width, y + asset.height))
                        self.assertEqual(actual.tobytes(), expected.convert("RGB").tobytes())

    def test_color_key_requires_opt_in_and_handles_small_image(self):
        source = Image.new("RGBA", (2, 2), (255, 0, 255, 255))
        self.assertIsNone(pipeline.key_background(source).getchannel("A").getbbox())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source.save(root / "source.png")
            subprocess.run([sys.executable, "-B", str(Path(pipeline.__file__)), str(root / "source.png"),
                            "--out", str(root / "out"), "--key-background"], check=True, capture_output=True)
            with Image.open(root / "out/source_master.png") as saved:
                self.assertIsNone(saved.getchannel("A").getbbox())


if __name__ == "__main__":
    unittest.main()
