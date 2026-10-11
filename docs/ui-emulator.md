# Emulator screenshots

[English](ui-emulator.md) · [Türkçe](ui-emulator_TR.md) · [Contributing](../CONTRIBUTING.md)

## What it is for

The optional emulator captures the screens drawn by the running KlipperDWIN service. Use it to review layouts, refresh documentation and report visual bugs as original-size images. It follows the real LCD UI; it is not a standalone printer simulator or live browser viewer. Navigate with the physical encoder, then request a capture over SSH.

## Enable or disable

Dependencies are included in normal installation and Moonraker updates. In `~/.config/KlipperDWIN/KlipperDWIN.env`, change the default:

```ini
DWIN_EMULATOR=1
```

Then restart:

```bash
sudo systemctl restart KlipperDWIN.service
```

To disable, set `DWIN_EMULATOR=0` and restart again. Re-running installation/configuration preserves an existing enabled value. For an older installation missing dependencies:

```bash
cd ~/KlipperDWIN
~/klipperdwin-env/bin/python -m pip install -r requirements.txt
```

## Capture over SSH

1. Open the desired screen on the LCD and wait for it to finish drawing.
2. In SSH, run **as the service user, without sudo**:

```bash
~/klipperdwin-env/bin/python ~/KlipperDWIN/tools/screenshot.py
```

The command prints the saved path. By default images go to `~/KlipperDWIN-screenshots/` with timestamped, unique filenames. Output is lossless **272×480 RGB PNG**, without resizing. No screenshots are saved automatically.

For BMP output:

```bash
~/klipperdwin-env/bin/python ~/KlipperDWIN/tools/screenshot.py --format bmp
```

Copy images to your computer for review. Repository screenshots belong in `docs/assets/screens/` with names describing the screen/state.

## Optional settings

Set these in the same external environment file and restart the service:

| Variable | Purpose |
|---|---|
| `DWIN_SCREENSHOT_DIRECTORY` | Custom output directory |
| `DWIN_EMULATOR_SOCKET` | Custom local capture socket; default `~/.cache/KlipperDWIN-emulator/control.sock` |
| `DWIN_EMULATOR_FONT` | Font file matching a customized physical panel |

For a custom socket, use the same path in the capture command:

```bash
~/klipperdwin-env/bin/python ~/KlipperDWIN/tools/screenshot.py --socket /path/to/control.sock
```

## Troubleshooting and limits

| Problem | What to do |
|---|---|
| Cannot connect or permission denied | Check `DWIN_EMULATOR=1`, restart the service, run as its user and check the socket path |
| Capture rejected | Check panel connection, loaded assets and the service log; wait for a completed screen |
| Text/icons differ from the panel | Compare the font/icon files; see [emulator assets](../assets/emulator/README.md) |
| Dimming is not visible in the image | Captures show screen pixels, not physical backlight brightness |

The emulator mirrors drawing instructions rather than reading the LCD's memory. Fonts, JPEG decoding and QR patterns can differ from a physical panel. For those issues, provide both a screenshot and a photo; a capture alone does not prove physical display accuracy.
