"""
================================================================================
File: dialogs/coils_per_pole_dialog.py
Purpose: Manual coils-per-pole distribution.
         Values are stored at the ROOT of the project JSON.
Version: 0.1.2
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.notifications import show_error, show_success
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix
from utils.constants import (
    COILS_PER_POLE_MAX_SLOTS, COILS_PER_POLE_INPUT_HEIGHT,
    COILS_PER_POLE_INPUT_FONT, COILS_PER_POLE_LABEL_FONT,
)


class CoilsPerPoleDialog(Popup):

    def __init__(self, poles=4, coils_per_phase=0,
                 existing_values=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.55)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.poles = int(poles)
        self.coils_per_phase = int(coils_per_phase)
        self.existing_values = list(existing_values) if existing_values else []

        self.inputs = []
        self.pole_labels = []
        self.build_ui()
        self.load_values()

    def load_values(self):
        for i in range(COILS_PER_POLE_MAX_SLOTS):
            if i < len(self.existing_values) and self.existing_values[i] > 0:
                self.inputs[i].text = str(self.existing_values[i])
            elif i < self.poles:
                self.inputs[i].text = '1'

    def on_input_change(self, instance, value):
        try:
            idx = self.inputs.index(instance)
        except ValueError:
            return
        if idx >= self.poles:
            return
        if idx % 2 == 0:
            partners = [i for i in range(0, self.poles, 2) if i != idx]
        else:
            partners = [i for i in range(1, self.poles, 2) if i != idx]
        for pi in partners:
            if pi < len(self.inputs) and self.inputs[pi].text != value:
                self.inputs[pi].text = value

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        header = BoxLayout(size_hint_y=None, height=dp(42),
                            spacing=dp(6),
                            padding=[dp(12), dp(6), dp(12), dp(6)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=self.dismiss,
            size=(dp(32), dp(28)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='COILS PER POLE' + get_version_suffix(),
                                 font_size='14sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1, halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(32)))
        main.add_widget(header)

        info = BoxLayout(size_hint_y=None, height=dp(24),
                          padding=[dp(10), dp(4), dp(10), dp(4)])
        info.add_widget(Label(
            text='Total coils per phase: %d   |   Poles: %d' % (
                self.coils_per_phase, self.poles),
            font_size='11sp', color=Theme.TEXT_SECONDARY,
            halign='center', valign='middle'
        ))
        main.add_widget(info)

        row = BoxLayout(orientation='horizontal', spacing=dp(4),
                        size_hint_y=None,
                        height=dp(COILS_PER_POLE_INPUT_HEIGHT + 20),
                        padding=[dp(6), dp(4), dp(6), dp(4)])

        for i in range(COILS_PER_POLE_MAX_SLOTS):
            col = BoxLayout(orientation='vertical', spacing=dp(2),
                             size_hint_x=1.0)
            lbl = Label(text='Pole %d' % (i + 1),
                         font_size=COILS_PER_POLE_LABEL_FONT,
                         color=Theme.TEXT_SECONDARY,
                         size_hint_y=None, height=dp(14))
            col.add_widget(lbl)
            self.pole_labels.append(lbl)
            inp = TextInput(
                text='', multiline=False,
                font_size=COILS_PER_POLE_INPUT_FONT, halign='center',
                input_filter='int',
                background_color=Theme.INPUT_BG,
                foreground_color=Theme.INPUT_TEXT,
                size_hint_y=None, height=dp(COILS_PER_POLE_INPUT_HEIGHT)
            )
            inp.bind(text=self.on_input_change)
            col.add_widget(inp)
            self.inputs.append(inp)
            row.add_widget(col)

        main.add_widget(row)
        main.add_widget(BoxLayout(size_hint_y=1))

        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8),
                          padding=[dp(10), dp(4), dp(10), dp(4)])
        btns.add_widget(make_icon_text_button(
            text='Cancel', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(42), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        btns.add_widget(make_icon_text_button(
            text='Apply', icon_name='apply',
            on_press=self.apply_values,
            height=dp(42), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_SUCCESS_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(btns)

        self.add_widget(main)

        for i in range(COILS_PER_POLE_MAX_SLOTS):
            if i >= self.poles:
                self.inputs[i].disabled = True
                self.inputs[i].background_color = Theme.INPUT_DISABLED_BG
                self.pole_labels[i].color = Theme.TEXT_MUTED

    def apply_values(self, inst=None):
        values = []
        total = 0
        for i in range(COILS_PER_POLE_MAX_SLOTS):
            if i < self.poles:
                try:
                    v = (int(self.inputs[i].text.strip())
                         if self.inputs[i].text.strip() else 0)
                except Exception:
                    v = 0
                v = max(0, v)
                values.append(v)
                total += v
            else:
                values.append(0)
        if total != self.coils_per_phase:
            show_error('Sum of coils (%d) must equal %d' % (
                total, self.coils_per_phase), 4)
            return
        for i in range(0, self.poles, 2):
            for j in range(0, self.poles, 2):
                if i != j and values[i] != values[j]:
                    show_error('Even poles must have equal values', 4)
                    return
        for i in range(1, self.poles, 2):
            for j in range(1, self.poles, 2):
                if i != j and values[i] != values[j]:
                    show_error('Odd poles must have equal values', 4)
                    return

        # Save directly to the project JSON file at ROOT level
        json_manager.set_coils_per_pole_values(values)

        show_success('Coils per pole saved', 2)
        self.dismiss()


def show_coils_per_pole_dialog(poles=4, coils_per_phase=0, existing_values=None):
    CoilsPerPoleDialog(poles=poles, coils_per_phase=coils_per_phase,
                        existing_values=existing_values).open()