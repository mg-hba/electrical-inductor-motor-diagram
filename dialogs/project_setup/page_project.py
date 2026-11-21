"""
================================================================================
File: dialogs/project_setup/page_project.py
Purpose: Wizard page 1 - PROJECT INFORMATION
         Fields: Name, Power, Connection.
Version: 0.1.4
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from dialogs.project_setup.base_page import BasePage
from dialogs.project_setup.setup_sections import (
    make_section, make_label, make_input, make_spinner,
)
from ui.theme import Theme
from utils.constants import (
    PROJECT_SETUP_INPUT_HEIGHT, PROJECT_SETUP_LABEL_HEIGHT,
)


class PageProject(BasePage):

    title = "PROJECT"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_data({})

    def build_content(self):
        section = make_section('PROJECT INFORMATION')
        row = BoxLayout(orientation='horizontal', spacing=dp(3),
                        size_hint_y=None,
                        height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                  PROJECT_SETUP_LABEL_HEIGHT + 2))

        name_col = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_x=0.42)
        name_col.add_widget(make_label('Name:'))
        self.name_input = make_input('project')
        name_col.add_widget(self.name_input)

        power_col = BoxLayout(orientation='vertical', spacing=dp(1),
                              size_hint_x=0.28)
        power_col.add_widget(make_label('Power:'))
        self.power_input = make_input('kW', input_filter='float')
        power_col.add_widget(self.power_input)

        conn_col = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_x=0.30)
        conn_col.add_widget(make_label('Conn:'))
        self.conn_spinner = make_spinner(
            'Star', ('Star', 'Delta', 'Star-Delta'), None,
        )
        conn_col.add_widget(self.conn_spinner)

        row.add_widget(name_col)
        row.add_widget(power_col)
        row.add_widget(conn_col)
        section.add_widget(row)
        section.height = dp(44)

        self.content.add_widget(section)

    def validate(self):
        ok = True
        if not self.name_input.text.strip():
            self.name_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        else:
            self.name_input.background_color = Theme.INPUT_BG
        try:
            p = float(self.power_input.text.strip())
            if p <= 0:
                raise ValueError
            self.power_input.background_color = Theme.INPUT_BG
        except Exception:
            self.power_input.background_color = Theme.INPUT_ERROR_BG
            ok = False
        return ok

    def get_data(self):
        return {
            'project_name': self.name_input.text.strip(),
            'nominal_power': self.power_input.text.strip(),
            'connection_type': self.conn_spinner.text,
        }

    def load_data(self, data):
        self.name_input.text = data.get('project_name', '')
        self.power_input.text = data.get('nominal_power', '')
        self.conn_spinner.text = data.get('connection_type', 'Star')

    def get_focus_order(self):
        return [self.name_input, self.power_input, self.conn_spinner]
