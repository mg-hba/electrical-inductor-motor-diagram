"""
================================================================================
File: app/app_connection.py
Purpose: Connection panel open/close + sync.
Version: 0.1.4
================================================================================
"""

from kivy.clock import Clock

from managers.json_manager import json_manager
from ui.connection_panel import FloatingConnectionPanel


def handle_connection_toggle(app):
    if not hasattr(app, "winding_widget"):
        return
    if app.edit_diagram_panel is not None:
        return
    if app.connection_panel is not None:
        close_connection_panel(app)
    else:
        open_connection_panel(app)


def open_connection_panel(app):
    widget = app.winding_widget
    app._saved_snapshot = widget.connection.snapshot()

    if not widget.connection.wire_points:
        widget.connection.load_from_json(json_manager)

    widget.connection.set_active(True)

    from app.app_connection_actions import (
        handle_connection_pull,
        handle_connection_connect,
        handle_connection_delete,
        handle_connection_phase_start,
        handle_connection_phase_end,
        handle_connection_clear,
        handle_connection_crossing,
        handle_connection_pencil,
        handle_connection_select_box,
        handle_connection_back,
        handle_connection_redo,
        handle_connection_reset,
    )
    from app.app_connection_actions import (
        apply_connection, cancel_connection,
    )

    app.connection_panel = FloatingConnectionPanel(
        on_pull=lambda: handle_connection_pull(app),
        on_connect=lambda: handle_connection_connect(app),
        on_delete=lambda: handle_connection_delete(app),
        on_phase_start=lambda: handle_connection_phase_start(app),
        on_phase_end=lambda: handle_connection_phase_end(app),
        on_clear=lambda: handle_connection_clear(app),
        on_crossing=lambda: handle_connection_crossing(app),
        on_pencil=lambda: handle_connection_pencil(app),
        on_select_box=lambda: handle_connection_select_box(app),
        on_back=lambda: handle_connection_back(app),
        on_redo=lambda: handle_connection_redo(app),
        on_reset=lambda: handle_connection_reset(app),
        on_apply=lambda: apply_connection(app),
        on_cancel=lambda: cancel_connection(app),
    )
    app.root.add_widget(app.connection_panel)

    from app.app_edit_diagram import set_buttons_enabled
    set_buttons_enabled(app, False)

    app._sync_clock = Clock.schedule_interval(
        lambda dt: sync_selected_label(app), 0.3
    )
    widget._rebuild_all()
    sync_history_buttons(app)


def close_connection_panel(app):
    if app._sync_clock is not None:
        app._sync_clock.cancel()
        app._sync_clock = None
    if app.connection_panel is not None:
        if app.connection_panel.parent is not None:
            app.root.remove_widget(app.connection_panel)
        app.connection_panel = None
    if hasattr(app, "winding_widget"):
        app.winding_widget.connection.set_active(False)
    from app.app_edit_diagram import set_buttons_enabled
    set_buttons_enabled(app, True)


def sync_selected_label(app):
    if app.connection_panel is None:
        return
    widget = app.winding_widget
    names = widget.connection.get_selected_names()
    app.connection_panel.set_selected_text(names)
    sync_history_buttons(app)


def sync_history_buttons(app):
    if app.connection_panel is None:
        return
    widget = app.winding_widget
    app.connection_panel.update_history_buttons(
        widget.connection.can_undo(),
        widget.connection.can_redo()
    )


def refresh_connection_ui(app):
    """
    Central helper: rebuild the winding widget and refresh the
    selection label. Replaces the repeating pattern:
        widget._rebuild_all()
        sync_selected_label(app)
    """
    if not hasattr(app, "winding_widget"):
        return
    app.winding_widget._rebuild_all()
    sync_selected_label(app)