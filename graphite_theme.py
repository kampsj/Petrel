"""Graphite icon compositing policy, separate from the generic panel API."""


def show_icon(lcd, library, icons, x, y):
    # Filter the source JPEG's black backing to preserve the current surface.
    lcd.show_icon(library, icons, x, y, background=False, enhanced=True)
