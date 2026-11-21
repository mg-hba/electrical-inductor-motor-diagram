"""
================================================================================
File: dialogs/app_info.py
Purpose: Lightweight App Info dialog with icon+text category buttons.
Version: 0.1.2.0
================================================================================
"""

import os
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button, get_icon_path
from version import (
    get_version_suffix, __version__, __release_date__,
    __developer_senior__, __developer_junior__,
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
ZARIN_LOGO = os.path.join(ASSETS_DIR, 'zarin.png')


class AppInfoPopup(Popup):

    def __init__(self, docs_manager, on_open_docs=None,
                 on_open_changelog=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.94, 0.88)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = True

        self.docs_manager = docs_manager
        self.on_open_docs = on_open_docs
        self.on_open_changelog = on_open_changelog

        self.build_ui()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            self._bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(self._bg, 'pos', i.pos),
                  size=lambda i, v: setattr(self._bg, 'size', i.size))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6),
                            padding=[dp(8), dp(6), dp(8), dp(6)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))

        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(30), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='APP INFO' + get_version_suffix(),
                                  font_size='14sp', bold=True,
                                  color=Theme.HEADER_TEXT, size_hint_x=1,
                                  halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(30)))
        main.add_widget(header)

        # Banner
        banner = BoxLayout(orientation='horizontal',
                            size_hint_y=None, height=dp(110),
                            spacing=dp(10),
                            padding=[dp(10), dp(8), dp(10), dp(8)])
        with banner.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            bbg = Rectangle(pos=banner.pos, size=banner.size)
        banner.bind(pos=lambda i, v: setattr(bbg, 'pos', i.pos),
                    size=lambda i, v: setattr(bbg, 'size', i.size))

        if os.path.exists(ZARIN_LOGO):
            banner.add_widget(Image(source=ZARIN_LOGO,
                                      size_hint=(None, 1),
                                      width=dp(90),
                                      allow_stretch=True,
                                      keep_ratio=True))

        info_box = BoxLayout(orientation='vertical', spacing=dp(2),
                              size_hint_x=1)
        info_box.add_widget(Label(text='ZARIN TILE FACTORY',
                                    font_size='14sp', bold=True,
                                    color=[0.15, 0.35, 0.6, 1],
                                    halign='left', valign='middle',
                                    size_hint_y=None, height=dp(22)))
        info_box.add_widget(Label(text='Motor Winding Diagram',
                                    font_size='13sp', bold=True,
                                    color=[0, 0, 0, 1],
                                    halign='left', valign='middle',
                                    size_hint_y=None, height=dp(20)))
        info_box.add_widget(Label(text='Version ' + __version__ +
                                    ' - ' + __release_date__,
                                    font_size='11sp',
                                    color=[0.4, 0.4, 0.4, 1],
                                    halign='left', valign='middle',
                                    size_hint_y=None, height=dp(18)))
        info_box.add_widget(Label(
            text='Senior: ' + __developer_senior__,
            font_size='11sp', color=[0.2, 0.2, 0.2, 1],
            halign='left', valign='middle',
            size_hint_y=None, height=dp(16)))
        info_box.add_widget(Label(
            text='Junior: ' + __developer_junior__,
            font_size='11sp', color=[0.2, 0.2, 0.2, 1],
            halign='left', valign='middle',
            size_hint_y=None, height=dp(16)))
        banner.add_widget(info_box)
        main.add_widget(banner)

        # Category buttons (icon + text)
        categories = self.docs_manager.get_categories()
        for cat in categories:
            cid = cat.get('id', '')
            ctitle = cat.get('title', '')
            ctype = cat.get('type', 'single')
            cicon = cat.get('icon', 'info')

            btn = make_icon_text_button(
                text=ctitle, icon_name=cicon,
                on_press=lambda x, c=cid, t=ctype:
                    self._open_category(c, t),
                height=dp(46),
                icon_size=dp(28), font_size='14sp',
                bg_color=[0.9, 0.93, 0.97, 1],
                fg_color=[0.1, 0.2, 0.4, 1],
            )
            main.add_widget(btn)

        # Bottom close
        bottom = BoxLayout(size_hint_y=None, height=dp(52),
                            padding=[dp(10), dp(6), dp(10), dp(6)])
        close_btn = make_icon_text_button(
            text='Close', icon_name='close',
            on_press=lambda x: self.dismiss(),
            height=dp(40), icon_size=dp(22), font_size='14sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        bottom.add_widget(close_btn)
        main.add_widget(bottom)

        self.add_widget(main)

    def _open_category(self, cat_id, cat_type):
        if cat_type == 'tree' and self.on_open_changelog:
            self.on_open_changelog()
            return
        if self.on_open_docs:
            self.on_open_docs(cat_id)


def show_app_info(docs_manager, on_open_docs=None, on_open_changelog=None):
    AppInfoPopup(docs_manager,
                  on_open_docs=on_open_docs,
                  on_open_changelog=on_open_changelog).open()