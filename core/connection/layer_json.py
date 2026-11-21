"""
================================================================================
File: core/connection/layer_json.py
Purpose: JSON load / save helpers for connection data.
Version: 0.1.1.1
================================================================================
"""

from core.connection.models import WirePoint, Junction, LineSegment


class JsonIO:

    def __init__(self, layer):
        self.layer = layer

    def load_from_json(self, json_manager):
        wires = []
        for d in json_manager.get_last_wire_points():
            try:
                wires.append(WirePoint.from_dict(d))
            except (ValueError, TypeError):
                continue

        junctions = []
        for d in json_manager.get_last_junction_points():
            try:
                junctions.append(Junction.from_dict(d))
            except (ValueError, TypeError):
                continue

        lines = []
        for d in json_manager.get_last_line_segments():
            try:
                lines.append(LineSegment.from_dict(d))
            except (ValueError, TypeError):
                continue

        endpoints = dict(json_manager.get_last_phase_endpoints()) or {}

        for wp in wires:
            if endpoints.get('R') == wp.wire_id:
                wp.is_phase_start = True
            if endpoints.get('U') == wp.wire_id:
                wp.is_phase_end = True
        for j in junctions:
            if endpoints.get('R') == j.junction_id:
                j.is_phase_start = True
            if endpoints.get('U') == j.junction_id:
                j.is_phase_end = True

        self.layer.wire_points = wires
        self.layer.junctions = junctions
        self.layer.lines = lines
        self.layer.phase_endpoints = endpoints
        self.layer._reinit()
        self.layer._topo.cleanup_invalid_junctions()

    def save_to_json(self, json_manager):
        self.layer._topo.cleanup_invalid_junctions()

        junctions_data = [j.to_dict() for j in self.layer.junctions]
        lines_data = [ln.to_dict() for ln in self.layer.lines]
        endpoints_data = dict(self.layer.phase_endpoints)

        json_manager.set_last_junction_points(junctions_data)
        json_manager.set_last_line_segments(lines_data)
        json_manager.set_last_phase_endpoints(endpoints_data)

        json_manager.update_project_field('junction_points', junctions_data)
        json_manager.update_project_field('line_segments', lines_data)
        json_manager.update_project_field('phase_endpoints', endpoints_data)