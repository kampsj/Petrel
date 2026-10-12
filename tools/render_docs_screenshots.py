#!/usr/bin/env python3
"""Render documentation through the real UI and T5UIC1 emulator, offline.

Uses the regression fixtures as isolated Moonraker/GPIO/serial doubles. Nothing
connects to a printer, and no production renderer is replaced by a mock.
"""
import argparse
from concurrent.futures import Future
from io import BytesIO
import logging
import math
from pathlib import Path
import shutil
import sys
import tempfile
import time
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]

from PIL import Image, ImageDraw
from test_capabilities import display
from test_bed_mesh import data as mesh_snapshot
from test_screws_tilt import data as screw_snapshot, payload as screw_results
from test_mmu_control import mmu_snapshot, hardware_status, add_motor_status, add_led_status, add_multiple_units
from test_t5uic1_driver import driver
from dwin_emulator.assets import PanelAssets
from dwin_emulator.framebuffer import Framebuffer
from bed_mesh import MeshData
from test_regressions import ui as application_ui
BuzzerSettings = application_ui.BuzzerSettings
from preview_metadata import PreviewDetails, Filament
from thumbnail_cache import ThumbnailCache
from mmu_filament_view import filament_color

SCENES = []


def scene(name, group, english, turkish):
    def register(draw):
        SCENES.append((name, group, english, turkish, draw))
        return draw
    return register


def sample(mmu=False, **changes):
    data = mesh_snapshot()
    data['settings'].update(screw_snapshot()['settings'])
    data['objects'] += ['screws_tilt_adjust', 'manual_probe', 'output_pin case_light', 'pwm_cycle_time Buzzer']
    data['settings']['output_pin case_light'] = {'pwm': True, 'value': .65}
    data['settings']['pwm_cycle_time buzzer'] = {'value': 0, 'cycle_time': .001}
    data['status'].update(manual_probe={'is_active': False},
                          **{'screws_tilt_adjust': {'results': {}}, 'output_pin case_light': {'value': .65}})
    data['status']['toolhead'].update(position=[125, 125, 5, 0], max_velocity=300,
                                     max_accel=5000, square_corner_velocity=5, minimum_cruise_ratio=.5)
    data['status']['motion_report'].update(live_position=[125, 125, 5, 0], live_velocity=0, live_extruder_velocity=0)
    data['status']['gcode_move']['position'] = [125,125,5,0]
    data['status']['extruder'].update(temperature=27, target=0)
    data['status']['heater_bed'].update(temperature=26, target=0)
    data['status']['fan']['speed'] = 0
    if mmu:
        raw = mmu_snapshot(**changes)['status']['mmu']
        raw.update(gate_color=['303030', 'eee9cf', '36a7ef', 'd52b28'],
                   gate_color_rgb=[[.19,.19,.19], [.93,.91,.81], [.21,.65,.94], [.84,.17,.16]],
                   gate_filament_name=['Black', 'Natural', 'Ocean Blue', 'Red'],
                   gate_material=['PLA'] * 4, gate_status=[1] * 4,
                   gate_spool_id=[101,102,103,104], gate_temperature=[215] * 4,
                   sensors={'mmu_shared_exit': True, 'extruder': True, 'toolhead': True},
                   filament_position=620, filament_remaining=0, filament_remaining_color='')
        raw.update(changes)
        data['status']['mmu'] = raw
        data['objects'] += ['mmu', 'mmu_machine']
        data['status']['mmu_machine'] = hardware_status('LinearServoSelector')
        data['status']['mmu_machine']['unit_0'].update(is_homed=True, display_name='Petrel MMU')
        raw.update(unit=0, is_homed=True, selector={'grip': 'Gripped'})
        data['settings']['mmu'] = {'gate_homing_endstop': 'mmu_gate', 'extruder_homing_endstop': 'extruder'}
        add_motor_status(data)
        add_led_status(data)
        data['status']['extruder'].update(temperature=215, target=215)
    return data


