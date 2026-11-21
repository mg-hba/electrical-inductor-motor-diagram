"""
================================================================================
File: dialogs/setup_sections.py
Purpose: UI section builders for Project Setup dialog.
Version: 0.1.1
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme
from managers.json_manager import json_manager

from utils.constants import (
    PROJECT_SETUP_INPUT_HEIGHT,
    PROJECT_SETUP_LABEL_HEIGHT,
    PROJECT_SETUP_LABEL_FONT,
    PROJECT_SETUP_INPUT_FONT,
    PROJECT_SETUP_TITLE_FONT,
    PROJECT_SETUP_SECTION_PADDING,
    UNIT_OPTIONS,
    DEFAULT_UNIT,
)


def get_spinner_colors():
    return {
        'bg': json_manager.get_spinner_bg_color(),
        'text': json_manager.get_spinner_text_color(),
        'height': json_manager.get_spinner_height(),
        'font_size': json_manager.get_spinner_font_size(),
    }


def make_section(title_text):
    section = BoxLayout(orientation='vertical',
                        spacing=dp(0),
                        padding=[dp(5), dp(PROJECT_SETUP_SECTION_PADDING),
                                 dp(5), dp(PROJECT_SETUP_SECTION_PADDING)],
                        size_hint_y=None)
    with section.canvas.before:
        Color(*Theme.SECTION_BG)
        bg = Rectangle(pos=section.pos, size=section.size)
    section.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                 size=lambda i, v: setattr(bg, 'size', i.size))
    section.add_widget(Label(text=title_text,
                              font_size=PROJECT_SETUP_TITLE_FONT, bold=True,
                              color=Theme.TEXT_SECONDARY,
                              size_hint_y=None,
                              height=dp(PROJECT_SETUP_LABEL_HEIGHT),
                              halign='center', valign='middle'))
    return section


def make_divider():
    d = Label(size_hint_y=None, height=dp(4))
    with d.canvas.before:
        Color(*Theme.SECTION_DIVIDER_COLOR)
        Rectangle(pos=d.pos, size=d.size)
    d.bind(pos=lambda i, v: i.canvas.before.clear() or
           (i.canvas.before.add(Color(*Theme.SECTION_DIVIDER_COLOR)),
            i.canvas.before.add(Rectangle(pos=i.pos, size=i.size))))
    return d


def make_label(text):
    return Label(text=text,
                  font_size=PROJECT_SETUP_LABEL_FONT,
                  color=Theme.TEXT_PRIMARY,
                  size_hint_y=None,
                  height=dp(PROJECT_SETUP_LABEL_HEIGHT),
                  halign='left', valign='middle')


def make_input(hint='', input_filter=None, disabled=False):
    kwargs = {
        'text': '',
        'multiline': False,
        'font_size': PROJECT_SETUP_INPUT_FONT,
        'background_color': Theme.INPUT_BG if not disabled else Theme.INPUT_DISABLED_BG,
        'foreground_color': Theme.INPUT_TEXT,
        'size_hint_y': None,
        'height': dp(PROJECT_SETUP_INPUT_HEIGHT),
        'hint_text': hint,
        'disabled': disabled,
    }
    if input_filter:
        kwargs['input_filter'] = input_filter
    return TextInput(**kwargs)


def make_spinner(text='', values=(), register=None):
    colors = get_spinner_colors()
    sp = Spinner(text=text, values=values,
                  font_size=PROJECT_SETUP_INPUT_FONT,
                  background_color=colors['bg'],
                  color=colors['text'],
                  size_hint_y=None,
                  height=dp(PROJECT_SETUP_INPUT_HEIGHT))
    if register is not None:
        register.append(sp)
    return sp