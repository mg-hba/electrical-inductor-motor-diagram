"""
================================================================================
File: dialogs/file_browser.py
Purpose: Reusable file browser widget.
Version: 0.1.1.1
================================================================================
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from ui.theme import Theme


class FileBrowser(BoxLayout):

    def __init__(self, on_select=None, on_enter_folder=None,
                 filter_extensions=None, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(4), **kwargs)
        self.on_select = on_select
        self.on_enter_folder = on_enter_folder
        self.filter_extensions = filter_extensions or []
        self.current_path = os.getcwd()

        addr = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(3))
        addr.add_widget(Label(text='Path:', size_hint_x=0.08,
                                font_size='12sp'))
        self.address_input = TextInput(
            text=self.current_path,
            multiline=False, font_size='12sp',
            size_hint_x=0.60,
            background_color=Theme.INPUT_BG,
            foreground_color=Theme.INPUT_TEXT
        )
        addr.add_widget(self.address_input)

        go_btn = Button(text='Go', size_hint_x=0.16, font_size='11sp',
                        background_color=Theme.BUTTON_PRIMARY_BG,
                        color=Theme.BUTTON_TEXT, background_normal='')
        go_btn.bind(on_press=self.go_to_path)
        addr.add_widget(go_btn)

        back_btn = Button(text='Back', size_hint_x=0.16, font_size='11sp',
                          background_color=Theme.BUTTON_PRIMARY_BG,
                          color=Theme.BUTTON_TEXT, background_normal='')
        back_btn.bind(on_press=self.go_back)
        addr.add_widget(back_btn)
        self.add_widget(addr)

        scroll = ScrollView()
        self.file_list = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        scroll.add_widget(self.file_list)
        self.add_widget(scroll)

    def set_path(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.address_input.text = path
            self.refresh()

    def refresh(self):
        self.file_list.clear_widgets()
        try:
            items = os.listdir(self.current_path)
            dirs = sorted(
                [d for d in items
                 if os.path.isdir(os.path.join(self.current_path, d))],
                key=str.lower
            )
            exts = set(e.lower() for e in self.filter_extensions)
            files = sorted(
                [f for f in items
                 if os.path.isfile(os.path.join(self.current_path, f)) and
                 (not exts or f.rsplit('.', 1)[-1].lower() in exts)],
                key=str.lower
            )

            for d in dirs:
                btn = Button(text=d + '/', size_hint_y=None, height=dp(34),
                             background_color=[0.85, 0.85, 0.9, 1],
                             color=[0, 0, 0, 1], background_normal='',
                             font_size='13sp', halign='left')
                btn.bind(on_press=lambda x, name=d: self._enter(name))
                self.file_list.add_widget(btn)

            for f in files:
                btn = Button(text=f, size_hint_y=None, height=dp(34),
                             background_color=[0.9, 0.95, 0.85, 1],
                             color=[0, 0.4, 0, 1], background_normal='',
                             font_size='12sp', halign='left')
                btn.bind(on_press=lambda x, name=f: self._select(name))
                self.file_list.add_widget(btn)

        except Exception as e:
            self.file_list.add_widget(Label(
                text='Error: ' + str(e),
                color=Theme.ERROR_TEXT,
                size_hint_y=None, height=dp(36)
            ))

    def _enter(self, name):
        new = os.path.join(self.current_path, name)
        if os.path.isdir(new):
            self.current_path = new
            self.address_input.text = new
            self.refresh()
            if self.on_enter_folder:
                self.on_enter_folder(new)

    def _select(self, name):
        if self.on_select:
            self.on_select(name, os.path.join(self.current_path, name))

    def go_back(self, instance):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.address_input.text = parent
            self.refresh()

    def go_to_path(self, instance):
        path = self.address_input.text.strip()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.refresh()