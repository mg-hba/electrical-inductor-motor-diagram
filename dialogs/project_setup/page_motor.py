"""
================================================================================
File: dialogs/project_setup/page_motor.py
Purpose: Wizard page 2 - MOTOR SETTINGS + DIAGRAM + COIL SPECS
Version: 0.1.4
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from dialogs.project_setup.base_page import BasePage
from dialogs.project_setup.setup_sections import (
    make_section, make_label, make_input, make_spinner,
)
from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from utils.constants import (
    PROJECT_SETUP_INPUT_HEIGHT, PROJECT_SETUP_LABEL_HEIGHT,
)


class PageMotor(BasePage):

    title = "MOTOR SETTINGS"

    def __init__(self, **kwargs):
        self.wire_items = []
        self.turns_items = []
        self.span_active_type = 'chained'
        super().__init__(**kwargs)
        self._bind_events()
        self.load_data({})

    # ============================================================
    # ================== BUILD CONTENT ==========================
    # ============================================================

    def build_content(self):
        self._build_motor_section()
        self._build_diagram_section()
        self._build_coil_section()

    def _build_motor_section(self):
        section = make_section('MOTOR SETTINGS')
        row = BoxLayout(orientation='horizontal', spacing=dp(3),
                        size_hint_y=None,
                        height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                  PROJECT_SETUP_LABEL_HEIGHT + 2))

        slots_col = BoxLayout(orientation='vertical', spacing=dp(1),
                              size_hint_x=0.20)
        slots_col.add_widget(make_label('Slots:'))
        self.all_slots_input = make_input(input_filter='int')
        self.all_slots_input.text = '60'
        slots_col.add_widget(self.all_slots_input)

        poles_col = BoxLayout(orientation='vertical', spacing=dp(1),
                              size_hint_x=0.20)
        poles_col.add_widget(make_label('Poles:'))
        self.poles_spinner = make_spinner(
            '4', ('2', '4', '6'), None,
        )
        poles_col.add_widget(self.poles_spinner)

        speed_col = BoxLayout(orientation='vertical', spacing=dp(1),
                              size_hint_x=0.60)
        speed_col.add_widget(make_label('Speed:'))
        self.speed_value_label = Label(
            text='---', font_size='12sp', bold=True,
            color=Theme.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(PROJECT_SETUP_INPUT_HEIGHT),
            halign='center', valign='middle',
        )
        speed_col.add_widget(self.speed_value_label)

        row.add_widget(slots_col)
        row.add_widget(poles_col)
        row.add_widget(speed_col)
        section.add_widget(row)
        section.height = dp(44)
        self.content.add_widget(section)

    def _build_diagram_section(self):
        section = make_section('DIAGRAM SETTINGS')

        row_winding = BoxLayout(orientation='horizontal', spacing=dp(3),
                                size_hint_y=None,
                                height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                          PROJECT_SETUP_LABEL_HEIGHT + 2))
        winding_col = BoxLayout(orientation='vertical', spacing=dp(1),
                                size_hint_x=1)
        winding_col.add_widget(make_label('Winding:'))
        self.layer_spinner = make_spinner(
            'Two Layer', ('Two Layer', 'Single Layer'), None,
        )
        winding_col.add_widget(self.layer_spinner)
        row_winding.add_widget(winding_col)
        section.add_widget(row_winding)

        row_spans = BoxLayout(orientation='horizontal', spacing=dp(3),
                              size_hint_y=None,
                              height=dp(PROJECT_SETUP_INPUT_HEIGHT +
                                        PROJECT_SETUP_LABEL_HEIGHT + 4))

        chained_col = BoxLayout(orientation='vertical', spacing=dp(1),
                                size_hint_x=0.5)
        chained_col.add_widget(make_label('Span Chained:'))
        chained_row = BoxLayout(orientation='horizontal', spacing=dp(2),
                                size_hint_y=None,
                                height=dp(PROJECT_SETUP_INPUT_HEIGHT))
        self.chained_span_btn = make_icon_button(
            text='Chained', icon_name='span_chained',
            on_press=lambda x: self._on_span_btn_click('chained'),
            size=(dp(60), dp(PROJECT_SETUP_INPUT_HEIGHT)),
            bg_color=[0.2, 0.7, 0.3, 1],
        )
        chained_row.add_widget(self.chained_span_btn)
        self.chained_span_input = make_input(input_filter='int')
        self.chained_span_input.size_hint_x = 1
        self.chained_span_input.bind(
            focus=self._on_chained_span_focus
        )
        chained_row.add_widget(self.chained_span_input)
        chained_col.add_widget(chained_row)

        concentric_col = BoxLayout(orientation='vertical', spacing=dp(1),
                                   size_hint_x=0.5)
        concentric_col.add_widget(make_label('Span Concentric:'))
        concentric_row = BoxLayout(orientation='horizontal',
                                   spacing=dp(2),
                                   size_hint_y=None,
                                   height=dp(PROJECT_SETUP_INPUT_HEIGHT))
        self.concentric_span_btn = make_icon_button(
            text='Conc', icon_name='span_concentric',
            on_press=lambda x: self._on_span_btn_click('concentric'),
            size=(dp(60), dp(PROJECT_SETUP_INPUT_HEIGHT)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        concentric_row.add_widget(self.concentric_span_btn)
        self.concentric_span_input = make_input(
            input_filter='int', disabled=True,
        )
        self.concentric_span_input.size_hint_x = 1
        self.concentric_span_input.bind(
            focus=self._on_concentric_span_focus
        )
        concentric_row.add_widget(self.concentric_span_input)
        concentric_col.add_widget(concentric_row)

        row_spans.add_widget(chained_col)
        row_spans.add_widget(concentric_col)
        section.add_widget(row_spans)

        section.height = dp(88)
        self.content.add_widget(section)

    def _build_coil_section(self):
        section = make_section('COIL SPECIFICATIONS')
        coil_row = BoxLayout(orientation='horizontal', spacing=dp(6),
                             size_hint_y=None, height=dp(200))

        # Wires
        left = BoxLayout(orientation='vertical', spacing=dp(2),
                         size_hint_x=0.5)
        left.add_widget(Label(text='WIRE GAUGE (mm)', font_size='10sp',
                              bold=True, color=Theme.TEXT_SECONDARY,
                              size_hint_y=None,
                              height=dp(PROJECT_SETUP_LABEL_HEIGHT)))
        wire_scroll = ScrollView(size_hint_y=None, height=dp(105))
        self.wire_container = BoxLayout(orientation='vertical',
                                        spacing=dp(2),
                                        size_hint_y=None)
        self.wire_container.bind(
            minimum_height=self.wire_container.setter('height')
        )
        wire_scroll.add_widget(self.wire_container)
        left.add_widget(wire_scroll)

        wire_add = make_icon_text_button(
            text='Add Wire', icon_name='add_wire',
            on_press=lambda x: self.add_wire_item(),
            height=dp(26), icon_size=dp(18), font_size='11sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        left.add_widget(wire_add)

        self.wire_sum_input = TextInput(
            text='0.00 mm', font_size='10sp', disabled=True,
            background_color=Theme.INPUT_DISABLED_BG,
            foreground_color=Theme.TEXT_SECONDARY,
            halign='center',
            size_hint_y=None, height=dp(22),
        )
        left.add_widget(self.wire_sum_input)

        # Turns
        right = BoxLayout(orientation='vertical', spacing=dp(2),
                          size_hint_x=0.5)
        right.add_widget(Label(text='NUMBER OF TURNS', font_size='10sp',
                               bold=True, color=Theme.TEXT_SECONDARY,
                               size_hint_y=None,
                               height=dp(PROJECT_SETUP_LABEL_HEIGHT)))
        turns_scroll = ScrollView(size_hint_y=None, height=dp(105))
        self.turns_container = BoxLayout(orientation='vertical',
                                         spacing=dp(2),
                                         size_hint_y=None)
        self.turns_container.bind(
            minimum_height=self.turns_container.setter('height')
        )
        turns_scroll.add_widget(self.turns_container)
        right.add_widget(turns_scroll)

        turns_add = make_icon_text_button(
            text='Add Turns', icon_name='add_turns',
            on_press=lambda x: self.add_turns_item(),
            height=dp(26), icon_size=dp(18), font_size='11sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        )
        right.add_widget(turns_add)

        self.turns_sum_input = TextInput(
            text='0 turns', font_size='10sp', disabled=True,
            background_color=Theme.INPUT_DISABLED_BG,
            foreground_color=Theme.TEXT_SECONDARY,
            halign='center',
            size_hint_y=None, height=dp(22),
        )
        right.add_widget(self.turns_sum_input)

        coil_row.add_widget(left)
        coil_row.add_widget(right)
        section.add_widget(coil_row)
        section.height = dp(235)
        self.content.add_widget(section)

    # ============================================================
    # ================== DYNAMIC ROWS ===========================
    # ============================================================

    def add_wire_item(self, instance=None, value=None, focus_new=True):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.add_wire_item(self, instance, value, focus_new)

    def remove_wire_item(self, row):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.remove_wire_item(self, row)

    def on_enter_in_wire(self, instance):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.on_enter_in_wire(self, instance)

    def update_wire_sum(self):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.update_wire_sum(self)

    def add_turns_item(self, instance=None, value=None, focus_new=True):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.add_turns_item(self, instance, value, focus_new)

    def remove_turns_item(self, row):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.remove_turns_item(self, row)

    def on_enter_in_turns(self, instance):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.on_enter_in_turns(self, instance)

    def update_turns_sum(self):
        from dialogs.project_setup import setup_wire_turns as wt
        wt.update_turns_sum(self)

    # ============================================================
    # ================== SPAN CONTROLS ==========================
    # ============================================================

    def update_speed_display(self, *args):
        from dialogs.project_setup import setup_span_controls as sc
        sc.update_speed_display(self, *args)

    def update_span_state(self):
        from dialogs.project_setup import setup_span_controls as sc
        sc.update_span_state(self)

    def _on_span_btn_click(self, span_type):
        from dialogs.project_setup import setup_span_controls as sc
        self.span_active_type = span_type
        sc.update_span_state(self)

    def _on_chained_span_focus(self, instance, focused):
        if not focused:
            from dialogs.project_setup import setup_span_controls as sc
            sc.recompute_other_span(self, 'chained')

    def _on_concentric_span_focus(self, instance, focused):
        if not focused:
            from dialogs.project_setup import setup_span_controls as sc
            sc.recompute_other_span(self, 'concentric')

    def _bind_events(self):
        self.conn_spinner = None  # not on this page
        self.poles_spinner.bind(
            text=lambda s, t: self._on_poles_change()
        )
        self.layer_spinner.bind(
            text=lambda s, t: self.update_span_state()
        )

    def _on_poles_change(self):
        self.update_speed_display()
        from dialogs.project_setup import setup_span_controls as sc
        sc.recompute_other_span(self, self.span_active_type)

    # ============================================================
    # ================== DATA ===================================
    # ============================================================

    def validate(self):
        ok = True

        # Slots
        try:
            slots = int(self.all_slots_input.text.strip())
            if slots < 6:
                raise ValueError
            self.all_slots_input.background_color = Theme.INPUT_BG
        except Exception:
            self.all_slots_input.background_color = Theme.INPUT_ERROR_BG
            ok = False

        # Poles
        try:
            poles = int(self.poles_spinner.text.strip())
            if poles <= 0:
                raise ValueError
        except Exception:
            ok = False

        # Slots % Poles
        try:
            if slots % poles != 0:
                ok = False
        except Exception:
            pass

        # Wire count
        wire_ok, wire_has = self._check_wire_items()
        if not (wire_ok and wire_has):
            ok = False

        # Turns count
        turns_ok, turns_has = self._check_turns_items()
        if not (turns_ok and turns_has):
            ok = False

        return ok

    def _check_wire_items(self):
        from kivy.uix.textinput import TextInput
        is_valid = True
        has_value = False
        for row in self.wire_items:
            for child in row.children:
                if isinstance(child, TextInput):
                    if child.text.strip():
                        child.background_color = Theme.INPUT_BG
                        has_value = True
                    else:
                        child.background_color = Theme.INPUT_ERROR_BG
                        is_valid = False
        return is_valid, has_value

    def _check_turns_items(self):
        from kivy.uix.textinput import TextInput
        is_valid = True
        has_value = False
        for row in self.turns_items:
            for child in row.children:
                if isinstance(child, TextInput):
                    if child.text.strip():
                        child.background_color = Theme.INPUT_BG
                        has_value = True
                    else:
                        child.background_color = Theme.INPUT_ERROR_BG
                        is_valid = False
        return is_valid, has_value

    def get_data(self):
        from kivy.uix.textinput import TextInput

        wire_gauges = []
        for row in self.wire_items:
            for child in row.children:
                if isinstance(child, TextInput):
                    v = child.text.strip()
                    if v:
                        wire_gauges.append(v)

        turns_counts = []
        for row in self.turns_items:
            for child in row.children:
                if isinstance(child, TextInput):
                    v = child.text.strip()
                    if v:
                        turns_counts.append(v)

        winding_type = ('two_layer'
                        if self.layer_spinner.text == 'Two Layer'
                        else 'single_layer')

        try:
            all_slots_value = int(self.all_slots_input.text.strip())
        except Exception:
            all_slots_value = 60
        try:
            poles_value = int(self.poles_spinner.text.strip())
        except Exception:
            poles_value = 4

        active_pattern = 'lap'
        if self.layer_spinner.text == 'Two Layer':
            active_pattern = ('lap'
                              if self.span_active_type == 'chained'
                              else 'concentric')

        if self.layer_spinner.text == 'Two Layer':
            try:
                chained_value = int(self.chained_span_input.text.strip()
                                    or '11')
            except Exception:
                chained_value = 11
            try:
                concentric_value = int(
                    self.concentric_span_input.text.strip() or '9'
                )
            except Exception:
                concentric_value = 9
        else:
            chained_value = 0
            concentric_value = 0

        return {
            'winding_type': winding_type,
            'active_pattern': active_pattern,
            'wire_gauges': wire_gauges,
            'turns_counts': turns_counts,
            'all_slots': all_slots_value,
            'poles': poles_value,
            'coil_span_chained': chained_value,
            'coil_span_concentric': concentric_value,
        }

    def load_data(self, data):
        # Slots
        self.all_slots_input.text = str(data.get('all_slots', 60))
        self.poles_spinner.text = str(data.get('poles', 4))

        # Winding
        wt = data.get('winding_type', 'two_layer')
        self.layer_spinner.text = ('Single Layer' if wt == 'single_layer'
                                   else 'Two Layer')

        # Spans
        self.chained_span_input.text = str(
            data.get('coil_span_chained', '11')
        )
        self.concentric_span_input.text = str(
            data.get('coil_span_concentric', '9')
        )

        # Active span type
        ap = data.get('active_pattern', 'lap')
        self.span_active_type = ('concentric'
                                 if ap == 'concentric' else 'chained')

        # Dynamic rows - clear first
        self._clear_dynamic_rows()

        wires = data.get('wire_gauges', []) or ['1']
        for w in wires:
            self.add_wire_item(value=w, focus_new=False)

        turns = data.get('turns_counts', []) or ['1']
        for t in turns:
            self.add_turns_item(value=t, focus_new=False)

        self.update_wire_sum()
        self.update_turns_sum()
        self.update_speed_display()
        self.update_span_state()

    def _clear_dynamic_rows(self):
        for row in list(self.wire_items):
            if row in self.wire_container.children:
                self.wire_container.remove_widget(row)
        self.wire_items = []
        for row in list(self.turns_items):
            if row in self.turns_container.children:
                self.turns_container.remove_widget(row)
        self.turns_items = []

    def get_focus_order(self):
        order = [self.all_slots_input, self.poles_spinner,
                 self.layer_spinner]
        if self.layer_spinner.text == 'Two Layer':
            if self.span_active_type == 'chained':
                order.append(self.chained_span_input)
            else:
                order.append(self.concentric_span_input)
        return order
