import unittest
from unittest.mock import Mock, patch
from concurrent.futures import Future
import test_print_tuning
from test_capabilities import display
from test_mmu_control import mmu_snapshot
from test_t5uic1_driver import driver
from PIL import Image
from io import BytesIO
from thumbnail_preview import image_jpeg


class PrintFocusTests(unittest.TestCase):
    def view(self, mmu=False):
        data=test_print_tuning.PrintTuningTests().data()
        data['status']['print_stats'].update(state='printing',filename='part.gcode',print_duration=120,info={'current_layer':85,'total_layer':200})
        data['status']['virtual_sdcard']['progress']=.42
        if mmu:
            data['status']['mmu']=mmu_snapshot()['status']['mmu'];data['objects'].append('mmu')
        v=display(data);v.lcd.DWIN_WIDTH=272;v.lcd.DWIN_HEIGHT=480
        v._sync_thumbnail_cache=Mock();v._print_thumbnail_key=None
        v._sync_fan_animation=Mock();v.checkkey=v.PrintProcess
        v.get_encoder_state=Mock(return_value=v.ENCODER_DIFF_ENTER)
        return v,data

    def test_all_seventeen_settings_fit_one_screen(self):
        v,_=self.view();v._focus_tune_open()
        self.assertEqual(len(v._focus_tune_rows()),18)
        self.assertLessEqual(max(y+(24 if s is None else 20) for s,y in v._focus_tune_rows()),480)
        self.assertEqual(v.checkkey,v.Tune)
        v.lcd.reset_mock();v._focus_tune_tick();v.lcd.draw_rectangle.assert_not_called()

    def test_quiet_edit_is_optimistic_and_rejects_without_popup(self):
        v,_=self.view();future=Future();v.pd.set_print_setting=Mock(return_value=future)
        v._focus_tune_open();v._tune_edit=v.pd.print_settings()[0];v._tune_target=125;v.checkkey=v.TuneEdit
        v._show_message=Mock();v._focus_edit_input()
        self.assertEqual(v._quiet_edits['speed']['target'],125)
        v.pd.set_print_setting.assert_called_once_with('speed',125,report_error=False)
        future.set_exception(ValueError('Rejected'));v._focus_tune_tick()
        self.assertNotIn('speed',v._quiet_edits);self.assertIn('speed',v._quiet_blinks)
        v._show_message.assert_not_called()

    def test_late_old_failure_does_not_revert_newer_edit(self):
        v,_=self.view();old=Future();new=Future()
        v._focus_submit('speed',120,lambda:old);v._focus_submit('speed',130,lambda:new)
        old.set_exception(ValueError('Old failure'));v._focus_tick_quiet()
        self.assertEqual(v._quiet_edits['speed']['target'],130);self.assertNotIn('speed',v._quiet_blinks)

    def test_slow_request_is_not_rejected_by_elapsed_time(self):
        v,_=self.view();f=Future()
        with patch('ui_print_focus.time.monotonic',return_value=0):v._focus_submit('speed',130,lambda:f)
        with patch('ui_print_focus.time.monotonic',return_value=1000):v._focus_tick_quiet()
        self.assertIn('speed',v._quiet_edits);self.assertFalse(v._quiet_blinks)

    def test_subscription_confirmation_is_silent_and_epoch_clears_pending(self):
        v,data=self.view();f=Future();v._focus_submit('speed',130,lambda:f)
        data['status']['gcode_move']['speed_factor']=1.3;v.pd.update_variable();v._focus_tick_quiet()
        self.assertNotIn('speed',v._quiet_edits);self.assertFalse(v._quiet_blinks)
        v._focus_submit('speed',140,lambda:Future());data['epoch']+=1;v.pd.update_variable();v._focus_tick_quiet()
        self.assertFalse(v._quiet_edits)

    def test_pause_direct_stop_requires_safe_confirmation(self):
        v,_=self.view();v.select_print.set(1);v.pd.pause_job=Mock(return_value=Future())
        v.Popup_window_PauseOrStop=Mock();v.HMI_Printing()
        v.pd.pause_job.assert_called_once_with(report_error=False);v.Popup_window_PauseOrStop.assert_not_called()
        self.assertEqual(v._focus_buttons()[1][0],'Resume')
        v.select_print.set(2);v.HMI_Printing();v.Popup_window_PauseOrStop.assert_called_once()
        self.assertFalse(v.pd.HMI_flag.select_flag)

    def test_power_popup_restores_editor_draft(self):
        v,_=self.view();v._tune_edit=v.pd.print_settings()[0];v._tune_target=137;v.checkkey=v.TuneEdit
        self.assertTrue(v._restore_power_editor());self.assertEqual(v._tune_target,137)

    def test_mmu_full_error_reader_recovery_and_return(self):
        v,data=self.view(mmu=True)
        data['status']['mmu'].update(print_state='pause_locked',reason_for_pause='Toolhead sensor is still active. '*30)
        v.pd.update_variable();self.assertEqual(v._focus_buttons()[1][0],'MMU')
        v._focus_error_open();self.assertGreater(len(v._focus_error_lines),15)
        v._focus_error_input();self.assertEqual(v.checkkey,v.MMUMenu)
        self.assertEqual(v._mmu_page,'recover');self.assertTrue(v._mmu_return_print)
        v.Goto_PrintProcess=Mock();v._mmu_history=[];v.pd.mmu_session.pending=None;v._mmu_back()
        v.Goto_PrintProcess.assert_called_once();self.assertFalse(v._mmu_return_print)

    def test_print_render_has_no_work_when_unchanged(self):
        v,_=self.view();v._focus_print_open();v.lcd.reset_mock()
        v._focus_print_tick();v.lcd.draw_rectangle.assert_not_called();v.lcd.draw_text.assert_not_called()

    def test_print_preview_is_small_baseline_420_and_dark_foreground_protected(self):
        from PIL import JpegImagePlugin
        stream=BytesIO();Image.new('RGBA',(256,256),(0,0,0,255)).save(stream,'PNG')
        with Image.open(BytesIO(image_jpeg(stream.getvalue(),size=88))) as image:
            self.assertEqual(image.size,(88,88));self.assertEqual(JpegImagePlugin.get_sampling(image),2)
            self.assertGreaterEqual(min(image.getpixel((44,44))),48)

    def test_every_real_draw_stays_inside_panel(self):
        v,_=self.view();v.lcd=driver();v.lcd.DWIN_WIDTH=272;v.lcd.DWIN_HEIGHT=480
        v.Goto_PrintProcess();v._focus_tune_open();v._tune_edit=v.pd.print_settings()[0];v._tune_target=100;v._focus_edit_draw()
        for frame in v.lcd.serial.frames:
            if frame[1]==5:
                x0,y0,x1,y1=[int.from_bytes(frame[i:i+2],'big') for i in (5,7,9,11)]
                self.assertTrue(0<=x0<=x1<272,(x0,y0,x1,y1));self.assertTrue(0<=y0<=y1<480,(x0,y0,x1,y1))

    def test_pause_state_change_updates_fields_without_clearing_screen(self):
        v,data=self.view();v.Goto_PrintProcess();v.Goto_PrintProcess=Mock()
        data['status']['print_stats']['state']='paused';v.pd.update_variable()
        v._present_print_state();v.Goto_PrintProcess.assert_not_called()
        self.assertEqual(v._focus_buttons()[1][0],'Resume')
