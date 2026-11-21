"""
================================================================================
File: app/app_orientation.py
Purpose: Orientation tracking + resize handling.
Version: 0.1.3
================================================================================
"""

from kivy.core.window import Window
from kivy.clock import Clock


def update_orientation(app):
    app.current_orientation = (
        "Landscape" if Window.width > Window.height else "Portrait"
    )


def on_window_resize(app, window, width, height):
    previous_orientation = getattr(app, "current_orientation", None)
    update_orientation(app)
    if previous_orientation != app.current_orientation:
        rebuild_ui(app)
    Clock.schedule_once(lambda dt: reposition_zoom_panel(app), 0.1)


def rebuild_ui(app):
    connection_panel_was_visible = app.connection_panel is not None
    edit_panel_was_visible = app.edit_diagram_panel is not None

    app.main_layout.clear_widgets()
    from app.app_main_ui import build_main_ui
    build_main_ui(app)

    if connection_panel_was_visible:
        from app.app_connection import open_connection_panel
        open_connection_panel(app)

    if edit_panel_was_visible:
        from app.app_edit_diagram import handle_edit_diagram
        handle_edit_diagram(app)

    if hasattr(app, "winding_widget"):
        app.winding_widget.refresh_paper_dimensions()

    from app.app_info_labels import update_info_labels
    update_info_labels(app)