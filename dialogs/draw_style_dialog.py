"""
================================================================================
File: dialogs/draw_style_dialog.py
Purpose: Draw Style - coil pattern and coil spans with icons.
         Conversion formula:
           concentric_span = chained_span - coils_per_pole + 1
           chained_span = concentric_span + coils_per_pole - 1
         coils_per_pole = all_slots / (3 * poles)
Version: 0.1.2
================================================================================
"""

import os
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from ui.components import PatternRadioOption
from diagrams.patterns.registry import PatternRegistry
from version import get_version_suffix


class DrawStyleDialog(Popup):

    ##
    ###### Initialize dialog with current pattern and spans ######
    ##
    def __init__(self, on_apply_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.92, 0.85)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.on_apply_callback = on_apply_callback
        self.selected_pattern = json_manager.get_active_pattern()
        self.span_active_type = ('concentric'
                                  if self.selected_pattern == 'concentric'
                                  else 'chained')
        self.chained_span = str(json_manager.get_group_coil_span_chained())
        self.concentric_span = str(json_manager.get_group_coil_span_concentric())

        self.pattern_radios = {}
        self.span_radios = {}

        self.build_ui()
        self._sync_pattern_selection()
        self._sync_span_selection()
    # end __init__

    ##
    ###### Build the complete dialog UI ######
    ##
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        with main_layout.canvas.before:
            Color(*Theme.DIALOG_BG)
            background_rect = Rectangle(pos=main_layout.pos,
                                         size=main_layout.size)
        main_layout.bind(
            pos=lambda i, v: setattr(background_rect, 'pos', i.pos),
            size=lambda i, v: setattr(background_rect, 'size', i.size)
        )

        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6),
                            padding=[dp(12), dp(6), dp(12), dp(6)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            header_bg = Rectangle(pos=header.pos, size=header.size)
        header.bind(
            pos=lambda i, v: setattr(header_bg, 'pos', i.pos),
            size=lambda i, v: setattr(header_bg, 'size', i.size)
        )
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(32), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='DRAW STYLE' + get_version_suffix(),
                                 font_size='14sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1,
                                 halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(32)))
        main_layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(8),
                            padding=[dp(12), dp(10), dp(12), dp(10)],
                            size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(self._make_title_label('Coil Pattern'))
        groups, ungrouped = PatternRegistry.get_grouped()
        for group_id, group_data in groups.items():
            content.add_widget(Label(text=group_data['display'] + ':',
                                       font_size='12sp', bold=True,
                                       color=Theme.TEXT_SECONDARY,
                                       size_hint_y=None, height=dp(20)))
            for pattern_class in group_data['items']:
                pattern_id = pattern_class.pattern_id
                option = PatternRadioOption(
                    group_name='pattern', option_id=pattern_id,
                    label_text=pattern_class.display_name,
                    icon_name=pattern_id + '.png',
                    on_select=self._on_pattern_select,
                    is_selected=(pattern_id == self.selected_pattern)
                )
                self.pattern_radios[pattern_id] = option
                content.add_widget(option)

        for pattern_class in ungrouped:
            pattern_id = pattern_class.pattern_id
            option = PatternRadioOption(
                group_name='pattern', option_id=pattern_id,
                label_text=pattern_class.display_name,
                icon_name=pattern_id + '.png',
                on_select=self._on_pattern_select,
                is_selected=(pattern_id == self.selected_pattern)
            )
            self.pattern_radios[pattern_id] = option
            content.add_widget(option)

        content.add_widget(self._make_title_label('Span'))
        self.span_radios['chained'] = self._make_span_option(
            'chained', 'Chained', self.chained_span, 'span_chained'
        )
        self.span_radios['concentric'] = self._make_span_option(
            'concentric', 'Concentric', self.concentric_span, 'span_concentric'
        )
        content.add_widget(self.span_radios['chained'])
        content.add_widget(self.span_radios['concentric'])

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
        content.add_widget(make_icon_text_button(
            text='Coils per Pole', icon_name='coils_per_pole',
            on_press=self.open_coils_per_pole_dialog,
            height=dp(44), icon_size=dp(22), font_size='14sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        footer = BoxLayout(size_hint_y=None, height=dp(56),
                            spacing=dp(8),
                            padding=[dp(12), dp(6), dp(12), dp(6)])
        footer.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(46), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        footer.add_widget(make_icon_text_button(
            text='Apply', icon_name='apply',
            on_press=self.apply_and_close,
            height=dp(46), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_SUCCESS_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main_layout.add_widget(footer)

        self.add_widget(main_layout)
    # end build_ui

    ##
    ###### Create a title label for a section ######
    ##
    def _make_title_label(self, text):
        return Label(text=text, font_size='13sp', bold=True,
                      color=Theme.TEXT_SECONDARY,
                      size_hint_y=None, height=dp(22))
    # end _make_title_label

    ##
    ###### Create a span input row (label button + text input) ######
    ##
    def _make_span_option(self, span_id, label, value, icon_name):
        row = BoxLayout(orientation='horizontal', spacing=dp(6),
                        size_hint_y=None, height=dp(40))
        button = make_icon_button(
            text=label, icon_name=icon_name,
            on_press=lambda x: self._on_span_select('span', span_id),
            size=(dp(80), dp(36)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        )
        input_field = TextInput(text=str(value), multiline=False,
                                 font_size='13sp',
                                 size_hint_x=1,
                                 background_color=Theme.INPUT_BG,
                                 foreground_color=Theme.INPUT_TEXT,
                                 input_filter='int')
        if span_id == 'chained':
            input_field.bind(focus=self._on_chained_focus)
        else:
            input_field.bind(focus=self._on_concentric_focus)
        row.add_widget(button)
        row.add_widget(input_field)
        row.span_id = span_id
        row.value_input = input_field
        row.label_btn = button
        return row
    # end _make_span_option

    ##
    ###### Handle chained span focus loss - recompute other span ######
    ##
    def _on_chained_focus(self, instance, focused):
        if not focused and instance.text.strip():
            self.chained_span = instance.text.strip()
            self._recompute_other_span('chained')
    # end _on_chained_focus

    ##
    ###### Handle concentric span focus loss - recompute other span ######
    ##
    def _on_concentric_focus(self, instance, focused):
        if not focused and instance.text.strip():
            self.concentric_span = instance.text.strip()
            self._recompute_other_span('concentric')
    # end _on_concentric_focus

    ##
    ###### Recompute the other span using the conversion formula ######
    ##
    def _recompute_other_span(self, source):
        coils_per_pole = self._get_coils_in_pole()
        if coils_per_pole <= 0:
            return
        try:
            if source == 'chained':
                chained_value = int(self.chained_span)
                concentric_value = chained_value - coils_per_pole + 1
                self.concentric_span = str(concentric_value)
                self.span_radios['concentric'].value_input.text = str(
                    concentric_value
                )
            else:
                concentric_value = int(self.concentric_span)
                chained_value = concentric_value + coils_per_pole - 1
                self.chained_span = str(chained_value)
                self.span_radios['chained'].value_input.text = str(
                    chained_value
                )
        except Exception:
            pass
    # end _recompute_other_span

    ##
    ###### Get coils per pole from project or default calculation ######
    ##
    def _get_coils_in_pole(self):
        project_data = json_manager.project_data
        if project_data:
            values = project_data.get('coils_per_pole_values', None)
            if values and isinstance(values, list):
                filtered = [int(v) for v in values if v > 0]
                if filtered:
                    return sum(filtered) / len(filtered)
        try:
            all_slots = (int(project_data.get('all_slots', 60))
                         if project_data else 60)
            poles = (int(project_data.get('poles', 4))
                     if project_data else 4)
        except Exception:
            return 1
        if poles <= 0:
            return 1
        return all_slots / (3 * poles)
    # end _get_coils_in_pole

    ##
    ###### Handle pattern radio selection ######
    ##
    def _on_pattern_select(self, group_name, pattern_id):
        if pattern_id is None:
            return
        self.selected_pattern = pattern_id
        for pid, option in self.pattern_radios.items():
            if pid != pattern_id:
                option.set_active(False)
        new_type = 'concentric' if pattern_id == 'concentric' else 'chained'
        self._on_span_select('span', new_type)
    # end _on_pattern_select

    ##
    ###### Handle span radio selection ######
    ##
    def _on_span_select(self, group_name, span_id):
        if span_id is None:
            return
        self.span_active_type = span_id
        for sid, option in self.span_radios.items():
            if sid == span_id:
                option.label_btn.background_color = [0.2, 0.7, 0.3, 1]
                option.value_input.disabled = False
                option.value_input.background_color = Theme.INPUT_BG
            else:
                option.label_btn.background_color = Theme.BUTTON_PRIMARY_BG
                option.value_input.disabled = True
                option.value_input.background_color = Theme.INPUT_DISABLED_BG
    # end _on_span_select

    ##
    ###### Sync pattern radios with current selection ######
    ##
    def _sync_pattern_selection(self):
        for pid, option in self.pattern_radios.items():
            option.set_active(pid == self.selected_pattern)
    # end _sync_pattern_selection

    ##
    ###### Sync span radios with current selection ######
    ##
    def _sync_span_selection(self):
        self._on_span_select('span', self.span_active_type)
    # end _sync_span_selection

    ##
    ###### Apply changes and close dialog ######
    ##
    def apply_and_close(self, instance=None):
        json_manager.set_active_pattern(self.selected_pattern)
        json_manager.update_project_field('active_pattern',
                                           self.selected_pattern)
        try:
            json_manager.set_group_coil_span_chained(int(self.chained_span))
            json_manager.update_project_field('coil_span_chained',
                                               int(self.chained_span))
        except Exception:
            pass
        try:
            json_manager.set_group_coil_span_concentric(
                int(self.concentric_span)
            )
            json_manager.update_project_field('coil_span_concentric',
                                               int(self.concentric_span))
        except Exception:
            pass
        if self.on_apply_callback:
            self.on_apply_callback()
        self.dismiss()
    # end apply_and_close

    ##
    ###### Open coils per pole dialog ######
    ##
    def open_coils_per_pole_dialog(self, instance=None):
        filepath = json_manager.current_project_file
        if filepath and os.path.exists(filepath):
            json_manager.load_project_data(filepath)

        project_data = json_manager.project_data
        if not project_data:
            return
        try:
            all_slots = int(project_data.get('all_slots', 60))
            poles = int(project_data.get('poles', 4))
        except Exception:
            return
        coils_per_phase = (all_slots / 3) / 2
        existing_values = json_manager.get_coils_per_pole_values()
        from dialogs.coils_per_pole_dialog import show_coils_per_pole_dialog
        show_coils_per_pole_dialog(poles=poles,
                                    coils_per_phase=int(coils_per_phase),
                                    existing_values=existing_values)
    # end open_coils_per_pole_dialog


##
###### Module-level function to open draw style dialog ######
##
def show_draw_style_dialog(on_apply_callback=None):
    DrawStyleDialog(on_apply_callback=on_apply_callback).open()
# end show_draw_style_dialog