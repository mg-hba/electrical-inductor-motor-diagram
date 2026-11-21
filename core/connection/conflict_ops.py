"""
================================================================================
File: core/connection/conflict_ops.py
Purpose: Conflict detection and resolution (Connect / Pass Over / Stop Before).
Version: 0.1.1
================================================================================
"""

from core.connection.geometry import (
    point_on_segment_interior,
)


class ConflictInfo:
    """Describes a conflict when pulling into a perpendicular line."""

    def __init__(self, line, hit_point, path_start, path_end, start_point):
        self.line = line
        self.hit_point = hit_point
        self.path_start = path_start
        self.path_end = path_end
        self.start_point = start_point


class ConflictOps:

    def __init__(self, wires, junctions, lines, topo, topo_ops):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines
        self.topo = topo
        self.topo_ops = topo_ops

    # ============================================================
    # ================== APPLY ==================================
    # ============================================================

    def apply(self, conflict, action):
        if action == 'connect':
            return self._resolve_connect(conflict)
        elif action == 'pass_over':
            return self._resolve_pass_over(conflict)
        elif action == 'stop_before':
            return self._resolve_stop_before(conflict)
        return False

    # ============================================================
    # ================== RESOLVERS ==============================
    # ============================================================

    def _resolve_connect(self, conflict):
        """Connect: point lands on line, junction created, line splits."""
        px, py = conflict.hit_point
        blocking = conflict.line

        # Ensure junction at intersection
        self.topo_ops.ensure_junction_at(px, py)

        # Split the blocking line if the intersection is interior
        if point_on_segment_interior(px, py, blocking.x1, blocking.y1,
                                       blocking.x2, blocking.y2):
            self.topo_ops.split_line_at(blocking, px, py)

        # Move the pulled vertical line to end at (px, py)
        pulled = self.topo_ops.find_pulled_vertical(
            conflict.path_start, conflict.path_end
        )
        if pulled is not None:
            if pulled.y1 > pulled.y2:
                pulled.y2 = py
            else:
                pulled.y1 = py
            return True
        return False

    def _resolve_pass_over(self, conflict):
        """Pass Over: line continues past the blocking line."""
        sx, sy = conflict.path_start
        ex, ey = conflict.path_end

        pulled = self.topo_ops.find_pulled_vertical(
            conflict.path_start, conflict.path_end
        )
        if pulled is not None:
            if pulled.y1 > pulled.y2:
                pulled.y2 = ey
            else:
                pulled.y1 = ey
            return True
        return False

    def _resolve_stop_before(self, conflict):
        """Stop Before: line stops one grid above the blocking line."""
        px, py = conflict.hit_point
        stop_y = py + 1.0

        pulled = self.topo_ops.find_pulled_vertical(
            conflict.path_start, conflict.path_end
        )
        if pulled is not None:
            if pulled.y1 > pulled.y2:
                pulled.y2 = stop_y
            else:
                pulled.y1 = stop_y

            if (self.topo.find_junction_at(pulled.x1, stop_y) is None and
                    self.topo.find_wire_at(pulled.x1, stop_y) is None):
                from core.connection.models import Junction
                self.junctions.append(Junction(pulled.x1, stop_y))
            return True
        return False