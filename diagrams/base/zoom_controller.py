"""
================================================================================
File: diagrams/base/zoom_controller.py
Purpose: Zoom, pan, pinch, zoom-history, zoom-box controller.
Version: 0.1.2
================================================================================
"""

from kivy.core.window import Window
from math import hypot

from core.view_transform import ViewTransform

from utils.constants import (
    ZOOM_MIN, ZOOM_MAX, ZOOM_STEP,
    ZOOM_BOX_MIN_SIZE,
    PAN_BOUNDS_MARGIN_PX,
)


class ZoomController:

    def __init__(self, diagram):
        self.diagram = diagram
        self.view = ViewTransform()
        self.view._diagram = diagram  # link for delegation

        self.touch_list = []
        self.pinch_ids = []
        self.pinch_start_dist = 0.0
        self.pinch_start_scale = 1.0
        self.pinch_center_world = None
        self.pan_start_offset = None
        self.pan_start_pos = None
        self._touch_on_point = False

        self.zoom_box_active = False
        self.zoom_box_start = None
        self.zoom_box_current = None

    def sync(self):
        d = self.diagram
        self.view.grid_x_min = d.GRID_x_min
        self.view.grid_y_min = d.GRID_y_min
        self.view.cell_size_px = d.GRID_cell_size_px
        self.view.screen_scale = d.SCREEN_scale
        self.view.offset_x = d.SCREEN_offset_x
        self.view.offset_y = d.SCREEN_offset_y
        self.view.margin_px = 0
        self.view.page_width_px = d.PAGE_width_px
        self.view.page_height_px = d.PAGE_height_px
        self.view.invalidate()

    def auto_fit_scale(self):
        d = self.diagram
        if d.PAGE_width_px > 0:
            return min(Window.width / d.PAGE_width_px,
                       Window.height / max(d.PAGE_height_px, 1))
        return 1.0

    def clamp_offsets(self):
        d = self.diagram
        s = d.SCREEN_scale
        margin = PAN_BOUNDS_MARGIN_PX

        paper_x = d.SCREEN_offset_x
        paper_y = d.SCREEN_offset_y
        paper_w = d.PAGE_width_px * s
        paper_h = d.PAGE_height_px * s

        min_x = margin - paper_w
        max_x = Window.width - margin
        min_y = margin - paper_h
        max_y = Window.height - margin

        new_paper_x = max(min_x, min(paper_x, max_x))
        new_paper_y = max(min_y, min(paper_y, max_y))

        d.SCREEN_offset_x = new_paper_x
        d.SCREEN_offset_y = new_paper_y

    def auto_fit(self):
        d = self.diagram
        d.SCREEN_scale = self.auto_fit_scale()
        d.SCREEN_offset_x = 0.0
        d.SCREEN_offset_y = 0.0
        self.sync()

    def zoom_all(self):
        self.view.push_zoom_history()
        self.auto_fit()

    def zoom_in(self, anchor_screen=None):
        self._zoom_step(ZOOM_STEP, anchor_screen)

    def zoom_out(self, anchor_screen=None):
        self._zoom_step(1.0 / ZOOM_STEP, anchor_screen)

    def _zoom_step(self, factor, anchor_screen=None):
        d = self.diagram
        old_scale = d.SCREEN_scale
        new_scale = old_scale * factor

        min_scale = self.auto_fit_scale()
        if new_scale < min_scale:
            new_scale = min_scale
        if new_scale > ZOOM_MAX:
            new_scale = ZOOM_MAX
        if abs(new_scale - old_scale) < 0.0001:
            return

        if anchor_screen is None:
            anchor_screen = (Window.width / 2, Window.height / 2)

        anchor_world = self.view.screen_to_world(*anchor_screen)

        self.view.push_zoom_history()

        d.SCREEN_scale = new_scale
        self.sync()

        new_anchor = self.view.world_to_screen(*anchor_world)
        d.SCREEN_offset_x += anchor_screen[0] - new_anchor[0]
        d.SCREEN_offset_y += anchor_screen[1] - new_anchor[1]

        self.clamp_offsets()
        self.sync()

    def zoom_back(self):
        if self.view.pop_zoom_history_back():
            d = self.diagram
            d.SCREEN_scale = self.view.screen_scale
            d.SCREEN_offset_x = self.view.offset_x
            d.SCREEN_offset_y = self.view.offset_y
            self.sync()
            return True
        return False

    def zoom_redo(self):
        if self.view.pop_zoom_history_redo():
            d = self.diagram
            d.SCREEN_scale = self.view.screen_scale
            d.SCREEN_offset_x = self.view.offset_x
            d.SCREEN_offset_y = self.view.offset_y
            self.sync()
            return True
        return False

    def zoom_reset(self):
        self.view.clear_zoom_history()
        self.auto_fit()

    def activate_zoom_box(self, active=None):
        if active is None:
            active = not self.zoom_box_active
        self.zoom_box_active = active
        self.zoom_box_start = None
        self.zoom_box_current = None

    def apply_zoom_box(self, sx1, sy1, sx2, sy2):
        d = self.diagram
        if (abs(sx2 - sx1) < ZOOM_BOX_MIN_SIZE or
                abs(sy2 - sy1) < ZOOM_BOX_MIN_SIZE):
            return

        xmin, xmax = min(sx1, sx2), max(sx1, sx2)
        ymin, ymax = min(sy1, sy2), max(sy1, sy2)
        box_w = xmax - xmin
        box_h = ymax - ymin

        cx = (xmin + xmax) / 2
        cy = (ymin + ymax) / 2

        # Get world coords of box center (delegates to diagram)
        world_x, world_y = self.view.screen_to_world(cx, cy)

        self.view.push_zoom_history()

        new_sx = (Window.width * 0.9) / box_w * d.SCREEN_scale
        new_sy = (Window.height * 0.9) / box_h * d.SCREEN_scale
        new_scale = min(new_sx, new_sy)

        min_scale = self.auto_fit_scale()
        new_scale = max(min_scale, min(ZOOM_MAX, new_scale))

        d.SCREEN_scale = new_scale

        # Compute offset so that world point appears at screen center
        # using DIAGRAM's exact formula
        from diagrams.base.diagram_base import mm_to_px
        layout = d._layout_mm()
        grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']
        grid_x_px = mm_to_px(grid_x_mm)
        grid_y_px = mm_to_px(grid_y_mm)
        grid_w_px = mm_to_px(grid_w_mm)
        grid_h_px = mm_to_px(grid_h_mm)

        x_range = d.GRID_x_max - d.GRID_x_min
        y_range = d.GRID_y_max - d.GRID_y_min

        fraction_x = (world_x - d.GRID_x_min) / max(x_range, 0.0001)
        fraction_y = (world_y - d.GRID_y_min) / max(y_range, 0.0001)

        px_x = grid_x_px + fraction_x * grid_w_px
        px_y = grid_y_px + fraction_y * grid_h_px

        target_sx = Window.width / 2
        target_sy = Window.height / 2

        d.SCREEN_offset_x = target_sx - px_x * new_scale
        d.SCREEN_offset_y = target_sy - px_y * new_scale

        self.clamp_offsets()
        self.sync()

    def get_zoom_anchor(self):
        d = self.diagram
        if d._drag_target is not None:
            return d.world_to_screen(d._drag_target.x, d._drag_target.y)
        if d._pencil_current is not None:
            return d.world_to_screen(*d._pencil_current)

        conn = d.connection
        if d.connection_mode_active():
            for j in conn.junctions:
                if j.junction_id in conn.selection.junction_ids:
                    return d.world_to_screen(j.x, j.y)
            for wp in conn.wire_points:
                if wp.wire_id in conn.selection.wire_ids:
                    return d.world_to_screen(wp.x, wp.y)
        return (Window.width / 2, Window.height / 2)

    def on_touch_down(self, touch):
        self.touch_list.append(touch)
        if len(self.touch_list) == 2:
            self.pinch_ids = [t.uid for t in self.touch_list]
            p1, p2 = self.touch_list[0].pos, self.touch_list[1].pos
            self.pinch_start_dist = hypot(p1[0] - p2[0], p1[1] - p2[1])
            self.pinch_start_scale = self.diagram.SCREEN_scale
            cx = (p1[0] + p2[0]) / 2
            cy = (p1[1] + p2[1]) / 2
            self.pinch_center_world = self.view.screen_to_world(cx, cy)
            self.view.push_zoom_history()
        else:
            self.pan_start_offset = (self.diagram.SCREEN_offset_x,
                                      self.diagram.SCREEN_offset_y)
            self.pan_start_pos = touch.pos
        return True

    def on_touch_move(self, touch):
        d = self.diagram

        if touch.uid in self.pinch_ids and len(self.touch_list) == 2:
            p1, p2 = self.touch_list[0].pos, self.touch_list[1].pos
            dist = hypot(p1[0] - p2[0], p1[1] - p2[1])
            if self.pinch_start_dist > 0:
                factor = dist / self.pinch_start_dist
                new_scale = self.pinch_start_scale * factor

                min_scale = self.auto_fit_scale()
                new_scale = max(min_scale, min(ZOOM_MAX, new_scale))

                if abs(new_scale - d.SCREEN_scale) > 0.001:
                    d.SCREEN_scale = new_scale
                    self.sync()

                    if self.pinch_center_world is not None:
                        cx = (p1[0] + p2[0]) / 2
                        cy = (p1[1] + p2[1]) / 2
                        new_anchor = self.view.world_to_screen(
                            *self.pinch_center_world
                        )
                        d.SCREEN_offset_x += cx - new_anchor[0]
                        d.SCREEN_offset_y += cy - new_anchor[1]
                    self.clamp_offsets()
                    self.sync()
            return True

        if self.pan_start_pos and not self._touch_on_point:
            dx = touch.pos[0] - self.pan_start_pos[0]
            dy = touch.pos[1] - self.pan_start_pos[1]
            new_x = self.pan_start_offset[0] + dx
            new_y = self.pan_start_offset[1] + dy
            if (new_x, new_y) != (d.SCREEN_offset_x, d.SCREEN_offset_y):
                d.SCREEN_offset_x = new_x
                d.SCREEN_offset_y = new_y
                self.clamp_offsets()
                self.sync()
            return True

        return False

    def on_touch_up(self, touch):
        if touch in self.touch_list:
            self.touch_list.remove(touch)
        if touch.uid in self.pinch_ids:
            self.pinch_ids.remove(touch.uid)
        if len(self.touch_list) == 0:
            self.pinch_start_dist = 0
            self.pinch_center_world = None
            self.pan_start_offset = None
            self.pan_start_pos = None
            self._touch_on_point = False
