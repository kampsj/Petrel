#!/usr/bin/env python3
"""Reload LCD atlas artwork after reinstalling panel resources."""
import argparse
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from t5uic1_driver import T5UIC1Display


def configured_port():
    if os.environ.get('DWIN_SERIAL_PORT'):
        return os.environ['DWIN_SERIAL_PORT']
    config = Path.home() / '.config/KlipperDWIN/KlipperDWIN.env'
    if config.exists():
        for line in config.read_text().splitlines():
            key, separator, value = line.partition('=')
            if separator and key.strip() == 'DWIN_SERIAL_PORT':
                values = shlex.split(value, comments=True)
                if len(values) == 1:
                    return values[0]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial-port', default=configured_port())
    parser.add_argument('--force', action='store_true',
                        help='Rewrite active atlases even when their saved versions match')
    args = parser.parse_args()
    if not args.serial_port:
        parser.error('UART not configured; specify --serial-port /dev/your-uart')
    state = subprocess.run(['systemctl', 'is-active', 'KlipperDWIN.service'],
                           capture_output=True, text=True).stdout.strip()
    if state not in ('inactive', 'failed', 'unknown'):
        parser.error('Stop the service first: sudo systemctl stop KlipperDWIN.service')
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    lcd = None
    try:
        lcd = T5UIC1Display(args.serial_port, force_atlases=args.force)
        if not lcd._atlas_synced:
            raise RuntimeError('Atlas synchronization failed; check the messages above')
        print('Atlas artwork loaded successfully.')
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f'{error}\n')
    finally:
        if lcd is not None:
            lcd.close()


if __name__ == '__main__':
    main()
