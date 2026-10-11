"""Host-side custom icon-atlas manifest for KlipperDWIN.

The UI must not depend on atlas coordinates or virtual-area selection. Add or
move custom static icons only by updating ICON_COORDINATES and the corresponding
JPEG file. Required popup artwork is also managed here so it remains available
when a panel ships with a different stock 9.ICO library.

T5UIC1 JPEG files are stored at the physical 480x272 panel resolution, while
source rectangles below use the runtime portrait virtual-area coordinate space
(272x480) after direction=1 is applied.
"""

# KlipperDWIN custom icon IDs. UI code imports these symbolic IDs and calls
# lcd.draw_atlas_icon(icon_id, x, y); it never sees atlas coordinates.
ICON_MMU_HOME_NORMAL = 0x0100
ICON_MMU_HOME_SELECTED = 0x0101
ICON_FOLDER = 0x0102
ICON_MCU = 0x0103
ICON_MACHINE = 0x0104
ICON_HOST = 0x0105
ICON_SOFTWARE = 0x0106
ICON_POWER = 0x0107
ICON_DISPLAY = 0x0108
ICON_HOMING = 0x0109
ICON_SPOOL_EMPTY = 0x010A

# virtual_area: (repo-relative JPEG path, reserved Picture Flash ID)
ATLAS_FILES = {
    0: ("assets/klipperdwin_atlas_0.jpg", 14),
    1: ("assets/klipperdwin_atlas_1.jpg", 15),
}

# icon_id: (virtual_area, source_x, source_y, width, height)
#
# Coordinates are in the runtime 272x480 virtual-area orientation.
# Atlas 1 holds compact sizes of the shared empty spool.
ICON_COORDINATES = {
    ICON_MMU_HOME_NORMAL: (0, 0, 0, 77, 47),
    ICON_MMU_HOME_SELECTED: (0, 80, 0, 77, 47),
    ICON_FOLDER: (0, 160, 0, 20, 18),
    ICON_MCU: (0, 192, 0, 20, 20),
    ICON_MACHINE: (0, 224, 0, 20, 20),
    ICON_HOST: (0, 160, 32, 20, 20),
    ICON_SOFTWARE: (0, 192, 32, 20, 20),
    ICON_POWER: (0, 224, 32, 20, 20),
    ICON_DISPLAY: (0, 0, 48, 52, 64),
    ICON_HOMING: (0, 64, 48, 73, 66),
    ICON_SPOOL_EMPTY: (0, 144, 64, 42, 52),
}

# Native LCD copies do not scale: compact lanes use pre-sized copies of the same spool.
SPOOL_EMPTY_ICONS = {42: ICON_SPOOL_EMPTY,
    34: 0x0222,
    28: 0x021C,
    23: 0x0217,
    21: 0x0215,
    18: 0x0212,
    16: 0x0210,
    15: 0x020F,
    14: 0x020E,
    12: 0x020C,
    11: 0x020B,
    10: 0x020A,
    9: 0x0209,
    8: 0x0208,
    7: 0x0207,
    6: 0x0206,
    5: 0x0205,
    4: 0x0204,
    3: 0x0203,
    2: 0x0202,
    1: 0x0201,
}
ICON_COORDINATES.update({
    0x0222: (1, 0, 0, 34, 52),
    0x021C: (1, 42, 0, 28, 52),
    0x0217: (1, 78, 0, 23, 52),
    0x0215: (1, 109, 0, 21, 52),
    0x0212: (1, 138, 0, 18, 52),
    0x0210: (1, 164, 0, 16, 52),
    0x020F: (1, 188, 0, 15, 52),
    0x020E: (1, 211, 0, 14, 52),
    0x020C: (1, 233, 0, 12, 52),
    0x020B: (1, 253, 0, 11, 52),
    0x020A: (1, 0, 64, 10, 52),
    0x0209: (1, 18, 64, 9, 52),
    0x0208: (1, 35, 64, 8, 52),
    0x0207: (1, 51, 64, 7, 52),
    0x0206: (1, 66, 64, 6, 52),
    0x0205: (1, 80, 64, 5, 52),
    0x0204: (1, 93, 64, 4, 52),
    0x0203: (1, 105, 64, 3, 52),
    0x0202: (1, 116, 64, 2, 52),
    0x0201: (1, 126, 64, 1, 52),
})
