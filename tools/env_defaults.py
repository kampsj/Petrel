#!/usr/bin/env python3
"""Add new opt-in defaults without resetting an existing installation."""
from pathlib import Path
import re
import sys


def ensure_emulator_default(path):
    path = Path(path)
    text = path.read_text()
    if re.search(r'^\s*DWIN_EMULATOR=', text, re.MULTILINE):
        return False
    with path.open('a') as stream:
        stream.write(('' if not text or text.endswith('\n') else '\n') + 'DWIN_EMULATOR=0\n')
    return True


if __name__ == '__main__':
    ensure_emulator_default(sys.argv[1])
