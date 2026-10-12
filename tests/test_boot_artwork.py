import unittest
from unittest.mock import Mock, patch

import boot_artwork


class BootArtworkTests(unittest.TestCase):
    def setUp(self):
        boot_artwork._attempts.clear()

    def tearDown(self):
        boot_artwork._attempts.clear()

    @patch('boot_artwork.time.sleep')
    def test_picture_is_acknowledged_before_checkpoint_and_unchanged_image_skips(self, _):
        lcd = Mock()
        flash = {}
        lcd.read_flash.side_effect = lambda address, size: flash.get(address, bytes(size))
        lcd.write_flash.side_effect = lambda address, data: flash.update({address: data})
        self.assertTrue(boot_artwork.sync(lcd))
        lcd.write_sram.assert_called_once_with(0, boot_artwork.SOURCE.read_bytes())
        self.assertLessEqual(len(lcd.write_sram.call_args.args[1]), 32767)
        lcd.store_sram_as_picture.assert_called_once_with(0, timeout=5)
        names = [call[0] for call in lcd.mock_calls]
        self.assertLess(names.index('store_sram_as_picture'), names.index('write_flash'))
        lcd.reset_mock()
        self.assertFalse(boot_artwork.sync(lcd))
        lcd.write_sram.assert_not_called()
        lcd.store_sram_as_picture.assert_not_called()
        lcd.write_flash.assert_not_called()

    @patch('boot_artwork.time.sleep')
    def test_failed_picture_write_does_not_mark_image_loaded_or_retry_in_process(self, _):
        lcd = Mock()
        lcd.read_flash.return_value = bytes(boot_artwork.SIZE)
        lcd.store_sram_as_picture.side_effect = TimeoutError('no acknowledgement')
        with self.assertRaises(TimeoutError):
            boot_artwork.sync(lcd)
        lcd.write_flash.assert_not_called()
        with self.assertRaisesRegex(RuntimeError, 'already failed'):
            boot_artwork.sync(lcd)
        self.assertEqual(lcd.store_sram_as_picture.call_count, 1)
