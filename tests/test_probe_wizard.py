from concurrent.futures import Future
import unittest
from unittest.mock import ANY, Mock, patch

import probe_wizard
from test_capabilities import snapshot, printer, display


def data():
    result = snapshot(probe=True)
    result['objects'].append('manual_probe')
    result['status']['manual_probe'] = {'is_active': False}
    result['status']['configfile'] = {'save_config_pending': False, 'save_config_pending_items': {}}
    return result


class ProbeTests(unittest.TestCase):
    def printer(self):
        result = printer(data())
        result.subscription.request.side_effect = lambda *a, **k: Future()
        return result

    def status(self, result, active, pending=None):
        source = data()
        source['status']['manual_probe']['is_active'] = active
        if pending is not None:
            source['status']['configfile'] = dict(save_config_pending=bool(pending), save_config_pending_items=pending)
        result.subscription.snapshot.return_value = source
        result.update_variable()

    def started(self):
        result = self.printer()
        future = result.probe_wizard.start()
        future.set_result('ok')
        self.status(result, True)
        result.probe_wizard.update()
        return result

    def test_start_requires_homing_and_never_auto_homes_or_moves_z_zero(self):
        result = self.printer()
        future = result.probe_wizard.start()
        result.subscription.request.assert_called_once_with('printer.gcode.script', {'script': 'PROBE_CALIBRATE'}, guard=ANY)
        self.assertEqual(result.probe_wizard.phase, 'starting')
        future.set_result('ok')
        result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'starting')
        self.status(result, True)
        result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'active')
        blocked = self.printer()
        source = data()
        source['status']['toolhead']['homed_axes'] = 'xy'
        blocked.subscription.snapshot.return_value = source
        blocked.update_variable()
        with self.assertRaises(ValueError):
            blocked.probe_wizard.start()
        blocked.subscription.request.assert_not_called()

    def test_testz_requires_owned_session_and_serializes_steps(self):
        result = self.printer()
        with self.assertRaises(ValueError):
            result.probe_wizard.testz(-.01)
        result = self.started()
        future = result.probe_wizard.testz(-.01)
        self.assertEqual(result.subscription.request.call_args.args[1]['script'], 'TESTZ Z=-0.01')
        with self.assertRaises(ValueError):
            result.probe_wizard.testz(-.1)
        future.set_result('ok')
        result.probe_wizard.update()
        with self.assertRaises(ValueError):
            result.probe_wizard.testz(-10)

    def test_accept_checks_pending_offset_and_save_is_separate(self):
        result = self.started()
        future = result.probe_wizard.accept()
        future.set_result('ok')
        self.status(result, False, {'bltouch': {'z_offset': '2.100'}})
        result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'accepted')
        self.assertNotIn('SAVE_CONFIG', [call.args[1]['script'] for call in result.subscription.request.call_args_list])
        result.probe_wizard.save()
        self.assertEqual(result.subscription.request.call_args.args[1]['script'], 'SAVE_CONFIG')

    def test_unsuccessful_accept_response_does_not_allow_save(self):
        result = self.started()
        future = result.probe_wizard.accept()
        future.set_result('ok')
        self.status(result, False)
        with patch.object(probe_wizard.time, 'monotonic', return_value=result.probe_wizard.pending[2] + 31):
            result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'error')
        with self.assertRaises(ValueError):
            result.probe_wizard.save()

    def test_abort_does_not_save_and_waits_for_inactive_status(self):
        result = self.started()
        result.probe_wizard.abort().set_result('ok')
        result.probe_wizard.update()
        self.assertIsNotNone(result.probe_wizard.pending)
        self.status(result, False)
        result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'idle')
        self.assertEqual(result.subscription.request.call_args.args[1]['script'], 'ABORT')

    def test_external_session_existing_changes_and_print_block_start(self):
        for active, pending, state in ((True, {}, 'standby'), (False, {}, 'printing')):
            result = self.printer()
            source = data()
            source['status']['manual_probe']['is_active'] = active
            source['status']['configfile']['save_config_pending'] = bool(pending)
            source['status']['print_stats']['state'] = state
            result.subscription.snapshot.return_value = source
            result.update_variable()
            with self.assertRaises(ValueError):
                result.probe_wizard.start()
            result.subscription.request.assert_not_called()

    def test_epoch_change_does_not_replay_commands(self):
        result = self.started()
        source = data()
        source['epoch'] = 2
        result.subscription.snapshot.return_value = source
        result.update_variable()
        result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'interrupted')
        result.subscription.request.assert_called_once()
        with self.assertRaises(ValueError):
            result.probe_wizard.testz(.1)

    def test_ui_offers_probe_separately_from_runtime_offset(self):
        result = display(data())
        self.assertIn('PROBE', [item[0] for item in result._menus['control']])
        result._probe_selection = 0
        result.checkkey = result.ProbeWizardID
        result.Draw_Probe_Wizard()
        result.pd.sendGCode.assert_not_called()

    def test_save_rejects_unrelated_or_changed_pending_configuration(self):
        for pending in ({'bltouch': {'z_offset': '2.1'}, 'extruder': {'pid_kp': '1'}},
                        {'bltouch': {'z_offset': '2.2'}}):
            result = self.started()
            result.probe_wizard.accept().set_result('ok')
            self.status(result, False, {'bltouch': {'z_offset': '2.1'}})
            result.probe_wizard.update()
            self.status(result, False, pending)
            with self.assertRaises(ValueError):
                result.probe_wizard.save()
            self.assertNotIn('SAVE_CONFIG', [call.args[1]['script'] for call in result.subscription.request.call_args_list])


