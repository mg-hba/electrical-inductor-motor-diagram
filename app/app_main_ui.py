"""
================================================================================
File: app/app_main_ui.py
Purpose: Main layout: header, info labels, buttons row, diagram widget.
Version: 0.1.3
================================================================================
"""

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from managers.json_manager import json_manager
from ui.theme import Theme
from ui.icon_button import make_icon_button

from version import get_version_suffix


ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
)


class LogoButton(ButtonBehavior, Image):
    pass


def build_main_ui(app):
    header = BoxLayout(
        size_hint_y=None, height=dp(44),
        spacing=dp(4), padding=[dp(6), dp(6), dp(6), dp(6)]
    )
    with header.canvas.before:
        Color(*Theme.HEADER_BG)
        app.header_bg_rect = Rectangle(pos=header.pos, size=header.size)
    header.bind(
        pos=lambda i, v: setattr(app.header_bg_rect, "pos", i.pos),
        size=lambda i, v: setattr(app.header_bg_rect, "size", i.size)
    )

    app.menu_btn = make_icon_button(
        text="Menu", icon_name="menu",
        on_press=lambda x: open_main_menu(app),
        size=(dp(80), dp(32)),
    )
    header.add_widget(app.menu_btn)

    title_label = Label(
        text="Motor Winding Diagram" + get_version_suffix(),
        font_size="12sp", bold=True,
        color=Theme.HEADER_TEXT, size_hint_x=1,
        halign="center", valign="middle"
    )
    header.add_widget(title_label)

    close_btn = make_icon_button(
        text="X", icon_name="close",
        on_press=lambda x: close_app(app),
        size=(dp(40), dp(32)),
    )
    header.add_widget(close_btn)
    app.main_layout.add_widget(header)

    info_container = BoxLayout(
        orientation="vertical", spacing=dp(2),
        size_hint_y=None, height=dp(48),
        padding=[dp(8), dp(4), dp(8), dp(4)]
    )
    with info_container.canvas.before:
        Color(*Theme.SECTION_BG)
        app.info_bg = Rectangle(pos=info_container.pos,
                                 size=info_container.size)
    info_container.bind(
        pos=lambda i, v: setattr(app.info_bg, "pos", i.pos),
        size=lambda i, v: setattr(app.info_bg, "size", i.size)
    )

    is_portrait = app.current_orientation == "Portrait"
    info_font_size = (
        Theme.FONT_INFO_PORTRAIT if is_portrait
        else Theme.FONT_INFO_LANDSCAPE
    )
    app.info_line1 = Label(
        text="", font_size=info_font_size,
        color=Theme.TEXT_SECONDARY,
        halign="center", valign="middle"
    )
    app.info_line2 = Label(
        text="", font_size=info_font_size,
        color=Theme.TEXT_SECONDARY,
        halign="center", valign="middle"
    )
    info_container.add_widget(app.info_line1)
    info_container.add_widget(app.info_line2)
    app.main_layout.add_widget(info_container)

    buttons_row = BoxLayout(
        orientation="horizontal", spacing=dp(6),
        size_hint_y=None, height=dp(60)
    )

    logo_path = os.path.join(ASSETS_DIR, "zarin.png")
    if os.path.exists(logo_path):
        app.logo_btn = LogoButton(
            source=logo_path,
            size_hint=(None, 1),
            width=dp(66),
            allow_stretch=True,
            keep_ratio=True
        )
        app.logo_btn.bind(on_press=lambda x: open_app_info(app))
        buttons_row.add_widget(app.logo_btn)

    from app.app_actions import handle_draw, handle_reset, handle_rotate

    app.btn_draw = make_icon_button(
        text="Draw", icon_name="draw",
        on_press=lambda x: handle_draw(app, x),
        size=(dp(80), dp(52)),
        font_size="16sp",
    )
    app.btn_reset = make_icon_button(
        text="Reset", icon_name="reset",
        on_press=lambda x: handle_reset(app, x),
        size=(dp(80), dp(52)),
        font_size="16sp",
    )
    app.btn_rotate = make_icon_button(
        text="Rotate", icon_name="rotate",
        on_press=lambda x: handle_rotate(app, x),
        size=(dp(80), dp(52)),
        font_size="16sp",
    )

    buttons_row.add_widget(app.btn_draw)
    buttons_row.add_widget(app.btn_reset)
    buttons_row.add_widget(app.btn_rotate)

    app.main_layout.add_widget(buttons_row)

    from app.app_diagram_widget import create_diagram_widget
    app.winding_widget = create_diagram_widget(app)
    app.main_layout.add_widget(app.winding_widget)

    Clock.schedule_once(lambda dt: initial_state(app), 0.3)


def initial_state(app):
    app.winding_widget.clear_diagram()
    from app.app_info_labels import update_info_labels
    update_info_labels(app)


def close_app(app, *args):
    from managers.debug_logger import debug_logger
    from kivy.core.window import Window
    debug_logger.close()
    Window.close()


def open_main_menu(app):
    from app.app_menu import show_main_menu_for_app
    show_main_menu_for_app(app)


def open_app_info(app, *args):
    from app.app_app_info import open_app_info_dialog
    open_app_info_dialog(app)