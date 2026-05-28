#!/usr/bin/env python3
"""Generate Windows Store icon assets from a programmatic brain-leaf logo.

Produces every PNG variant required by AppxManifest.xml plus app_icon.ico.
Run from project root:

    python scripts/generate_store_assets.py

Outputs go to windows_store/assets/.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Brand palette from windows_store/assets/README.md
OCEAN_BLUE = (58, 124, 165, 255)    # #3A7CA5
DEEP_BLUE = (44, 95, 124, 255)      # #2C5F7C
SAGE_GREEN = (107, 159, 120, 255)   # #6B9F78
CLOUD_WHITE = (247, 249, 252, 255)
TRANSPARENT = (0, 0, 0, 0)

ASSETS_DIR = Path(__file__).parent.parent / "windows_store" / "assets"


def draw_logo(
    size: int,
    *,
    transparent_bg: bool = True,
    monochrome: bool = False,
    splash: bool = False,
    wide: bool = False,
) -> Image.Image:
    """Render the brain-leaf mark at the given size.

    The mark is a soft rounded square (representing a brain hemisphere) with
    a single sage-green leaf rising from the top — built from primitives so it
    scales cleanly at every size from 16px to 2480px.
    """
    if wide:
        w, h = size, size // 2  # for 310x150 etc, caller passes width
    else:
        w = h = size

    bg = TRANSPARENT if transparent_bg else OCEAN_BLUE
    img = Image.new("RGBA", (w, h), bg)
    d = ImageDraw.Draw(img)

    # Center the icon mark in a square area, ~70% of min dimension
    side = int(min(w, h) * 0.72)
    cx, cy = w // 2, int(h * 0.55)
    x0, y0 = cx - side // 2, cy - side // 2
    x1, y1 = x0 + side, y0 + side

    fg_brain = CLOUD_WHITE if monochrome else OCEAN_BLUE
    fg_leaf = CLOUD_WHITE if monochrome else SAGE_GREEN
    stroke_w = max(2, side // 18)

    # Brain — rounded square with two soft lobes hinted via concentric arcs
    radius = side // 4
    d.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=radius,
        outline=fg_brain,
        width=stroke_w,
    )
    # Inner lobe arcs (suggest hemispheres)
    inset = side // 6
    d.arc(
        [x0 + inset, y0 + inset, x1 - inset, y1 - inset],
        start=200, end=340, fill=fg_brain, width=max(1, stroke_w - 1),
    )
    # Vertical midline
    d.line(
        [(cx, y0 + inset), (cx, y1 - inset)],
        fill=fg_brain, width=max(1, stroke_w - 1),
    )

    # Leaf rising from the top center
    leaf_h = side // 3
    leaf_w = side // 4
    lx, ly = cx, y0 - leaf_h // 4
    leaf_box = [lx - leaf_w // 2, ly - leaf_h, lx + leaf_w // 2, ly]
    d.ellipse(leaf_box, fill=fg_leaf)
    # Stem
    d.line(
        [(cx, ly), (cx, y0 + stroke_w)],
        fill=fg_leaf, width=max(2, stroke_w - 1),
    )

    # Splash adds a wordmark below
    if splash:
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                size=max(20, h // 12),
            )
        except OSError:
            font = ImageFont.load_default()
        text = "Hearth"
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(
            ((w - tw) // 2, y1 + th // 2),
            text,
            fill=DEEP_BLUE if not monochrome else CLOUD_WHITE,
            font=font,
        )

    return img


def save(img: Image.Image, name: str) -> None:
    out = ASSETS_DIR / name
    img.save(out, "PNG")
    print(f"  wrote {out.name} ({img.size[0]}x{img.size[1]})")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating assets in {ASSETS_DIR}")

    # Square logos at multiple scales (Windows Store conventions)
    square_specs = {
        "Square44x44Logo":  44,
        "Square71x71Logo":  71,
        "Square150x150Logo": 150,
        "Square310x310Logo": 310,
        "StoreLogo":        50,
        "FileTypeLogo":     44,
    }
    scales = [100, 125, 150, 200, 400]

    for name, base in square_specs.items():
        for scale in scales:
            px = int(base * scale / 100)
            save(draw_logo(px), f"{name}.scale-{scale}.png")
        # default
        save(draw_logo(base), f"{name}.png")

    # Target-size variants for Square44 and FileType
    for name, _base in [("Square44x44Logo", 44), ("FileTypeLogo", 44)]:
        for ts in (16, 24, 32, 48, 256):
            save(draw_logo(ts), f"{name}.targetsize-{ts}.png")

    # Wide tile 310x150
    for scale in scales:
        w = int(310 * scale / 100)
        h = int(150 * scale / 100)
        # Compose: square logo on the left, text on the right
        composite = Image.new("RGBA", (w, h), TRANSPARENT)
        mark = draw_logo(h).resize((h, h))
        composite.paste(mark, (0, 0), mark)
        d = ImageDraw.Draw(composite)
        try:
            font = ImageFont.truetype(
                "/System/Library/Fonts/Supplemental/Arial.ttf", size=max(14, h // 5)
            )
        except OSError:
            font = ImageFont.load_default()
        d.text((h + 8, h // 3), "Hearth", fill=OCEAN_BLUE, font=font)
        save(composite, f"Wide310x150Logo.scale-{scale}.png")
    save(composite.resize((310, 150)), "Wide310x150Logo.png")

    # Badge (monochrome white)
    for scale in scales:
        px = int(24 * scale / 100)
        save(draw_logo(px, monochrome=True), f"BadgeLogo.scale-{scale}.png")
    save(draw_logo(24, monochrome=True), "BadgeLogo.png")

    # Splash screen 620x300
    for scale in scales:
        w = int(620 * scale / 100)
        h = int(300 * scale / 100)
        canvas = Image.new("RGBA", (w, h), TRANSPARENT)
        mark = draw_logo(int(h * 0.7), splash=True)
        canvas.paste(mark, ((w - mark.size[0]) // 2, (h - mark.size[1]) // 2), mark)
        save(canvas, f"SplashScreen.scale-{scale}.png")
    canvas_default = Image.new("RGBA", (620, 300), TRANSPARENT)
    mark = draw_logo(210, splash=True)
    canvas_default.paste(mark, ((620 - mark.size[0]) // 2, (300 - mark.size[1]) // 2), mark)
    save(canvas_default, "SplashScreen.png")

    # Multi-resolution ICO for PyInstaller
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base = draw_logo(256)
    base.save(ASSETS_DIR / "app_icon.ico", format="ICO", sizes=ico_sizes)
    print("  wrote app_icon.ico (multi-resolution)")

    # Also a generic PNG copy used by main.py for the QApplication window icon
    base.save(ASSETS_DIR / "app_icon.png", "PNG")

    print("Done.")


if __name__ == "__main__":
    main()
