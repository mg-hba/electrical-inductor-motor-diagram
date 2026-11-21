"""
================================================================================
File: diagrams/motor_common/base_diagram.py
Purpose: Main BaseMotorDiagram class (coordinator).
         Delegates work to diagram_cutting, diagram_edit_mode,
         diagram_labels, diagram_table, diagram_connection.
         Contains shared methods used by TwoLayerMotorDiagram
         and SingleLayerMotorDiagram.
Version: 0.1.4
================================================================================
"""

from kivy.uix.label import Label

from managers.json_manager import json_manager
from managers.debug_logger import debug_logger
from diagrams.base.diagram_base import (
    DiagramBase, get_speed, get_paper_dimensions, mm_to_px,
)

from diagrams.motor_common.diagram_cutting import (
    wrap_coil_segments, cut_coil_points,
)
from diagrams.motor_common.diagram_edit_mode import (
    enter_edit_mode as _enter_edit_mode,
    exit_edit_mode as _exit_edit_mode,
    apply_edit_shifts as _apply_edit_shifts,
    reset_edit_shifts as _reset_edit_shifts,
    get_edit_diamonds as _get_edit_diamonds,
    draw_edit_diamonds as _draw_edit_diamonds,
    handle_edit_touch_down as _handle_edit_touch_down,
    handle_edit_touch_move as _handle_edit_touch_move,
    handle_edit_touch_up as _handle_edit_touch_up,
)
from diagrams.motor_common.diagram_labels import (
    calculate_slot_numbers as _calculate_slot_numbers,
    get_font_size_for_slot as _get_font_size_for_slot,
    rebuild_slot_labels as _rebuild_slot_labels,
    update_slot_labels as _update_slot_labels,
    ensure_slot_labels_visible as _ensure_slot_labels_visible,
    update_phase_labels as _update_phase_labels,
    get_motor_name_text as _get_motor_name_text,
    update_motor_name_label as _update_motor_name_label,
    update_labels as _update_labels,
)
from diagrams.motor_common.diagram_table import (
    get_table_geometry as _get_table_geometry,
    get_table_data as _get_table_data,
    rebuild_table_labels as _rebuild_table_labels,
    update_table_labels as _update_table_labels,
    draw_table as _draw_table,
    draw_table_lines as _draw_table_lines,
    export_table_text as _export_table_text,
    get_table_font_size as _get_table_font_size,
    get_table_text_color as _get_table_text_color,
    get_table_bg_color as _get_table_bg_color,
)
from diagrams.motor_common.diagram_connection import (
    restore_connections_from_project as _restore_connections_from_project,
    set_connection_mode as _set_connection_mode,
    handle_connection_touch_down as _handle_connection_touch_down,
)

from utils.constants import (
    ENABLE_INFO_TABLE, ENABLE_SLOT_NUMBERS, X_SHIFT,
)


