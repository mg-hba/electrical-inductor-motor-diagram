"""
================================================================================
File: main0.1.3.py
Purpose: Entry point.
Version: 0.1.3
================================================================================
"""

import os
from kivy.config import Config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

_app_icon = os.path.join(ASSETS_DIR, "app_icon.png")
if os.path.exists(_app_icon):
    Config.set("graphics", "window_icon", _app_icon)

from app.main_app import MotorWindingApp


if __name__ == "__main__":
    MotorWindingApp().run()
