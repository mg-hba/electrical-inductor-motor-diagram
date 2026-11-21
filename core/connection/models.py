"""
================================================================================
File: core/connection/models.py
Purpose: Data models with phase_group and rename support.
Version: 0.1.1.1
================================================================================
"""

from math import hypot


class WirePoint:
    """Terminal point from diagram. NOT deletable, NOT movable."""

    def __init__(self, wire_id, pole_index, wire_type, x, y):
        self.wire_id = wire_id
        self.pole_index = pole_index
        self.wire_type = wire_type
        self.x = float(x)
        self.y = float(y)

        self.selected = False
        self.is_phase_start = False
        self.is_phase_end = False
        self.phase_group = None

    @property
    def is_deletable(self):
        return False

    def to_dict(self):
        return {
            'id': self.wire_id,
            'pole': self.pole_index,
            'type': self.wire_type,
            'x': self.x,
            'y': self.y,
            'phase_group': self.phase_group,
        }

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise ValueError("WirePoint data must be dict")
        try:
            wp = cls(
                str(d.get('id', '')),
                int(d.get('pole', 0)),
                str(d.get('type', 'start')),
                float(d.get('x', 0)),
                float(d.get('y', 0)),
            )
            wp.phase_group = d.get('phase_group')
            return wp
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid WirePoint values: " + str(d)) from e


class Junction:
    """User-created junction."""

    _counter = 0

    def __init__(self, x, y, junction_id=None):
        if junction_id is None:
            Junction._counter += 1
            junction_id = "J_%03d" % Junction._counter
        else:
            # Extract numeric suffix from id like "J_001" or "J_R_002"
            try:
                parts = junction_id.split('_')
                num = int(parts[-1])
                if num > Junction._counter:
                    Junction._counter = num
            except (ValueError, IndexError):
                pass

        self.junction_id = junction_id
        self.x = float(x)
        self.y = float(y)

        self.selected = False
        self.is_phase_start = False
        self.is_phase_end = False
        self.phase_group = None

    @property
    def is_deletable(self):
        return True

    def rename_with_group(self, group):
        """Update id to include group prefix."""
        parts = self.junction_id.split('_')
        if len(parts) >= 3 and parts[1] in ('R', 'U'):
            num = parts[2]
        elif len(parts) == 2:
            num = parts[1]
        else:
            num = parts[-1]

        if group == 'R':
            self.junction_id = "J_R_" + num
        elif group == 'U':
            self.junction_id = "J_U_" + num
        else:
            self.junction_id = "J_" + num

    def to_dict(self):
        return {
            'id': self.junction_id,
            'x': self.x,
            'y': self.y,
            'phase_group': self.phase_group,
        }

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise ValueError("Junction data must be dict")
        try:
            j = cls(
                float(d.get('x', 0)),
                float(d.get('y', 0)),
                str(d.get('id', '')) or None,
            )
            j.phase_group = d.get('phase_group')
            return j
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid Junction values: " + str(d)) from e


class LineSegment:
    """Independent line segment. Always H or V."""

    _counter = 0

    def __init__(self, x1, y1, x2, y2, line_id=None):
        if line_id is None:
            LineSegment._counter += 1
            line_id = "L_%03d" % LineSegment._counter
        else:
            try:
                parts = line_id.split('_')
                num = int(parts[-1])
                if num > LineSegment._counter:
                    LineSegment._counter = num
            except (ValueError, IndexError):
                pass

        self.line_id = line_id

        # Force H or V (no diagonals allowed)
        x1 = float(x1); y1 = float(y1)
        x2 = float(x2); y2 = float(y2)
        if abs(x2 - x1) >= abs(y2 - y1):
            y2 = y1  # horizontal
        else:
            x2 = x1  # vertical

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.selected = False
        self.phase_group = None

    @property
    def is_horizontal(self):
        return abs(self.y1 - self.y2) < 0.01

    @property
    def is_vertical(self):
        return abs(self.x1 - self.x2) < 0.01

    @property
    def is_deletable(self):
        return True

    def length(self):
        return hypot(self.x2 - self.x1, self.y2 - self.y1)

    def endpoints(self):
        return (self.x1, self.y1), (self.x2, self.y2)

    def rename_with_group(self, group):
        """Update id to include group prefix."""
        parts = self.line_id.split('_')
        if len(parts) >= 3 and parts[1] in ('R', 'U'):
            num = parts[2]
        elif len(parts) == 2:
            num = parts[1]
        else:
            num = parts[-1]

        if group == 'R':
            self.line_id = "L_R_" + num
        elif group == 'U':
            self.line_id = "L_U_" + num
        else:
            self.line_id = "L_" + num

    def to_dict(self):
        return {
            'id': self.line_id,
            'x1': self.x1, 'y1': self.y1,
            'x2': self.x2, 'y2': self.y2,
            'phase_group': self.phase_group,
        }

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise ValueError("LineSegment data must be dict")
        try:
            ls = cls(
                float(d.get('x1', 0)),
                float(d.get('y1', 0)),
                float(d.get('x2', 0)),
                float(d.get('y2', 0)),
                str(d.get('id', '')) or None,
            )
            ls.phase_group = d.get('phase_group')
            return ls
        except (ValueError, TypeError) as e:
            raise ValueError("Invalid LineSegment values: " + str(d)) from e