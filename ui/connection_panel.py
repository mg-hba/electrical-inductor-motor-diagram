"""
================================================================================
File: ui/connection_panel.py
Purpose: Floating connection toolbar with R/U group support.
Version: 0.1.1.2
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

from ui.theme import Theme
from ui.icon_button import make_icon_button


class FloatingConnectionPanel(BoxLayout):

    def __init__(self,
                 on_pull=None, on_connect=None, on_delete=None,
                 on_phase_start=None, on_phase_end=None, on_clear=None,
                 on_crossing=None, on_apply=None, on_cancel=None,
                 on_pencil=None, on_select_box=None,
                 on_back=None, on_redo=None, on_reset=None,
                 **kwargs):
        super().__init__(orientation='vertical',
                         size_hint=(None, None), **kwargs)

        self._init_size_and_position()

        self.on_pull = on_pull
        self.on_connect = on_connect
        self.on_delete = on_delete
        self.on_phase_start = on_phase_start
        self.on_phase_end = on_phase_end
        self.on_clear = on_clear
        self.on_crossing = on_crossing
        self.on_apply = on_apply
        self.on_cancel = on_cancel
        self.on_pencil = on_pencil
        self.on_select_box = on_select_box
        self.on_back = on_back
        self.on_redo = on_redo
        self.on_reset = on_reset

        self._drag_offset = None
        self._resize_offset = None
        self._resize_mode = False

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rects, size=self._update_rects)
        Window.bind(on_resize=self._on_window_resize)

        # ===== Header =====
        self.header = BoxLayout(size_hint_y=None, height=dp(28),
                                 spacing=dp(4),
                                 padding=[dp(6), dp(2), dp(6), dp(2)])
        with self.header.canvas.before:
            Color(0.15, 0.35, 0.6, 1)
            self._header_bg = Rectangle(pos=self.header.pos,
                                          size=self.header.size)
        self.header.bind(pos=self._update_header, size=self._update_header)

        from version import get_version_suffix
        self.header.add_widget(Label(
            text='CONNECTION TOOLS' + get_version_suffix(),
            font_size='11sp', bold=True,
            color=[1, 1, 1, 1], size_hint_x=1,
            halign='center', valign='middle'
        ))
        close_btn = make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self._do_cancel(),
            size=(dp(26), dp(22)),
        )
        self.header.add_widget(close_btn)
        self.add_widget(self.header)

        # ===== Tools row =====
        tools_row = BoxLayout(size_hint_y=None, height=dp(34),
                               spacing=dp(3),
                               padding=[dp(5), dp(2), dp(5), dp(2)])
        self.btn_pull = self._make_tool('|', 'pull', on_pull, width=dp(38))
        self.pull_step_input = TextInput(
            text='1', multiline=False, input_filter='int',
            size_hint_x=None, width=dp(36),
            size_hint_y=None, height=dp(28),
            font_size='13sp', halign='center',
            background_color=[1, 1, 1, 1], foreground_color=[0, 0, 0, 1],
            padding=[dp(2), dp(6), dp(2), dp(6)]
        )
        self.pull_step_input.bind(text=self._on_pull_step_change)
        self.pull_step_input.bind(on_text_validate=self._on_pull_enter)
        self.btn_line = self._make_tool('_', 'connect', on_connect, width=dp(38))
        self.btn_delete = self._make_tool('X', 'delete', on_delete, width=dp(38))
        self.btn_crossing = self._make_tool('\u25a0', 'crossing',
                                              on_crossing, width=dp(38))
        self.btn_R = self._make_tool('R', 'phase_r',
                                       on_phase_start, width=dp(38))
        self.btn_U = self._make_tool('U', 'phase_u',
                                       on_phase_end, width=dp(38))
        self.btn_clear = self._make_tool('C', 'clear', on_clear, width=dp(38))
        tools_row.add_widget(self.btn_pull)
        tools_row.add_widget(self.pull_step_input)
        tools_row.add_widget(self.btn_line)
        tools_row.add_widget(self.btn_delete)
        tools_row.add_widget(self.btn_crossing)
        tools_row.add_widget(self.btn_R)
        tools_row.add_widget(self.btn_U)
        tools_row.add_widget(self.btn_clear)
        self.add_widget(tools_row)

        # ===== Modes + history =====
        modes_row = BoxLayout(size_hint_y=None, height=dp(30),
                               spacing=dp(3),
                               padding=[dp(5), dp(2), dp(5), dp(2)])
        self.btn_hand = self._make_tool('Hand', 'hand',
                                          on_select_box, width=dp(52))
        self.btn_pencil = self._make_tool('Pencil', 'pencil',
                                            on_pencil, width=dp(60))
        self.btn_back = self._make_tool('Back', 'back',
                                          on_back, width=dp(52))
        self.btn_back.background_color = [0.5, 0.5, 0.5, 1]
        self.btn_redo = self._make_tool('Redo', 'redo',
                                          on_redo, width=dp(52))
        self.btn_redo.background_color = [0.5, 0.5, 0.5, 1]
        self.btn_reset = self._make_tool('Reset', 'conn_reset',
                                           on_reset, width=dp(52))
        self.btn_reset.background_color = [0.75, 0.35, 0.35, 1]
        modes_row.add_widget(self.btn_hand)
        modes_row.add_widget(self.btn_pencil)
        modes_row.add_widget(Label(size_hint_x=1))
        modes_row.add_widget(self.btn_back)
        modes_row.add_widget(self.btn_redo)
        modes_row.add_widget(self.btn_reset)
        self.add_widget(modes_row)

        # ===== Selected label =====
        self.selected_label = Label(text='Selected:',
                                     font_size='10sp',
                                     color=Theme.TEXT_SECONDARY,
                                     halign='left', valign='middle',
                                     size_hint_y=None, height=dp(18))
        self.add_widget(self.selected_label)

        # ===== Apply / Cancel =====
        btn_row = BoxLayout(size_hint_y=None, height=dp(30),
                             spacing=dp(5),
                             padding=[dp(5), dp(2), dp(5), dp(2)])
        apply_btn = Button(text='Apply', font_size='12sp', bold=True,
                           background_color=[0.2, 0.7, 0.3, 1],
                           color=[1, 1, 1, 1], background_normal='')
        apply_btn.bind(on_press=lambda x: self._do_apply())
        cancel_btn = Button(text='Cancel', font_size='12sp', bold=True,
                            background_color=[0.7, 0.3, 0.3, 1],
                            color=[1, 1, 1, 1], background_normal='')
        cancel_btn.bind(on_press=lambda x: self._do_cancel())
        btn_row.add_widget(apply_btn)
        btn_row.add_widget(cancel_btn)
        self.add_widget(btn_row)

    # ============================================================
    # ================== INIT ===================================
    # ============================================================

    def _init_size_and_position(self):
        max_w = max(dp(280), Window.width - dp(16))
        max_h = max(dp(160), int(Window.height * 0.55))
        w = min(dp(500), max_w)
        h = min(dp(190), max_h)
        self.size = (w, h)
        self.pos = (dp(8), Window.height - h - dp(70))

    def _clamp_on_screen(self):
        w, h = self.size
        min_x, min_y = dp(2), dp(2)
        max_x = Window.width - w - dp(2)
        max_y = Window.height - h - dp(2)
        if max_x < min_x:
            max_x = min_x
        if max_y < min_y:
            max_y = min_y
        x = max(min_x, min(self.x, max_x))
        y = max(min_y, min(self.y, max_y))
        self.pos = (x, y)

    def _on_window_resize(self, *args):
        max_w = max(dp(280), Window.width - dp(16))
        max_h = max(dp(160), int(Window.height * 0.55))
        new_w = min(self.width, max_w)
        new_h = min(self.height, max_h)
        if new_w != self.width or new_h != self.height:
            self.size = (new_w, new_h)
        self._clamp_on_screen()

    # ============================================================
    # ================== PULL STEP ==============================
    # ============================================================

    def _on_pull_step_change(self, instance, value):
        cleaned = ''.join(c for c in value if c.isdigit())
        if cleaned:
            try:
                v = int(cleaned)
                if v < 1:
                    cleaned = '1'
                elif v > 5:
                    cleaned = '5'
            except Exception:
                cleaned = '1'
        else:
            cleaned = ''
        if cleaned != value:
            instance.text = cleaned

    def _on_pull_enter(self, instance):
        if self.on_pull:
            self.on_pull()
        Clock.schedule_once(lambda dt: setattr(instance, 'focus', True), 0.1)

    def get_pull_step(self):
        try:
            v = int(self.pull_step_input.text.strip())
            return max(1, min(5, v))
        except Exception:
            return 1

    # ============================================================
    # ================== HELPERS ================================
    # ============================================================

    def _make_tool(self, text, icon_name, callback, width=dp(38)):
        return make_icon_button(
            text=text,
            icon_name=icon_name,
            on_press=(lambda x: callback()) if callback else None,
            size=(width, dp(28)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )

    def _do_apply(self):
        if self.on_apply:
            self.on_apply()

    def _do_cancel(self):
        if self.on_cancel:
            self.on_cancel()

    # ============================================================
    # ================== STATE VISUAL ===========================
    # ============================================================

    def set_selected_text(self, names):
        if not names:
            self.selected_label.text = 'Selected:'
        else:
            text = 'Selected: ' + ', '.join(names)
            if len(text) > 60:
                text = text[:57] + '...'
            self.selected_label.text = text

    def update_history_buttons(self, can_undo, can_redo):
        self.btn_back.background_color = (
            Theme.BUTTON_PRIMARY_BG if can_undo else [0.5, 0.5, 0.5, 1]
        )
        self.btn_redo.background_color = (
            Theme.BUTTON_PRIMARY_BG if can_redo else [0.5, 0.5, 0.5, 1]
        )

    def highlight_delete_mode(self, active):
        self.btn_delete.background_color = (
            [0.9, 0.2, 0.2, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    def highlight_crossing_mode(self, active):
        self.btn_crossing.background_color = (
            [0.9, 0.5, 0.1, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    def highlight_pencil_mode(self, active):
        self.btn_pencil.background_color = (
            [0.9, 0.5, 0.1, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    def highlight_select_box_mode(self, active):
        self.btn_hand.background_color = (
            [0.9, 0.5, 0.1, 1] if active else Theme.BUTTON_PRIMARY_BG
        )
        self.btn_hand.text = 'Select' if active else 'Hand'

    def set_R_active(self, active):
        self.btn_R.background_color = (
            [1.0, 0.55, 0.0, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    def set_U_active(self, active):
        self.btn_U.background_color = (
            [0.6, 0.2, 0.8, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    def set_group_clear_active(self, active):
        if active:
            self.btn_delete.background_color = [0.95, 0.55, 0.0, 1]
        else:
            self.btn_delete.background_color = Theme.BUTTON_PRIMARY_BG

    # ============================================================
    # ================== DRAG / RESIZE ==========================
    # ============================================================

    def _update_rects(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_header(self, *args):
        self._header_bg.pos = self.header.pos
        self._header_bg.size = self.header.size

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        resize_x = self.right - dp(24)
        resize_y = self.y
        if touch.x >= resize_x and touch.y <= resize_y + dp(24):
            self._resize_mode = True
            self._resize_offset = (touch.x - self.right, touch.y - self.y)
            return True
        header_bottom = self.top - dp(28)
        if touch.y >= header_bottom:
            self._drag_offset = (touch.x - self.x, touch.y - self.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._resize_mode:
            dw = touch.x - self._resize_offset[0] - self.right
            dh = touch.y - self._resize_offset[1] - self.y
            new_w = max(dp(280), min(self.width + dw, Window.width - dp(8)))
            new_h = max(dp(140), min(self.height + dh, Window.height - dp(8)))
            self.size = (new_w, new_h)
            return True
        if self._drag_offset:
            new_x = touch.x - self._drag_offset[0]
            new_y = touch.y - self._drag_offset[1]
            new_x = max(dp(2), min(new_x, Window.width - self.width - dp(2)))
            new_y = max(dp(2), min(new_y, Window.height - self.height - dp(2)))
            self.pos = (new_x, new_y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._resize_mode or self._drag_offset:
            self._resize_mode = False
            self._drag_offset = None
            self._clamp_on_screen()
            return True
        return super().on_touch_up(touch)