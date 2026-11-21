"""
================================================================================
File: core/view_transform.py
Purpose: View transform that delegates to diagram.
         This guarantees NO mismatch between drawing and touch.
Version: 0.1.6
================================================================================
"""

from utils.constants import ZOOM_HISTORY_SIZE


class ViewTransform:
    """
    World <-> Screen transform.
    DELEGATES to diagram when available (safe, no mismatch).
    Falls back to internal formula if diagram is None.
    """

    def __init__(self):
        # Reference to diagram (set by zoom_controller)
        self._diagram = None

        # Fallback state (used only if _diagram is None)
        self.grid_x_min = 0
        self.grid_y_min = 0
        self.cell_size_px = 10.0
        self.screen_scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.margin_px = 30.0

        self.page_width_px = 1
        self.page_height_px = 1

        # Cache (only used in fallback mode)
        self._cache = {}
        self._version = 0

        # Zoom history
        self._undo_stack = []
        self._redo_stack = []

    def invalidate(self):
        self._cache.clear()
        self._version += 1

    # ============================================================
    # ================== WORLD <-> SCREEN ========================
    # ============================================================

    def world_to_screen(self, x, y):
        """Convert world → screen pixels."""
        # DELEGATE to diagram (safest)
        if self._diagram is not None:
            return self._diagram.world_to_screen(x, y)

        # Fallback: internal formula
        key = (round(x, 2), round(y, 2), self._version)
        c = self._cache.get(key)
        if c is not None:
            return c

        sx = (self.margin_px +
              (x - self.grid_x_min) * self.cell_size_px * self.screen_scale +
              self.offset_x)
        sy = (self.margin_px +
              (y - self.grid_y_min) * self.cell_size_px * self.screen_scale +
              self.offset_y)
        result = (sx, sy)
        self._cache[key] = result
        return result

    def screen_to_world(self, sx, sy):
        """Convert screen pixels → world."""
        # DELEGATE to diagram
        if self._diagram is not None:
            return self._diagram.screen_to_world(sx, sy)

        # Fallback
        x = ((sx - self.margin_px - self.offset_x) /
             (self.cell_size_px * self.screen_scale) + self.grid_x_min)
        y = ((sy - self.margin_px - self.offset_y) /
             (self.cell_size_px * self.screen_scale) + self.grid_y_min)
        return x, y

    # ============================================================
    # ================== ZOOM HISTORY ===========================
    # ============================================================

    def _state(self):
        return (self.screen_scale, self.offset_x, self.offset_y)

    def push_zoom_history(self):
        state = self._state()
        if self._undo_stack and self._undo_stack[-1] == state:
            return
        self._undo_stack.append(state)
        if len(self._undo_stack) > ZOOM_HISTORY_SIZE:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def pop_zoom_history_back(self):
        if not self._undo_stack:
            return False
        self._redo_stack.append(self._state())
        if len(self._redo_stack) > ZOOM_HISTORY_SIZE:
            self._redo_stack.pop(0)
        scale, ox, oy = self._undo_stack.pop()
        self.screen_scale = scale
        self.offset_x = ox
        self.offset_y = oy
        self.invalidate()
        return True

    def pop_zoom_history_redo(self):
        if not self._redo_stack:
            return False
        self._undo_stack.append(self._state())
        scale, ox, oy = self._redo_stack.pop()
        self.screen_scale = scale
        self.offset_x = ox
        self.offset_y = oy
        self.invalidate()
        return True

    def clear_zoom_history(self):
        self._undo_stack.clear()
        self._redo_stack.clear()

    def has_zoom_back(self):
        return len(self._undo_stack) > 0

    def has_zoom_redo(self):
        return len(self._redo_stack) > 0
