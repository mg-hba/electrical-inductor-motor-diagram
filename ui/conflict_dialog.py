"""
================================================================================
File: ui/conflict_dialog.py
Purpose: 3-button dialog for line conflict resolution (icon+text).
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.icon_button import make_icon_text_button, get_icon_path

from utils.constants import (
    CONFLICT_TITLE, CONFLICT_MESSAGE,
    CONFLICT_BTN_CONNECT, CONFLICT_BTN_PASS_OVER, CONFLICT_BTN_STOP_BEFORE,
)


class ConflictDialog(Popup):

    def __init__(self, on_connect=None, on_pass_over=None,
                 on_stop_before=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (None, None)
        self.size = (dp(360), dp(280))
        self.background_color = [0, 0, 0, 0.4]
        self.auto_dismiss = True

        self._on_connect = on_connect
        self._on_pass_over = on_pass_over
        self._on_stop_before = on_stop_before

        main = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
        with main.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        # Title row with warning icon
        title_row = BoxLayout(orientation='horizontal', spacing=dp(8),
                               size_hint_y=None, height=dp(38))
        icon_path = get_icon_path('conflict_connect')
        if icon_path:
            title_row.add_widget(Image(source=icon_path,
                                        size_hint=(None, 1),
                                        width=dp(32),
                                        allow_stretch=True,
                                        keep_ratio=True))
        title_row.add_widget(Label(text=CONFLICT_TITLE, font_size='14sp',
                                     bold=True, color=[0, 0, 0, 1],
                                     halign='left', valign='middle'))
        main.add_widget(title_row)

        main.add_widget(Label(text=CONFLICT_MESSAGE, font_size='12sp',
                                color=[0.3, 0.3, 0.3, 1],
                                halign='center', valign='middle',
                                size_hint_y=None, height=dp(24)))

        btns = BoxLayout(orientation='vertical', spacing=dp(6))

        b1 = make_icon_text_button(
            text=CONFLICT_BTN_CONNECT, icon_name='conflict_connect',
            on_press=self._do_connect,
            height=dp(42), icon_size=dp(24), font_size='13sp',
            bg_color=[0.2, 0.7, 0.3, 1],
            fg_color=[1, 1, 1, 1],
        )
        b2 = make_icon_text_button(
            text=CONFLICT_BTN_PASS_OVER, icon_name='conflict_pass_over',
            on_press=self._do_pass_over,
            height=dp(42), icon_size=dp(24), font_size='13sp',
            bg_color=[0.2, 0.5, 0.85, 1],
            fg_color=[1, 1, 1, 1],
        )
        b3 = make_icon_text_button(
            text=CONFLICT_BTN_STOP_BEFORE, icon_name='conflict_stop_before',
            on_press=self._do_stop_before,
            height=dp(42), icon_size=dp(24), font_size='13sp',
            bg_color=[0.85, 0.5, 0.1, 1],
            fg_color=[1, 1, 1, 1],
        )

        btns.add_widget(b1)
        btns.add_widget(b2)
        btns.add_widget(b3)
        main.add_widget(btns)

        self.add_widget(main)

    def _do_connect(self, *args):
        self.dismiss()
        if self._on_connect:
            self._on_connect()

    def _do_pass_over(self, *args):
        self.dismiss()
        if self._on_pass_over:
            self._on_pass_over()

    def _do_stop_before(self, *args):
        self.dismiss()
        if self._on_stop_before:
            self._on_stop_before()