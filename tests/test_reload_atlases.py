import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools import reload_atlases as tool


class ReloadAtlasTests(unittest.TestCase):
    def test_reads_configured_uart_without_executing_environment_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / '.config/KlipperDWIN/KlipperDWIN.env'
            config.parent.mkdir(parents=True)
            config.write_text('DWIN_SERIAL_PORT="/dev/serial0"\nIGNORED=$(false)\n')
            with patch.dict(os.environ, {}, clear=True), patch.object(tool.Path, 'home', return_value=Path(tmp)):
                self.assertEqual(tool.configured_port(), '/dev/serial0')

    def test_active_service_cannot_open_uart(self):
        with patch.object(tool, 'configured_port', return_value='/dev/serial0'), \
                patch.object(tool.sys, 'argv', ['reload_atlases.py', '--force']), \
                patch.object(tool.subprocess, 'run', return_value=Mock(stdout='active\n')), \
                patch.object(tool, 'T5UIC1Display') as display:
            with self.assertRaises(SystemExit):
                tool.main()
            display.assert_not_called()

    def test_force_is_explicit_and_uart_closes_after_success(self):
        lcd = Mock(_atlas_synced=True)
        with patch.object(tool, 'configured_port', return_value='/dev/serial0'), \
                patch.object(tool.sys, 'argv', ['reload_atlases.py', '--force']), \
                patch.object(tool.subprocess, 'run', return_value=Mock(stdout='inactive\n')), \
                patch.object(tool, 'T5UIC1Display', return_value=lcd) as display:
            tool.main()
            display.assert_called_once_with('/dev/serial0', force_atlases=True)
            lcd.close.assert_called_once_with()

    def test_failed_sync_is_reported_and_uart_closes(self):
        lcd = Mock(_atlas_synced=False)
        with patch.object(tool, 'configured_port', return_value='/dev/serial0'), \
                patch.object(tool.sys, 'argv', ['reload_atlases.py']), \
                patch.object(tool.subprocess, 'run', return_value=Mock(stdout='inactive\n')), \
                patch.object(tool, 'T5UIC1Display', return_value=lcd):
            with self.assertRaises(SystemExit):
                tool.main()
            lcd.close.assert_called_once_with()
