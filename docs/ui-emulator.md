# Developer framebuffer emulator

This optional feature mirrors the **successfully written T5UIC1 UART packets**
from the running UI. It does not implement a second menu system, read the UART,
simulate Moonraker, host a live viewer or continuously save pictures.

## Enable on the Pi

Check out `feature/ui-emulator` and install its optional dependency:

```bash
cd ~/KlipperDWIN
~/klipperdwin-env/bin/python -m pip install -r requirements-emulator.txt
```

Add this to the external service environment file
`~/.config/KlipperDWIN/KlipperDWIN.env`, then restart:

```ini
DWIN_EMULATOR=1
```

```bash
sudo systemctl restart KlipperDWIN.service
```

Normal installations leave this unset or use `DWIN_EMULATOR=0`. No framebuffer,
asset loading, socket server or emulator imports occur in the disabled UI path.
The driver's optional observer check is the only addition to normal sends.
The LCD remains on the configured UART (the reference installation uses
`/dev/ttyS0`); the emulator does not open another serial connection.

## Capture over SSH

Navigate on the real LCD, then run **as the service user**, without sudo:

```bash
~/klipperdwin-env/bin/python ~/KlipperDWIN/tools/screenshot.py
```

The command prints the saved absolute path. Default output is
`~/KlipperDWIN-screenshots/YYYY-MM-DD_HH-MM-SS_microseconds_unique.png`.
Screenshots are RGB at the original 272x480 portrait size, with no scaling,
antialiasing or JPEG conversion. PNG uses compression level 0 and is lossless;
BMP is available for a completely uncompressed bitmap:

```bash
~/klipperdwin-env/bin/python ~/KlipperDWIN/tools/screenshot.py --format bmp
```

No image is saved until requested. Each request copies the last completed
`0x3D` LCD update under the framebuffer lock; encoding and disk I/O run outside
that lock. Simultaneous drawing cannot create a half-rendered screenshot.
Disconnected panels, missing assets and unsupported visual instructions return
an error instead of claiming a valid capture. Screenshots survive service exits.

## Configuration

| Environment | CLI | Purpose |
|---|---|---|
| `DWIN_EMULATOR` | `--emulator` / `--no-emulator` | Default off |
| `DWIN_EMULATOR_SOCKET` | `--emulator-socket` | Private Unix socket path |
| `DWIN_SCREENSHOT_DIRECTORY` | `--screenshot-directory` | Output directory |
| `DWIN_EMULATOR_FONT` | `--emulator-font` | HZK font matching the physical LCD |

The socket defaults to `$XDG_RUNTIME_DIR/KlipperDWIN-emulator/control.sock`, or
`~/.cache/KlipperDWIN-emulator/control.sock` if XDG_RUNTIME_DIR is unset. Its
directory must be owned by the service user with permissions 0700; the socket
uses 0600. Pass the same custom path to `screenshot.py --socket PATH`.
Only local screenshot requests are accepted; there is no TCP port or browser.
Owned stale sockets from a crashed process are recovered; active servers and
regular files are never replaced.

## Rendering and fidelity

- Original bitmap glyphs, stock JPEG icons, managed atlas slots 14/15, slot-0
  bootsplash and SRAM thumbnails are decoded into RGB565 colors.
- Direction 1 rotates physical 480x272 JPEGs clockwise into portrait space.
- Areas 0/1 are independent. `show_jpeg` updates the screen and area 0;
  `cache_jpeg` updates area 1 only. Copy, transparency and restoration flags
  operate on those buffers.
- Clear, points, lines, rectangles/XOR, bitmaps, text, ordinary native numeric
  fonts, QR, region translation/wrap and SRAM writes/picture storage are handled.
- Backlight changes do not darken saved pixels: captures represent framebuffer
  contents, including when the physical backlight is dimmed.

This is an instruction/asset mirror, **not a readback of the LCD hardware RAM**.
Font/library mismatches cannot be detected automatically. The supplied DGUS font
is not the native T5UIC1 font; the bundled original T5UIC1 file is the default.
Select an installed custom font explicitly when applicable.

Hardware JPEG rounding, the undocumented enhanced black-filter threshold and
automatic glyph-width adjustment can differ from the host decoder. Enhanced
filtering currently drops RGB channel values at or below 31. QR uses fixed
version 7/L, byte mode, a 46-module box, inferred from the documented 154-byte
capacity and dimensions; the panel's mask selection can differ. QR captures are
valid standard codes, but exact module-for-module equality needs a physical
comparison. Native numeric fonts 0x0A/0x0B, animation and barcode commands are
not used by the current UI and fail explicitly if encountered. Do not describe
these unverified cases as proven pixel-identical hardware output.

## Future conditional activation

`Emulator.set_enabled(bool)` is a separate, locked lifecycle API; there is no
condition hard-coded into the packet interpreter. Disabled observers discard
packets and release the model. Re-enabling creates a fresh model but deliberately
rejects snapshots until `reset_panel()` establishes a baseline and an update
arrives. A future condition should run on the UI owner thread and reconnect/
reinitialize the LCD after enabling, then attach the observer to its driver.
No unbounded command history is retained while disabled.

## Verification

Tests cover transmitted-frame observation, partial-write exclusion, font bits,
stock libraries and holes, atlas rotation/copies, real UI packet replay, region
movement, SRAM thumbnails, XOR, QR capacity, lifecycle/reset and lossless output.
Unix-socket tests run on Linux CI; environments that prohibit creating Unix
sockets explicitly skip those two integration tests. Other tests still verify
the file writer byte-for-byte. The CI workflow includes this feature branch.
