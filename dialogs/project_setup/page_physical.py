"""
================================================================================
File: dialogs/project_setup/page_physical.py
Purpose: Wizard page 4 - PHYSICAL (optional)
         Fields: Slot Length, Core Diameter, Unit.
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
    UNIT_OPTIONS, DEFAULT_UNIT,
)


class PagePhysical(BasePage):

    title = "PHYSICAL"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_data({})

    def build_content(self):
        section = make_section('PHYSICAL')
        row = BoxLayout(orientation='horizontal', spacing=dp(3),
                        size_hint_y=None,
                        height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                  PROJECT_SETUP_LABEL_HEIGHT + 2))

        slot_col = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_x=0.33)
        slot_col.add_widget(make_label('Slot Length (mm):'))
        self.slot_length_input = make_input(input_filter='int')
        slot_col.add_widget(self.slot_length_input)

        core_col = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_x=0.33)
        core_col.add_widget(make_label('Core Diameter (mm):'))
        self.core_diameter_input = make_input(input_filter='int')
        core_col.add_widget(self.core_diameter_input)

        unit_col = BoxLayout(orientation='vertical', spacing=dp(1),
                             size_hint_x=0.34)
        unit_col.add_widget(make_label('Unit:'))
        self.unit_spinner = make_spinner(
            DEFAULT_UNIT, UNIT_OPTIONS, None,
        )
        unit_col.add_widget(self.unit_spinner)

        row.add_widget(slot_col)
        row.add_widget(core_col)
        row.add_widget(unit_col)
        section.add_widget(row)
        section.height = dp(44)

        self.content.add_widget(section)

    def validate(self):
        """Optional page: either all empty or all valid."""
        slot = self.slot_length_input.text.strip()
        core = self.core_diameter_input.text.strip()

        # Both empty = OK (user skipped)
        if not slot and not core:
            return True

        ok = True

        if slot:
            try:
                v = int(slot)
                if v <= 0:
                    raise ValueError
                self.slot_length_input.background_color = Theme.INPUT_BG
            except Exception:
                self.slot_length_input.background_color = Theme.INPUT_ERROR_BG
                ok = False
        else:
            self.slot_length_input.background_color = Theme.INPUT_ERROR_BG
            ok = False

        if core:
            try:
                v = int(core)
                if v <= 0:
                    raise ValueError
                self.core_diameter_input.background_color = Theme.INPUT_BG
            except Exception:
                self.core_diameter_input.background_color = Theme.INPUT_ERROR_BG
                ok = False
        else:
            self.core_diameter_input.background_color = Theme.INPUT_ERROR_BG
            ok = False

        return ok

    def get_data(self):
        try:
            slot = int(self.slot_length_input.text.strip() or '0')
        except Exception:
            slot = 0
        try:
            core = int(self.core_diameter_input.text.strip() or '0')
        except Exception:
            core = 0

        return {
            'slot_length': slot,
            'core_diameter': core,
            'unit': self.unit_spinner.text,
        }

    def load_data(self, data):
        self.slot_length_input.text = str(data.get('slot_length', ''))
        self.core_diameter_input.text = str(data.get('core_diameter', ''))
        self.unit_spinner.text = data.get('unit', DEFAULT_UNIT)

    def get_focus_order(self):
        return [self.slot_length_input, self.core_diameter_input,
                self.unit_spinner]
