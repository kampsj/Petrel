"""Bed mesh screens, profile browsing and encoder navigation."""
import math
from t5uic1_driver import T5UIC1Display


# Mainsail's default Portland palette and unscaled heightmap range.
# https://github.com/mainsail-crew/mainsail/blob/develop/src/store/gui/heightmap/getters.ts
MESH_PALETTE = ('313695', '4575b4', '74add1', 'abd9e9', 'e0f3f8', 'ffffbf',
                'fee090', 'fdae61', 'f46d43', 'd73027', 'a50026')


def mesh_color(z):
    position = max(0.0, min(1.0, (z + .1) / .2)) * (len(MESH_PALETTE)-1)
    index = min(int(position), len(MESH_PALETTE)-2)
    fraction = position-index
    low, high = MESH_PALETTE[index:index+2]
    rgb = [math.floor(int(low[i:i+2], 16)*(1-fraction)
                      + int(high[i:i+2], 16)*fraction + .5) for i in (0, 2, 4)]
    return ((rgb[0] >> 3) << 11) | ((rgb[1] >> 2) << 5) | (rgb[2] >> 3)


def point_style(z, columns):
    value = max(-20, min(20, round(z * 100)))
    color = mesh_color(z)
    maximum = min(23, int(111 / (columns - 1)))
    minimum = min(5, maximum)
    radius = round(minimum + (value+20)/40 * (maximum-minimum))
    return color, radius


def point_label(z, columns):
    if abs(z) < .005:
        return '0.00' if columns < 9 else '0'
    if columns < 9:
        label = '{:+.2f}'.format(z)
        return label if len(label) <= 6 else '######'
    if abs(z) < 1:
        return ('-' if z < 0 else '') + '.{:02d}'.format(min(99, round(abs(z)*100)))
    label = '{:.1f}'.format(z)
    return label if len(label) <= 4 else '####'