def canvas(data=None):
    v = display(data or sample())
    v.lcd = driver()
    v.framebuffer = Framebuffer(PanelAssets())
    v.lcd._packet_observer = v.framebuffer
    v.lcd.clear(0)
    v.get_encoder_state = Mock(return_value=v.ENCODER_DIFF_NO)
    v._offline = False
    v.checkkey = v.MainMenu
    v._power_focus = False
    v._display_values = [85, 5, 15]
    v._display_saved = tuple(v._display_values)
    v._buzzer_values = v._buzzer_saved = BuzzerSettings()
    v._case_light_on, v._case_light_brightness = True, 65
    v._live_jog = False
    v.pd.subscription.responses_since.return_value = (0, ())
    v.pd.subscription.request.side_effect = lambda *a, **k: Future()
    v.pd.refresh_system_info = Mock(return_value=False)
    v.pd.system_info.update(petrel='v4.0.0', moonraker='v0.11.0', mainsail='v2.19.0',
                           network='Online', ip='192.168.1.50', wifi_ssid='Workshop', wifi_rssi=-58,
                           host_cpu=18, host_ram=42, host_temp=46.2,
                           mcus=({'name': 'mcu', 'load': 1.4, 'temperature': 42.1, 'version': 'v0.13.0'},
                                 {'name': 'mmu', 'load': .6, 'temperature': 39.8, 'version': 'v0.13.0'}))
    v.pd.SHORT_BUILD_VERSION = 'v0.13.0'
    v.pd.MACHINE_SIZE = '250x228x205'
    if v.pd.mmu:
        v.pd.mmu.update(remaining_percent=(2, 39, 69, 57), name='Petrel MMU',
                        exit_led_rgb=((0,.25,0), (0,.25,0), (0,.5,0), (0,.25,0)))
    return v


def finish(v, dashboard=True):
    if dashboard:
        v.Draw_Status_Area(False)
    v.lcd.update()
    return v.framebuffer.snapshot()[0]


@scene('home', 'home', 'Home with Happy Hare and Spoolman', 'Happy Hare ve Spoolman ile ana ekran')
def home():
    v = canvas(sample(mmu=True)); v.select_page.set(0); v.Goto_MainMenu()
    return finish(v)


@scene('home-page-2', 'home', 'MMU, Display, Maintenance and Info tiles', 'MMU, Display, Maintenance ve Info simgeleri')
def home_page_two():
    v = canvas(sample(mmu=True)); v.select_page.set(5); v.Goto_MainMenu()
    return finish(v)


@scene('boot-splash', 'home', 'Petrel startup and progress', 'Petrel açılışı ve ilerleme göstergesi')
def boot():
    v = canvas(); v.lcd.show_jpeg(0); v._draw_boot_progress(70, message='Waiting for printer...')
    return finish(v, False)


def menu(method, selection=None, configure=None):
    v = canvas()
    if configure:
        configure(v)
    if selection:
        getattr(v, selection[0]).set(selection[1])
    getattr(v, method)()
    return finish(v)


for name, method, en, tr in (
        ('prepare', 'Draw_Prepare_Menu', 'Prepare', 'Hazırlık'),
        ('control', 'Draw_Control_Menu', 'Control', 'Kontrol'),
        ('temperature', 'Draw_Temperature_Menu', 'Temperature targets', 'Sıcaklık hedefleri'),
        ('motion-runtime', 'Draw_Motion_Menu', 'Runtime motion settings', 'Çalışma anındaki hareket ayarları'),
        ('move', 'Draw_Move_Menu', 'Move with Live jog disabled', 'Live jog kapalı hareket menüsü'),
        ('maintenance', 'Draw_Maintenance_Menu', 'Maintenance placeholder', 'Bakım menüsü'),
        ('display', 'Draw_Display_Menu', 'Brightness and idle dimming', 'Parlaklık ve boşta karartma')):
    scene(name, 'controls', en, tr)(lambda method=method: menu(method))


@scene('move-live-jog', 'controls', 'Move with Live jog enabled', 'Live jog açık hareket menüsü')
def live_jog():
    return menu('Draw_Move_Menu', ('select_axis', 5), lambda v: setattr(v, '_live_jog', True))


@scene('prepare-preheat', 'controls', 'Preheat presets and cooldown', 'Ön ısıtma presetleri ve soğutma')
def preheat():
    return menu('Draw_Prepare_Menu', ('select_prepare', 7), lambda v: setattr(v, 'index_prepare', 7))


