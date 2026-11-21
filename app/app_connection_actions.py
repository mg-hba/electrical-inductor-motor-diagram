"""
================================================================================
File: app/app_connection_actions.py
Purpose: Connection handlers (pull/connect/delete/crossing/phase/...).
Version: 0.1.4
================================================================================
"""

import os

from managers.json_manager import json_manager
from ui.notifications import show_error
from ui.conflict_dialog import ConflictDialog


# ============================================================
# ================== HELPERS =================================
# ============================================================

def _refresh(app):
    """Rebuild diagram + sync selection label."""
    from app.app_connection import refresh_connection_ui
    refresh_connection_ui(app)


def _apply_conflicts(app, conflicts, action):
    """Apply a batch of conflict resolutions and refresh once."""
    widget = app.winding_widget
    for conflict in conflicts:
        widget.connection.apply_conflict_resolution(conflict, action)
    _refresh(app)


# ============================================================
# ================== PULL ====================================
# ============================================================

def handle_connection_pull(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection
    step = (
        app.connection_panel.get_pull_step()
        if app.connection_panel else 1
    )

    if connection.delete_mode:
        if connection.shrink_selected_lines(step):
            _refresh(app)
        return

    result = connection.pull_selected(step)

    if result is False:
        error = connection.get_last_error()
        if error:
            show_error(error, 3)
        return

    if isinstance(result, list) and result:
        show_conflicts_single(app, result, connection)
        return

    if result:
        _refresh(app)


def show_conflicts_single(app, conflicts, connection):
    ConflictDialog(
        on_connect=lambda: _apply_conflicts(app, conflicts, "connect"),
        on_pass_over=lambda: _apply_conflicts(app, conflicts, "pass_over"),
        on_stop_before=lambda: _apply_conflicts(app, conflicts, "stop_before"),
    ).open()


# ============================================================
# ================== CONNECT / DELETE ========================
# ============================================================

def handle_connection_connect(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    result = widget.connection.connect_selected()
    if result is False:
        error = widget.connection.get_last_error()
        if error:
            show_error(error, 3)
        return
    _refresh(app)


def handle_connection_delete(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection

    if connection.delete_mode:
        connection.set_delete_mode(False)
        connection.set_group_clear_mode(False)
        widget._rebuild_all()
        if app.connection_panel is not None:
            app.connection_panel.highlight_delete_mode(False)
            app.connection_panel.set_group_clear_active(False)
        return

    if connection.selection.has_any():
        if connection.any_pending_delete():
            connection.delete_all_pending()
        else:
            connection.mark_all_selected_as_delete()
        _refresh(app)
        return

    connection.set_delete_mode(True)
    widget._rebuild_all()
    if app.connection_panel is not None:
        app.connection_panel.highlight_delete_mode(True)


# ============================================================
# ================== CROSSING ================================
# ============================================================

def handle_connection_crossing(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection
    if len(connection.selection.line_ids) >= 2:
        connection.apply_crossing()
        _refresh(app)
    else:
        new_state = not connection.crossing_mode
        connection.set_crossing_mode(new_state)
        if app.connection_panel is not None:
            app.connection_panel.highlight_crossing_mode(new_state)


# ============================================================
# ================== PHASE R / U =============================
# ============================================================

def _handle_phase(app, group, panel_setter_name):
    """
    Unified handler for phase R/U buttons.
    `group` is 'R' or 'U'.
    `panel_setter_name` is 'set_R_active' or 'set_U_active'.
    """
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection
    panel = app.connection_panel

    def _clear_ui_flags():
        connection.set_group_clear_mode(False)
        connection.set_delete_mode(False)
        if panel is not None:
            panel.highlight_delete_mode(False)
            panel.set_group_clear_active(False)
            getattr(panel, panel_setter_name)(False)

    if connection.delete_mode and connection.group_clear_mode:
        if connection.clear_group_from_selection(group):
            _refresh(app)
        _clear_ui_flags()
        return

    if connection.delete_mode:
        connection.set_group_clear_mode(True)
        if panel is not None:
            panel.set_group_clear_active(True)
            getattr(panel, panel_setter_name)(True)

        if connection.selection.has_any():
            if connection.clear_group_from_selection(group):
                _refresh(app)
            _clear_ui_flags()
        return

    if connection.set_group_label(group):
        _refresh(app)
        return

    if group == "R":
        result = connection.set_group_R()
    else:
        result = connection.set_group_U()

    if result:
        _refresh(app)
    else:
        error = connection.get_last_error()
        if error:
            show_error(error, 2)


def handle_connection_phase_start(app):
    _handle_phase(app, "R", "set_R_active")


def handle_connection_phase_end(app):
    _handle_phase(app, "U", "set_U_active")


# ============================================================
# ================== SELECT ALL ==============================
# ============================================================

def handle_connection_clear(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    widget.connection.toggle_select_all()
    _refresh(app)


# ============================================================
# ================== PENCIL / SELECT BOX =====================
# ============================================================

def handle_connection_pencil(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection
    new_state = not connection.pencil_mode
    connection.set_pencil_mode(new_state)
    if new_state:
        connection.set_select_box_mode(False)
    if app.connection_panel is not None:
        app.connection_panel.highlight_pencil_mode(new_state)
        app.connection_panel.highlight_select_box_mode(False)


def handle_connection_select_box(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    connection = widget.connection
    new_state = not connection.select_box_mode
    connection.set_select_box_mode(new_state)
    if new_state:
        connection.set_pencil_mode(False)
    if app.connection_panel is not None:
        app.connection_panel.highlight_select_box_mode(new_state)
        app.connection_panel.highlight_pencil_mode(False)


# ============================================================
# ================== HISTORY / RESET =========================
# ============================================================

def handle_connection_back(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    if widget.connection.undo():
        _refresh(app)


def handle_connection_redo(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    if widget.connection.redo():
        _refresh(app)


def handle_connection_reset(app):
    if not hasattr(app, "winding_widget"):
        return
    widget = app.winding_widget
    if widget.connection.reset_to_initial():
        _refresh(app)


# ============================================================
# ================== APPLY / CANCEL ==========================
# ============================================================

def apply_connection(app):
    widget = app.winding_widget
    widget.connection.save_to_json(json_manager)
    from app.app_connection import close_connection_panel
    close_connection_panel(app)
    app._saved_snapshot = None

    filepath = json_manager.current_project_file
    if filepath and os.path.exists(filepath):
        json_manager.load_project_data(filepath)

    from app.app_actions import handle_draw
    handle_draw(app, None)


def cancel_connection(app):
    widget = app.winding_widget
    if app._saved_snapshot is not None:
        widget.connection.restore_from_snapshot(app._saved_snapshot)
        widget._rebuild_all()
    from app.app_connection import close_connection_panel
    close_connection_panel(app)
    app._saved_snapshot = None