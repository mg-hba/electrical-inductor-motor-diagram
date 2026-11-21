"""
================================================================================
File: ui/components.py
Purpose: Reusable UI widgets.
Version: 0.1.1
================================================================================
"""

import os
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import RoundedRectangle, Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')


class RoundedButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0.2, 0.6, 0.9, 1]
        self.background_normal = ''
        self.color = Theme.BUTTON_TEXT
        self.font_size = 20
        with self.canvas.before:
            Color(0.2, 0.6, 0.9, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size,
                                          radius=[8])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class IntegerInput(TextInput):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input_filter = 'int'
        self.multiline = False
        self.background_color = Theme.INPUT_BG
        self.foreground_color = Theme.INPUT_TEXT
        self.font_size = 18


class PatternRadioOption(ButtonBehavior, BoxLayout):

    def __init__(self, group_name, option_id, label_text, icon_name,
                 on_select=None, is_selected=False, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(6),
                          size_hint_y=None, height=dp(34), **kwargs)
        self.group_name = group_name
        self.option_id = option_id
        self.on_select = on_select
        self.icon_name = icon_name

        with self.canvas.before:
            Color(*Theme.SECTION_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.checkbox = CheckBox(size_hint_x=None, width=dp(28),
                                  active=is_selected)
        self.checkbox.bind(active=self._on_check)
        self.add_widget(self.checkbox)

        icon_path = os.path.join(ASSETS_DIR, icon_name)
        if os.path.exists(icon_path):
            self.add_widget(Image(source=icon_path, size_hint_x=None,
                                    width=dp(34), allow_stretch=True,
                                    keep_ratio=True))
        else:
            self.add_widget(Label(text=label_text, font_size='13sp',
                                    color=Theme.TEXT_PRIMARY,
                                    halign='left', valign='middle'))
        self.add_widget(Label(size_hint_x=1))

    def _on_check(self, checkbox, active):
        if active and self.on_select:
            self.on_select(self.group_name, self.option_id)
        elif not active and self.on_select:
            self.on_select(self.group_name, None)

    def set_active(self, active):
        self.checkbox.active = active

    def on_press(self):
        self.checkbox.active = not self.checkbox.active

    def _update_bg(self, instance, value):
        self._bg.pos = instance.pos
        self._bg.size = instance.size


class RadioOption(BoxLayout):

    def __init__(self, group_name, option_id, label_text,
                 on_select=None, is_selected=False, **kwargs):
        super().__init__(orientation='horizontal', spacing=dp(6),
                          size_hint_y=None, height=dp(30), **kwargs)
        self.group_name = group_name
        self.option_id = option_id
        self.on_select = on_select
        self.checkbox = CheckBox(size_hint_x=None, width=dp(28),
                                  active=is_selected)
        self.checkbox.bind(active=self._on_check)
        self.add_widget(self.checkbox)
        self.label = Label(text=label_text, font_size='14sp',
                            color=Theme.TEXT_PRIMARY,
                            halign='left', valign='middle')
        self.add_widget(self.label)

    def _on_check(self, checkbox, active):
        if active and self.on_select:
            self.on_select(self.group_name, self.option_id)

    def set_active(self, active):
        self.checkbox.active = active


class RadioGroup(BoxLayout):

    def __init__(self, group_name, options, selected_id=None,
                 on_change=None, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(4),
                          size_hint_y=None, **kwargs)
        self.group_name = group_name
        self.on_change = on_change
        self.selected_id = selected_id
        self.options = {}
        for opt_id, opt_label in options:
            opt = RadioOption(group_name=group_name, option_id=opt_id,
                               label_text=opt_label,
                               on_select=self._handle_select,
                               is_selected=(opt_id == selected_id))
            self.options[opt_id] = opt
            self.add_widget(opt)
        self.height = dp(30) * len(options) + dp(4) * (len(options) - 1)

    def _handle_select(self, group_name, option_id):
        if option_id is None:
            return
        self.selected_id = option_id
        for opt_id, opt in self.options.items():
            if opt_id != option_id:
                opt.set_active(False)
        if self.on_change:
            self.on_change(option_id)

    def get_selected(self):
        return self.selected_id

    def set_selected(self, option_id):
        self.selected_id = option_id
        for opt_id, opt in self.options.items():
            opt.set_active(opt_id == option_id)