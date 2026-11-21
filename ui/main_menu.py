"""
================================================================================
File: ui/main_menu.py
Purpose: Dropdown menu with icon+text rows (entire row clickable).
         v0.1.4: Adds standalone project page entries.
Version: 0.1.4
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

from ui.icon_button import make_icon_text_button


class MainMenu(Popup):

    def __init__(self, anchor_widget=None, **callbacks):
        super().__init__()
        self.title = ''
        self.size_hint = (None, None)
        self.background_color = [0, 0, 0, 0.15]
        self.auto_dismiss = True

        self._callbacks = callbacks
        self.size = (dp(280), dp(640))

        if anchor_widget is not None:
            anchor_pos = anchor_widget.to_window(anchor_widget.x,
                                                  anchor_widget.y)
            self.pos = (anchor_pos[0], anchor_pos[1] - self.height)
        else:
            self.pos = (dp(10), Window.height - self.height - dp(50))

        if self.pos[0] + self.size[0] > Window.width:
            self.pos = (Window.width - self.size[0] - dp(4), self.pos[1])
        if self.pos[1] < 0:
            self.pos = (self.pos[0], dp(4))

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        with main_layout.canvas.before:
            Color(0.97, 0.97, 0.97, 1)
            self._bg = Rectangle(pos=main_layout.pos,
                                   size=main_layout.size)
        main_layout.bind(
            pos=lambda i, v: setattr(self._bg, 'pos', i.pos),
            size=lambda i, v: setattr(self._bg, 'size', i.size)
        )

        items = [
            
            ('New / Open Project', 'new_open', 'new_open', False),
            ('Diagnose', 'settings', 'diagnose', False),
            ('Debug Overlay', 'settings', 'debug_overlay', False),
            ('SEP', None, None, False),
            ('Project Info', 'structure', 'project_info', False),
            ('Motor Settings', 'settings', 'motor_settings', False),
            ('Paper Settings', 'span_chained', 'paper_settings', False),
            ('Physical Settings', 'setup', 'physical_settings', False),
            ('SEP', None, None, False),
            ('Draw Style', 'draw_style', 'draw_style', False),
            ('Edit Diagram', 'draw', 'edit_diagram', False),
            ('Add Pattern', 'add_pattern', 'add_pattern', False),
            ('Connection Mode', 'connection', 'connection', False),
            ('SEP', None, None, False),
            ('Export', 'export', 'export', False),
            ('Import', 'import', 'import', False),
            ('SEP', None, None, False),
            ('Settings', 'settings', 'settings', False),
            ('Log Manager', 'log_manager', 'log_manager', False),
            ('SEP', None, None, False),
            ('Motor Info', 'motor_info', 'motor_info', False),
            ('App Info', 'app_info', 'app_info', False),
            ('SEP', None, None, False),
            ('Exit', 'exit', 'exit', True),
        ]

        for label_text, icon_name, key, danger in items:
            if key is None:
                separator = Label(size_hint_y=None, height=dp(6))
                with separator.canvas.before:
                    Color(0.85, 0.85, 0.85, 1)
                    separator._rect = Rectangle(pos=separator.pos,
                                                  size=separator.size)
                separator.bind(
                    pos=lambda i, v: setattr(i._rect, 'pos', i.pos),
                    size=lambda i, v: setattr(i._rect, 'size', i.size)
                )
                main_layout.add_widget(separator)
                continue

            fg_color = [0.7, 0.2, 0.2, 1] if danger else [0.1, 0.1, 0.1, 1]
            main_layout.add_widget(make_icon_text_button(
                text=label_text, icon_name=icon_name,
                on_press=lambda x, k=key: self._trigger(k),
                height=dp(36),
                icon_size=dp(22),
                font_size='12sp',
                fg_color=fg_color,
            ))

        self.add_widget(main_layout)

    def _trigger(self, key):
        callback = self._callbacks.get(key)
        self.dismiss()
        if callback:
            Clock.schedule_once(lambda dt: callback(), 0.05)


def show_main_menu(anchor_widget=None, **callbacks):
    menu = MainMenu(anchor_widget=anchor_widget, **callbacks)
    menu.open()
    return menu
