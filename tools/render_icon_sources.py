#!/usr/bin/env python3
"""Render the editable Graphite SVG sources into native baseline JPEG icons."""
import argparse
from io import BytesIO
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    import cairosvg  # Optional developer tool, not a service dependency.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-directory', type=Path, default=ROOT / 'assets/icon-source')
    parser.add_argument('--output-directory', type=Path, default=ROOT / 'assets/icons')
    args = parser.parse_args()
    args.output_directory.mkdir(parents=True, exist_ok=True)
    for path in sorted(args.source_directory.glob('*.svg')):
        root = ET.fromstring(path.read_bytes())
        width, height = int(root.attrib['width']), int(root.attrib['height'])
        png = cairosvg.svg2png(bytestring=path.read_bytes(), output_width=width * 4,
                              output_height=height * 4)
        with Image.open(BytesIO(png)) as image:
            image.convert('RGB').resize((width, height), Image.Resampling.LANCZOS).save(
                args.output_directory / (path.stem + '.jpg'), 'JPEG',
                quality=94, subsampling=0, progressive=False)


if __name__ == '__main__':
    main()
