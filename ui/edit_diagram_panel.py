"""
================================================================================
File: ui/edit_diagram_panel.py
Purpose: Floating panel for Edit Diagram mode (Apply / Reset / Cancel).
Version: 0.1.3
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class EditDiagramPanel(BoxLayout):

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, on_apply=None, on_reset=None, on_cancel=None, **kwargs):
        super().__init__(orientation='vertical',
                         size_hint=(None, None),
                         size=(dp(320), dp(100)),
                         **kwargs)
        self.pos = (dp(8), Window.height - dp(180))

        self.on_apply = on_apply
        self.on_reset = on_reset
        self.on_cancel = on_cancel

        self._drag_offset = None

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        header = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(4),
                            padding=[dp(6), dp(2), dp(6), dp(2)])
        with header.canvas.before:
            Color(0.15, 0.35, 0.6, 1)
            self._header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_header_bg,
                     size=self._update_header_bg)
        header.add_widget(Label(text='EDIT DIAGRAM' + get_version_suffix(),
                                 font_size='11sp', bold=True,
                                 color=[1, 1, 1, 1], size_hint_x=1,
                                 halign='center', valign='middle'))
        close_button = make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self._do_cancel(),
            size=(dp(26), dp(22)),
            bg_color=[0.8, 0.2, 0.2, 1],
        )
        header.add_widget(close_button)
        self.add_widget(header)

        info_label = Label(
            text='Drag diamonds to shift diagrams',
            font_size='11sp', color=Theme.TEXT_SECONDARY,
            size_hint_y=None, height=dp(22),
            halign='center', valign='middle'
        )
        self.add_widget(info_label)

        buttons_row = BoxLayout(size_hint_y=None, height=dp(36),
                                 spacing=dp(4),
                                 padding=[dp(6), dp(2), dp(6), dp(2)])
        buttons_row.add_widget(make_icon_text_button(
            text='Apply', icon_name='apply',
            on_press=lambda x: self._do_apply(),
            height=dp(32), icon_size=dp(18), font_size='12sp',
            bg_color=Theme.BUTTON_SUCCESS_BG,
            fg_color=[1, 1, 1, 1],
        ))
        buttons_row.add_widget(make_icon_text_button(
            text='Reset', icon_name='conn_reset',
            on_press=lambda x: self._do_reset(),
            height=dp(32), icon_size=dp(18), font_size='12sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        ))
        buttons_row.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self._do_cancel(),
            height=dp(32), icon_size=dp(18), font_size='12sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        self.add_widget(buttons_row)
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########_update_bg###############
    ###################################
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    ###################################
    ##########end of _update_bg#######
    ###################################

    ###################################
    ##########_update_header_bg########
    ###################################
    def _update_header_bg(self, *args):
        header = self.children[-1] if self.children else None
        if header is not None:
            self._header_bg.pos = header.pos
            self._header_bg.size = header.size
    ###################################
    ##########end of _update_header_bg
    ###################################

    ###################################
    ##########_do_apply################
    ###################################
    def _do_apply(self):
        if self.on_apply:
            self.on_apply()
    ###################################
    ##########end of _do_apply########
    ###################################

    ###################################
    ##########_do_reset################
    ###################################
    def _do_reset(self):
        if self.on_reset:
            self.on_reset()
    ###################################
    ##########end of _do_reset########
    ###################################

    ###################################
    ##########_do_cancel###############
    ###################################
    def _do_cancel(self):
        if self.on_cancel:
            self.on_cancel()
    ###################################
    ##########end of _do_cancel#######
    ###################################

    ###################################
    ##########on_touch_down############
    ###################################
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        header_bottom = self.top - dp(28)
        if touch.y >= header_bottom:
            self._drag_offset = (touch.x - self.x, touch.y - self.y)
            return True
        return super().on_touch_down(touch)
    ###################################
    ##########end of on_touch_down####
    ###################################

    ###################################
    ##########on_touch_move############
    ###################################
    def on_touch_move(self, touch):
        if self._drag_offset:
            new_x = touch.x - self._drag_offset[0]
            new_y = touch.y - self._drag_offset[1]
            new_x = max(dp(2), min(new_x, Window.width - self.width - dp(2)))
            new_y = max(dp(2), min(new_y, Window.height - self.height - dp(2)))
            self.pos = (new_x, new_y)
            return True
        return super().on_touch_move(touch)
    ###################################
    ##########end of on_touch_move####
    ###################################

    ###################################
    ##########on_touch_up##############
    ###################################
    def on_touch_up(self, touch):
        if self._drag_offset:
            self._drag_offset = None
            return True
        return super().on_touch_up(touch)
    ###################################
    ##########end of on_touch_up######
    ###################################