"""
================================================================================
File: exporters/export_dialog.py
Purpose: Export file dialog with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

import os
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.notifications import show_error, show_success
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class ExportDialog(Popup):

    def __init__(self, diagram_widget, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.92)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.diagram_widget = diagram_widget

        project_dir = json_manager.get_current_directory()
        if project_dir and os.path.exists(project_dir):
            self.current_path = project_dir
        else:
            self.current_path = '/storage/emulated/0/Documents'
            if not os.path.exists(self.current_path):
                self.current_path = os.path.expanduser('~/Documents')
            if not os.path.exists(self.current_path):
                self.current_path = os.getcwd()

        project_name = json_manager.get_current_project_name()
        self.default_basename = (project_name.replace('.json', '')
                                  if project_name else 'motor_winding')

        self.all_formats = ['svg', 'pdf', 'eps', 'dxf', 'png', 'jpg']
        self.format = 'svg'
        self.dpi = 300
        self.quality = 95

        self.build_ui()
        self.refresh_file_list()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(8))

        header = BoxLayout(size_hint_y=None, height=dp(50),
                            spacing=dp(6),
                            padding=[dp(10), dp(8), dp(10), dp(8)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=self.dismiss,
            size=(dp(36), dp(34)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(
            text='EXPORT DIAGRAM' + get_version_suffix(),
            font_size='16sp', bold=True,
            color=Theme.HEADER_TEXT, halign='center', valign='middle',
            size_hint_x=1
        ))
        header.add_widget(Label(size_hint_x=None, width=dp(36)))
        main.add_widget(header)

        addr = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
        addr.add_widget(Label(text='Path:', size_hint_x=0.1, font_size='13sp'))
        self.address_input = TextInput(text=self.current_path, multiline=False,
                                        font_size='13sp', size_hint_x=0.62,
                                        background_color=Theme.INPUT_BG,
                                        foreground_color=Theme.INPUT_TEXT)
        addr.add_widget(self.address_input)
        addr.add_widget(make_icon_button(
            text='Go', icon_name='go',
            on_press=self.go_to_path,
            size=(dp(40), dp(38)),
        ))
        addr.add_widget(make_icon_button(
            text='Back', icon_name='back',
            on_press=self.go_back,
            size=(dp(46), dp(38)),
        ))
        main.add_widget(addr)

        scroll = ScrollView(size_hint_y=1)
        self.file_list = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        scroll.add_widget(self.file_list)
        main.add_widget(scroll)

        nav = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        nav.add_widget(make_icon_text_button(
            text='New Folder', icon_name='new_folder',
            on_press=self.create_new_folder,
            height=dp(38), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(nav)

        bottom = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        bottom.add_widget(Label(text='Format:', size_hint_x=0.15, font_size='13sp'))
        self.format_spinner = Spinner(text=self.format, values=self.all_formats,
                                        size_hint_x=0.2, font_size='14sp')
        self.format_spinner.bind(text=self.on_format_change)
        bottom.add_widget(self.format_spinner)
        bottom.add_widget(Label(text='DPI: 300', size_hint_x=0.15, font_size='12sp'))
        bottom.add_widget(Label(size_hint_x=0.15))

        bottom.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(44), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        bottom.add_widget(make_icon_text_button(
            text='Save', icon_name='save',
            on_press=self.save_file,
            height=dp(44), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))

        main.add_widget(bottom)
        self.add_widget(main)

    def on_format_change(self, spinner, text):
        self.format = text

    def refresh_file_list(self):
        self.file_list.clear_widgets()
        try:
            items = os.listdir(self.current_path)
            dirs = sorted([d for d in items
                            if os.path.isdir(os.path.join(self.current_path, d))],
                          key=str.lower)
            files = sorted([f for f in items
                            if not os.path.isdir(os.path.join(self.current_path, f))],
                           key=str.lower)
            for d in dirs:
                btn = Button(text=d + '/', size_hint_y=None, height=dp(38),
                             background_color=[0.85, 0.85, 0.9, 1],
                             color=[0, 0, 0, 1], background_normal='',
                             font_size='14sp')
                btn.bind(on_press=lambda x, name=d: self.enter_folder(name))
                self.file_list.add_widget(btn)
            for f in files:
                btn = Button(text=f, size_hint_y=None, height=dp(38),
                             background_color=[1, 1, 1, 1],
                             color=[0, 0, 0, 1], background_normal='',
                             font_size='13sp')
                self.file_list.add_widget(btn)
        except Exception as e:
            self.file_list.add_widget(Label(text='Error: ' + str(e),
                                              color=Theme.ERROR_TEXT))

    def enter_folder(self, name):
        new = os.path.join(self.current_path, name)
        if os.path.isdir(new):
            self.current_path = new
            self.address_input.text = new
            self.refresh_file_list()

    def go_back(self, instance=None):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.address_input.text = parent
            self.refresh_file_list()

    def go_to_path(self, instance=None):
        path = self.address_input.text.strip()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.refresh_file_list()
        else:
            show_error('Path does not exist', 2)

    def create_new_folder(self, instance=None):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text='Folder name:', font_size='16sp'))
        name_input = TextInput(multiline=False, font_size='15sp')
        content.add_widget(name_input)
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        popup = Popup(title='New Folder', content=content, size_hint=(0.7, 0.35))

        btn_box.add_widget(make_icon_text_button(
            text='Create', icon_name='create',
            on_press=lambda x: do_create(),
            height=dp(42), icon_size=dp(20), font_size='14sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        btn_box.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: popup.dismiss(),
            height=dp(42), icon_size=dp(20), font_size='14sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        ))
        content.add_widget(btn_box)

        def do_create():
            name = name_input.text.strip()
            if name:
                try:
                    os.makedirs(os.path.join(self.current_path, name),
                                exist_ok=True)
                    self.refresh_file_list()
                    popup.dismiss()
                    show_success('Folder created: ' + name, 2)
                except Exception as e:
                    show_error('Failed: ' + str(e), 2)
            else:
                show_error('Enter folder name', 2)

        popup.open()

    def save_file(self, instance=None):
        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        content.add_widget(Label(text='File name:', font_size='16sp',
                                  size_hint_y=None, height=dp(30)))
        default = self.default_basename + '.' + self.format
        name_input = TextInput(text=default, multiline=False, font_size='15sp',
                                size_hint_y=None, height=dp(42))
        content.add_widget(name_input)
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        popup = Popup(title='Save As', content=content, size_hint=(0.75, 0.35))

        btn_box.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: popup.dismiss(),
            height=dp(42), icon_size=dp(20), font_size='14sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        ))
        btn_box.add_widget(make_icon_text_button(
            text='Save', icon_name='save',
            on_press=lambda x: do_save(),
            height=dp(42), icon_size=dp(20), font_size='14sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        content.add_widget(btn_box)

        def do_save():
            filename = name_input.text.strip() or default
            if not filename.endswith('.' + self.format):
                filename += '.' + self.format
            full = os.path.join(self.current_path, filename)
            popup.dismiss()
            try:
                q = int(self.quality) if self.format in ('jpg', 'jpeg') else 95
                ok = self.diagram_widget.save_diagram(full, self.format,
                                                        dpi=self.dpi, quality=q)
                if ok:
                    show_success('Saved: ' + os.path.basename(full), 2)
                    self.dismiss()
                else:
                    show_error('Failed to save file', 3)
            except Exception as e:
                show_error('Failed: ' + str(e), 3)

        popup.open()