@scene('case-light', 'controls', 'Case light enabled', 'Kasa ışığı açık')
def case_light():
    return menu('Draw_Case_Light_Menu')


@scene('case-light-off', 'controls', 'Case light disabled', 'Kasa ışığı kapalı')
def case_light_off():
    return menu('Draw_Case_Light_Menu', configure=lambda v: setattr(v, '_case_light_on', False))


@scene('buzzer', 'controls', 'Choose the buzzer output', 'Buzzer çıkışını seçme')
def buzzer():
    v = canvas(); v._buzzer_values = BuzzerSettings('Buzzer', 60, 2, 1)
    v._buzzer_selection = 2; v.Draw_Buzzer_Menu()
    return finish(v)


@scene('display-sound-settings', 'controls', 'Volume, click and encoder tones', 'Ses seviyesi, tıklama ve enkoder tonları')
def sound():
    v = canvas(); v._buzzer_values = BuzzerSettings('Buzzer', 60, 2, 1)
    v._display_selection = 7; v.Draw_Display_Menu()
    return finish(v)


@scene('display-volume-edit', 'controls', 'Editing sound volume', 'Ses seviyesini düzenleme')
def volume():
    v = canvas(); v._buzzer_values = BuzzerSettings('Buzzer', 60, 2, 1)
    v._display_selection = 5; v._display_edit = True; v.Draw_Display_Menu()
    return finish(v)


@scene('temperature-edit', 'controls', 'Editing a hotend target', 'Hotend hedefini düzenleme')
def thermal_edit():
    v=canvas(); v.Draw_Temperature_Menu(); v._open_thermal_editor('TEMP',1)
    return finish(v)


@scene('preheat-settings', 'controls', 'Edit and save a preheat preset', 'Ön ısıtma presetini düzenleme ve kaydetme')
def preset():
    v=canvas(); v._draw_capability_menu('preheat', v.select_PLA, profile=0)
    return finish(v)


@scene('power-confirm', 'controls', 'Printer power-off confirmation', 'Yazıcıyı kapatma onayı')
def power():
    v=canvas(); v._power_confirm_yes=True; v._draw_power_confirmation()
    return finish(v)


def cube_thumbnail():
    # Representative slicer-style sample model; UI uses the normal SRAM path.
    image=Image.new('RGB',(128,128),'black'); draw=ImageDraw.Draw(image)
    draw.polygon([(20,50),(64,25),(108,50),(64,75)],fill='#a2d5ef')
    draw.polygon([(20,50),(64,75),(64,113),(20,88)],fill='#369bd4')
    draw.polygon([(64,75),(108,50),(108,88),(64,113)],fill='#22668a')
    for y in range(58,88,5):
        draw.line([(21,y),(63,y+25)],fill='#2c84b5')
        draw.line([(65,y+25),(107,y)],fill='#185776')
    stream=BytesIO(); image.save(stream,format='JPEG',quality=92)
    return stream.getvalue()


@scene('print-file', 'printing', 'Folders and G-code files', 'Klasörler ve G-code dosyaları')
def files():
    v=canvas(); v._file_paths=('parts/','calibration_cube.gcode','bracket.gcode','spool_holder.gcode')
    v.select_file.set(2); v.index_file=v.MROWS
    v.Draw_Print_File_Menu()
    return finish(v)


@scene('print-preview', 'printing', 'Thumbnail, metadata and print confirmation', 'Önizleme, bilgiler ve yazdırma onayı')
def preview():
    v=canvas(); key=('calibration_cube.gcode',1,123456)
    v._thumbnail_cache=ThumbnailCache(v.pd.client)
    v._preview_path=key[0]; v._preview_cache_key=key; v._preview_choice=1; v._preview_error=None
    payload=cube_thumbnail(); v.lcd.write_sram(0,payload)
    v._thumbnail_cache.entries[key]=(0,len(payload))
    v._thumbnail_cache.details[key]=PreviewDetails(7320,24,11200,33.4,
        (Filament(0,'PLA',filament_color('303030'),8.2),Filament(1,'PLA',filament_color('eee9cf'),9.6),
         Filament(2,'PLA',filament_color('36a7ef'),11.2),Filament(3,'PLA',filament_color('d52b28'),4.4)))
    v.Draw_File_Preview(); v.lcd.show_sram_jpeg(8,68,0)
    return finish(v)


