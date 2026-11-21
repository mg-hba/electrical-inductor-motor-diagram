"""
================================================================================
File: dialogs/project_setup/page_paper.py
Purpose: Wizard page 3 - PAPER (with Physical Settings button)
Version: 0.1.4
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from dialogs.project_setup.base_page import BasePage
from dialogs.project_setup.setup_sections import (
    make_section, make_label, make_spinner,
)
from ui.theme import Theme
from ui.icon_button import make_icon_text_button
from utils.constants import (
    PROJECT_SETUP_INPUT_HEIGHT, PROJECT_SETUP_LABEL_HEIGHT,
)


class PagePaper(BasePage):

    title = "PAPER"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_data({})

    def build_content(self):
        section = make_section('PAPER')
        row = BoxLayout(orientation='horizontal', spacing=dp(3),
                        size_hint_y=None,
                        height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                  PROJECT_SETUP_LABEL_HEIGHT + 2))

        paper_col = BoxLayout(orientation='vertical', spacing=dp(1),
                              size_hint_x=0.50)
        paper_col.add_widget(make_label('Paper:'))
        self.paper_spinner = make_spinner(
            'A4',
            ('A0', 'A1', 'A2', 'A3', 'A4', 'A5',
             'Letter', 'Legal', 'Tabloid'),
            None,
        )
        paper_col.add_widget(self.paper_spinner)

        orient_col = BoxLayout(orientation='vertical', spacing=dp(1),
                               size_hint_x=0.50)
        orient_col.add_widget(make_label('Orient:'))
        self.orient_spinner = make_spinner(
            'Landscape', ('Portrait', 'Landscape'), None,
        )
        orient_col.add_widget(self.orient_spinner)

        row.add_widget(paper_col)
        row.add_widget(orient_col)
        section.add_widget(row)
        section.height = dp(44)

        self.content.add_widget(section)

    def build_extra_footer_buttons(self):
        phys_btn = make_icon_text_button(
            text='Physical',
            icon_name='settings',
            on_press=lambda x: self._do_physical(),
            height=dp(44), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        )
        return [phys_btn]

    def _do_physical(self):
        if self.on_physical:
            self.on_physical(self)

    def validate(self):
        ok = True
        if not self.paper_spinner.text:
            ok = False
        if not self.orient_spinner.text:
            ok = False
        return ok

    def get_data(self):
        return {
            'paper_size': self.paper_spinner.text,
            'orientation': self.orient_spinner.text,
        }

    def load_data(self, data):
        self.paper_spinner.text = data.get('paper_size', 'A4')
        self.orient_spinner.text = data.get('orientation', 'Landscape')

    def get_focus_order(self):
        return [self.paper_spinner, self.orient_spinner]
