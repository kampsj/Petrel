"""Rebuild Atlas 1 compact spools from the shared empty-spool source PNG."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lcd_atlas import ATLAS_FILES, ICON_COORDINATES, SPOOL_EMPTY_ICONS
from tools.patch_atlas_icon import panel_jpeg_headers


def build():
    root = Path(__file__).resolve().parents[1]
    source = Image.open(root / 'assets/spool-empty.png').convert('RGB')
    wood, edge, hub = (source.getpixel(p) for p in ((3, 10), (0, 0), (21, 26)))
    canvas = Image.new('RGB', (272, 480), 'black')
    for width, icon_id in SPOOL_EMPTY_ICONS.items():
        area, x, y, _, height = ICON_COORDINATES[icon_id]
        if area != 1:
            continue
        sprite = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(sprite)
        flange = min(max(1, round(width / 6)), max(0, (width - 1) // 2))
        if flange:
            for left, right in ((0, flange - 1), (width - flange, width - 1)):
                draw.rectangle((left, 0, right, height - 1), fill=wood, outline=edge)
        draw.rectangle((flange, 20, width - flange - 1, 31), fill=hub)
        canvas.paste(sprite, (x, y))
    path = root / ATLAS_FILES[1][0]
    canvas.transpose(Image.Transpose.ROTATE_90).save(path, quality=95, subsampling=0)
    data = panel_jpeg_headers(path.read_bytes())
    if len(data) > 32768:
        raise ValueError('Compact spool atlas exceeds panel SRAM')
    path.write_bytes(data)


if __name__ == '__main__':
    build()
