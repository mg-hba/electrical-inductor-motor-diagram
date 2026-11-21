"""
================================================================================
File: dialogs/coming_soon_dialog.py
Purpose: "Coming Soon" popup with icon.
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
from ui.icon_button import make_icon_text_button, get_icon_path
from version import get_version_suffix


class ComingSoonDialog(Popup):

    def __init__(self, feature_name="Feature", description="", **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.8, None)
        self.height = dp(250)
        self.background_color = [0, 0, 0, 0.4]
        self.auto_dismiss = True

        main = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(14))
        with main.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        # Header with icon
        header = BoxLayout(size_hint_y=None, height=dp(42),
                            spacing=dp(8),
                            padding=[dp(10), dp(4), dp(10), dp(4)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        icon_path = get_icon_path('info')
        if icon_path:
            header.add_widget(Image(source=icon_path,
                                     size_hint=(None, 1),
                                     width=dp(26),
                                     allow_stretch=True,
                                     keep_ratio=True))
        header.add_widget(Label(text='COMING SOON' + get_version_suffix(),
                                 font_size='16sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1,
                                 halign='center', valign='middle'))
        main.add_widget(header)

        main.add_widget(Label(
            text=feature_name, font_size='15sp', bold=True,
            color=[0.1, 0.3, 0.55, 1],
            size_hint_y=None, height=dp(30),
            halign='center', valign='middle'
        ))

        if description:
            main.add_widget(Label(
                text=description, font_size='12sp',
                color=[0.3, 0.3, 0.3, 1],
                halign='center', valign='middle'
            ))

        main.add_widget(make_icon_text_button(
            text='OK', icon_name='ok',
            on_press=lambda x: self.dismiss(),
            height=dp(44), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))

        self.add_widget(main)


def show_coming_soon(feature_name, description=""):
    ComingSoonDialog(feature_name, description).open()