"""
================================================================================
File: dialogs/changelog_viewer.py
Purpose: Tree view of version history with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class ChangelogViewer(Popup):

    def __init__(self, docs_manager, on_open_version=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.94, 0.85)
        self.background_color = [0, 0, 0, 0.3]
        self.auto_dismiss = True

        self.docs_manager = docs_manager
        self.on_open_version = on_open_version

        self.build_ui()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            self._bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(self._bg, 'pos', i.pos),
                  size=lambda i, v: setattr(self._bg, 'size', i.size))

        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(4),
                            padding=[dp(10), dp(6), dp(10), dp(6)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))

        header.add_widget(make_icon_button(
            text='<', icon_name='back',
            on_press=lambda x: self.dismiss(),
            size=(dp(32), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='Version History' + get_version_suffix(),
                                  font_size='13sp', bold=True,
                                  color=Theme.HEADER_TEXT, size_hint_x=1,
                                  halign='center', valign='middle'))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(30), dp(30)),
            bg_color=[0.8, 0.2, 0.2, 1],
        ))
        main.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(4),
                             size_hint_y=None,
                             padding=[dp(8), dp(8), dp(8), dp(8)])
        content.bind(minimum_height=content.setter('height'))

        versions = self.docs_manager.get_versions()
        for v in versions:
            version_id = v.get('id', '')
            title = v.get('title', '')
            date = v.get('date', '')
            is_current = v.get('current', False)

            text = version_id + ' - ' + title
            if is_current:
                text += '  (current)'
            text += '  ' + date

            btn = make_icon_text_button(
                text=text, icon_name='version_history',
                on_press=lambda x, vid=version_id,
                          fpath=v.get('file', ''): self._open_version(vid, fpath),
                height=dp(40), icon_size=dp(22), font_size='12sp',
                bg_color=([0.2, 0.7, 0.3, 1] if is_current
                            else [0.95, 0.95, 0.95, 1]),
                fg_color=([1, 1, 1, 1] if is_current
                            else [0, 0, 0, 1]),
            )
            content.add_widget(btn)

        scroll.add_widget(content)
        main.add_widget(scroll)

        self.add_widget(main)

    def _open_version(self, version_id, filepath):
        if self.on_open_version:
            self.on_open_version(version_id, filepath)


def show_changelog_viewer(docs_manager, on_open_version=None):
    ChangelogViewer(docs_manager, on_open_version=on_open_version).open()