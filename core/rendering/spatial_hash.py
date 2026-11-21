"""
================================================================================
File: core/rendering/spatial_hash.py
Purpose: Fast hit testing using a spatial grid.
Version: 0.1.1
================================================================================
"""

from math import floor

from core.connection.geometry import point_to_segment_distance


class SpatialHash:

    def __init__(self, cell_size=2.0):
        self.cell_size = cell_size
        self._line_cells = {}
        self._point_cells = {}
        self._lines = []
        self._points = []

    def _key(self, x, y):
        return (int(floor(x / self.cell_size)),
                int(floor(y / self.cell_size)))

    def clear(self):
        self._line_cells.clear()
        self._point_cells.clear()
        self._lines.clear()
        self._points.clear()

    def add_line(self, line_id, x1, y1, x2, y2):
        self._lines.append((line_id, x1, y1, x2, y2))
        for key in self._cells_for_segment(x1, y1, x2, y2):
            self._line_cells.setdefault(key, []).append(line_id)

    def add_point(self, point_id, x, y):
        self._points.append((point_id, x, y))
        self._point_cells.setdefault(self._key(x, y), []).append(point_id)

    def _cells_for_segment(self, x1, y1, x2, y2):
        minx, maxx = min(x1, x2), max(x1, x2)
        miny, maxy = min(y1, y2), max(y1, y2)
        kx0, ky0 = self._key(minx, miny)
        kx1, ky1 = self._key(maxx, maxy)
        for kx in range(kx0, kx1 + 1):
            for ky in range(ky0, ky1 + 1):
                yield (kx, ky)

    def query_near_point(self, x, y, radius_world):
        found = set()
        kx0, ky0 = self._key(x - radius_world, y - radius_world)
        kx1, ky1 = self._key(x + radius_world, y + radius_world)
        r2 = radius_world * radius_world
        for kx in range(kx0, kx1 + 1):
            for ky in range(ky0, ky1 + 1):
                for pid in self._point_cells.get((kx, ky), []):
                    for (p, px, py) in self._points:
                        if p == pid:
                            dx = px - x
                            dy = py - y
                            if dx * dx + dy * dy <= r2:
                                found.add(pid)
                            break
        return found

    def query_near_line(self, x, y, radius_world):
        candidates = set()
        kx0, ky0 = self._key(x - radius_world, y - radius_world)
        kx1, ky1 = self._key(x + radius_world, y + radius_world)
        for kx in range(kx0, kx1 + 1):
            for ky in range(ky0, ky1 + 1):
                for lid in self._line_cells.get((kx, ky), []):
                    candidates.add(lid)
        result = []
        for lid in candidates:
            for (l_id, lx1, ly1, lx2, ly2) in self._lines:
                if l_id != lid:
                    continue
                d = point_to_segment_distance(x, y, lx1, ly1, lx2, ly2)
                if d <= radius_world:
                    result.append((lid, d))
                break
        return result