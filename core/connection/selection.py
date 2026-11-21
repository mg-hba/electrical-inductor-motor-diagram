"""
================================================================================
File: core/connection/selection.py
Purpose: Selection state, hit tester with fair priority, box selection.
Version: 0.1.1
================================================================================
"""

from core.connection.geometry import (
    point_to_segment_distance,
    point_in_rect,
    segment_intersects_rect,
    segment_contained_in_rect,
)

from utils.constants import (
    CONNECTION_TOUCH_TOLERANCE_BASE,
    CONNECTION_TOUCH_TOLERANCE_MIN,
    CONNECTION_TOUCH_TOLERANCE_MAX,
    POINT_PRIORITY_FACTOR,
)


def compute_tolerance(scale, cell_size_px=10.0):
    if scale <= 0:
        scale = 1.0
    tol_px = CONNECTION_TOUCH_TOLERANCE_BASE
    tol_px = max(CONNECTION_TOUCH_TOLERANCE_MIN,
                 min(CONNECTION_TOUCH_TOLERANCE_MAX, tol_px))
    world_per_px = 1.0 / max(cell_size_px * scale, 0.0001)
    return tol_px * world_per_px


class SelectionState:

    def __init__(self):
        self.wire_ids = set()
        self.junction_ids = set()
        self.line_ids = set()
        self.pending_delete_ids = set()

    def clear(self):
        self.wire_ids.clear()
        self.junction_ids.clear()
        self.line_ids.clear()

    def clear_all(self):
        self.clear()
        self.pending_delete_ids.clear()

    def has_any(self):
        return bool(self.wire_ids or self.junction_ids or self.line_ids)

    def add_wire(self, wid):
        self.wire_ids.add(wid)

    def add_junction(self, jid):
        self.junction_ids.add(jid)

    def add_line(self, lid):
        self.line_ids.add(lid)

    def toggle_wire(self, wid):
        if wid in self.wire_ids:
            self.wire_ids.discard(wid)
            return False
        self.wire_ids.add(wid)
        return True

    def toggle_junction(self, jid):
        if jid in self.junction_ids:
            self.junction_ids.discard(jid)
            return False
        self.junction_ids.add(jid)
        return True

    def toggle_line(self, lid):
        if lid in self.line_ids:
            self.line_ids.discard(lid)
            return False
        self.line_ids.add(lid)
        return True


class HitTester:

    def __init__(self, wires, junctions, lines):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines

    def hit_wire(self, wx, wy, tol_world):
        best = None
        best_d = tol_world
        for wp in self.wires:
            d = ((wp.x - wx) ** 2 + (wp.y - wy) ** 2) ** 0.5
            if d < best_d:
                best_d = d
                best = wp
        return best

    def hit_junction(self, wx, wy, tol_world):
        best = None
        best_d = tol_world
        for j in self.junctions:
            d = ((j.x - wx) ** 2 + (j.y - wy) ** 2) ** 0.5
            if d < best_d:
                best_d = d
                best = j
        return best

    def hit_line(self, wx, wy, tol_world):
        best = None
        best_d = tol_world
        for ln in self.lines:
            d = point_to_segment_distance(wx, wy, ln.x1, ln.y1, ln.x2, ln.y2)
            if d < best_d:
                best_d = d
                best = ln
        return best

    def hit_any(self, wx, wy, tol_world):
        best_kind = None
        best_obj = None
        best_score = None

        wp = self.hit_wire(wx, wy, tol_world)
        if wp is not None:
            d = ((wp.x - wx) ** 2 + (wp.y - wy) ** 2) ** 0.5
            best_kind = 'wire'
            best_obj = wp
            best_score = d * POINT_PRIORITY_FACTOR

        j = self.hit_junction(wx, wy, tol_world)
        if j is not None:
            d = ((j.x - wx) ** 2 + (j.y - wy) ** 2) ** 0.5
            score = d * POINT_PRIORITY_FACTOR
            if best_score is None or score < best_score:
                best_kind = 'junction'
                best_obj = j
                best_score = score

        ln = self.hit_line(wx, wy, tol_world)
        if ln is not None:
            d = point_to_segment_distance(wx, wy, ln.x1, ln.y1, ln.x2, ln.y2)
            if best_score is None or d < best_score:
                best_kind = 'line'
                best_obj = ln
                best_score = d

        if best_kind is None:
            return None
        return (best_kind, best_obj)

    def lines_touching_point(self, x, y, eps=0.05):
        result = []
        for ln in self.lines:
            if (abs(ln.x1 - x) < eps and abs(ln.y1 - y) < eps) or \
               (abs(ln.x2 - x) < eps and abs(ln.y2 - y) < eps):
                result.append(ln)
        return result


def box_select(wires, junctions, lines, x1, y1, x2, y2, mode='contain'):
    rx1, ry1, rx2, ry2 = x1, y1, x2, y2

    wire_ids = set()
    for wp in wires:
        if point_in_rect(wp.x, wp.y, rx1, ry1, rx2, ry2):
            wire_ids.add(wp.wire_id)

    junction_ids = set()
    for j in junctions:
        if point_in_rect(j.x, j.y, rx1, ry1, rx2, ry2):
            junction_ids.add(j.junction_id)

    line_ids = set()
    for ln in lines:
        if mode == 'contain':
            if segment_contained_in_rect(ln.x1, ln.y1, ln.x2, ln.y2,
                                          rx1, ry1, rx2, ry2):
                line_ids.add(ln.line_id)
        else:
            if segment_intersects_rect(ln.x1, ln.y1, ln.x2, ln.y2,
                                        rx1, ry1, rx2, ry2):
                line_ids.add(ln.line_id)

    return wire_ids, junction_ids, line_ids