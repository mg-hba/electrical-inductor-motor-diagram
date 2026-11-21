"""
================================================================================
File: app/app_actions.py
Purpose: Draw, Reset, Rotate, Export, Motor Info.
Version: 0.1.3
================================================================================
"""

import os

from managers.json_manager import json_manager
from diagrams.base.diagram_base import get_speed
from dialogs.motor_info import show_motor_info
from exporters.export_dialog import ExportDialog
from ui.notifications import show_error


def handle_draw(app, instance):
    if not json_manager.project_data:
        show_error("Please load a project first", 3)
        return

    filepath = json_manager.current_project_file
    if filepath and os.path.exists(filepath):
        json_manager.load_project_data(filepath)

    project_data = json_manager.project_data
    if not project_data:
        show_error("Please load a project first", 3)
        return

    try:
        all_slots = int(project_data.get("all_slots", 60))
        poles = int(project_data.get("poles", 4))
    except Exception:
        show_error("Invalid motor parameters", 3)
        return

    if all_slots < 6:
        show_error("All slots must be at least 6", 3)
        return
    if poles <= 0 or all_slots % poles != 0:
        show_error(
            "Slots (" + str(all_slots) + ") must be divisible by " +
            "Poles (" + str(poles) + ")",
            3
        )
        return

    group_name = json_manager.get_active_group_name()
    group_data = project_data.get(group_name, {})
    span_chained = group_data.get("coil_span_chained", 11)
    span_concentric = group_data.get("coil_span_concentric", 9)

    from app.app_diagram_widget import recreate_diagram_widget
    recreate_diagram_widget(app)

    try:
        if app.current_winding_type == "single_layer":
            app.winding_widget.set_parameters(all_slots, poles)
        else:
            app.winding_widget.set_parameters(
                all_slots, poles,
                coil_span_chained=span_chained,
                coil_span_concentric=span_concentric
            )
    except Exception as error:
        show_error("Draw error: " + str(error), 3)
        return

    from app.app_info_labels import update_info_labels
    update_info_labels(app)


def handle_reset(app, instance):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    if hasattr(app, "winding_widget"):
        app.winding_widget.clear_diagram()
        app.winding_widget.auto_fit()
    from app.app_connection import close_connection_panel
    close_connection_panel(app)


def handle_rotate(app, instance):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    if hasattr(app, "winding_widget"):
        app.winding_widget.toggle_rotation()


def handle_export(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    if not hasattr(app, "winding_widget"):
        return
    ExportDialog(app.winding_widget).open()


def handle_motor_info(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    if not json_manager.project_data:
        show_error("No project loaded", 2)
        return

    project_data = json_manager.project_data
    try:
        all_slots = int(project_data.get("all_slots", 0))
        poles = int(project_data.get("poles", 0))

        group_name = json_manager.get_active_group_name()
        group_data = project_data.get(group_name, {})
        coil_span = int(group_data.get("coil_span_chained", 0))

        show_motor_info(all_slots, coil_span, poles, get_speed(poles))
    except Exception as error:
        show_error("Error: " + str(error), 2)