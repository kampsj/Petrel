# Managed LCD icons

[English](README.md) · [Türkçe](README_TR.md)

Add or replace baseline **4:2:0 JPEGs** here. Use the icon ID as the filename prefix: `092.jpg`, `092-about.jpg` or `092_about.jpeg`. IDs are 0–255; each ID must occur once. Existing IDs retain their meaning. Renaming an icon without changing its ID or bytes does not trigger an upload. A new image enters the library; UI code chooses where its ID is displayed.

JPEGs are preserved without resizing or recompression. Progressive JPEGs, other color sampling formats, duplicate IDs and images larger than 32767 bytes are rejected. The whole library must fit Picture Flash slots 3–15; stock pictures 1–2 are untouched; picture 0 holds the separately managed Petrel boot artwork.

After an application update, the first LCD connection builds the library from this directory. The packer places larger icons first and fits smaller icons into remaining holes. Icon IDs do not depend on physical placement. Every block's last byte is reserved and excluded from UART writes. No JPEG crosses a block boundary.

Only changed blocks are uploaded; the directory block is committed last. Panel metadata records successful blocks, so a subsequent start resumes incomplete uploads. Unchanged libraries cause no Flash writes. A failed Picture Flash attempt is not repeated in the same process. Logs describe upload progress and failures.

Preview/export the exact runtime pack:

```bash
python tools/pack_icon_library.py assets/icons /tmp/3.ICO
```

The emulator uses these same JPEG sources. `assets/emulator/3.ICO` is a reference export, not the source for automatic updates.

Custom UI icons use IDs 100–109 and 124. MMU uses 100/101 and Display uses 108/109 for normal/selected 110×100 home tiles, using the established native tile footprint. The empty spool uses ID 124. Metal spool flanges use IDs 110–123 for widths 1–7, so compact lanes need no separate complete spool artwork. The symbolic mapping is in `lcd_resources.py`. All UI icons render directly through library 3.

After reinstalling panel resources, force a reload because stored metadata may still describe the previous installation:

```bash
sudo systemctl stop Petrel.service
~/petrel-env/bin/python ~/Petrel/tools/reload_icons.py
sudo systemctl start Petrel.service
```

Write acknowledgements and metadata readback are verified; Picture Flash itself is not read back. Confirm the newly packed icon layout on the physical display.

## Graphite

Graphite adds dedicated IDs 210–234 for light, brightness, sound settings, motion parameters, calibration and profiles. Editable SVG sources are in `assets/icon-source`; use `python tools/render_icon_sources.py` to regenerate JPEGs (developer dependency: CairoSVG). Black JPEG backing is filtered with the native transparent/enhanced icon mode; menu and dashboard surfaces remain visible. The icon pack starts at picture slot 3 and may use slots 3–15; its 512-byte metadata record occupies Data Flash `0x0200–0x03FF`.

## JPEG compatibility rule

All managed icons must be baseline RGB/YCbCr JPEG with 4:2:0 sampling (`Pillow: subsampling=2`). Render directly from SVG using `tools/render_icon_sources.py`; do not repeatedly recompress JPEGs. Physical T5UIC1 tests reproduced damaged selected home tiles and homing artwork with 4:4:4 from both Flash and byte-verified SRAM; 4:2:0 rendered correctly. A clean emulator preview cannot validate the panel JPEG decoder. The source loader rejects other sampling formats before any panel access, and CI checks every shipped icon and the exported ICO against its sources. Check selected/unselected home tiles, homing, small menu/status icons and animation on hardware after artwork updates.
