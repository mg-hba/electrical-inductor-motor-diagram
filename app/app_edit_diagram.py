"""
================================================================================
File: app/app_edit_diagram.py
Purpose: Edit Diagram mode (panel + apply/reset/cancel).
Version: 0.1.3
================================================================================
"""

from managers.json_manager import json_manager
from ui.notifications import show_error
from ui.edit_diagram_panel import EditDiagramPanel


def handle_edit_diagram(app):
    if not hasattr(app, "winding_widget"):
        return
    if not json_manager.project_data:
        show_error("Please load a project first", 3)
        return
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return

    app.winding_widget.enter_edit_mode()

    app.edit_diagram_panel = EditDiagramPanel(
        on_apply=lambda: apply_edit_shifts(app),
        on_reset=lambda: reset_edit_shifts(app),
        on_cancel=lambda: cancel_edit_shifts(app),
    )
    app.root.add_widget(app.edit_diagram_panel)
    set_buttons_enabled(app, False)


def apply_edit_shifts(app):
    if not hasattr(app, "winding_widget"):
        return
    app.winding_widget.apply_edit_shifts()
    close_edit_diagram_panel(app)


def reset_edit_shifts(app):
    if not hasattr(app, "winding_widget"):
        return
    app.winding_widget.reset_edit_shifts()


def cancel_edit_shifts(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    widget.edit_current_main_shift = json_manager.get_main_diagram_shift_y()
    widget.edit_current_phase_shift = json_manager.get_phase_diagram_shift_y()
    widget.exit_edit_mode()
    close_edit_diagram_panel(app)


def close_edit_diagram_panel(app):
    if app.edit_diagram_panel is not None:
        if app.edit_diagram_panel.parent is not None:
            app.root.remove_widget(app.edit_diagram_panel)
        app.edit_diagram_panel = None
    set_buttons_enabled(app, True)


def set_buttons_enabled(app, enabled):
    for button in [app.btn_draw, app.btn_reset, app.btn_rotate]:
        button.disabled = not enabled
    if hasattr(app, "menu_btn"):
        app.menu_btn.disabled = not enabled