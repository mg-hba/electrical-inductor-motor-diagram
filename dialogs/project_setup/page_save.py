"""
================================================================================
File: dialogs/project_setup/page_save.py
Purpose: Wizard page 5 - SAVE / OPEN PROJECT with file browser
Version: 0.1.4.4
================================================================================
"""

import os

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp

from dialogs.project_setup.base_page import BasePage
from dialogs.project_setup.setup_sections import (
    make_section, make_label, make_input,
)
from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from managers.json_manager import json_manager
from utils.constants import (
    PROJECT_SETUP_INPUT_HEIGHT, PROJECT_SETUP_LABEL_HEIGHT,
)


class PageSave(BasePage):

    title = "SAVE PROJECT"

    def __init__(self, open_mode=False, **kwargs):
        self.open_mode = open_mode
        if open_mode:
            self.title = "OPEN PROJECT"
        self.current_browse_path = None
        super().__init__(**kwargs)
        self.load_data({})
        # Load initial browse path
        self._refresh_file_list()

    # ============================================================
    # ================== BUILD ==================================
    # ============================================================

    def build_content(self):
        self.content.add_widget(self._build_path_section())
        self.content.add_widget(self._build_file_browser_section())
        self.content.add_widget(self._build_info_label())

    def _build_path_section(self):
        section = make_section('PROJECT LOCATION')

        # Path row
        path_row = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_y=None,
                             height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                       PROJECT_SETUP_LABEL_HEIGHT + 2))
        path_row.add_widget(make_label('Path:'))

        path_input_row = BoxLayout(orientation='horizontal',
                                   spacing=dp(4),
                                   size_hint_y=None,
                                   height=dp(PROJECT_SETUP_INPUT_HEIGHT))

        self.path_input = make_input('')
        self.path_input.size_hint_x = 1
        self.path_input.bind(on_text_validate=self._on_path_enter)
        path_input_row.add_widget(self.path_input)

        go_btn = make_icon_button(
            text='Go', icon_name='go',
            on_press=lambda x: self._go_to_path(),
            size=(dp(34), dp(PROJECT_SETUP_INPUT_HEIGHT)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        path_input_row.add_widget(go_btn)

        home_btn = make_icon_button(
            text='Home', icon_name='home',
            on_press=lambda x: self._go_home(),
            size=(dp(34), dp(PROJECT_SETUP_INPUT_HEIGHT)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        path_input_row.add_widget(home_btn)

        default_btn = make_icon_button(
            text='Set Default', icon_name='set_default',
            on_press=lambda x: self._set_default(),
            size=(dp(34), dp(PROJECT_SETUP_INPUT_HEIGHT)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        path_input_row.add_widget(default_btn)

        path_row.add_widget(path_input_row)
        section.add_widget(path_row)

        # File name row
        name_row = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_y=None,
                             height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                       PROJECT_SETUP_LABEL_HEIGHT + 2))
        name_row.add_widget(make_label('File Name:'))
        self.filename_input = make_input('project.json')
        name_row.add_widget(self.filename_input)
        section.add_widget(name_row)

        section.height = dp(90)
        return section

    def _build_file_browser_section(self):
        section = make_section('BROWSE FILES')

        # Scrollable list
        scroll = ScrollView(size_hint_y=None, height=dp(180))

        self.file_list = GridLayout(cols=1, spacing=dp(1),
                                     size_hint_y=None,
                                     padding=[dp(2), dp(2), dp(2), dp(2)])
        self.file_list.bind(minimum_height=self.file_list.setter('height'))

        scroll.add_widget(self.file_list)
        section.add_widget(scroll)

        section.height = dp(220)
        return section

    def _build_info_label(self):
        info_text = (
            'Click a folder to navigate, or a .json file to open it.'
            if self.open_mode else
            'Navigate to the save location. The project will be saved '
            'as a folder containing the .json file.'
        )
        info = Label(
            text=info_text,
            font_size='11sp',
            color=Theme.TEXT_MUTED,
            size_hint_y=None,
            height=dp(28),
            halign='center', valign='middle',
        )
        info.bind(size=lambda i, v: setattr(i, 'text_size', (v[0], None)))
        return info

    # ============================================================
    # ================== FILE BROWSER ============================
    # ============================================================

    def _refresh_file_list(self):
        """Populate file_list with current_browse_path contents."""
        if self.file_list is None:
            return
        self.file_list.clear_widgets()

        path = self.path_input.text.strip() if hasattr(self, 'path_input') else ''
        if not path or not os.path.isdir(path):
            self.file_list.add_widget(Label(
                text='[ Invalid path ]',
                font_size='12sp',
                color=Theme.ERROR_TEXT,
                size_hint_y=None,
                height=dp(32),
                halign='center', valign='middle',
            ))
            return

        self.current_browse_path = path

        try:
            items = os.listdir(path)
        except Exception as e:
            self.file_list.add_widget(Label(
                text='Cannot read folder: ' + str(e),
                font_size='11sp',
                color=Theme.ERROR_TEXT,
                size_hint_y=None,
                height=dp(32),
            ))
            return

        # Sort: dirs first, then files
        dirs = sorted([d for d in items
                       if os.path.isdir(os.path.join(path, d))],
                      key=str.lower)
        files = sorted([f for f in items
                        if os.path.isfile(os.path.join(path, f))
                        and f.endswith('.json')],
                       key=str.lower)

        # Parent navigation
        parent = os.path.dirname(path)
        if parent and parent != path:
            parent_btn = Button(
                text='[..]  ' + os.path.basename(parent) + '/',
                size_hint_y=None, height=dp(30),
                background_color=[0.85, 0.85, 0.9, 1],
                color=[0.1, 0.1, 0.5, 1],
                background_normal='',
                font_size='12sp', halign='left',
            )
            parent_btn.bind(on_press=lambda x: self._navigate_to(parent))
            self.file_list.add_widget(parent_btn)

        # Directories
        for d in dirs:
            btn = Button(
                text='[+]  ' + d + '/',
                size_hint_y=None, height=dp(30),
                background_color=[0.90, 0.93, 0.97, 1],
                color=[0.1, 0.2, 0.5, 1],
                background_normal='',
                font_size='12sp', halign='left',
            )
            full = os.path.join(path, d)
            btn.bind(on_press=lambda x, p=full: self._navigate_to(p))
            self.file_list.add_widget(btn)

        # JSON files
        for f in files:
            btn = Button(
                text='[J]  ' + f,
                size_hint_y=None, height=dp(30),
                background_color=[0.92, 0.97, 0.88, 1],
                color=[0.0, 0.4, 0.0, 1],
                background_normal='',
                font_size='12sp', halign='left',
            )
            full = os.path.join(path, f)
            btn.bind(on_press=lambda x, fp=full, fn=f:
                     self._select_file(fp, fn))
            self.file_list.add_widget(btn)

        if not dirs and not files:
            self.file_list.add_widget(Label(
                text='[ Empty folder ]',
                font_size='11sp',
                color=Theme.TEXT_MUTED,
                size_hint_y=None,
                height=dp(30),
                halign='center', valign='middle',
            ))

    def _navigate_to(self, path):
        """Go to another folder and refresh."""
        if not os.path.isdir(path):
            return
        self.path_input.text = path
        self._refresh_file_list()

    def _select_file(self, full_path, filename):
        """Handle click on a .json file."""
        folder = os.path.dirname(full_path)
        self.path_input.text = folder
        self.filename_input.text = filename
        self._refresh_file_list()

    def _on_path_enter(self, instance):
        """Called when user presses Enter in path_input."""
        self._refresh_file_list()

    # ============================================================
    # ================== PATH ACTIONS ============================
    # ============================================================

    def _go_to_path(self):
        path = self.path_input.text.strip()
        if not path or not os.path.isdir(path):
            from ui.notifications import show_error
            show_error('Path does not exist', 2)
            return
        self._refresh_file_list()

    def _go_home(self):
        home = json_manager.get_default_directory()
        if not home or not os.path.isdir(home):
            for p in ['/storage/emulated/0/Documents',
                      os.path.expanduser('~/Documents'),
                      os.getcwd()]:
                if os.path.isdir(p):
                    home = p
                    break
        if home:
            self.path_input.text = home
            self._refresh_file_list()

    def _set_default(self):
        path = self.path_input.text.strip()
        if path and os.path.isdir(path):
            json_manager.set_default_directory(path)
            from ui.notifications import show_success
            show_success('Default: ' + os.path.basename(path), 2)
        else:
            from ui.notifications import show_error
            show_error('Invalid path', 2)

    # ============================================================
    # ================== FOOTER OVERRIDE =========================
    # ============================================================

    def _build_wizard_buttons(self, footer):
        if self.open_mode:
            if not self.is_first_page:
                back_btn = make_icon_text_button(
                    text='Back', icon_name='back',
                    on_press=lambda x: self._do_back(),
                    height=dp(38), icon_size=dp(20), font_size='12sp',
                    bg_color=Theme.BUTTON_NEUTRAL_BG,
                    fg_color=[1, 1, 1, 1],
                )
                footer.add_widget(back_btn)

            open_btn = make_icon_text_button(
                text='Open', icon_name='open',
                on_press=lambda x: self._do_open(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_SUCCESS_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(open_btn)

            cancel_btn = make_icon_text_button(
                text='Cancel', icon_name='cancel',
                on_press=lambda x: self._do_cancel(),
                height=dp(38), icon_size=dp(20), font_size='12sp',
                bg_color=Theme.BUTTON_DANGER_BG,
                fg_color=[1, 1, 1, 1],
            )
            footer.add_widget(cancel_btn)
            return

        super()._build_wizard_buttons(footer)

    # ============================================================
    # ================== VALIDATION ==============================
    # ============================================================

    def validate(self):
        ok = True

        path = self.path_input.text.strip()
        if not path:
            self.path_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        elif not os.path.isdir(path):
            self.path_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        else:
            self.path_input.background_color = Theme.INPUT_BG

        name = self.filename_input.text.strip()
        if not name:
            self.filename_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        elif not name.endswith('.json'):
            self.filename_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        else:
            full = os.path.join(path, name) if path else ''
            if self.open_mode and not os.path.exists(full):
                self.filename_input.background_color = Theme.INPUT_ERROR_BG
                ok = False
            else:
                self.filename_input.background_color = Theme.INPUT_BG

        return ok

    # ============================================================
    # ================== DATA ====================================
    # ============================================================

    def get_data(self):
        path = self.path_input.text.strip()
        name = self.filename_input.text.strip()
        return {
            'save_path': path,
            'save_filename': name,
            'full_path': os.path.join(path, name) if path and name else '',
        }

    def load_data(self, data):
        default_dir = json_manager.get_default_directory() or ''
        if not default_dir or not os.path.isdir(default_dir):
            for p in ['/storage/emulated/0/Documents',
                      os.path.expanduser('~/Documents'),
                      os.getcwd()]:
                if os.path.isdir(p):
                    default_dir = p
                    break

        self.path_input.text = data.get('save_path', default_dir)
        self.filename_input.text = data.get(
            'save_filename', 'project.json'
        )

    def set_default_filename(self, project_name, power, poles):
        try:
            speed = 6000 // int(poles)
        except Exception:
            speed = 0
        name = (str(project_name).strip().replace(' ', '_')
                if project_name else 'project')
        pw = str(power).strip() if power else '0'
        self.filename_input.text = f"{name}_{pw}kw_{speed}rpm.json"

    def get_focus_order(self):
        return [self.path_input, self.filename_input]