class BaseMotorDiagram(DiagramBase):

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Shared state used by TwoLayer / SingleLayer diagrams
        self.rotated = False
        self.diagram_enabled = False

        self.TABLE_labels = []
        self.TABLE_cells = []
        self.TABLE_last_hash = None
        self.TABLE_last_level = -1

        self.SLOT_labels = []
        self.SLOT_last_level = -1
        self.SLOT_numbers_cache = {}
        self.SLOT_numbers_export_cache = None

        self.PHASE_labels = []
        self.MOTOR_NAME_label = None

        self.current_level = self.get_zoom_level()

        self.edit_mode_active = False
        self._canvas_initialized = False
        self.edit_drag_target = None
        self.edit_drag_start_y = None
        self.edit_current_main_shift = 0.0
        self.edit_current_phase_shift = 0.0

        debug_logger.log_draw(
            "INIT", "BaseMotorDiagram initialized", "Base"
        )
    ###################################
    ##########end of __init__#########
    ###################################

    # ============================================================
    # ================== SHARED SUBCLASS METHODS =================
    # ============================================================

    ###################################
    ##########_get_pattern#############
    ###################################
    def _get_pattern(self):
        """Return the currently active coil pattern instance."""
        from diagrams.patterns.registry import PatternRegistry
        pattern_id = json_manager.get_last_coil_pattern() or 'lap'
        return PatternRegistry.get(pattern_id)
    ###################################
    ##########end of _get_pattern#####
    ###################################

    ###################################
    ##########_diagram_shift###########
    ###################################
    def _diagram_shift(self):
        """Main diagram vertical shift (edit-mode aware)."""
        if self.edit_mode_active:
            return self.edit_current_main_shift
        return json_manager.get_main_diagram_shift_y()
    ###################################
    ##########end of _diagram_shift####
    ###################################

    ###################################
    ##########_phase_diagram_shift#####
    ###################################
    def _phase_diagram_shift(self):
        """Phase diagram vertical shift (edit-mode aware)."""
        if self.edit_mode_active:
            return self.edit_current_phase_shift
        return json_manager.get_phase_diagram_shift_y()
    ###################################
    ##########end of _phase_diagram_shift
    ###################################

    ###################################
    ##########toggle_rotation##########
    ###################################
    def toggle_rotation(self):
        """Rotate diagram 90 degrees and re-fit."""
        self.rotated = not self.rotated
        self.auto_fit()
    ###################################
    ##########end of toggle_rotation##
    ###################################

    ###################################
    ##########clear_diagram############
    ###################################
    def clear_diagram(self):
        """Hide the diagram (does not clear project data)."""
        self.diagram_enabled = False
        self.redraw()
    ###################################
    ##########end of clear_diagram#####
    ###################################

    ###################################
    ##########_draw_coil_segments######
    ###################################
    def _draw_coil_segments(self, backends, x_start, x_end,
                            color, line_width, y_vals, shift,
                            x_peak_world=None):
        """
        Draw one coil. Handles wrapping, cutting, and rotation.
        Used by both SingleLayer and TwoLayer draw_diagram.

        backends: list of render backends (CanvasBackend + VectorBackend)
        x_start, x_end: coil slot positions (world)
        color, line_width: drawing style
        y_vals: list of y values (4 or 5 points)
        shift: vertical shift
        x_peak_world: optional peak x for concentric pattern
        """
        y_offset = self.get_diagram_area_bottom()
        y_shifted = [y + shift + y_offset for y in y_vals]
        segments = self._wrap_coil_segments(x_start, x_end, y_shifted)

        for (segment_start, segment_end, segment_y_vals,
             is_wrapped) in segments:
            x1 = segment_start + X_SHIFT
            x2 = segment_end + X_SHIFT

            if len(segment_y_vals) == 4:
                points = [
                    (x1, segment_y_vals[0]),
                    (x1, segment_y_vals[1]),
                    (x2, segment_y_vals[2]),
                    (x2, segment_y_vals[3]),
                ]
            else:
                if x_peak_world is not None:
                    xc_base = x_peak_world
                    if is_wrapped:
                        xc_base = xc_base - self.MOTOR_all_slots
                    xc = xc_base + X_SHIFT
                else:
                    xc = x1 + (x2 - x1) * 0.5
                points = [
                    (x1, segment_y_vals[0]),
                    (x1, segment_y_vals[1]),
                    (xc, segment_y_vals[2]),
                    (x2, segment_y_vals[3]),
                    (x2, segment_y_vals[4]),
                ]

            cut_points = self._cut_coil_points(points)

            for i in range(len(cut_points) - 1):
                ax1, ay1 = cut_points[i]
                ax2, ay2 = cut_points[i + 1]
                if abs(ax2 - ax1) < 0.001 and abs(ay2 - ay1) < 0.001:
                    continue
                if self.rotated:
                    for backend in backends:
                        backend.line(ay1, ax1, ay2, ax2, color, line_width)
                else:
                    for backend in backends:
                        backend.line(ax1, ay1, ax2, ay2, color, line_width)
    ###################################
    ##########end of _draw_coil_segments
    ###################################

    ###################################
    ##########clear_caches#############
    ###################################
    def clear_caches(self):
        self.TABLE_last_hash = None
        self.TABLE_last_level = -1
        self.SLOT_last_level = -1
        self.SLOT_numbers_cache = {}
        self.SLOT_numbers_export_cache = None

        for label in self.TABLE_labels:
            self.remove_widget(label)
        self.TABLE_labels = []
        self.TABLE_cells = []

        for label in self.SLOT_labels:
            self.remove_widget(label)
        self.SLOT_labels = []

        for label in self.PHASE_labels:
            self.remove_widget(label)
        self.PHASE_labels = []

        if self.MOTOR_NAME_label is not None:
            self.remove_widget(self.MOTOR_NAME_label)
            self.MOTOR_NAME_label = None
    ###################################
    ##########end of clear_caches#####
    ###################################

    ###################################
    ##########_wrap_coil_segments######
    ###################################
    def _wrap_coil_segments(self, coil_start, coil_end, y_values):
        return wrap_coil_segments(self, coil_start, coil_end, y_values)
    ###################################
    ##########end of _wrap_coil_segments
    ###################################

    ###################################
    ##########_cut_coil_points#########
    ###################################
    def _cut_coil_points(self, points):
        return cut_coil_points(self, points)
    ###################################
    ##########end of _cut_coil_points##
    ###################################

    ###################################
    ##########get_diagram_area_bottom##
    ###################################
    def get_diagram_area_bottom(self):
        return self.GRID_y_min
    ###################################
    ##########end of get_diagram_area_bottom
    ###################################

    ###################################
    ##########get_diagram_area_top#####
    ###################################
    def get_diagram_area_top(self):
        return self.GRID_y_max
    ###################################
    ##########end of get_diagram_area_top
    ###################################

    ###################################
    ##########enter_edit_mode##########
    ###################################
    def enter_edit_mode(self):
        _enter_edit_mode(self)
    ###################################
    ##########end of enter_edit_mode##
    ###################################

    ###################################
    ##########exit_edit_mode###########
    ###################################
    def exit_edit_mode(self):
        _exit_edit_mode(self)
    ###################################
    ##########end of exit_edit_mode###
    ###################################

    ###################################
    ##########apply_edit_shifts########
    ###################################
    def apply_edit_shifts(self):
        _apply_edit_shifts(self)
    ###################################
    ##########end of apply_edit_shifts
    ###################################

    ###################################
    ##########reset_edit_shifts########
    ###################################
    def reset_edit_shifts(self):
        _reset_edit_shifts(self)
    ###################################
    ##########end of reset_edit_shifts
    ###################################

    ###################################
    ##########_get_edit_diamonds#######
    ###################################
    def _get_edit_diamonds(self):
        return _get_edit_diamonds(self)
    ###################################
    ##########end of _get_edit_diamonds
    ###################################

    ###################################
    ##########_draw_edit_diamonds######
    ###################################
    def _draw_edit_diamonds(self):
        return _draw_edit_diamonds(self)
    ###################################
    ##########end of _draw_edit_diamonds
    ###################################

    ###################################
    ##########handle_edit_touch_down###
    ###################################
    def handle_edit_touch_down(self, touch):
        return _handle_edit_touch_down(self, touch)
    ###################################
    ##########end of handle_edit_touch_down
    ###################################

    ###################################
    ##########handle_edit_touch_move###
    ###################################
    def handle_edit_touch_move(self, touch):
        return _handle_edit_touch_move(self, touch)
    ###################################
    ##########end of handle_edit_touch_move
    ###################################

    ###################################
    ##########handle_edit_touch_up#####
    ###################################
    def handle_edit_touch_up(self, touch):
        return _handle_edit_touch_up(self, touch)
    ###################################
    ##########end of handle_edit_touch_up
    ###################################

    ###################################
    ##########_calculate_slot_numbers##
    ###################################
    def _calculate_slot_numbers(self, level, is_export=False):
        return _calculate_slot_numbers(self, level, is_export)
    ###################################
    ##########end of _calculate_slot_numbers
    ###################################

    ###################################
    ##########_get_font_size_for_slot##
    ###################################
    def _get_font_size_for_slot(self):
        return _get_font_size_for_slot(self)
    ###################################
    ##########end of _get_font_size_for_slot
    ###################################

    ###################################
    ##########_update_labels############
    ###################################
    def _update_labels(self):
        if ENABLE_SLOT_NUMBERS:
            _update_slot_labels(self)
        if ENABLE_INFO_TABLE:
            _update_table_labels(self)
        _update_phase_labels(self)
        _update_motor_name_label(self)
    ###################################
    ##########end of _update_labels####
    ###################################

    ###################################
    ##########_rebuild_slot_labels#####
    ###################################
    def _rebuild_slot_labels(self):
        _rebuild_slot_labels(self)
    ###################################
    ##########end of _rebuild_slot_labels
    ###################################

    ###################################
    ##########_update_slot_labels######
    ###################################
    def _update_slot_labels(self):
        _update_slot_labels(self)
    ###################################
    ##########end of _update_slot_labels
    ###################################

    ###################################
    ##########_ensure_slot_labels_visible
    ###################################
    def _ensure_slot_labels_visible(self):
        _ensure_slot_labels_visible(self)
    ###################################
    ##########end of _ensure_slot_labels_visible
    ###################################

    ###################################
    ##########_update_motor_name_label##
    ###################################
    def _update_motor_name_label(self):
        _update_motor_name_label(self)
    ###################################
    ##########end of _update_motor_name_label
    ###################################

    ###################################
    ##########_get_motor_name_text######
    ###################################
    def _get_motor_name_text(self):
        return _get_motor_name_text(self)
    ###################################
    ##########end of _get_motor_name_text
    ###################################

    ###################################
    ##########_update_phase_labels######
    ###################################
    def _update_phase_labels(self):
        _update_phase_labels(self)
    ###################################
    ##########end of _update_phase_labels
    ###################################

    ###################################
    ##########_get_table_geometry######
    ###################################
    def _get_table_geometry(self):
        return _get_table_geometry(self)
    ###################################
    ##########end of _get_table_geometry
    ###################################

    ###################################
    ##########_get_table_data###########
    ###################################
    def _get_table_data(self):
        return _get_table_data(self)
    ###################################
    ##########end of _get_table_data###
    ###################################

    ###################################
    ##########_get_table_font_size#####
    ###################################
    def _get_table_font_size(self, row_type):
        return _get_table_font_size(self, row_type)
    ###################################
    ##########end of _get_table_font_size
    ###################################

    ###################################
    ##########_get_table_text_color####
    ###################################
    def _get_table_text_color(self, row_type):
        return _get_table_text_color(row_type)
    ###################################
    ##########end of _get_table_text_color
    ###################################

    ###################################
    ##########_get_table_bg_color######
    ###################################
    def _get_table_bg_color(self, row_type):
        return _get_table_bg_color(row_type)
    ###################################
    ##########end of _get_table_bg_color
    ###################################

    ###################################
    ##########_rebuild_table_labels####
    ###################################
    def _rebuild_table_labels(self):
        _rebuild_table_labels(self)
    ###################################
    ##########end of _rebuild_table_labels
    ###################################

    ###################################
    ##########_update_table_labels#####
    ###################################
    def _update_table_labels(self):
        _update_table_labels(self)
    ###################################
    ##########end of _update_table_labels
    ###################################

    ###################################
    ##########draw_table###############
    ###################################
    def draw_table(self):
        _draw_table(self)
    ###################################
    ##########end of draw_table#######
    ###################################

    ###################################
    ##########_draw_table_lines########
    ###################################
    def _draw_table_lines(self):
        _draw_table_lines(self)
    ###################################
    ##########end of _draw_table_lines##
    ###################################

    ###################################
    ##########_export_table_text#######
    ###################################
    def _export_table_text(self):
        _export_table_text(self)
    ###################################
    ##########end of _export_table_text
    ###################################

    ###################################
    ##########redraw###################
    ###################################
    def redraw(self):
        self.clear_caches()
        self.canvas.clear()

        from kivy.graphics import (
            Color, Rectangle, InstructionGroup,
            StencilPush, StencilUse, StencilUnUse, StencilPop,
        )

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        for name in self.layers.layers.keys():
            self.layers.set(name, InstructionGroup())

        self._update_cell_size()
        self.zoom_controller.sync()

        # CRITICAL: refresh viewport bounds for culling
        self._cached_viewport_bounds = self.get_viewport_world()

        with self.canvas:
            StencilPush()
            Rectangle(pos=self.pos, size=self.size)
            StencilUse()
            for group in self.layers.all():
                self.canvas.add(group)
            StencilUnUse()
            StencilPop()

        self.layer_renderer.draw_paper_border()
        self.layer_renderer.draw_grid()
        self.draw_diagram()
        self.draw_table()
        self.layer_renderer.draw_connections()
        self._update_labels()
        self.layer_renderer.draw_overlay()
        self._draw_edit_diamonds()
        self._ensure_slot_labels_visible()
        self._canvas_initialized = True

        # Force GC to release old textures
        import gc
        gc.collect()

    ###################################
    ##########_light_redraw#############
    ###################################
    def _light_redraw(self):
        """
        FAST redraw — NO canvas.clear(), reuses instruction groups.
        This is what's called during pan/zoom.
        """
        self.clear_caches()

        from kivy.graphics import InstructionGroup
        for name in self.layers.layers.keys():
            existing = self.layers.get(name)
            if existing is not None:
                existing.clear()
            else:
                self.layers.set(name, InstructionGroup())

        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.size = self.size
            self.bg_rect.pos = self.pos

        self._update_cell_size()
        self.zoom_controller.sync()

        # ===== COMPUTE VIEWPORT BOUNDS FOR CULLING =====
        self._cached_viewport_bounds = self.get_viewport_world()

        # Each draw method uses cached bounds for culling
        self.layer_renderer.draw_paper_border()
        self.layer_renderer.draw_grid()
        self.draw_diagram()
        self.draw_table()
        self.layer_renderer.draw_connections()
        self._update_labels()
        self.layer_renderer.draw_overlay()
        self._draw_edit_diamonds()
        self._ensure_slot_labels_visible()
    ###################################
    ##########end of _light_redraw#####
    ###################################

    ###################################
    ##########end of redraw############
    ###################################


    ###################################
    ##########get_viewport_world######
    ###################################
    ###################################
    ##########end of get_viewport_world
    ###################################

    ###################################
    ##########world_rect_visible#######
    ###################################
    ###################################
    ##########end of world_rect_visible
    ###################################


    ###################################
    ##########get_viewport_world######
    ###################################
    def get_viewport_world(self):
        """
        World bounds of the visible widget area.
        CRITICAL: use local coords (0, 0) not (self.x, self.y).
        """
        from kivy.core.window import Window

        try:
            # CORRECT: local (0,0) to (width, height) converted to window
            wx1, wy1 = self.to_window(0, 0)
            wx2, wy2 = self.to_window(self.width, self.height)
        except Exception:
            wx1, wy1 = 0, 0
            wx2, wy2 = Window.width, Window.height

        # Margin for partial elements
        m = 80
        wx1 -= m
        wy1 -= m
        wx2 += m
        wy2 += m

        # Convert to world coords
        corners = [(wx1, wy1), (wx2, wy1), (wx1, wy2), (wx2, wy2)]
        world = []
        for sx, sy in corners:
            try:
                world.append(self.screen_to_world(sx, sy))
            except Exception:
                pass

        if not world:
            return (self.GRID_x_min, self.GRID_y_min,
                    self.GRID_x_max, self.GRID_y_max)

        xs = [c[0] for c in world]
        ys = [c[1] for c in world]
        return (min(xs), min(ys), max(xs), max(ys))
    ###################################
    ##########end of get_viewport_world
    ###################################

    ###################################
    ##########end of get_viewport_world
    ###################################

    ###################################
    ##########world_rect_visible#######
    ###################################
    def world_rect_visible(self, x1, y1, x2, y2):
        """Fast rect intersection test against cached viewport bounds."""
        bounds = getattr(self, '_cached_viewport_bounds', None)
        if bounds is None:
            return True
        bx1, by1, bx2, by2 = bounds

        if max(x1, x2) < bx1:
            return False
        if min(x1, x2) > bx2:
            return False
        if max(y1, y2) < by1:
            return False
        if min(y1, y2) > by2:
            return False
        return True
    ###################################
    ##########end of world_rect_visible
    ###################################

    ###################################
    ##########restore_connections_from_project
    ###################################
    def restore_connections_from_project(self):
        _restore_connections_from_project(self)
    ###################################
    ##########end of restore_connections_from_project
    ###################################

    ###################################
    ##########reset_zoom_and_focus#####
    ###################################
    def reset_zoom_and_focus(self):
        self.SCREEN_offset_x = 0.0
        self.SCREEN_offset_y = 0.0
        self.auto_fit()
    ###################################
    ##########end of reset_zoom_and_focus
    ###################################

    ###################################
    ##########set_connection_mode######
    ###################################
    def set_connection_mode(self, active):
        _set_connection_mode(self, active)
    ###################################
    ##########end of set_connection_mode
    ###################################

    ###################################
    ##########handle_connection_touch_down
    ###################################
    def handle_connection_touch_down(self, touch):
        return _handle_connection_touch_down(self, touch)
    ###################################
    ##########end of handle_connection_touch_down
    ###################################

    ###################################
    ##########connection_mode_active###
    ###################################
    def connection_mode_active(self):
        return self.connection.active
    ###################################
    ##########end of connection_mode_active
    ###################################


BaseMotorCore = BaseMotorDiagram


__all__ = [
    'BaseMotorDiagram', 'BaseMotorCore',
    'get_speed', 'get_paper_dimensions',
]