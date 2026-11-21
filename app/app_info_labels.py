"""
================================================================================
File: app/app_info_labels.py
Purpose: Update info labels at top of screen.
Version: 0.1.3
================================================================================
"""

from diagrams.base.diagram_base import get_speed
from managers.json_manager import json_manager


def update_info_labels(app):
    if not json_manager.project_data:
        app.info_line1.text = ""
        app.info_line2.text = ""
        return

    project_data = json_manager.project_data
    project_name = project_data.get("project_name", "---")
    nominal_power = project_data.get("nominal_power", "---")
    connection_type = project_data.get("connection_type", "---")
    all_slots = project_data.get("all_slots", "---")
    poles = project_data.get("poles", "---")

    group_name = json_manager.get_active_group_name()
    group_data = project_data.get(group_name, {})
    coil_span = group_data.get("coil_span_chained", "---")

    try:
        speed = get_speed(int(poles))
    except Exception:
        speed = "---"

    app.info_line1.text = (
        "Motor: " + str(project_name) + "   |   Power: " +
        str(nominal_power) + " kW   |   Connection: " +
        str(connection_type)
    )
    app.info_line2.text = (
        "Slots: " + str(all_slots) + "   |   Poles: " + str(poles) +
        "   |   Span: " + str(coil_span) + "   |   Speed: " +
        str(speed) + " RPM"
    )