"""
================================================================================
File: dialogs/motor_info.py
Purpose: Motor info popup with icon.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button, get_icon_path
from version import get_version_suffix


class MotorInfoPopup(Popup):

    def __init__(self, all_slots, coil_span, poles, speed, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.8, 0.5)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        # Header with icon
        header = BoxLayout(size_hint_y=None, height=dp(50),
                            spacing=dp(8),
                            padding=[dp(15), dp(8), dp(15), dp(8)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            Rectangle(pos=header.pos, size=header.size)

        icon_path = get_icon_path('motor_info')
        if icon_path:
            header.add_widget(Image(source=icon_path,
                                     size_hint=(None, 1),
                                     width=dp(30),
                                     allow_stretch=True,
                                     keep_ratio=True))

        header.add_widget(Label(
            text='MOTOR INFORMATION' + get_version_suffix(),
            font_size='16sp', bold=True,
            color=Theme.HEADER_TEXT, halign='center', valign='middle'
        ))
        main.add_widget(header)

        info_box = BoxLayout(orientation='vertical', spacing=dp(8),
                              padding=[dp(20), dp(20), dp(20), dp(20)])
        for line in [
            'Total Slots: %s' % all_slots,
            'Coil Span: %s' % coil_span,
            'Poles: %s' % poles,
            'Speed: %s RPM' % speed,
        ]:
            info_box.add_widget(Label(text=line, font_size='16sp',
                                        color=Theme.TEXT_PRIMARY,
                                        halign='left', valign='middle'))
        main.add_widget(info_box)

        btn_box = BoxLayout(size_hint_y=None, height=dp(56),
                             padding=[dp(15), dp(8), dp(15), dp(8)])
        close_btn = make_icon_text_button(
            text='Close', icon_name='close',
            on_press=lambda x: self.dismiss(),
            height=dp(42), icon_size=dp(22), font_size='15sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        btn_box.add_widget(close_btn)
        main.add_widget(btn_box)

        self.add_widget(main)


def show_motor_info(all_slots, coil_span, poles, speed):
    MotorInfoPopup(all_slots, coil_span, poles, speed).open()