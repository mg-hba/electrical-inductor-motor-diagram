"""
================================================================================
File: app/main_app.py
Purpose: MotorWindingApp (coordinator). Delegates to app submodules.
Version: 0.1.3
================================================================================
"""

import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from managers.json_manager import json_manager
from managers.docs_manager import DocsManager
from ui.theme import Theme

from app.app_orientation import (
    update_orientation, on_window_resize,
)
from app.app_zoom import build_zoom_panel
from app.app_main_ui import build_main_ui
from app.app_menu import open_project_setup


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")


Window.clearcolor = Theme.MAIN_BG


class MotorWindingApp(App):

    def build(self):
        self.current_winding_type = "two_layer"
        self.project_loaded = False
        self.connection_panel = None
        self.zoom_panel = None
        self.edit_diagram_panel = None
        self._saved_snapshot = None
        self._sync_clock = None
        self.docs_manager = DocsManager(DOCS_DIR)

        update_orientation(self)
        Window.bind(on_resize=lambda w, h, width, height:
                    on_window_resize(self, w, h, width, height))

        self.root = FloatLayout()
        self.main_layout = BoxLayout(
            orientation="vertical", spacing=dp(4),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            size_hint=(1, 1), pos_hint={"x": 0, "y": 0}
        )
        self.root.add_widget(self.main_layout)

        build_main_ui(self)

        Clock.schedule_once(lambda dt: build_zoom_panel(self), 0.1)
        Clock.schedule_once(lambda dt: open_project_setup(self), 0.5)
        return self.root