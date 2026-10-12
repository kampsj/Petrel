"""Read the configured LCD UART without executing the environment file."""
import os
from pathlib import Path
import shlex


def configured_port():
    if os.environ.get('PETREL_SERIAL_PORT'):
        return os.environ['PETREL_SERIAL_PORT']
    config = Path.home() / '.config/Petrel/Petrel.env'
    if config.exists():
        for line in config.read_text().splitlines():
            key, separator, value = line.partition('=')
            if separator and key.strip() == 'PETREL_SERIAL_PORT':
                values = shlex.split(value, comments=True)
                if len(values) == 1:
                    return values[0]
    return None

