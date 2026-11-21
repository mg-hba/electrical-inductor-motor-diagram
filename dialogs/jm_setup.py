"""
================================================================================
File: dialogs/jm_setup.py
Purpose: JSON Manager setup dialog with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class JMSetupPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.94, 0.88)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.bg_color = json_manager.get_spinner_bg_color().copy()
        self.text_color = json_manager.get_spinner_text_color().copy()
        self.spinner_height = json_manager.get_spinner_height()
        self.spinner_font_size = json_manager.get_spinner_font_size()

        self.on_save_callback = None
        self.build_ui()

    def set_on_save_callback(self, cb):
        self.on_save_callback = cb

    def create_color_slider(self, parent, label, channel, initial, is_bg=True):
        row = BoxLayout(orientation='horizontal', size_hint_y=None,
                        height=dp(34), spacing=dp(6))
        row.add_widget(Label(text=label, font_size='11sp',
                              color=Theme.TEXT_PRIMARY, size_hint_x=0.12,
                              halign='right', valign='middle'))
        minus_btn = make_icon_button(
            text='-', icon_name='minus',
            on_press=lambda x: setattr(slider, 'value',
                                        max(0, slider.value - 0.05)),
            size=(dp(28), dp(28)),
            bg_color=Theme.BUTTON_NEUTRAL_BG,
        )
        slider = Slider(min=0, max=1, value=initial, size_hint_x=0.56,
                         height=20, size_hint_y=None)
        plus_btn = make_icon_button(
            text='+', icon_name='plus',
            on_press=lambda x: setattr(slider, 'value',
                                        min(1, slider.value + 0.05)),
            size=(dp(28), dp(28)),
            bg_color=Theme.BUTTON_NEUTRAL_BG,
        )
        value_lbl = Label(text='%.2f' % initial, font_size='10sp',
                           color=Theme.TEXT_PRIMARY, size_hint_x=0.10,
                           halign='center', valign='middle')
        row.add_widget(minus_btn)
        row.add_widget(slider)
        row.add_widget(plus_btn)
        row.add_widget(value_lbl)

        def on_change(inst, val):
            value_lbl.text = '%.2f' % val
            idx = {'r': 0, 'g': 1, 'b': 2, 'a': 3}[channel]
            if is_bg:
                self.bg_color[idx] = val
            else:
                self.text_color[idx] = val
            self.update_preview()

        slider.bind(value=on_change)
        parent.add_widget(row)

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        header = BoxLayout(size_hint_y=None, height=dp(50),
                            spacing=dp(6),
                            padding=[dp(12), dp(8), dp(12), dp(8)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(34), dp(34)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='JSON MANAGER SETUP' + get_version_suffix(),
                                 font_size='15sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1, halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(34)))
        main.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=dp(10),
                            padding=[dp(15), dp(12), dp(15), dp(12)],
                            size_hint=(1, 0.85))
        preview_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                 height=dp(80),
                                 padding=[dp(10), dp(5), dp(10), dp(5)])
        with preview_box.canvas.before:
            Color(*Theme.SECTION_BG)
            Rectangle(pos=preview_box.pos, size=preview_box.size)
        preview_box.add_widget(Label(text='Preview:', font_size='12sp',
                                       bold=True, color=Theme.TEXT_SECONDARY,
                                       size_hint_y=0.3,
                                       halign='left', valign='middle'))
        self.spinner_preview = Spinner(
            text='1', values=('1', '2'),
            font_size=str(self.spinner_font_size) + 'sp',
            background_color=self.bg_color, color=self.text_color,
            size_hint_y=None, height=dp(self.spinner_height)
        )
        preview_box.add_widget(self.spinner_preview)
        content.add_widget(preview_box)

        sliders_box = BoxLayout(orientation='vertical', spacing=dp(2))
        sliders_box.add_widget(Label(text='--- Background Colors ---',
                                       font_size='10sp',
                                       color=Theme.TEXT_MUTED,
                                       size_hint_y=None, height=dp(18)))
        for ch, idx in [('R:', 0), ('G:', 1), ('B:', 2), ('A:', 3)]:
            self.create_color_slider(sliders_box, ch, ch[0].lower(),
                                      self.bg_color[idx], True)
        sliders_box.add_widget(Label(text='--- Text Colors ---',
                                       font_size='10sp',
                                       color=Theme.TEXT_MUTED,
                                       size_hint_y=None, height=dp(18)))
        for ch, idx in [('R:', 0), ('G:', 1), ('B:', 2), ('A:', 3)]:
            self.create_color_slider(sliders_box, ch, ch[0].lower(),
                                      self.text_color[idx], False)
        content.add_widget(sliders_box)

        size_box = BoxLayout(orientation='horizontal', spacing=dp(10),
                              size_hint_y=None, height=dp(50))
        h_col = BoxLayout(orientation='vertical', size_hint_x=0.5)
        h_col.add_widget(Label(text='Height:', font_size='11sp',
                                 color=Theme.TEXT_PRIMARY,
                                 size_hint_y=None, height=dp(16)))
        self.height_slider = Slider(min=30, max=80, value=self.spinner_height,
                                      size_hint_y=None, height=dp(24))
        self.height_slider.bind(value=self.on_height_change)
        h_col.add_widget(self.height_slider)
        f_col = BoxLayout(orientation='vertical', size_hint_x=0.5)
        f_col.add_widget(Label(text='Font Size:', font_size='11sp',
                                 color=Theme.TEXT_PRIMARY,
                                 size_hint_y=None, height=dp(16)))
        self.font_slider = Slider(min=10, max=30, value=self.spinner_font_size,
                                    size_hint_y=None, height=dp(24))
        self.font_slider.bind(value=self.on_font_change)
        f_col.add_widget(self.font_slider)
        size_box.add_widget(h_col)
        size_box.add_widget(f_col)
        content.add_widget(size_box)
        main.add_widget(content)

        buttons = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12),
                             padding=[dp(15), dp(8), dp(15), dp(8)])
        buttons.add_widget(make_icon_text_button(
            text='SAVE', icon_name='save',
            on_press=self.save_and_close,
            height=dp(44), icon_size=dp(22), font_size='15sp',
            bg_color=Theme.BUTTON_PRIMARY_BG,
            fg_color=[1, 1, 1, 1],
        ))
        buttons.add_widget(make_icon_text_button(
            text='CANCEL', icon_name='cancel',
            on_press=lambda x: self.dismiss(),
            height=dp(44), icon_size=dp(22), font_size='15sp',
            bg_color=Theme.BUTTON_DANGER_BG,
            fg_color=[1, 1, 1, 1],
        ))
        main.add_widget(buttons)

        self.add_widget(main)

    def on_height_change(self, inst, val):
        self.spinner_height = int(val)
        self.spinner_preview.height = dp(self.spinner_height)

    def on_font_change(self, inst, val):
        self.spinner_font_size = int(val)
        self.spinner_preview.font_size = str(self.spinner_font_size) + 'sp'

    def update_preview(self):
        self.spinner_preview.background_color = self.bg_color
        self.spinner_preview.color = self.text_color

    def save_and_close(self, inst=None):
        json_manager.set_spinner_bg_color(self.bg_color)
        json_manager.set_spinner_text_color(self.text_color)
        json_manager.set_spinner_height(self.spinner_height)
        json_manager.set_spinner_font_size(self.spinner_font_size)
        if self.on_save_callback:
            self.on_save_callback()
        self.dismiss()


def show_jm_setup(on_save_callback=None):
    popup = JMSetupPopup()
    if on_save_callback:
        popup.set_on_save_callback(on_save_callback)
    popup.open()
    return popup