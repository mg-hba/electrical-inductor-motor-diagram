"""
================================================================================
File: core/connection/geometry.py
Purpose: Pure geometry helpers (no state).
Version: 0.1.1
================================================================================
"""

from math import hypot

from utils.constants import SPLIT_EPSILON


def points_equal(x1, y1, x2, y2, eps=SPLIT_EPSILON):
    return abs(x1 - x2) < eps and abs(y1 - y2) < eps


def point_to_segment_distance(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) < 0.0001 and abs(dy) < 0.0001:
        return hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def point_on_segment_interior(px, py, x1, y1, x2, y2, eps=SPLIT_EPSILON):
    if abs(x1 - x2) < eps:
        if abs(px - x1) > eps:
            return False
        ymin = min(y1, y2) + eps
        ymax = max(y1, y2) - eps
        return ymin < py < ymax
    if abs(y1 - y2) < eps:
        if abs(py - y1) > eps:
            return False
        xmin = min(x1, x2) + eps
        xmax = max(x1, x2) - eps
        return xmin < px < xmax
    return False


def is_horizontal(x1, y1, x2, y2, eps=SPLIT_EPSILON):
    return abs(y1 - y2) < eps


def is_vertical(x1, y1, x2, y2, eps=SPLIT_EPSILON):
    return abs(x1 - x2) < eps


def point_in_rect(px, py, rx1, ry1, rx2, ry2):
    xmin, xmax = min(rx1, rx2), max(rx1, rx2)
    ymin, ymax = min(ry1, ry2), max(ry1, ry2)
    return xmin <= px <= xmax and ymin <= py <= ymax


def segment_intersects_rect(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    xmin, xmax = min(rx1, rx2), max(rx1, rx2)
    ymin, ymax = min(ry1, ry2), max(ry1, ry2)

    if point_in_rect(x1, y1, xmin, ymin, xmax, ymax):
        return True
    if point_in_rect(x2, y2, xmin, ymin, xmax, ymax):
        return True

    if min(y1, y2) <= ymin <= max(y1, y2) and abs(y1 - y2) > SPLIT_EPSILON:
        if xmin <= x1 <= xmax:
            return True
    if min(y1, y2) <= ymax <= max(y1, y2) and abs(y1 - y2) > SPLIT_EPSILON:
        if xmin <= x1 <= xmax:
            return True
    if min(x1, x2) <= xmin <= max(x1, x2) and abs(x1 - x2) > SPLIT_EPSILON:
        if ymin <= y1 <= ymax:
            return True
    if min(x1, x2) <= xmax <= max(x1, x2) and abs(x1 - x2) > SPLIT_EPSILON:
        if ymin <= y1 <= ymax:
            return True

    return False


def segment_contained_in_rect(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    return (point_in_rect(x1, y1, rx1, ry1, rx2, ry2) and
            point_in_rect(x2, y2, rx1, ry1, rx2, ry2))