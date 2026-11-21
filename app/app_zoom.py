"""
================================================================================
File: app/app_zoom.py
Purpose: Zoom panel + zoom actions.
Version: 0.1.3
================================================================================
"""

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

from ui.zoom_panel import FloatingZoomPanel


def build_zoom_panel(app):
    if app.zoom_panel is not None:
        reposition_zoom_panel(app)
        return
    app.zoom_panel = FloatingZoomPanel(
        on_zoom_all=lambda: handle_zoom_all(app),
        on_zoom_in=lambda: handle_zoom_in(app),
        on_zoom_out=lambda: handle_zoom_out(app),
        on_zoom_back=lambda: handle_zoom_back(app),
        on_zoom_redo=lambda: handle_zoom_redo(app),
        on_zoom_reset=lambda: handle_zoom_reset(app),
        on_zoom_box=lambda: handle_zoom_box(app),
    )
    app.root.add_widget(app.zoom_panel)
    Clock.schedule_once(lambda dt: reposition_zoom_panel(app), 0.05)


def reposition_zoom_panel(app):
    if app.zoom_panel is None:
        return
    x = Window.width - app.zoom_panel.width - dp(40)
    y = Window.height - app.zoom_panel.height - dp(250)
    app.zoom_panel.pos = (max(dp(4), x), max(dp(4), y))


def handle_zoom_all(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_all()


def handle_zoom_in(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_in(
            app.winding_widget._get_zoom_anchor()
        )


def handle_zoom_out(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_out(
            app.winding_widget._get_zoom_anchor()
        )


def handle_zoom_back(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_back()


def handle_zoom_redo(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_redo()


def handle_zoom_reset(app):
    if hasattr(app, "winding_widget"):
        app.winding_widget.zoom_reset()


def handle_zoom_box(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    active = not widget.is_zoom_box_active()
    widget.zoom_box_activate(active)
    if app.zoom_panel is not None:
        app.zoom_panel.highlight_box_mode(active)