"""
================================================================================
File: core/rendering/canvas_backend.py
Purpose: Draws lines/coils/rects to a Kivy InstructionGroup.
Version: 0.1.1
================================================================================
"""

from kivy.graphics import Color, Line, Rectangle


class CanvasBackend:

    def __init__(self, group, world_to_screen):
        self.group = group
        self.world_to_screen = world_to_screen

    def clear(self):
        pass

    def is_ready(self):
        return True

    def line(self, x1, y1, x2, y2, color, width=1):
        sx1, sy1 = self.world_to_screen(x1, y1)
        sx2, sy2 = self.world_to_screen(x2, y2)
        self.group.add(Color(*color))
        self.group.add(Line(points=[sx1, sy1, sx2, sy2], width=width))

    def coil(self, x_start, x_end, y_vals, color, width=2):
        if len(y_vals) < 4:
            return
        xc = x_start + (x_end - x_start) / 2
        self.group.add(Color(*color))
        if len(y_vals) == 4:
            pts = [
                (x_start, y_vals[0], x_start, y_vals[1]),
                (x_start, y_vals[1], x_end, y_vals[2]),
                (x_end, y_vals[2], x_end, y_vals[3]),
            ]
        else:
            pts = [
                (x_start, y_vals[0], x_start, y_vals[1]),
                (x_start, y_vals[1], xc, y_vals[2]),
                (xc, y_vals[2], x_end, y_vals[3]),
                (x_end, y_vals[3], x_end, y_vals[4]),
            ]
        for (ax1, ay1, ax2, ay2) in pts:
            sx1, sy1 = self.world_to_screen(ax1, ay1)
            sx2, sy2 = self.world_to_screen(ax2, ay2)
            self.group.add(Line(points=[sx1, sy1, sx2, sy2], width=width))

    def rect(self, x, y, w, h, color, filled=True):
        sx, sy = self.world_to_screen(x, y)
        sx2, sy2 = self.world_to_screen(x + w, y + h)
        self.group.add(Color(*color))
        if filled:
            self.group.add(Rectangle(
                pos=(min(sx, sx2), min(sy, sy2)),
                size=(abs(sx2 - sx), abs(sy2 - sy))
            ))
        else:
            pts = [sx, sy, sx2, sy, sx2, sy2, sx, sy2, sx, sy]
            self.group.add(Line(points=pts, width=1))

    def text(self, *args, **kwargs):
        pass

    def image(self, *args, **kwargs):
        pass

    def set_view_state(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        return False