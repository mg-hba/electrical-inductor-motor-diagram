"""
================================================================================
File: diagrams/motor_common/diagram_connection.py
Purpose: Restore connections from JSON, connection mode helpers.
Version: 0.1.4
================================================================================
"""

from managers.json_manager import json_manager


def restore_connections_from_project(diagram):
    project_data = json_manager.project_data
    connection = diagram.connection

    if project_data is None:
        connection.junctions = []
        connection.lines = []
        connection.phase_endpoints = {}
        connection._reinit()
        return

    group = json_manager.get_active_group_name()
    group_data = project_data.get(group, {})

    if group == "concentric":
        connection_data = group_data.get('concentric_connection', {})
    else:
        connection_data = group_data.get('chained_connection', {})

    from core.connection.models import Junction, LineSegment

    connection.junctions = []
    for entry in connection_data.get('junction_points', []):
        try:
            connection.junctions.append(Junction.from_dict(entry))
        except (ValueError, TypeError):
            continue

    connection.lines = []
    for entry in connection_data.get('line_segments', []):
        try:
            connection.lines.append(LineSegment.from_dict(entry))
        except (ValueError, TypeError):
            continue

    connection.phase_endpoints = dict(
        connection_data.get('phase_endpoints', {})
    )

    for wire in connection.wire_points:
        if connection.phase_endpoints.get('R') == wire.wire_id:
            wire.is_phase_start = True
        if connection.phase_endpoints.get('U') == wire.wire_id:
            wire.is_phase_end = True
    for junction in connection.junctions:
        if connection.phase_endpoints.get('R') == junction.junction_id:
            junction.is_phase_start = True
        if connection.phase_endpoints.get('U') == junction.junction_id:
            junction.is_phase_end = True

    connection._reinit()
    connection._topo.cleanup_invalid_junctions()


def set_connection_mode(diagram, active):
    diagram.connection.set_active(active)
    if active:
        diagram.connection.load_from_json(json_manager)
    diagram._rebuild_all()


def handle_connection_touch_down(diagram, touch):
    if not diagram.connection.active:
        return False
    world_x, world_y = diagram.screen_to_world(*touch.pos)
    result = diagram.connection.handle_touch_down_world(
        world_x, world_y, diagram.SCREEN_scale, diagram.GRID_cell_size_px
    )
    if result:
        diagram.connection.apply_hit(result)
        diagram._rebuild_all()
        update_phase_labels(diagram)
        return True
    return False