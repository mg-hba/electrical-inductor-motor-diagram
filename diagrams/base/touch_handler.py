"""
================================================================================
File: diagrams/base/touch_handler.py
Purpose: Central touch dispatcher for diagram canvas.
         Subtracts shift_y from touch world coords when in connection mode
         so pencil/drag use absolute coordinates (no shift).
Version: 0.1.3
================================================================================
"""

from kivy.core.window import Window
import time


class TouchHandler:

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, diagram):
        self.diagram = diagram

        self._last_tap_time = 0
        self._last_tap_pos = (0, 0)
        self._double_tap_threshold = 0.35
        self._double_tap_distance = 40
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########on_touch_down############
    ###################################
    def on_touch_down(self, touch):
        d = self.diagram
        if not d.collide_point(*touch.pos):
            return False

        if self._is_double_tap(touch):
            if d.connection_mode_active():
                d.connection.clear_selection()
                d._rebuild_all()
            self._last_tap_time = 0
            return True

        d._touch_on_point = False

        if d.edit_mode_active:
            if d.handle_edit_touch_down(touch):
                return True

        zc = d.zoom_controller
        if zc.zoom_box_active:
            zc.zoom_box_start = touch.pos
            zc.zoom_box_current = touch.pos
            d._rebuild_overlay()
            return True

        if d.connection_mode_active():
            wx_raw, wy_raw = d.screen_to_world(*touch.pos)
            shift = getattr(d.connection, 'shift_y', 0.0)
            wx = wx_raw
            wy = wy_raw - shift

            if d.connection.pencil_mode:
                d._pencil_start = (wx, wy)
                d._pencil_current = (wx, wy)
                d._rebuild_overlay()
                return True

            if d.connection.select_box_mode:
                d._box_start = (wx, wy)
                d._box_current = (wx, wy)
                d._rebuild_overlay()
                return True

            hit = d.connection.handle_touch_down_world(
                wx, wy, d.SCREEN_scale, d.GRID_cell_size_px
            )
            if hit is not None:
                kind, obj = hit
                if kind == 'junction':
                    d._drag_target = obj
                    d._drag_start_world = (wx, wy)
                    d._touch_on_point = True
                    return True
                else:
                    d.connection.apply_hit(hit)
                    d._rebuild_all()
                    return True

        d.zoom_controller._touch_on_point = d._touch_on_point
        d.zoom_controller.on_touch_down(touch)
        return True
    ###################################
    ##########end of on_touch_down####
    ###################################

    ###################################
    ##########on_touch_move############
    ###################################
    def on_touch_move(self, touch):
        d = self.diagram
        zc = d.zoom_controller

        if d.edit_mode_active and d.edit_drag_target is not None:
            d.handle_edit_touch_move(touch)
            return True

        if zc.zoom_box_active and zc.zoom_box_start is not None:
            zc.zoom_box_current = touch.pos
            d._rebuild_overlay()
            return True

        if d._drag_target is not None:
            wx_raw, wy_raw = d.screen_to_world(*touch.pos)
            shift = getattr(d.connection, 'shift_y', 0.0)
            d.connection.move_point(d._drag_target, round(wx_raw),
                                     round(wy_raw - shift))
            d._rebuild_all()
            return True

        if d._pencil_start is not None:
            wx_raw, wy_raw = d.screen_to_world(*touch.pos)
            shift = getattr(d.connection, 'shift_y', 0.0)
            d._pencil_current = (wx_raw, wy_raw - shift)
            d.zoom_controller.sync()
            d._rebuild_overlay()
            return True

        if d._box_start is not None:
            wx_raw, wy_raw = d.screen_to_world(*touch.pos)
            shift = getattr(d.connection, 'shift_y', 0.0)
            d._box_current = (wx_raw, wy_raw - shift)
            d.zoom_controller.sync()
            d._rebuild_overlay()
            return True

        if zc.on_touch_move(touch):
            d._rebuild_all()
            return True
        return True
    ###################################
    ##########end of on_touch_move####
    ###################################

    ###################################
    ##########on_touch_up##############
    ###################################
    def on_touch_up(self, touch):
        d = self.diagram
        zc = d.zoom_controller

        if d.edit_mode_active:
            if d.handle_edit_touch_up(touch):
                return True

        if zc.zoom_box_active and zc.zoom_box_start is not None:
            if zc.zoom_box_current is not None:
                x1, y1 = zc.zoom_box_start
                x2, y2 = zc.zoom_box_current
                zc.apply_zoom_box(x1, y1, x2, y2)
            zc.zoom_box_start = None
            zc.zoom_box_current = None
            d._rebuild_all()
            return True

        if d._drag_target is not None:
            d._drag_target = None
            d._drag_start_world = None
            d._rebuild_all()
            return True

        if d._pencil_start is not None:
            x1, y1 = d._pencil_start
            if d._pencil_current is not None:
                x2, y2 = d._pencil_current
                d.connection.draw_pencil_line(x1, y1, x2, y2)
            d._pencil_start = None
            d._pencil_current = None
            d._rebuild_all()
            return True

        if d._box_start is not None:
            if d._box_current is not None:
                x1, y1 = d._box_start
                x2, y2 = d._box_current
                if abs(x2 - x1) > 0.5 or abs(y2 - y1) > 0.5:
                    d.connection.apply_box_select(x1, y1, x2, y2)
            d._box_start = None
            d._box_current = None
            d._rebuild_all()
            return True

        zc.on_touch_up(touch)
        return True
    ###################################
    ##########end of on_touch_up######
    ###################################

    def _is_double_tap(self, touch):
        now = time.time()
        dt = now - self._last_tap_time
        dx = abs(touch.pos[0] - self._last_tap_pos[0])
        dy = abs(touch.pos[1] - self._last_tap_pos[1])
        is_double = (dt < self._double_tap_threshold and
                     dx < self._double_tap_distance and
                     dy < self._double_tap_distance)
        self._last_tap_time = now
        self._last_tap_pos = touch.pos
        return is_double
    ###################################
    ##########end of _is_double_tap####
    ###################################