class BedMeshMixin:
    def _mesh_menu_entries(self):
        entries = [('BACK', 'Back', self.ICON_Back)]
        if self.pd.capabilities.bed_mesh:
            if self.pd.capabilities.probe:
                entries.append(('CALIBRATE', 'Bed Mesh Calibrate', self.ICON_HotendTemp))
            entries.append(('VIEWER', 'Mesh Viewer', self.ICON_HotendTemp))
        return tuple(entries)

    def Draw_Bed_Mesh_Menu(self):
        self.Clear_Main_Window()
        self.Draw_Title('Bed Mesh')
        entries = self._mesh_menu_entries()
        choice = min(getattr(self, '_mesh_menu_selection', 0), len(entries)-1)
        self._mesh_menu_selection = choice
        for index, (_, label, icon) in enumerate(entries):
            self.Draw_Menu_Line(index, icon, label)
        self.Draw_Menu_Cursor(choice)
        self.lcd.update()

    def HMI_Bed_Mesh_Menu(self):
        event = self.get_encoder_state()
        if event == self.ENCODER_DIFF_NO:
            return
        entries = self._mesh_menu_entries()
        choice = min(getattr(self, '_mesh_menu_selection', 0), len(entries)-1)
        if event == self.ENCODER_DIFF_CW:
            self._mesh_menu_selection = min(len(entries)-1, choice+1)
        elif event == self.ENCODER_DIFF_CCW:
            self._mesh_menu_selection = max(0, choice-1)
        elif event == self.ENCODER_DIFF_ENTER:
            key = entries[choice][0]
            if key == 'BACK':
                self.Goto_MainMenu()
            elif key == 'CALIBRATE':
                self._start_bed_mesh(self.BedMeshMenu)
            elif key == 'VIEWER':
                self._mesh_profile_selection = 0
                self._open_mesh_profiles()
            return
        self.Draw_Bed_Mesh_Menu()

    def _return_to_mesh_menu(self):
        self.checkkey = self.BedMeshMenu
        self.Draw_Bed_Mesh_Menu()

    def _mesh_text(self, text, y, size=8, color=None):
        text = T5UIC1Display._panel_text(text)[:272 // size]
        self.lcd.draw_text(False, False, self.lcd.font6x12 if size == 6 else self.lcd.font8x16,
                             self.lcd.Color_White if color is None else color,
                             self.lcd.Color_Bg_Black, max(0, (272-len(text)*size)//2), y, text)

    def _mesh_button(self, label, x, selected=False):
        self.lcd.draw_rectangle(1, 0x03B5, x, 305, x+99, 343)
        self.lcd.draw_text(False, False, self.lcd.font8x16, self.lcd.Color_White,
                             0x03B5, x+(99-len(label)*8)//2, 316, label)
        if selected:
            self.lcd.draw_rectangle(0, self.lcd.Color_White, x-2, 303, x+101, 345)

    def _draw_mesh_grid(self, columns, rows, points):
        xs = [round(25 + x*222/(columns-1)) for x in range(columns)]
        ys = [round(277 - y*222/(rows-1)) for y in range(rows)]
        color = 0x03B5
        self.lcd.draw_rectangle(0, color, 25, 55, 247, 277)
        for x in xs[1:-1]: self.lcd.draw_line(color, x, 55, x, 277)
        for y in ys[1:-1]: self.lcd.draw_line(color, 25, y, 247, y)
        # Avoid overlaps in dense grids without changing any underlying values.
        stride = max(1, math.ceil((36 if columns < 9 else 24) / (222/(columns-1))))
        row_stride = max(1, math.ceil(12 / (222/(rows-1))))
        for (x, y), z in sorted(points.items()):
            color, radius = point_style(z, max(columns, rows))
            for dy in range(-radius, radius+1):
                dx = math.isqrt(radius*radius-dy*dy)
                self.lcd.draw_rectangle(1, color, xs[x]-dx, ys[y]+dy, xs[x]+dx, ys[y]+dy)
            if x % stride == 0 and y % row_stride == 0:
                label = point_label(z, columns)
                tx = max(0, min(272-len(label)*6, xs[x]-len(label)*3))
                self.lcd.draw_text(False, False, self.lcd.font6x12, self.lcd.Color_White,
                                     self.lcd.Color_Bg_Black, tx, ys[y]-6, label)

    def _draw_live_mesh_cell(self, columns, rows, index, z):
        x, y = index
        xs = [round(25 + i*222/(columns-1)) for i in range(columns)]
        ys = [round(277 - i*222/(rows-1)) for i in range(rows)]
        cx, cy = xs[x], ys[y]
        left = (xs[x-1]+cx)//2+1 if x else max(0, cx-23)
        right = (cx+xs[x+1])//2 if x+1 < columns else min(271, cx+23)
        top = (ys[y+1]+cy)//2+1 if y+1 < rows else max(31, cy-23)
        bottom = (cy+ys[y-1])//2 if y else min(300, cy+23)
        self.lcd.draw_rectangle(1, self.lcd.Color_Bg_Black, left, top, right, bottom)
        self.lcd.draw_line(0x03B5, cx, max(55, top), cx, min(277, bottom))
        self.lcd.draw_line(0x03B5, max(25, left), cy, min(247, right), cy)
        color, radius = point_style(z, max(columns, rows))
        for dy in range(max(-radius, top-cy), min(radius, bottom-cy)+1):
            dx = math.isqrt(radius*radius-dy*dy)
            self.lcd.draw_rectangle(1, color, max(left, cx-dx), cy+dy, min(right, cx+dx), cy+dy)
        label = point_label(z, columns)
        if len(label)*6 <= right-left+1 and bottom-top+1 >= 12:
            tx = max(left, min(right-len(label)*6+1, cx-len(label)*3))
            self.lcd.draw_text(False, False, self.lcd.font6x12, self.lcd.Color_White,
                               self.lcd.Color_Bg_Black, tx, cy-6, label)

    def Draw_Bed_Mesh(self):
        session = self.pd.bed_mesh
        self.Clear_Main_Window()
        title = ('Mesh: ' + session.mesh.name) if session.phase == 'viewing' and session.mesh else 'Mesh Viewer'
        if session.phase in ('measuring', 'stopping'): title = 'Bed Mesh Calibrate'
        self.Draw_Title(T5UIC1Display._panel_text(title)[:24])
        confirmation = getattr(self, '_mesh_confirmation', None)
        if confirmation:
            self._mesh_text('Stop probing?' if confirmation == 'cancel' else 'Save mesh profile?', 100)
            self._mesh_text('Klipper will shut down' if confirmation == 'cancel' else session.profile_name, 135)
            self._mesh_text('Restart with FIRMWARE_RESTART' if confirmation == 'cancel' else 'Klipper will restart', 165, size=6)
            choice = getattr(self, '_mesh_button_selection', 0)
            self._mesh_button('Back', 26, choice == 0)
            self._mesh_button('Stop' if confirmation == 'cancel' else 'Save', 146, choice == 1)
        elif session.mesh:
            mesh = session.mesh
            self._draw_mesh_grid(len(mesh.points[0]), len(mesh.points),
                                 {(x,y):z for y,row in enumerate(mesh.points) for x,z in enumerate(row)})
            low, high = mesh.extrema
            self._mesh_text('minZ: {:.2f}  maxZ: {:.2f}'.format(low, high), 347, size=6)
            if session.phase == 'complete':
                choice = getattr(self, '_mesh_button_selection', 0)
                self._mesh_button('Save', 26, choice == 0)
                self._mesh_button('Continue', 146, choice == 1)
            elif session.pending:
                self._mesh_text(session.message, 310, size=6)
            else:
                self._mesh_button('Continue', 86, True)
                if session.message: self._mesh_text(session.message, 285, size=6)
        elif session.phase == 'measuring':
            counts, _, _ = session.layout
            self._draw_mesh_grid(*counts, session.progress)
            self._mesh_button('Cancel', 86, True)
            self._mesh_text(session.message + ' (raw Z)', 347, size=6)
        else:
            self._mesh_text(session.message or 'Mesh unavailable', 150, size=6)
            if not session.pending: self._mesh_button('Continue', 86, True)
        self.lcd.update()

    def Draw_Mesh_Profiles(self):
        session = self.pd.bed_mesh
        self.Clear_Main_Window()
        self.Draw_Title('Mesh Viewer')
        if session.pending or session.phase not in ('listed', 'viewing'):
            self._mesh_text(session.message or 'Reading mesh profiles...', 150, size=6)
            if not session.pending: self._mesh_button('Continue', 86, True)
        else:
            entries = ('Back',) + tuple('Current Mesh' if n is None else n for n in session.entries())
            choice = getattr(self, '_mesh_profile_selection', 0)
            choice = min(choice, len(entries)-1)
            self._mesh_profile_selection = choice
            start = max(0, choice-self.MROWS)
            for index in range(start, min(len(entries), start+self.TROWS)):
                label = T5UIC1Display._panel_text(entries[index])[:25]
                self.Draw_Menu_Line(index-start, self.ICON_Back if index == 0 else self.ICON_HotendTemp, label)
            self.Draw_Menu_Cursor(choice-start)
        self.lcd.update()

    def _open_mesh_profiles(self, selected=None, view_after=False):
        try:
            self.pd.bed_mesh.refresh()
        except ValueError as error:
            self._show_message(str(error))
            return
        self._mesh_after_refresh = (view_after, selected)
        self._mesh_confirmation = None
        self.checkkey = self.MeshProfiles
        self.Draw_Mesh_Profiles()

    def _start_bed_mesh(self, origin):
        try:
            self.pd.bed_mesh.start()
        except ValueError as error:
            self.checkkey = origin
            self._show_message(str(error))
            return
        self._mesh_origin = origin
        self._mesh_confirmation = None
        self._mesh_button_selection = 0
        self.checkkey = self.BedMeshScreen
        self.Draw_Bed_Mesh()

    def HMI_Leveling(self):
        self._mesh_menu_selection = 0
        self._mesh_confirmation = None
        self._return_to_mesh_menu()

    def _return_from_mesh(self):
        self._mesh_confirmation = None
        if getattr(self, '_mesh_origin', self.BedMeshMenu) == self.BedMeshMenu:
            self._return_to_mesh_menu()
        elif getattr(self, '_mesh_origin', self.Prepare) == self.MainMenu:
            self.Goto_MainMenu()
        elif getattr(self, '_mesh_origin', self.Prepare) == self.Control:
            self.checkkey = self.Control
            self.Draw_Control_Menu()
        else:
            self.checkkey = self.Prepare
            self.Draw_Prepare_Menu()
        self.lcd.update()

    def HMI_Mesh_Profiles(self):
        event = self.get_encoder_state()
        session = self.pd.bed_mesh
        if event == self.ENCODER_DIFF_NO or session.pending:
            return
        if session.phase != 'listed':
            if event == self.ENCODER_DIFF_ENTER:
                self._return_to_mesh_menu()
            return
        choice = getattr(self, '_mesh_profile_selection', 0)
        if event == self.ENCODER_DIFF_CW:
            self._mesh_profile_selection = min(len(session.entries()), choice+1)
        elif event == self.ENCODER_DIFF_CCW:
            self._mesh_profile_selection = max(0, choice-1)
        elif event == self.ENCODER_DIFF_ENTER:
            if choice == 0:
                self._return_to_mesh_menu()
                return
            name = session.entries()[choice-1]
            self._open_mesh_profiles(name, view_after=True)
            return
        self.Draw_Mesh_Profiles()

    def HMI_Bed_Mesh(self):
        event = self.get_encoder_state()
        if event == self.ENCODER_DIFF_NO:
            return
        session = self.pd.bed_mesh
        confirmation = getattr(self, '_mesh_confirmation', None)
        two_buttons = bool(confirmation) or session.phase == 'complete'
        if two_buttons and event in (self.ENCODER_DIFF_CW, self.ENCODER_DIFF_CCW):
            previous = getattr(self, '_mesh_button_selection', 0)
            selected = 1 if event == self.ENCODER_DIFF_CW else 0
            if selected != previous:
                self._mesh_button_selection = selected
                old_x, new_x = (26, 146)[previous], (26, 146)[selected]
                self.lcd.draw_rectangle(0, self.lcd.Color_Bg_Black,
                                        old_x-2, 303, old_x+101, 345)
                self.lcd.draw_rectangle(0, self.lcd.Color_White,
                                        new_x-2, 303, new_x+101, 345)
                self.lcd.update()
            return
        if event != self.ENCODER_DIFF_ENTER:
            return
        choice = getattr(self, '_mesh_button_selection', 0)
        if confirmation:
            if choice == 0:
                self._mesh_confirmation = None
                self._mesh_button_selection = 0
            else:
                try:
                    session.cancel() if confirmation == 'cancel' else session.save()
                    self._mesh_confirmation = None
                except ValueError as error:
                    self._mesh_confirmation = None
                    self.Draw_Bed_Mesh()
                    self._show_message(str(error))
                    return
        elif session.phase == 'measuring':
            self._mesh_confirmation = 'cancel'
            self._mesh_button_selection = 0
        elif session.pending:
            return
        elif session.phase == 'complete' and choice == 0:
            self._mesh_confirmation = 'save'
            self._mesh_button_selection = 0
        elif session.phase == 'viewing':
            self._open_mesh_profiles()
            return
        else:
            self._return_from_mesh()
            return
        self.Draw_Bed_Mesh()

    def _poll_bed_mesh(self):
        session = self.pd.bed_mesh
        previous = session.revision
        previous_phase = session.phase
        previous_points = dict(session.progress)
        session.update()
        if self.checkkey not in (self.BedMeshScreen, self.MeshProfiles) or previous == session.revision:
            return
        if (self.checkkey == self.BedMeshScreen and previous_phase == session.phase == 'measuring'
                and not getattr(self, '_mesh_confirmation', None)):
            for index, z in session.progress.items():
                if previous_points.get(index) != z:
                    self._draw_live_mesh_cell(*session.layout[0], index, z)
            self.lcd.draw_rectangle(1, self.lcd.Color_Bg_Black, 0, 347, 271, 359)
            self._mesh_text(session.message + ' (raw Z)', 347, size=6)
            self.lcd.update()
            return
        if self.checkkey == self.MeshProfiles:
            if session.phase == 'listed':
                view_after, name = getattr(self, '_mesh_after_refresh', (False, None))
                self._mesh_after_refresh = (False, None)
                if view_after:
                    try:
                        session.view(name)
                        self._mesh_origin = self.BedMeshMenu
                        self.checkkey = self.BedMeshScreen
                        self.Draw_Bed_Mesh()
                        return
                    except ValueError as error:
                        session.message = str(error)
                        session.phase = 'error'
            self.Draw_Mesh_Profiles()
        else:
            if getattr(self, '_mesh_confirmation', None) == 'cancel' and session.phase != 'measuring':
                self._mesh_confirmation = None
                self._mesh_button_selection = 0
            if session.phase in ('interrupted', 'error'):
                self._mesh_confirmation = None
            self.Draw_Bed_Mesh()
