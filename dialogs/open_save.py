"""
================================================================================
File: dialogs/open_save.py
Purpose: Open/Save dialog with icon+text buttons.
         Save mode asks for overwrite confirmation when the file exists.
Version: 0.1.2
================================================================================
"""

import os
import json
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.notifications import show_error, show_success, show_confirm
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class OpenSaveDialog(Popup):

    def __init__(self, mode='open', project_data=None,
                 on_complete_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.92)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.mode = mode
        self.project_data = project_data
        self.on_complete_callback = on_complete_callback
        self.selected_file = None
        self.saved_file_path = None

        self.current_path = self._get_start_path()
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
                  os.path.expanduser('~/Documents'),
                  os.getcwd()]:
            if os.path.exists(p):
                return p
        return os.getcwd()

    def _default_filename(self):
        if not self.project_data:
            return 'motor_project.json'
        name = self.project_data.get(
            'project_name', 'project'
        ).strip().replace(' ', '_')
        power = self.project_data.get('nominal_power', '0').strip()
        try:
            speed = 6000 // int(self.project_data.get('poles', 0))
        except Exception:
            speed = 0
        return name + '_' + power + 'kw_' + str(speed) + 'rpm.json'

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=dp(4), padding=dp(6))

        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(4),
                            padding=[dp(10), dp(6), dp(10), dp(6)])
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
        mode_text = 'OPEN PROJECT' if self.mode == 'open' else 'SAVE PROJECT'
        header.add_widget(Label(text=mode_text + get_version_suffix(),
                                 font_size='14sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1, halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(30)))
        main.add_widget(header)

        # Address bar
        addr = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(3))
        addr.add_widget(Label(text='Path:', size_hint_x=0.08, font_size='12sp'))
        self.address_input = TextInput(text=self.current_path,
                                        multiline=False, font_size='12sp',
                                        size_hint_x=0.50,
                                        background_color=Theme.INPUT_BG,
                                        foreground_color=Theme.INPUT_TEXT)
        addr.add_widget(self.address_input)
        addr.add_widget(make_icon_button(
            text='Go', icon_name='go',
            on_press=self.go_to_path,
            size=(dp(38), dp(34)),
        ))
        addr.add_widget(make_icon_button(
            text='Home', icon_name='home',
            on_press=self.go_home,
            size=(dp(46), dp(34)),
        ))
        addr.add_widget(make_icon_button(
            text='Set as Default', icon_name='set_default',
            on_press=self.set_as_default,
            size=(dp(60), dp(34)),
        ))
        main.add_widget(addr)

        scroll = ScrollView(size_hint_y=1)
        self.file_list = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.file_list.bind(minimum_height=self.file_list.setter('height'))
        scroll.add_widget(self.file_list)
        main.add_widget(scroll)

        nav = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(4))
        nav.add_widget(make_icon_text_button(
            text='Back', icon_name='back',
            on_press=self.go_back,
            height=dp(36), icon_size=dp(20), font_size='12sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        nav.add_widget(make_icon_text_button(
            text='New Folder', icon_name='new_folder',
            on_press=self.create_new_folder,
            height=dp(36), icon_size=dp(20), font_size='12sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(nav)

        info_bar = BoxLayout(size_hint_y=None, height=dp(24))
        with info_bar.canvas.before:
            Color(*Theme.SECTION_BG)
            ibg = Rectangle(pos=info_bar.pos, size=info_bar.size)
        info_bar.bind(pos=lambda i, v: setattr(ibg, 'pos', i.pos),
                      size=lambda i, v: setattr(ibg, 'size', i.size))
        self.selected_label = Label(text='Selected: None', font_size='11sp',
                                     color=Theme.TEXT_SECONDARY,
                                     halign='center', valign='middle')
        info_bar.add_widget(self.selected_label)
        main.add_widget(info_bar)

        name_bar = BoxLayout(size_hint_y=None, height=dp(42),
                             spacing=dp(6),
                             padding=[dp(3), dp(3), dp(3), dp(3)])
        name_bar.add_widget(Label(text='File Name:', font_size='12sp',
                                    size_hint_x=0.22,
                                    color=Theme.TEXT_PRIMARY,
                                    halign='right', valign='middle'))
        if self.mode == 'open':
            self.file_name_input = TextInput(
                text='', multiline=False, font_size='13sp',
                size_hint_x=0.78, disabled=True,
                background_color=Theme.INPUT_DISABLED_BG,
                foreground_color=Theme.INPUT_TEXT
            )
        else:
            self.file_name_input = TextInput(
                text=self._default_filename(),
                multiline=False, font_size='13sp',
                size_hint_x=0.78,
                background_color=Theme.INPUT_BG,
                foreground_color=Theme.INPUT_TEXT
            )
        name_bar.add_widget(self.file_name_input)
        main.add_widget(name_bar)

        bottom = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        bottom.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(44), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        if self.mode == 'open':
            bottom.add_widget(make_icon_text_button(
                text='Open', icon_name='open_file',
                on_press=self.open_file,
                height=dp(44), icon_size=dp(22), font_size='13sp',
                bg_color=Theme.BUTTON_SUCCESS_BG,
                fg_color=[1, 1, 1, 1],
            ))
        else:
            bottom.add_widget(make_icon_text_button(
                text='Save', icon_name='save',
                on_press=self.save_file,
                height=dp(44), icon_size=dp(22), font_size='13sp',
                bg_color=Theme.BUTTON_PRIMARY_BG,
                fg_color=[1, 1, 1, 1],
            ))
        main.add_widget(bottom)

        self.add_widget(main)

    def refresh_file_list(self):
        self.file_list.clear_widgets()
        try:
            items = os.listdir(self.current_path)
            dirs = sorted(
                [d for d in items if os.path.isdir(
                    os.path.join(self.current_path, d))],
                key=str.lower
            )
            jsons = sorted(
                [f for f in items if f.endswith('.json') and
                 os.path.isfile(os.path.join(self.current_path, f))],
                key=str.lower
            )
            others = sorted(
                [f for f in items
                 if not os.path.isdir(os.path.join(self.current_path, f))
                 and not f.endswith('.json')],
                key=str.lower
            )

            for d in dirs:
                btn = Button(text=d + '/', size_hint_y=None, height=dp(36),
                             background_color=[0.85, 0.85, 0.9, 1],
                             color=[0, 0, 0, 1], background_normal='',
                             font_size='13sp', halign='left')
                btn.bind(on_press=lambda x, name=d: self.enter_folder(name))
                self.file_list.add_widget(btn)
            for f in jsons:
                btn = Button(text=f, size_hint_y=None, height=dp(36),
                             background_color=[0.9, 0.95, 0.85, 1],
                             color=[0, 0.4, 0, 1], background_normal='',
                             font_size='12sp', halign='left')
                btn.bind(on_press=lambda x, name=f: self.select_file(name))
                self.file_list.add_widget(btn)
            for f in others:
                btn = Button(text=f, size_hint_y=None, height=dp(32),
                             background_color=[0.95, 0.95, 0.95, 1],
                             color=[0.5, 0.5, 0.5, 1], background_normal='',
                             font_size='11sp', halign='left')
                self.file_list.add_widget(btn)
        except Exception as e:
            self.file_list.add_widget(Label(text='Error: ' + str(e),
                                              color=Theme.ERROR_TEXT,
                                              size_hint_y=None,
                                              height=dp(36)))

    def select_file(self, name):
        self.selected_file = name
        self.selected_label.text = 'Selected: ' + name
        if self.mode == 'open':
            self.file_name_input.text = name

    def enter_folder(self, name):
        new = os.path.join(self.current_path, name)
        if os.path.isdir(new):
            self.current_path = new
            self.address_input.text = new
            self.selected_file = None
            self.selected_label.text = 'Selected: None'
            self.refresh_file_list()

    def go_back(self, instance=None):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.address_input.text = parent
            self.selected_file = None
            self.selected_label.text = 'Selected: None'
            self.refresh_file_list()

    def go_home(self, instance=None):
        d = json_manager.get_default_directory()
        home = d if d and os.path.exists(d) else None
        if not home:
            for p in ['/storage/emulated/0/Documents',
                      os.path.expanduser('~/Documents'),
                      os.getcwd()]:
                if os.path.exists(p):
                    home = p
                    break
        if home:
            self.current_path = home
            self.address_input.text = home
            self.selected_file = None
            self.selected_label.text = 'Selected: None'
            self.refresh_file_list()

    def go_to_path(self, instance=None):
        path = self.address_input.text.strip()
        if os.path.exists(path) and os.path.isdir(path):
            self.current_path = path
            self.selected_file = None
            self.selected_label.text = 'Selected: None'
            self.refresh_file_list()
        else:
            show_error('Path does not exist', 2)

    def set_as_default(self, instance=None):
        path = self.address_input.text.strip()
        if os.path.exists(path) and os.path.isdir(path):
            json_manager.set_default_directory(path)
            show_success('Default: ' + os.path.basename(path), 2)
        else:
            show_error('Invalid path', 2)

    def create_new_folder(self, instance=None):
        content = BoxLayout(orientation='vertical', padding=dp(12),
                             spacing=dp(8))
        content.add_widget(Label(text='Folder name:', font_size='14sp'))
        name_input = TextInput(multiline=False, font_size='13sp',
                                size_hint_y=None, height=dp(36))
        content.add_widget(name_input)
        btn_box = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(40))
        popup = Popup(title='New Folder', content=content,
                       size_hint=(0.7, 0.35))

        create_btn = make_icon_text_button(
            text='Create', icon_name='create',
            on_press=lambda x: do_create(),
            height=dp(38), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        cancel_btn = make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: popup.dismiss(),
            height=dp(38), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        )
        btn_box.add_widget(create_btn)
        btn_box.add_widget(cancel_btn)
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

    def open_file(self, instance=None):
        if not self.selected_file:
            show_error('Please select a JSON file first', 2)
            return
        full_path = os.path.join(self.current_path, self.selected_file)
        data = json_manager.load_project_data(full_path)
        if not data:
            show_error('Failed to load file', 2)
            return
        parent_folder = os.path.dirname(full_path)
        paper_size = data.get('paper_size', 'A4')
        orientation = data.get('orientation', 'Portrait')
        if 'active_pattern' not in data:
            data['active_pattern'] = 'lap'
        json_manager.project_data = data
        json_manager.ensure_group_structure()
        json_manager.update_project_settings(
            file_path=full_path, file_name=self.selected_file,
            directory=parent_folder,
            paper_size=paper_size, orientation=orientation
        )
        self.saved_file_path = full_path
        json_manager.current_project_file = full_path
        if self.on_complete_callback:
            self.on_complete_callback('open', data, full_path)
        show_success('Loaded: ' + self.selected_file, 2)
        self.dismiss()

    def save_file(self, instance=None):
        if not self.project_data:
            show_error('No project data to save', 2)
            return
        filename = self.file_name_input.text.strip()
        if not filename:
            show_error('Please enter a file name', 2)
            return
        if not filename.endswith('.json'):
            filename += '.json'
        folder_name = filename[:-5]
        if not folder_name:
            show_error('Invalid file name', 2)
            return
        project_folder = os.path.join(self.current_path, folder_name)
        full_path = os.path.join(project_folder, filename)

        if os.path.exists(project_folder) or os.path.exists(full_path):
            def do_overwrite():
                self._write_project_file(project_folder, full_path, filename)
            def do_cancel():
                self.file_name_input.focus = True
            show_confirm(
                'Project "' + folder_name + '" already exists.\n'
                'Do you want to overwrite it?',
                on_confirm=do_overwrite,
                on_cancel=do_cancel,
                title='OVERWRITE'
            )
            return

        self._write_project_file(project_folder, full_path, filename)

    def _write_project_file(self, project_folder, full_path, filename):
        try:
            os.makedirs(project_folder, exist_ok=True)
        except Exception as e:
            show_error('Cannot create folder: ' + str(e), 2)
            return
        try:
            self.project_data['file_path'] = full_path
            self.project_data['directory'] = project_folder
            self.project_data['version'] = "0.1.2"

            for g in ['chained', 'concentric']:
                if g not in self.project_data:
                    self.project_data[g] = {
                        "winding_type": "two_layer",
                        "coil_pattern": ("lap" if g == "chained"
                                          else "concentric"),
                        "coil_span_chained": 11,
                        "coil_span_concentric": 9,
                        "coils_per_pole_values": [],
                        "wire_points": [],
                    }
                conn_key = ("chained_connection" if g == "chained"
                            else "concentric_connection")
                if conn_key not in self.project_data[g]:
                    self.project_data[g][conn_key] = {
                        "junction_points": [],
                        "line_segments": [],
                        "phase_endpoints": {}
                    }

            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, indent=4,
                           ensure_ascii=False)

            paper_size = self.project_data.get('paper_size', 'A4')
            orientation = self.project_data.get('orientation', 'Portrait')
            json_manager.update_project_settings(
                file_path=full_path, file_name=filename,
                directory=project_folder,
                paper_size=paper_size, orientation=orientation
            )

            self.saved_file_path = full_path
            json_manager.current_project_file = full_path

            if self.on_complete_callback:
                self.on_complete_callback('save', self.project_data,
                                           full_path)
            show_success('Saved: ' + filename, 2)
            self.dismiss()
        except Exception as e:
            show_error('Failed to save: ' + str(e), 2)


def show_open_save_dialog(mode='open', project_data=None,
                            on_complete_callback=None):
    dlg = OpenSaveDialog(mode=mode, project_data=project_data,
                          on_complete_callback=on_complete_callback)
    dlg.open()
    return dlg