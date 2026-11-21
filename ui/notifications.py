"""
================================================================================
File: ui/notifications.py
Purpose: Unified notification system with icons.
Version: 0.1.2.0
================================================================================
"""

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from ui.theme import Theme
from ui.icon_button import get_icon_path


class NotificationType:
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    CONFIRM = 'confirm'


_THEME_MAP = {
    NotificationType.INFO: {
        'bg': [0.90, 0.94, 0.98, 1], 'accent': [0.2, 0.5, 0.8, 1],
        'text_color': [0.15, 0.25, 0.4, 1], 'title': 'INFORMATION',
        'icon': 'info',
    },
    NotificationType.SUCCESS: {
        'bg': [0.90, 0.97, 0.91, 1], 'accent': [0.2, 0.6, 0.3, 1],
        'text_color': [0.15, 0.4, 0.2, 1], 'title': 'SUCCESS',
        'icon': 'ok',
    },
    NotificationType.WARNING: {
        'bg': [0.99, 0.96, 0.88, 1], 'accent': [0.85, 0.55, 0.1, 1],
        'text_color': [0.5, 0.35, 0.05, 1], 'title': 'WARNING',
        'icon': 'info',
    },
    NotificationType.ERROR: {
        'bg': [0.99, 0.91, 0.91, 1], 'accent': [0.75, 0.2, 0.2, 1],
        'text_color': [0.55, 0.15, 0.15, 1], 'title': 'ERROR',
        'icon': 'cancel',
    },
    NotificationType.CONFIRM: {
        'bg': [0.94, 0.94, 0.98, 1], 'accent': [0.4, 0.4, 0.7, 1],
        'text_color': [0.25, 0.25, 0.5, 1], 'title': 'CONFIRM',
        'icon': 'info',
    },
}


class NotificationPopup(Popup):

    def __init__(self, message, notif_type=NotificationType.INFO,
                 duration=3, title=None, on_confirm=None, on_cancel=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.85, None)
        self.height = dp(200)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        theme = _THEME_MAP.get(notif_type, _THEME_MAP[NotificationType.INFO])

        main = BoxLayout(orientation='vertical', spacing=0)
        with main.canvas.before:
            Color(*theme['bg'])
            self._main_bg = RoundedRectangle(pos=main.pos, size=main.size,
                                              radius=[12])
        main.bind(pos=self._update_main_bg, size=self._update_main_bg)

        header = BoxLayout(size_hint_y=None, height=dp(42),
                            padding=[dp(15), dp(5), dp(15), dp(5)],
                            spacing=dp(8))
        with header.canvas.before:
            Color(*theme['accent'])
            self._header_bg = RoundedRectangle(pos=header.pos,
                                                size=header.size,
                                                radius=[12, 12, 0, 0])
        header.bind(pos=self._update_header_bg, size=self._update_header_bg)

        # Header icon
        icon_path = get_icon_path(theme['icon'])
        if icon_path:
            header.add_widget(Image(source=icon_path,
                                     size_hint=(None, 1),
                                     width=dp(26),
                                     allow_stretch=True,
                                     keep_ratio=True))
        title_text = title if title else theme['title']
        header.add_widget(Label(text=title_text, font_size='16sp', bold=True,
                                 color=[1, 1, 1, 1], halign='center',
                                 valign='middle'))
        main.add_widget(header)

        # Body: [big icon] [message]
        body = BoxLayout(orientation='horizontal',
                          padding=[dp(20), dp(12), dp(20), dp(12)],
                          spacing=dp(12))
        if icon_path:
            body.add_widget(Image(source=icon_path,
                                    size_hint=(None, 1),
                                    width=dp(48),
                                    allow_stretch=True,
                                    keep_ratio=True))
        body.add_widget(Label(text=message, font_size='15sp',
                                color=theme['text_color'],
                                halign='left', valign='middle'))
        main.add_widget(body)

        if notif_type == NotificationType.CONFIRM:
            btn_box = BoxLayout(size_hint_y=None, height=dp(50),
                                spacing=dp(12),
                                padding=[dp(20), dp(0), dp(20), dp(10)])
            cancel_btn = Button(text='Cancel', font_size='15sp', bold=True,
                                background_color=Theme.BUTTON_NEUTRAL_BG,
                                color=[1, 1, 1, 1], background_normal='')
            cancel_btn.bind(on_press=lambda x: self._handle_cancel(on_cancel))
            confirm_btn = Button(text='Confirm', font_size='15sp', bold=True,
                                 background_color=theme['accent'],
                                 color=[1, 1, 1, 1], background_normal='')
            confirm_btn.bind(on_press=lambda x: self._handle_confirm(on_confirm))
            btn_box.add_widget(cancel_btn)
            btn_box.add_widget(confirm_btn)
            main.add_widget(btn_box)
        else:
            main.add_widget(BoxLayout(size_hint_y=None, height=dp(15)))
            if duration and duration > 0:
                Clock.schedule_once(lambda dt: self.dismiss(), duration)

        self.add_widget(main)

    def _handle_confirm(self, callback):
        self.dismiss()
        if callback:
            callback()

    def _handle_cancel(self, callback):
        self.dismiss()
        if callback:
            callback()

    def _update_main_bg(self, instance, value):
        self._main_bg.pos = instance.pos
        self._main_bg.size = instance.size

    def _update_header_bg(self, instance, value):
        self._header_bg.pos = instance.pos
        self._header_bg.size = instance.size


def show_info(message, duration=3, title=None):
    NotificationPopup(message, NotificationType.INFO, duration, title).open()


def show_success(message, duration=2, title=None):
    NotificationPopup(message, NotificationType.SUCCESS, duration, title).open()


def show_warning(message, duration=4, title=None):
    NotificationPopup(message, NotificationType.WARNING, duration, title).open()


def show_error(message, duration=4, title=None):
    NotificationPopup(message, NotificationType.ERROR, duration, title).open()


def show_confirm(message, on_confirm=None, on_cancel=None, title=None):
    NotificationPopup(message, NotificationType.CONFIRM, duration=0,
                       title=title, on_confirm=on_confirm,
                       on_cancel=on_cancel).open()