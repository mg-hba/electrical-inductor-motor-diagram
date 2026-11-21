"""
================================================================================
File: core/connection/topology_ops.py
Purpose: Low-level topology with group preservation on split.
Version: 0.1.1.1
================================================================================
"""

from core.connection.models import LineSegment
from core.connection.geometry import (
    points_equal,
    point_on_segment_interior,
)

from utils.constants import SPLIT_EPSILON


class TopologyOps:

    def __init__(self, wires, junctions, lines, topo):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines
        self.topo = topo

    def lines_on_path(self, x1, y1, x2, y2, exclude_ids=None):
        if exclude_ids is None:
            exclude_ids = set()
        is_h = abs(y1 - y2) < SPLIT_EPSILON
        is_v = abs(x1 - x2) < SPLIT_EPSILON
        found = []

        if is_v:
            ymin, ymax = min(y1, y2), max(y1, y2)
            for ln in self.lines:
                if ln.line_id in exclude_ids:
                    continue
                if not ln.is_horizontal:
                    continue
                hx1, hx2 = min(ln.x1, ln.x2), max(ln.x1, ln.x2)
                if hx1 - SPLIT_EPSILON < x1 < hx2 + SPLIT_EPSILON:
                    hy = ln.y1
                    if ymin + SPLIT_EPSILON < hy <= ymax + SPLIT_EPSILON:
                        found.append((ln, (x1, hy)))
        elif is_h:
            xmin, xmax = min(x1, x2), max(x1, x2)
            for ln in self.lines:
                if ln.line_id in exclude_ids:
                    continue
                if not ln.is_vertical:
                    continue
                vy1, vy2 = min(ln.y1, ln.y2), max(ln.y1, ln.y2)
                if vy1 - SPLIT_EPSILON < y1 < vy2 + SPLIT_EPSILON:
                    vx = ln.x1
                    if xmin + SPLIT_EPSILON < vx <= xmax + SPLIT_EPSILON:
                        found.append((ln, (vx, y1)))
        return found

    def line_overlaps_existing(self, x1, y1, x2, y2, exclude_line_id=None):
        is_h = abs(y1 - y2) < SPLIT_EPSILON
        is_v = abs(x1 - x2) < SPLIT_EPSILON

        if is_h:
            new_min, new_max = min(x1, x2), max(x1, x2)
            for ln in self.lines:
                if ln.line_id == exclude_line_id:
                    continue
                if not ln.is_horizontal:
                    continue
                if abs(ln.y1 - y1) > SPLIT_EPSILON:
                    continue
                ex_min, ex_max = min(ln.x1, ln.x2), max(ln.x1, ln.x2)
                if new_min < ex_max - SPLIT_EPSILON and new_max > ex_min + SPLIT_EPSILON:
                    return True
        elif is_v:
            new_min, new_max = min(y1, y2), max(y1, y2)
            for ln in self.lines:
                if ln.line_id == exclude_line_id:
                    continue
                if not ln.is_vertical:
                    continue
                if abs(ln.x1 - x1) > SPLIT_EPSILON:
                    continue
                ex_min, ex_max = min(ln.y1, ln.y2), max(ln.y1, ln.y2)
                if new_min < ex_max - SPLIT_EPSILON and new_max > ex_min + SPLIT_EPSILON:
                    return True
        return False

    def split_line_at(self, ln, x, y):
        """Split ln at (x,y). Groups and IDs are inherited."""
        new1 = LineSegment(ln.x1, ln.y1, x, y)
        new2 = LineSegment(x, y, ln.x2, ln.y2)
        new1.phase_group = ln.phase_group
        new2.phase_group = ln.phase_group
        if ln.phase_group:
            new1.rename_with_group(ln.phase_group)
            new2.rename_with_group(ln.phase_group)
        if ln in self.lines:
            self.lines.remove(ln)
        self.lines.append(new1)
        self.lines.append(new2)
        return new1, new2

    def ensure_junction_at(self, x, y):
        if self.topo.find_junction_at(x, y) is not None:
            return
        if self.topo.find_wire_at(x, y) is not None:
            return
        from core.connection.models import Junction
        self.junctions.append(Junction(x, y))

    def count_lines_at_point(self, x, y, eps=SPLIT_EPSILON):
        count = 0
        for ln in self.lines:
            if (abs(ln.x1 - x) < eps and abs(ln.y1 - y) < eps) or \
               (abs(ln.x2 - x) < eps and abs(ln.y2 - y) < eps):
                count += 1
        return count

    def find_pulled_vertical(self, path_start, path_end):
        sx, sy = path_start
        ex, ey = path_end
        for ln in self.lines:
            if not ln.is_vertical:
                continue
            if abs(ln.x1 - sx) < SPLIT_EPSILON:
                ymin, ymax = min(ln.y1, ln.y2), max(ln.y1, ln.y2)
                if (ymin - SPLIT_EPSILON <= ey <= ymax + SPLIT_EPSILON or
                        ymin - SPLIT_EPSILON <= sy <= ymax + SPLIT_EPSILON):
                    return ln
        return None

    def min_bottom_for_vertical(self, x, top_y, current_bottom):
        min_allowed = None
        for ln in self.lines:
            if not ln.is_horizontal:
                continue
            hx1, hx2 = min(ln.x1, ln.x2), max(ln.x1, ln.x2)
            if hx1 - SPLIT_EPSILON < x < hx2 + SPLIT_EPSILON:
                hy = ln.y1
                if (current_bottom + SPLIT_EPSILON < hy <
                        top_y - SPLIT_EPSILON):
                    if min_allowed is None or hy > min_allowed:
                        min_allowed = hy
        return min_allowed