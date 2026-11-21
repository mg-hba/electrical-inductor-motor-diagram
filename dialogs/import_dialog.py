"""
================================================================================
File: dialogs/import_dialog.py
Purpose: Import dialog with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

import os
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.notifications import show_info, show_error
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix
from importers.importer_registry import ImporterRegistry


class ImportDialog(Popup):

    def __init__(self, on_import=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.92)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.on_import = on_import
        self.current_path = self._get_start_path()
        self.selected_file = None
        self.build_ui()
        self.refresh_file_list()

    def _get_start_path(self):
        d = json_manager.get_default_directory()
        if d and os.path.exists(d):
            return d
        d = json_manager.get_current_directory()
        if d and os.path.exists(d):
            return d
        for p in ['/storage/emulated/0/Documents',
                  os.path.expanduser('~/Documents'), os.getcwd()]:
            if os.path.exists(p):
                return p
        return os.getcwd()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=dp(4), padding=dp(6))

        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6),
                            padding=[dp(10), dp(6), dp(10), dp(6)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=self.dismiss,
            size=(dp(32), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(
            text='IMPORT PROJECT' + get_version_suffix(),
            font_size='14sp', bold=True,
            color=Theme.HEADER_TEXT, halign='center', valign='middle',
            size_hint_x=1
        ))
        header.add_widget(Label(size_hint_x=None, width=dp(32)))
        main.add_widget(header)

        addr = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(3))
        addr.add_widget(Label(text='Path:', size_hint_x=0.08, font_size='12sp'))
        self.address_input = TextInput(text=self.current_path, multiline=False,
                                        font_size='12sp', size_hint_x=0.62,
                                        background_color=Theme.INPUT_BG,
                                        foreground_color=Theme.INPUT_TEXT)
        addr.add_widget(self.address_input)
        addr.add_widget(make_icon_button(
            text='Go', icon_name='go',
            on_press=self.go_to_path,
            size=(dp(40), dp(36)),
        ))
        addr.add_widget(make_icon_button(
            text='Back', icon_name='back',
            on_press=self.go_back,
            size=(dp(46), dp(36)),
        ))
        main.add_widget(addr)

        scroll = ScrollView(size_hint_y=1)
        self.file_list = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        scroll.add_widget(self.file_list)
        main.add_widget(scroll)

        info = BoxLayout(size_hint_y=None, height=dp(28))
        with info.canvas.before:
            Color(*Theme.SECTION_BG)
            ibg = Rectangle(pos=info.pos, size=info.size)
        info.bind(pos=lambda i, v: setattr(ibg, 'pos', i.pos),
                  size=lambda i, v: setattr(ibg, 'size', i.size))
        self.selected_label = Label(text='Select a file to import',
                                      font_size='11sp',
                                      color=Theme.TEXT_SECONDARY,
                                      halign='center', valign='middle')
        info.add_widget(self.selected_label)
        main.add_widget(info)

        supported = ', '.join(ImporterRegistry.all_extensions())
        main.add_widget(Label(text='Supported: ' + supported,
                                font_size='10sp',
                                color=Theme.TEXT_MUTED,
                                size_hint_y=None, height=dp(18)))

        bottom = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        bottom.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(44), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        bottom.add_widget(make_icon_text_button(
            text='Import', icon_name='import',
            on_press=self._do_import,
            height=dp(44), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_SUCCESS_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(bottom)

        self.add_widget(main)

    def refresh_file_list(self):
        self.file_list.clear_widgets()
        try:
            items = os.listdir(self.current_path)
            dirs = sorted([d for d in items
                            if os.path.isdir(os.path.join(self.current_path, d))],
                          key=str.lower)
            supported = set(ImporterRegistry.all_extensions())
            files = sorted([f for f in items
                            if os.path.isfile(os.path.join(self.current_path, f))
                            and f.rsplit('.', 1)[-1].lower() in supported],
                           key=str.lower)
            for d in dirs:
                btn = Button(text=d + '/', size_hint_y=None, height=dp(36),
                             background_color=[0.85, 0.85, 0.9, 1],
                             color=[0, 0, 0, 1], background_normal='',
                             font_size='13sp', halign='left')
                btn.bind(on_press=lambda x, name=d: self.enter_folder(name))
                self.file_list.add_widget(btn)
            for f in files:
                btn = Button(text=f, size_hint_y=None, height=dp(36),
                             background_color=[0.9, 0.95, 0.85, 1],
                             color=[0, 0.4, 0, 1], background_normal='',
                             font_size='12sp', halign='left')
                btn.bind(on_press=lambda x, name=f: self.select_file(name))
                self.file_list.add_widget(btn)
            if not dirs and not files:
                self.file_list.add_widget(Label(
                    text='No supported files in this folder',
                    color=Theme.TEXT_MUTED,
                    size_hint_y=None, height=dp(40)
                ))
        except Exception as e:
            self.file_list.add_widget(Label(text='Error: ' + str(e),
                                              color=Theme.ERROR_TEXT,
                                              size_hint_y=None, height=dp(36)))

    def select_file(self, name):
        self.selected_file = name
        self.selected_label.text = 'Selected: ' + name

    def enter_folder(self, name):
        new = os.path.join(self.current_path, name)
        if os.path.isdir(new):
            self.current_path = new
            self.address_input.text = new
            self.selected_file = None
            self.selected_label.text = 'Select a file to import'
            self.refresh_file_list()

    def go_back(self, instance=None):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.address_input.text = parent
            self.selected_file = None
            self.selected_label.text = 'Select a file to import'
            self.refresh_file_list()

    def go_to_path(self, instance=None):
        path = self.address_input.text.strip()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.selected_file = None
            self.selected_label.text = 'Select a file to import'
            self.refresh_file_list()
        else:
            show_error('Path does not exist', 2)

    def _do_import(self, instance=None):
        if not self.selected_file:
            show_error('Please select a file first', 2)
            return
        ext = self.selected_file.rsplit('.', 1)[-1].lower()
        importer = ImporterRegistry.get(ext)
        if importer is None:
            show_error('Unsupported format: .' + ext, 2)
            return
        full_path = os.path.join(self.current_path, self.selected_file)
        show_info(
            'Import for .' + ext + ' will be available in a later version.\n'
            'File: ' + self.selected_file,
            4, title='COMING SOON'
        )
        if self.on_import:
            self.on_import(full_path, importer)


def show_import_dialog(on_import=None):
    dlg = ImportDialog(on_import=on_import)
    dlg.open()
    return dlg