def printing(paused=False,tune=False):
    data=sample(); data['status']['print_stats'].update(state='paused' if paused else 'printing',
        filename='calibration_cube.gcode',print_duration=2700,total_duration=2800)
    data['status']['virtual_sdcard'].update(is_active=not paused,progress=.38)
    data['status']['extruder'].update(temperature=215,target=215)
    data['status']['heater_bed'].update(temperature=60,target=60)
    data['status']['fan']['speed']=.5
    data['status']['motion_report'].update(live_position=[125,125,8.4,200],live_velocity=0 if paused else 65,
                                         live_extruder_velocity=0 if paused else 2.1)
    v=canvas(data)
    if tune: v.Draw_Tune_Menu()
    else: v.Goto_PrintProcess()
    return finish(v)


scene('printing','printing','Print progress, time and controls','Baskı ilerlemesi, süre ve kontroller')(lambda:printing())
scene('printing-paused','printing','Paused print and Resume','Duraklatılmış baskı ve Resume')(lambda:printing(paused=True))
scene('tune','printing','Live print tuning','Canlı baskı ayarları')(lambda:printing(tune=True))


@scene('leveling', 'leveling', 'Leveling workflows', 'Tabla ayarı işlemleri')
def leveling():
    return menu('Draw_Bed_Mesh_Menu')


@scene('bed-mesh', 'leveling', 'Bed Mesh submenu', 'Bed Mesh alt menüsü')
def bed_mesh_menu():
    return menu('Draw_Bed_Mesh_Menu', configure=lambda v: setattr(v, '_mesh_submenu', True))


def mesh(phase='viewing', name='default', confirm=None):
    v = canvas(); s = v.pd.bed_mesh
    s.phase = phase; s.profile_name = 'lcd_mesh_1'; s.message = ''
    points = tuple(tuple(round(-.12 + .15 * math.exp(-((x-3)**2+(y-3)**2)/7) + .018*x, 3)
                         for x in range(7)) for y in range(7))
    s.mesh = MeshData(name, points, (20,30), (220,230))
    v._mesh_confirmation = confirm; v._mesh_button_selection = 0
    v.Draw_Bed_Mesh()
    return finish(v)


scene('mesh-viewer', 'leveling', 'Mesh Viewer: default profile', 'Mesh Viewer: default profili')(lambda: mesh())
scene('mesh-pei', 'leveling', 'Mesh Viewer: PEI profile', 'Mesh Viewer: PEI profili')(lambda: mesh(name='PEI'))
scene('mesh-results', 'leveling', 'Completed measurement: Save or Continue', 'Tamamlanan ölçüm: Save veya Continue')(lambda: mesh('complete', 'lcd_mesh_1'))
scene('mesh-save-confirm', 'leveling', 'Confirm mesh save and Klipper restart', 'Mesh kaydını ve Klipper yeniden başlatmasını onaylama')(lambda: mesh('complete', confirm='save'))
scene('mesh-stop-confirm', 'leveling', 'Confirm emergency stop during probing', 'Ölçüm sırasında acil durdurmayı onaylama')(lambda: mesh('measuring', confirm='cancel'))


@scene('mesh-calibrating', 'leveling', 'Live probe results during calibration', 'Kalibrasyon sırasında canlı prob sonuçları')
def mesh_live():
    v = canvas(); s = v.pd.bed_mesh
    s.phase, s.message, s.mesh = 'measuring', 'Probing bed...', None
    s.layout = ((7,7), (20,30), (220,230))
    s.progress = {(x,y): round(-.08 + .018*x + .012*y,3) for y in range(3) for x in range(7)}
    v.Draw_Bed_Mesh()
    return finish(v)