class ProbeRegressionTests(unittest.TestCase):
    printer = ProbeTests.printer
    status = ProbeTests.status
    started = ProbeTests.started
    def test_pending_mesh_does_not_block_start_or_trigger_save(self):
        result = self.printer()
        self.status(result, False, {'bed_mesh default': {'points': 'old'}})
        result.probe_wizard.start()
        result.subscription.request.assert_called_once_with('printer.gcode.script',
            {'script': 'PROBE_CALIBRATE'}, guard=ANY)
        result.sendGCode.assert_not_called()

    def test_long_probe_start_is_not_failed_after_http_timeout(self):
        result = self.printer()
        future = result.probe_wizard.start()
        started = result.probe_wizard.pending[2]
        with patch.object(probe_wizard.time, 'monotonic', return_value=started+45):
            result.probe_wizard.update()
            self.assertEqual(result.probe_wizard.phase, 'starting')
            future.set_result('ok')
            self.status(result, True)
            result.probe_wizard.update()
        self.assertEqual(result.probe_wizard.phase, 'active')

    def test_all_small_and_bracket_steps_dispatch_once(self):
        result = self.started()
        for step in (-.005, .005, -.01, .01, -.05, .05, -.1, .1, -1, 1, '--', '-', '+', '++'):
            before = result.subscription.request.call_count
            future = result.probe_wizard.testz(step)
            token = step if isinstance(step, str) else '{:g}'.format(step)
            self.assertEqual(result.subscription.request.call_args.args[1], {'script': 'TESTZ Z='+token})
            self.assertEqual(result.subscription.request.call_count, before+1)
            future.set_result('ok')
            result.probe_wizard.update()

    def test_compact_ui_shows_four_steps_and_live_bounds_without_waiting_text(self):
        view = display(data())
        view.pd = self.started()
        source = data()
        source['status']['manual_probe'] = {'is_active': True, 'z_position': 2.804,
            'z_position_lower': 2.779, 'z_position_upper': 2.829}
        view.pd.subscription.snapshot.return_value = source
        view.pd.update_variable()
        view.checkkey = view.ProbeWizardID
        view._probe_selection = 1
        self.assertEqual([label for label, _ in view._probe_options()],
                         ['--', '-', '+', '++', 'Cancel', 'Accept'])
        view.Draw_Probe_Wizard()
        labels = [c.args[-1] for c in view.lcd.draw_text.call_args_list]
        for text in ('2.779', '2.804', '2.829', '--', '-', '+', '++', 'Cancel', 'Accept'):
            self.assertIn(text, labels)
        view.Clear_Main_Window = Mock()
        view.Draw_Title = Mock()
        view.lcd.reset_mock()
        future = view.pd.probe_wizard.testz('-')
        view.Draw_Probe_Wizard()
        view.Clear_Main_Window.assert_not_called()
        view.lcd.update.assert_not_called()
        view.get_encoder_state = Mock(return_value=view.ENCODER_DIFF_ENTER)
        before = view.pd.subscription.request.call_count
        view.HMI_Probe_Wizard()
        self.assertEqual(view.pd.subscription.request.call_count, before)
        future.set_result('ok')
        source['status']['manual_probe']['z_position'] = 2.79
        view.pd.update_variable()
        view.pd.probe_wizard.update()
        view.Draw_Probe_Wizard()
        view.Clear_Main_Window.assert_not_called()
        view.Draw_Title.assert_not_called()
        labels = [c.args[-1] for c in view.lcd.draw_text.call_args_list]
        self.assertIn('2.790', labels)
        self.assertFalse(any('Waiting' in text or 'TESTZ' in text for text in labels))
        view.lcd.reset_mock()
        view.get_encoder_state.return_value = view.ENCODER_DIFF_CW
        view.HMI_Probe_Wizard()
        self.assertEqual(view._probe_selection, 2)
        view.Clear_Main_Window.assert_not_called()
        self.assertEqual([c.args[-1] for c in view.lcd.draw_text.call_args_list], ['-', '+'])
