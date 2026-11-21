"""
================================================================================
File: dialogs/log_manager.py
Purpose: Log Manager dialog with icon+text buttons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from managers.debug_logger import debug_logger, LogCategory
from ui.theme import Theme
from ui.icon_button import make_icon_button, make_icon_text_button
from version import get_version_suffix


class LogManagerPopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.88, 0.85)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False
        self.checkboxes = {}
        self.build_ui()
        self.load_current_settings()

    def load_current_settings(self):
        enabled = debug_logger.get_enabled_categories()
        for cat, cb in self.checkboxes.items():
            cb.active = enabled.get(cat, True)

    def build_ui(self):
        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*Theme.DIALOG_BG)
            bg = Rectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(bg, 'pos', i.pos),
                  size=lambda i, v: setattr(bg, 'size', i.size))

        header = BoxLayout(size_hint_y=None, height=dp(50),
                            spacing=dp(6),
                            padding=[dp(15), dp(8), dp(15), dp(8)])
        with header.canvas.before:
            Color(*Theme.HEADER_BG)
            hbg = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, v: setattr(hbg, 'pos', i.pos),
                    size=lambda i, v: setattr(hbg, 'size', i.size))
        header.add_widget(make_icon_button(
            text='X', icon_name='close',
            on_press=lambda x: self.dismiss(),
            size=(dp(40), dp(34)),
            bg_color=Theme.BUTTON_PRIMARY_BG,
        ))
        header.add_widget(Label(text='LOG MANAGER' + get_version_suffix(),
                                 font_size='16sp', bold=True,
                                 color=Theme.HEADER_TEXT,
                                 size_hint_x=1, halign='center', valign='middle'))
        header.add_widget(Label(size_hint_x=None, width=dp(40)))
        main.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=dp(10),
                            padding=[dp(20), dp(15), dp(20), dp(15)],
                            size_hint=(1, 0.85))
        content.add_widget(Label(text='Select log categories to enable:',
                                   font_size='14sp',
                                   color=Theme.TEXT_SECONDARY,
                                   size_hint_y=None, height=dp(30)))

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None,
                           padding=[dp(10), dp(5), dp(10), dp(5)])
        grid.bind(minimum_height=grid.setter('height'))
        cats = [
            (LogCategory.SYSTEM, "System", "Application core events"),
            (LogCategory.ERROR, "Errors", "Errors and exceptions"),
            (LogCategory.TOUCH, "Touch", "Touch, zoom and pan events"),
            (LogCategory.DRAW, "Drawing", "Grid and coils drawing"),
            (LogCategory.EXPORT, "Export", "Export operations"),
            (LogCategory.CONFIG, "Config", "JSON config read/write"),
            (LogCategory.PAPER, "Paper", "Paper size and orientation"),
            (LogCategory.TABLE, "Table", "Info table drawing"),
            (LogCategory.PERFORMANCE, "Performance", "Redraw time metrics"),
        ]
        for cat, name, desc in cats:
            row = BoxLayout(orientation='horizontal', spacing=dp(10),
                             size_hint_y=None, height=dp(50))
            cb = CheckBox(size_hint_x=0.1, active=True)
            self.checkboxes[cat.value] = cb
            ll = BoxLayout(orientation='vertical', size_hint_x=0.9)
            ll.add_widget(Label(text=name, font_size='14sp', bold=True,
                                 color=Theme.TEXT_PRIMARY,
                                 size_hint_y=0.5,
                                 halign='left', valign='middle'))
            ll.add_widget(Label(text=desc, font_size='11sp',
                                 color=Theme.TEXT_MUTED,
                                 size_hint_y=0.5,
                                 halign='left', valign='middle'))
            row.add_widget(cb)
            row.add_widget(ll)
            grid.add_widget(row)
        scroll.add_widget(grid)
        content.add_widget(scroll)
        
        content.add_widget(Label(text='Log file: ' +
                                    debug_logger.get_log_file_path(),
                                   font_size='11sp', color=Theme.TEXT_MUTED,
                                   size_hint_y=None, height=dp(20)))
        open_log_btn = make_icon_text_button(
            text='Open Log File', icon_name='open_file',
            on_press=lambda x: None,
            height=dp(42), icon_size=dp(22), font_size='13sp',
            bg_color=Theme.BUTTON_NEUTRAL_BG,
            fg_color=[1, 1, 1, 1],
        )
        open_log_btn.disabled = True
        content.add_widget(open_log_btn)
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

    def save_and_close(self, inst=None):
        for cat, cb in self.checkboxes.items():
            debug_logger.set_category_enabled(cat, cb.active)
        self.dismiss()


def show_log_manager():
    LogManagerPopup().open()