@scene('mesh-profiles', 'leveling', 'Current and saved mesh profiles', 'Geçerli ve kayıtlı mesh profilleri')
def mesh_profiles():
    v = canvas(); s = v.pd.bed_mesh; s.phase = 'listed'
    raw = dict(v.pd.state.status['bed_mesh'])
    raw['profiles'] = {'default': next(iter(raw['profiles'].values())), 'PEI': next(iter(raw['profiles'].values()))}
    s.status = raw; v._mesh_profile_selection = 1; v.Draw_Mesh_Profiles()
    return finish(v)


def screws(phase):
    v = canvas(); s = v.pd.screws_tilt; s.corners = s._layout()
    s.phase, s.message = ('measuring','Probing corners...') if phase=='probing' else ('reading','Reading results...')
    s.pending = Future()
    if phase in ('success','adjust'):
        result = screw_results()
        if phase=='success':
            for value in result['status']['screws_tilt_adjust']['results'].values():
                if not value['is_base']: value.update(z=.012,adjust='00:01')
        s._read_results(result); s.phase='complete'; s.pending=None
    v.Draw_Screws_Result()
    return finish(v)


scene('screws-tilt', 'leveling', 'Calculate screw adjustments', 'Vida ayarlarını hesaplama')(lambda: menu('Draw_Screws_Menu'))
scene('screws-tilt-probing', 'leveling', 'Measuring the screw corners', 'Vida köşelerini ölçme')(lambda: screws('probing'))
scene('screws-tilt-reading-results', 'leveling', 'Reading screw measurements', 'Vida ölçümlerini okuma')(lambda: screws('reading'))
scene('screws-tilt-success', 'leveling', 'Screw tolerance achieved', 'Vida ayarında toleransa ulaşıldı')(lambda: screws('success'))
scene('screws-tilt-adjust', 'leveling', 'Required manual screw adjustment', 'Gerekli manuel vida ayarı')(lambda: screws('adjust'))


def probe(phase):
    data = sample(); data['status']['manual_probe'] = dict(is_active=phase=='active', z_position_lower=2.779,
                                                         z_position=2.804, z_position_upper=2.829)
    v = canvas(data); v.pd.probe_wizard.phase = phase; v._probe_selection = 1 if phase=='active' else 0
    v.Draw_Probe_Wizard()
    return finish(v)


for name, phase, en, tr in (
        ('probe-calibration','idle','Start probe calibration','Prob kalibrasyonunu başlatma'),
        ('probe-calibration-active','active','Four controls and live Z bounds','Dört kontrol ve canlı Z sınırları'),
        ('probe-calibration-accepted','accepted','Save or continue after accepting the offset','Offset kabulünden sonra kaydetme veya devam etme')):
    scene(name,'leveling',en,tr)(lambda phase=phase:probe(phase))


def mmu(page='home', changes=None, setup=None):
    v = canvas(sample(mmu=True, **(changes or {}))); v.Enter_MMU_Menu()
    if page!='home': v._mmu_open(page)
    if setup: setup(v)
    v.Draw_MMU_Menu()
    return finish(v, False)


@scene('mmu-group-members', 'mmu', 'EndlessSpool group membership', 'EndlessSpool grup üyeliği')
def group_members():
    v=canvas(sample(mmu=True)); v.Enter_MMU_Menu(); v._mmu_open('endless')
    v._mmu_group=0; v._mmu_open('group')
    return finish(v,False)


@scene('mmu-confirm', 'mmu', 'Confirm a gate operation', 'Bir gate işlemini onaylama')
def mmu_confirm():
    v=canvas(sample(mmu=True)); v.Enter_MMU_Menu()
    v._mmu_confirmation=v.pd.mmu_session.prepare('unload',gate=2)
    v._mmu_open('confirm')
    return finish(v,False)


def unit_scene(page):
    data=sample(mmu=True,gate=0,tool=0,filament='Unloaded',filament_pos=0)
    add_multiple_units(data)
    v=canvas(data); v.Enter_MMU_Menu(); v._mmu_open(page)
    return finish(v,False)


scene('mmu-units','mmu','Browse MMU units','MMU ünitelerine göz atma')(lambda:unit_scene('units'))
scene('mmu-unit-gates','mmu','Gates of one MMU unit','Bir MMU ünitesinin gate listesi')(lambda:unit_scene('unit'))


