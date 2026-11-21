"""
================================================================================
File: ui/zoom_panel.py
Purpose: Collapsible floating zoom panel. Single row of icon buttons.
         Z_Box is a toggle.
Version: 0.1.1.2
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from ui.theme import Theme
from ui.icon_button import make_icon_button


class FloatingZoomPanel(BoxLayout):

    def __init__(self,
                 on_zoom_all=None,
                 on_zoom_in=None,
                 on_zoom_out=None,
                 on_zoom_back=None,
                 on_zoom_redo=None,
                 on_zoom_reset=None,
                 on_zoom_box=None,
                 **kwargs):
        super().__init__(orientation='vertical',
                         size_hint=(None, None),
                         size=(dp(60), dp(60)),
                         **kwargs)

        self.pos = (Window.width - dp(50), Window.height - dp(120))
        self._callbacks = {
            'all': on_zoom_all,
            'in': on_zoom_in,
            'out': on_zoom_out,
            'back': on_zoom_back,
            'redo': on_zoom_redo,
            'reset': on_zoom_reset,
            'box': on_zoom_box,
        }

        self._expanded = False
        self._drag_offset = None
        self._drag_start = None
        self._drag_moved = False
        self._buttons_built = False

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self._build_collapsed()

    # ============================================================
    # ================== COLLAPSED / EXPANDED ===================
    # ============================================================

    def _clear(self):
        self.clear_widgets()
        self._buttons_built = False


    def _build_collapsed(self):
        self._clear()
        self.size = (dp(50), dp(50))
        from ui.icon_button import make_icon_button
        btn = make_icon_button(
            text='Z', icon_name='zoom_in',
            on_press=lambda x: self._toggle(),
            size=(dp(50), dp(50)),
        )
        self.add_widget(btn)

              


    def _build_expanded(self):
        self._clear()
        self.size = (dp(370), dp(70))

        header = BoxLayout(size_hint_y=None, height=dp(24),
                           spacing=dp(2),
                           padding=[dp(4), dp(2), dp(4), dp(2)])
        with header.canvas.before:
            Color(0.15, 0.35, 0.6, 1)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))

        header.add_widget(Label(text='ZOOM', font_size='11sp', bold=True,
                                 color=[1, 1, 1, 1], size_hint_x=1,
                                 halign='center', valign='middle'))
        close_btn = make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self._collapse(),
            size=(dp(22), dp(20)),
        )
        header.add_widget(close_btn)
        self.add_widget(header)

        # All buttons in ONE row
        row = BoxLayout(size_hint_y=None, height=dp(42),
                        spacing=dp(2),
                        padding=[dp(3), dp(2), dp(3), dp(3)])

        self._all_btn = self._btn('Z_A', 'zoom_all',
                                    self._callbacks['all'])
        self._in_btn = self._btn('Z_I', 'zoom_in',
                                   self._callbacks['in'])
        self._out_btn = self._btn('Z_O', 'zoom_out',
                                    self._callbacks['out'])
        self._back_btn = self._btn('Z_B', 'zoom_back',
                                     self._callbacks['back'])
        self._redo_btn = self._btn('Z_R', 'zoom_redo',
                                     self._callbacks['redo'])
        self._reset_btn = self._btn('RST', 'zoom_reset',
                                      self._callbacks['reset'])
        self._box_btn = self._btn('Z_Box', 'zoom_box',
                                    self._callbacks['box'])

        for b in (self._all_btn, self._in_btn, self._out_btn,
                   self._back_btn, self._redo_btn,
                   self._reset_btn, self._box_btn):
            row.add_widget(b)

        self.add_widget(row)
        self._buttons_built = True

    def _btn(self, text, icon_name, callback):
        return make_icon_button(
            text=text,
            icon_name=icon_name,
            on_press=(lambda x: callback()) if callback else None,
            size=(dp(46), dp(28)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )

    def _toggle(self):
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        if self._expanded:
            return
        self._expanded = True
        old_right = self.right
        old_top = self.top
        self._build_expanded()
        self.pos = (old_right - self.width, old_top - self.height)

    def _collapse(self):
        if not self._expanded:
            return
        self._expanded = False
        old_right = self.right
        old_top = self.top
        self._build_collapsed()
        self.pos = (old_right - self.width, old_top - self.height)

    # ============================================================
    # ================== STATE VISUAL ===========================
    # ============================================================

    def highlight_box_mode(self, active):
        if not self._buttons_built:
            return
        self._box_btn.background_color = (
            [0.9, 0.5, 0.1, 1] if active else Theme.BUTTON_PRIMARY_BG
        )

    # ============================================================
    # ================== DRAG ===================================
    # ============================================================

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._drag_offset = (touch.x - self.x, touch.y - self.y)
        self._drag_start = touch.pos
        self._drag_moved = False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._drag_offset is None:
            return False
        dx = touch.x - self._drag_start[0]
        dy = touch.y - self._drag_start[1]
        if abs(dx) > dp(6) or abs(dy) > dp(6):
            self._drag_moved = True
        if self._drag_moved:
            self.pos = (touch.x - self._drag_offset[0],
                        touch.y - self._drag_offset[1])
            return True
        return False

    def on_touch_up(self, touch):
        if self._drag_offset is not None:
            self._drag_offset = None
            self._drag_start = None
            if self._drag_moved:
                self._drag_moved = False
                return True
        return super().on_touch_up(touch)