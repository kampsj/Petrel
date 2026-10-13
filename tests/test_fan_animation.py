import unittest
from unittest.mock import Mock
from test_capabilities import display, snapshot


class FanAnimationTests(unittest.TestCase):
    def view(self, speed=50):
        v = display(snapshot())
        v.pd.thermalManager['fan_speed'][0] = speed
        return v

    def test_same_rounded_interval_does_not_send_more_packets(self):
        v = self.view(50)
        v._sync_fan_animation(True)
        v.pd.thermalManager['fan_speed'][0] = 51
        v._sync_fan_animation(True)
        v.lcd.configure_animation.assert_called_once()
        self.assertEqual(v.lcd.configure_animation.call_args.args[-1], 2)

    def test_speed_change_continues_and_stop_only_sends_once(self):
        v = self.view(25)
        v._sync_fan_animation(True)
        v.pd.thermalManager['fan_speed'][0] = 100
        v._sync_fan_animation(True)
        self.assertEqual(v.lcd.configure_animation.call_args.args[-1], 1)
        self.assertFalse(v.lcd.configure_animation.call_args.kwargs['restart_from_first'])
        v.pd.thermalManager['fan_speed'][0] = 0
        v._sync_fan_animation(True)
        v._sync_fan_animation(True)
        self.assertEqual(v.lcd.configure_animation.call_count, 3)
        self.assertFalse(v.lcd.configure_animation.call_args.args[1])

    def test_redraw_and_reconnect_reconfigure_unchanged_speed(self):
        v = self.view()
        v._sync_fan_animation(True)
        v._sync_fan_animation(True, force=True)
        v._uart_epoch = 2
        v._sync_fan_animation(True)
        self.assertEqual(v.lcd.configure_animation.call_count, 3)

    def test_mmu_hides_animation_once(self):
        v = self.view()
        v._sync_fan_animation(True)
        v._sync_fan_animation(False)
        v._sync_fan_animation(False)
        self.assertEqual(v.lcd.configure_animation.call_count, 2)
        self.assertFalse(v.lcd.configure_animation.call_args.args[1])

    def test_all_percentages_are_bounded_and_monotonic(self):
        v = self.view()
        values = []
        for speed in range(1, 101):
            v.pd.thermalManager['fan_speed'][0] = speed
            v._sync_fan_animation(True)
            values.append(v._fan_animation_key[2])
        self.assertEqual(values[0], 100)
        self.assertEqual(values[-1], 1)
        self.assertEqual(values, sorted(values, reverse=True))
