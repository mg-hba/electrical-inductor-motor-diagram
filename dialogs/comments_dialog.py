"""
================================================================================
File: dialogs/comments_dialog.py
Purpose: Multiline comments editor with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class CommentsDialog(Popup):

    def __init__(self, initial_text='', on_apply=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.9, 0.5)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False
        self.on_apply = on_apply
        self.initial_text = initial_text
        self.build_ui()

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        header = BoxLayout(size_hint_y=None, height=dp(44),
                            spacing=dp(6),
                            padding=[dp(10), dp(4), dp(10), dp(4)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            Rectangle(pos=header.pos, size=header.size)
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(32), dp(30)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='COMMENTS' + get_version_suffix(),
                                 font_size='13sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1, halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(32)))
        main.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=dp(6),
                            padding=[dp(10), dp(8), dp(10), dp(8)])
        self.text_input = TextInput(
            text=self.initial_text, multiline=True, font_size='14sp',
            background_color=Theme.INPUT_BG,
            foreground_color=Theme.INPUT_TEXT
        )
        content.add_widget(self.text_input)
        main.add_widget(content)

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
            on_press=self._apply,
            height=dp(42), icon_size=dp(20), font_size='13sp',
            bg_color=Theme.BUTTON_SUCCESS_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(btns)

        self.add_widget(main)

    def _apply(self, inst=None):
        if self.on_apply:
            self.on_apply(self.text_input.text)
        self.dismiss()


def show_comments_dialog(initial_text='', on_apply=None):
    CommentsDialog(initial_text=initial_text, on_apply=on_apply).open()