for name,page,en,tr in (
        ('mmu','home','Loaded filament and direct tool controls','Yüklü filament ve doğrudan araç kontrolleri'),
        ('mmu-more','more','Additional MMU controls','Ek MMU kontrolleri'),
        ('mmu-gates','gates','Gate list','Gate listesi'),
        ('mmu-gate-details','gate','Actions for one gate','Bir gate için işlemler'),
        ('mmu-filament','filament','Filament and Spoolman details','Filament ve Spoolman bilgileri'),
        ('mmu-spool','spool','Assign a spool ID','Makara ID atama'),
        ('mmu-tool-map','map','Tool-to-gate mapping','Araç-gate eşlemesi'),
        ('mmu-endless-spool','endless','EndlessSpool groups','EndlessSpool grupları'),
        ('mmu-manage','manage','Management and recovery','Yönetim ve kurtarma'),
        ('mmu-status','status','Sensors and MMU status','Sensörler ve MMU durumu'),
        ('mmu-maintenance','maintenance','MMU maintenance actions','MMU bakım işlemleri'),
        ('mmu-options','options','MMU configuration options','MMU yapılandırma seçenekleri'),
        ('mmu-leds','leds','MMU LED modes','MMU LED modları'),
        ('mmu-bypass','bypass','Extruder and bypass controls','Ekstrüder ve bypass kontrolleri'),
        ('mmu-recovery','recover','Recovery actions','Kurtarma işlemleri'),
        ('mmu-manual-state','manual','Report the actual filament state','Gerçek filament durumunu bildirme')):
    scene(name,'mmu',en,tr)(lambda page=page:mmu(page, changes=dict(filament='Unloaded',filament_pos=0,filament_position=0) if page=='maintenance' else None))


for name,action,pos,progress,en,tr in (
        ('mmu-loading','Loading',3,45,'Filament moving through the Bowden tube','Bowden tüpünde ilerleyen filament'),
        ('mmu-unloading','Unloading',3,65,'Filament being withdrawn','Geri çekilen filament'),
        ('mmu-purging','Purging',10,100,'Purge and residual filament color','Purge ve kalan filament rengi')):
    scene(name,'mmu',en,tr)(lambda action=action,pos=pos,progress=progress:
        mmu(changes=dict(action=action,filament='Loaded' if pos==10 else 'Unknown',filament_pos=pos,
                         bowden_progress=progress,filament_position=310,filament_remaining=8,
                         filament_remaining_color='d52b28')))


def info(kind):
    v = canvas(); items=v._info_items()
    index = {'overview':0, 'mcu-details': next(i for i,item in enumerate(items) if item[0]=='section' and item[1].startswith('MCU:')),
             'mcu-overview': next(i for i,item in enumerate(items) if item[0]=='section' and item[1]=='MCU: mmu'),
             'software': next(i for i,item in enumerate(items) if item[0]=='section' and item[1]=='Software'),
             'project': next(i for i,item in enumerate(items) if item[0]=='qr')}
    v._info_scroll=index.get(kind,index['project'])
    updater=v._software_updater()
    if kind=='update-checking': updater.phase,updater.message='checking','Please wait...'
    if kind=='update-current': updater.phase,updater.message='current','Up to date'
    v.Draw_Info_Menu()
    return finish(v)


for name,kind,en,tr in (
        ('info-overview','overview','Machine, network and host','Makine, ağ ve host'),
        ('info-mcu-details','mcu-details','Main MCU measurements','Ana MCU ölçümleri'),
        ('info-mcu-overview','mcu-overview','MMU MCU and software','MMU MCU ve yazılım'),
        ('info-software','software','Installed software versions','Kurulu yazılım sürümleri'),
        ('info-project','project','Project QR and updater','Proje QR kodu ve updater'),
        ('info-update-checking','update-checking','Checking for updates','Güncellemeleri kontrol etme'),
        ('info-update-current','update-current','Software up to date','Yazılım güncel')):
    scene(name,'info',en,tr)(lambda kind=kind:info(kind))


