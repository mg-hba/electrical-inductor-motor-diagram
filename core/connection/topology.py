"""
================================================================================
File: core/connection/topology.py
Purpose: Structural operations - never removes grouped junctions.
Version: 0.1.1.1
================================================================================
"""

from core.connection.models import Junction, LineSegment
from core.connection.geometry import (
    points_equal,
)

from utils.constants import SPLIT_EPSILON


class Topology:

    def __init__(self, wires, junctions, lines):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines

    def find_wire_at(self, x, y):
        for wp in self.wires:
            if points_equal(wp.x, wp.y, x, y):
                return wp
        return None

    def find_junction_at(self, x, y):
        for j in self.junctions:
            if points_equal(j.x, j.y, x, y):
                return j
        return None

    def find_point_at(self, x, y):
        wp = self.find_wire_at(x, y)
        if wp is not None:
            return wp
        return self.find_junction_at(x, y)

    def line_touches_junction(self, ln, jx, jy):
        return (points_equal(ln.x1, ln.y1, jx, jy) or
                points_equal(ln.x2, ln.y2, jx, jy))

    def lines_touching_point(self, x, y):
        return [ln for ln in self.lines
                if self.line_touches_junction(ln, x, y)]

    def other_endpoint(self, ln, jx, jy):
        if points_equal(ln.x1, ln.y1, jx, jy):
            return (ln.x2, ln.y2)
        return (ln.x1, ln.y1)

    def count_lines_at_junction(self, j):
        return sum(1 for ln in self.lines
                   if self.line_touches_junction(ln, j.x, j.y))

    def junction_has_wire(self, j):
        return self.find_wire_at(j.x, j.y) is not None

    def junction_is_valid(self, j):
        jx, jy = j.x, j.y
        count_left = count_right = count_up = count_down = 0

        for ln in self.lines:
            if not self.line_touches_junction(ln, jx, jy):
                continue
            other = self.other_endpoint(ln, jx, jy)
            if ln.is_horizontal:
                if other[0] < jx:
                    count_left += 1
                elif other[0] > jx:
                    count_right += 1
            elif ln.is_vertical:
                if other[1] > jy:
                    count_up += 1
                elif other[1] < jy:
                    count_down += 1

        total = count_left + count_right + count_up + count_down
        if total == 0:
            return False
        if total == 1:
            return True
        if total == 2:
            if count_left == 1 and count_right == 1:
                return False
            if count_up == 1 and count_down == 1:
                return False
            return True
        return True

    def cleanup_invalid_junctions(self):
        changed = True
        while changed:
            changed = False
            to_remove = []
            for j in self.junctions:
                if self.junction_has_wire(j):
                    continue
                if getattr(j, 'phase_group', None) is not None:
                    continue
                if self.junction_is_valid(j):
                    continue
                to_remove.append(j)
            for j in to_remove:
                self.merge_and_remove_junction(j)
                changed = True

    def merge_and_remove_junction(self, j):
        jx, jy = j.x, j.y
        H_left, H_right, V_up, V_down = [], [], [], []

        for ln in self.lines:
            if not self.line_touches_junction(ln, jx, jy):
                continue
            if ln.is_horizontal:
                other = self.other_endpoint(ln, jx, jy)
                if other[0] < jx:
                    H_left.append(ln)
                elif other[0] > jx:
                    H_right.append(ln)
            elif ln.is_vertical:
                other = self.other_endpoint(ln, jx, jy)
                if other[1] > jy:
                    V_up.append(ln)
                elif other[1] < jy:
                    V_down.append(ln)

        if len(H_left) == 1 and len(H_right) == 1:
            p1 = self.other_endpoint(H_left[0], jx, jy)
            p2 = self.other_endpoint(H_right[0], jx, jy)
            old_group = H_left[0].phase_group or H_right[0].phase_group
            self.lines.remove(H_left[0])
            self.lines.remove(H_right[0])
            new_ln = LineSegment(p1[0], p1[1], p2[0], p2[1])
            if old_group:
                new_ln.phase_group = old_group
                new_ln.rename_with_group(old_group)
            self.lines.append(new_ln)
        else:
            for ln in H_left + H_right:
                if ln in self.lines:
                    self.lines.remove(ln)

        if len(V_up) == 1 and len(V_down) == 1:
            p1 = self.other_endpoint(V_up[0], jx, jy)
            p2 = self.other_endpoint(V_down[0], jx, jy)
            old_group = V_up[0].phase_group or V_down[0].phase_group
            self.lines.remove(V_up[0])
            self.lines.remove(V_down[0])
            new_ln = LineSegment(p1[0], p1[1], p2[0], p2[1])
            if old_group:
                new_ln.phase_group = old_group
                new_ln.rename_with_group(old_group)
            self.lines.append(new_ln)
        else:
            for ln in V_up + V_down:
                if ln in self.lines:
                    self.lines.remove(ln)

        if j in self.junctions:
            self.junctions.remove(j)