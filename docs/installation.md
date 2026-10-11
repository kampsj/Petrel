# Installation and configuration

[English](installation.md) · [Türkçe](installation_TR.md) · [Documentation](README.md)

## Before installation

Use a compatible DWIN T5UIC1 panel, a Linux SBC with UART/GPIO, Python 3.11+ and a working Klipper/Moonraker setup. Check [LCD compatibility](lcd-assets.md). The application installer does not flash the panel firmware or install the stock font/icon pack.

## Wiring and serial setup

| Display connection | Raspberry Pi connection |
|---|---|
| RX | GPIO14 / UART TX |
| TX | GPIO15 / UART RX |
| Encoder A | GPIO21 |
| Encoder B | GPIO19 |
| Encoder button | GPIO20 |
| VCC | 5 V |
| GND | GND |

GPIO numbers are **BCM numbers**. Encoder pins can be changed during configuration. See [wiring illustrations](../images/) for the physical connections.

In `sudo raspi-config`, enable serial hardware and disable the serial login console, then reboot. Confirm which UART device uses GPIO14/15 on your Pi and OS. The installer suggests `/dev/ttyS0`; choose the device appropriate for your installation.

## Install

Run as the user who will own the service. The checkout must be clean and located at `~/KlipperDWIN`:

```bash
cd ~
git clone https://github.com/sezgynus/KlipperDWIN.git
cd ~/KlipperDWIN
./install.sh
```

Press Enter to accept a prompt's default, or enter your own value:

| Setting | Installer default |
|---|---|
| Moonraker URL | `http://127.0.0.1:7125` |
| UART | `/dev/ttyS0` |
| Encoder A/B | `21 19` |
| Encoder button | `20` |
| Moonraker power device | `Printer` |
| Power-on hold | `2000` ms (2 seconds) |

Installation prepares `~/klipperdwin-env`, installs dependencies and enables `KlipperDWIN.service`. It keeps settings in `~/.config/KlipperDWIN/KlipperDWIN.env`, adds a `KlipperDWIN.conf` include beside `moonraker.conf` and registers the service for Moonraker updates. Existing settings are preserved when installation is repeated.

For a nonstandard Moonraker configuration location:

```bash
MOONRAKER_CONFIG=/path/to/moonraker.conf ./install.sh
```

## Change settings

```bash
cd ~/KlipperDWIN
./configure.sh
```

Current values become the prompt defaults. After saving, accept the offered service restart to apply them. Display brightness/dimming are adjusted on the LCD under **Home → Display**, rather than here.

For settings not prompted by the configurator, edit the external environment file. Use plain `KEY=value` lines, without `export`:

| Setting | Purpose / default |
|---|---|
| `MOONRAKER_URL` | Moonraker address / `http://127.0.0.1:7125` |
| `MOONRAKER_API_KEY` | Authentication key if required / empty |
| `DWIN_REQUEST_TIMEOUT` | Request timeout in seconds / `5` |
| `DWIN_SERIAL_PORT` | Configured UART / installer suggests `/dev/ttyS0` |
| `DWIN_ENCODER_PINS` | Encoder A/B in BCM numbering / `21 19` |
| `DWIN_BUTTON_PIN` | Encoder button in BCM numbering / `20` |
| `DWIN_SETTINGS_FILE` | Local preset fallback / `~/.config/KlipperDWIN/presets.json` |
| `DWIN_POWER_DEVICE` | Name of your Moonraker power device / `Printer` |
| `DWIN_POWER_ON_HOLD_MS` | Power-on hold in milliseconds / `2000`; `0` means immediate |
| `DWIN_EMULATOR` | Screenshot capture / `0` disabled, `1` enabled |

Restart after editing: `sudo systemctl restart KlipperDWIN.service`. Keep private keys and machine settings outside tracked repository files. See the [emulator guide](ui-emulator.md) for screenshot-specific options.

## Update

After Moonraker reloads its configuration, use **Mainsail → Machine → Update Manager → KlipperDWIN**. Refresh and update; dependencies and the service restart are handled automatically. Update Manager follows `master`.

You can also check and install KlipperDWIN updates from **Info** on the LCD while the printer is idle. See [Info and updates](user-guide.md#info-and-updates). Local edits to tracked repository files may block updating; inspect or back them up before recovery discards them.

## Troubleshooting

```bash
sudo systemctl status KlipperDWIN.service --no-pager
journalctl -u KlipperDWIN.service --since "10 minutes ago" --no-pager
sudo systemctl restart KlipperDWIN.service
```

| Symptom | What to check |
|---|---|
| Blank screen or repeated reconnects | Panel power, crossed TX/RX, selected UART, serial login console and permissions |
| Encoder does not respond | BCM pin settings and wiring |
| Startup stays on one stage | Klipper/Moonraker readiness, panel resources and service logs |
| Optional menu missing or locked | Required Klipper/Happy Hare configuration, connection and current printer state |
| Preview image or metadata missing | Slicer thumbnails and metadata available in Moonraker |
| Wi-Fi information unavailable | Wireless connection and availability of Linux `iw` |
| Update blocked | Local repository edits and Moonraker Update Manager status |
| Action failed or timed out | Check the actual printer state in Mainsail before repeating |

For a bug report, include the software revision, Pi/OS, configuration relevant to the problem and the log excerpt. Add a photo or [emulator screenshot](ui-emulator.md) for visual problems; remove credentials before sharing.
