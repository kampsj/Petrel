# LCD compatibility

[English](lcd-assets.md) · [Türkçe](lcd-assets_TR.md) · [Documentation](README.md)

## Supported display

Petrel targets the **272×480 portrait DWIN T5UIC1** layout used by the compatible 4.3-inch Ender 3 V2 panel. DWIN, DACAI and TJC firmware/resource packs are not interchangeable.

The physical panel needs the matching stock icon library **3 (`3.ICO`)**, fonts and English bitmap resources. Display direction is **1**. Custom Petrel artwork is supplied separately with the application; see the [artwork guide](../assets/README.md).

## Before installing or replacing a panel

Check the controller family and installed resource pack, not just the screen size. The application installer does not flash LCD kernel firmware or install the stock font/icon pack. For panel firmware work, use the optional [T5UIC1 reference](t5uic1-reference.md).

After setup, inspect menu labels/icons, colors, preview images and encoder navigation on the physical display. A working emulator screenshot does not guarantee that a different panel/resource pack renders the same way.

## Print previews

Previews come from Moonraker and do not need a new panel asset pack. Missing thumbnails do not prevent starting a print. Images are prepared again after restarting or reconnecting; they do not replace installed icons.

## Resource identification

The application now builds library 3 from [`assets/icons`](../assets/icons/README.md) and automatically uploads changed blocks at the first LCD connection after an update. Unchanged resources are skipped. Follow that guide to add JPEGs, export a pack or force a reload after reinstalling panel resources.

On the experimental library-3 branch, install the bundled `3.ICO` over UART without replacing panel firmware:

```sh
sudo systemctl stop Petrel.service
~/petrel-env/bin/python ~/Petrel/tools/flash_icon_library.py && sudo systemctl start Petrel.service
```

The tool uses the configured serial port and writes slots starting at 3 (one slot per 32 KiB block). Failed writes leave the service stopped. It checks write acknowledgements, without Flash readback. Inspect the icons on the physical panel after upload.

For contributor artwork, `tools/pack_icon_library.py source.ICO destination.ICO` preserves JPEG images while keeping each icon within one 32 KiB block. This layout avoids splitting icons at the boundaries associated with the observed rendering faults.

The [stock inventory](lcd-assets.json) records the resources previously audited for this project. It does not identify the files installed on your own panel. Contributor artwork and emulator font-selection instructions are linked from the [documentation index](README.md).

## Graphite font

The icon library updates automatically over UART. To match the Graphite screenshots, also install the bundled ASCII font from `assets/fonts/DWIN_SET/0T5UIC1.HZK` using the LCD panel’s SD-card resource update procedure. Copy the bundled `DWIN_SET` directory to a compatible LCD update card, power off the printer, insert the card in the LCD’s card reader, power on and wait for the resource update to finish. Power off, remove the card and start normally. The Pi service does not upload font Flash over UART. The emulator uses the same font; its DejaVu license is in `assets/emulator/Petrel-font-license.txt`.
