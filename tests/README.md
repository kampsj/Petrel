# Tests and hardware validation

[English](README.md) · [Türkçe](README_TR.md) · [Contributing](../CONTRIBUTING.md)

## Run automated checks

From the repository root, with the application's dependencies installed:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
```

On an installed Pi, replace `python3` with `~/klipperdwin-env/bin/python`. The suite uses isolated state and simulated serial/GPIO/network connections. It does not connect to or move the printer. Local Unix-socket tests require an environment that allows Unix sockets; otherwise those integration checks are skipped.

## What the suite checks

- Menus, encoder navigation, numeric edits and feature availability.
- File browsing, previews, sorting and print controls.
- Movement restrictions, temperature presets and calibration save/cancel behavior.
- MMU operations, mappings, recovery, LEDs and multiple units.
- Display settings, power/startup behavior and reconnection handling.
- Emulator rendering, capture requests and lossless output.

For a behavior change, add or update checks for the user outcome and failure cases. A passing suite does not prove physical rendering, motion, probing accuracy or external-service persistence. GitHub's regression workflow runs on `master` and the configured feature branches; use the local command on other branches too.

## Hardware validation

Choose checks relevant to your change and record the revision, hardware and result:

| Area | Check on the actual setup |
|---|---|
| Navigation/display | Page selection, Back, numeric edits, readable icons/text, brightness, dimming and wake input |
| Prints | Folder and sort changes, missing preview data, correct file selection, Pause/Resume/Stop |
| Motion/heat | Homed travel, extrusion temperature restrictions, preset save/apply and jog recovery |
| Calibration | Screw directions/results, mesh orientation, save/restart and explicit stop/shutdown |
| MMU | Gate/tool target, load/unload/eject/bypass, mapping drafts, recovery, sensors, LED output and unit selection |
| Power/startup | Long-press on, power-off confirmation, relay cycle, startup progress and clean return Home |
| Screenshots | Compare capture with the physical panel, including configured fonts and icons |

After a disconnect or uncertain operation, confirm actual state and verify the previous command is not repeated automatically. Share failures with logs and screenshots/photos. See the [user guide](../docs/user-guide.md), [MMU guide](../docs/mmu-guide.md) and [LCD compatibility](../docs/lcd-assets.md) for expected behavior.
