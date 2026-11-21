"""
================================================================================
File: core/connection/__init__.py
Purpose: Connection package initializer.
Version: 0.1.4
================================================================================
"""

from core.connection.mode import ConnectionMode
from core.connection.models import WirePoint, Junction, LineSegment
from core.connection.geometry import (
    points_equal,
    point_to_segment_distance,
    point_on_segment_interior,
    is_horizontal,
    is_vertical,
    point_in_rect,
    segment_intersects_rect,
    segment_contained_in_rect,
)
from core.connection.topology import Topology
from core.connection.layer import ConnectionLayer


__all__ = [
    'ConnectionMode', 'ConnectionLayer',
    'WirePoint', 'Junction', 'LineSegment',
    'Topology',
    'points_equal', 'point_to_segment_distance', 'point_on_segment_interior',
    'is_horizontal', 'is_vertical',
    'point_in_rect', 'segment_intersects_rect', 'segment_contained_in_rect',
]