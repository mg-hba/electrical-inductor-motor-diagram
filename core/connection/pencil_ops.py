"""
================================================================================
File: core/connection/pencil_ops.py
Purpose: Pencil mode - draws H or V lines that attach to existing
         points or lines. Both endpoints snap to integer grid.
         At least one endpoint must attach.
Version: 0.1.1.1
================================================================================
"""

from core.connection.models import LineSegment
from core.connection.geometry import point_on_segment_interior

from utils.constants import (
    SPLIT_EPSILON,
    PENCIL_SNAP_RADIUS,
)


class PencilOps:

    def __init__(self, wires, junctions, lines, topo, topo_ops):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines
        self.topo = topo
        self.topo_ops = topo_ops

    def draw_line(self, x1, y1, x2, y2):
        # Snap both endpoints to integer grid
        x1 = round(x1)
        y1 = round(y1)
        x2 = round(x2)
        y2 = round(y2)

        if (abs(x2 - x1) < SPLIT_EPSILON and
                abs(y2 - y1) < SPLIT_EPSILON):
            return None

        # Force H or V: keep longer axis, snap other to same
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dx >= dy:
            y2 = y1  # horizontal
        else:
            x2 = x1  # vertical

        # Verify H or V
        is_h = abs(y2 - y1) < SPLIT_EPSILON
        is_v = abs(x2 - x1) < SPLIT_EPSILON
        if not (is_h or is_v):
            return None

        if (abs(x2 - x1) < SPLIT_EPSILON and
                abs(y2 - y1) < SPLIT_EPSILON):
            return None

        # Try to snap each endpoint to a nearby attachment
        snap = PENCIL_SNAP_RADIUS
        x1n, y1n, attached1 = self._snap_endpoint(x1, y1, snap)
        x2n, y2n, attached2 = self._snap_endpoint(x2, y2, snap)

        # Re-align after snap
        if abs(x2n - x1n) >= abs(y2n - y1n):
            y2n = y1n
        else:
            x2n = x1n

        # At least one end must attach
        if not attached1 and not attached2:
            return None

        if (abs(x2n - x1n) < SPLIT_EPSILON and
                abs(y2n - y1n) < SPLIT_EPSILON):
            return None

        new_line = LineSegment(x1n, y1n, x2n, y2n)
        self.lines.append(new_line)

        self.topo_ops.ensure_junction_at(x1n, y1n)
        self.topo_ops.ensure_junction_at(x2n, y2n)

        return new_line

    def _snap_endpoint(self, x, y, radius):
        # 1. Wire point
        best_d = radius
        best = None
        for wp in self.wires:
            d = ((wp.x - x) ** 2 + (wp.y - y) ** 2) ** 0.5
            if d <= best_d:
                best_d = d
                best = (wp.x, wp.y)
        if best is not None:
            return (best[0], best[1], True)

        # 2. Junction
        best_d = radius
        best = None
        for j in self.junctions:
            d = ((j.x - x) ** 2 + (j.y - y) ** 2) ** 0.5
            if d <= best_d:
                best_d = d
                best = (j.x, j.y)
        if best is not None:
            return (best[0], best[1], True)

        # 3. Interior of a line -> split + junction
        for ln in list(self.lines):
            if point_on_segment_interior(x, y, ln.x1, ln.y1,
                                           ln.x2, ln.y2):
                self.topo_ops.split_line_at(ln, x, y)
                self.topo_ops.ensure_junction_at(x, y)
                return (x, y, True)

        # 4. Line endpoint
        best_d = radius
        best = None
        for ln in self.lines:
            for (ex, ey) in [(ln.x1, ln.y1), (ln.x2, ln.y2)]:
                d = ((ex - x) ** 2 + (ey - y) ** 2) ** 0.5
                if d <= best_d:
                    best_d = d
                    best = (ex, ey)
        if best is not None:
            return (best[0], best[1], True)

        # 5. No attach
        return (x, y, False)