def write_galleries():
    groups = [('home', 'Home and startup', 'Ana ekran ve açılış'),
              ('printing', 'Files and printing', 'Dosyalar ve baskı'),
              ('controls', 'Printer and display controls', 'Yazıcı ve ekran kontrolleri'),
              ('leveling', 'Bed leveling and calibration', 'Tabla ayarı ve kalibrasyon'),
              ('mmu', 'MMU and filament', 'MMU ve filament'),
              ('info', 'System information and updates', 'Sistem bilgileri ve güncellemeler')]
    for turkish in (False, True):
        title = 'Ekran galerisi' if turkish else 'Screenshot gallery'
        intro = ('Bu görseller güncel Petrel arayüzünden, emülatör aracılığıyla özgün **272×480 RGB PNG** boyutunda üretilmiştir. Yazıcı, sıcaklık, filament ve ağ değerleri örnektir; gerçek bir makineden alınmış ölçümler değildir. İsteğe bağlı menüler yazıcınızın özelliklerine göre görünür.' if turkish else
                 'These images are rendered from the current Petrel UI through the emulator as original-size **272×480 RGB PNGs**. Printer, temperature, filament and network values are examples, not measurements from a physical machine. Optional menus depend on your printer’s capabilities.')
        links = ('Forum yazılarında her görselin **PNG bağlantısını** kullanabilirsiniz. Bu `master` bağlantıları, aynı dosya adı korunarak güncellenir. `v4.0.0` gibi bir etikete verilen bağlantı ise o sürümün görselini göstermeye devam eder.' if turkish else
                 'Use each image’s **PNG link** in forum posts. These `master` links update when the same filename is replaced. Links pinned to a tag such as `v4.0.0` continue showing that release’s image.')
        guide = ('Kullanım adımları: [Günlük kullanım](user-guide_TR.md) · [MMU](mmu-guide_TR.md). Görüntü alma ve yeniden üretme: [Emülatör rehberi](ui-emulator_TR.md).' if turkish else
                 'Usage steps: [Daily use](user-guide.md) · [MMU](mmu-guide.md). Capture and regeneration: [Emulator guide](ui-emulator.md).')
        lines = [f'# {title}', '', '[English](screenshots.md) · [Türkçe](screenshots_TR.md)', '', intro, '', links, '', guide, '']
        for group, english, translated in groups:
            lines += [f'## {translated if turkish else english}', '',
                      '| Ekran | Önizleme | Dış bağlantı |' if turkish else '| Screen | Preview | External link |', '|---|---|---|']
            for name, category, en, tr, _ in SCENES:
                if category == group:
                    url = f'https://raw.githubusercontent.com/sezgynus/Petrel/master/docs/assets/screens/{name}.png'
                    caption = tr if turkish else en
                    lines.append(f'| {caption} | <img src="assets/screens/{name}.png" width="136" alt="{caption}"> | [PNG]({url}) |')
            lines.append('')
        path = ROOT / 'docs' / ('screenshots_TR.md' if turkish else 'screenshots.md')
        path.write_text('\n'.join(lines), encoding='utf-8', newline='\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory', type=Path, default=ROOT/'docs/assets/screens')
    args=parser.parse_args()
    names = [item[0] for item in SCENES]
    if len(names) != len(set(names)):
        raise SystemExit('Duplicate screenshot filenames in scene list')
    logging.getLogger().setLevel(logging.ERROR)
    args.output_directory.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='petrel-docs-') as temporary, \
            patch.object(time, 'strftime', return_value='12:34'), patch('mmu_filament_view.time.monotonic', return_value=3.6):
        output=Path(temporary)
        errors=[]
        for name,group,en,tr,draw in SCENES:
            try:
                image=draw()
                if image.size!=(272,480) or image.mode!='RGB': raise ValueError('Invalid panel image')
                image.save(output/(name+'.png'), optimize=True)
            except Exception as error:
                errors.append((name,error))
                import traceback
                traceback.print_exc()
        if errors:
            raise SystemExit('No images published; failed scenes: '+', '.join(n for n,_ in errors))
        for image in output.glob('*.png'):
            shutil.copyfile(image,args.output_directory/image.name)
    if args.output_directory.resolve() == (ROOT / 'docs/assets/screens').resolve():
        write_galleries()
    print('Rendered %d real-UI emulator screenshots.'%len(SCENES))


if __name__=='__main__': main()
