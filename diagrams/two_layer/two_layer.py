"""
================================================================================
File: diagrams/two_layer/two_layer.py
Purpose: Two Layer motor winding diagram.
         Wire points stored WITHOUT shift in JSON.
         Shift applied only at draw time.
Version: 0.1.4
================================================================================
"""

from diagrams.motor_common import BaseMotorDiagram
from managers.json_manager import json_manager

from utils.constants import (
    X_SHIFT,
    COLOR_MAIN_WINDING,
    COLOR_PHASE_1, COLOR_PHASE_2, COLOR_PHASE_3,
    LINE_WIDTH_MAIN_DISPLAY, LINE_WIDTH_PHASE_1_DISPLAY,
    LINE_WIDTH_PHASE_2_DISPLAY, LINE_WIDTH_PHASE_3_DISPLAY,
    EXPORT_LINE_WIDTH_MAIN, EXPORT_LINE_WIDTH_PHASE_1,
    EXPORT_LINE_WIDTH_PHASE_2, EXPORT_LINE_WIDTH_PHASE_3,
)


class TwoLayerMotorDiagram(BaseMotorDiagram):

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, **kwargs):
        self.all_slots = 60
        self.poles = 4
        self.coil_span_chained = 11
        self.coil_span_concentric = 9
        super().__init__(**kwargs)
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########_get_active_coil_span####
    ###################################
    def _get_active_coil_span(self, pattern_id):
        if pattern_id == 'concentric':
            return self.coil_span_concentric
        return self.coil_span_chained
    ###################################
    ##########end of _get_active_coil_span
    ###################################

    ###################################
    ##########set_parameters###########
    ###################################
    def set_parameters(self, all_slots, poles,
                       coil_span_chained=None, coil_span_concentric=None):
        self.all_slots = all_slots
        self.poles = poles

        if coil_span_chained is not None:
            self.coil_span_chained = coil_span_chained
        if coil_span_concentric is not None:
            self.coil_span_concentric = coil_span_concentric

        self.diagram_enabled = True

        pattern_id = json_manager.get_last_coil_pattern() or 'lap'
        active_span = self._get_active_coil_span(pattern_id)

        self.MOTOR_all_slots = all_slots
        self.MOTOR_coil_span = int(round(active_span))
        self.MOTOR_poles = poles

        self.connection.shift_y = self._diagram_shift()

        self._rebuild_grid_bounds()
        self._emit_wire_points()
        self.restore_connections_from_project()
        self.redraw()
    ###################################
    ##########end of set_parameters####
    ###################################

    ###################################
    ##########_emit_wire_points########
    ###################################
    def _emit_wire_points(self):
        points = []
        pattern = self._get_pattern()
        pattern_id = pattern.pattern_id
        coil_span = self._get_active_coil_span(pattern_id)
        coil_span_adjusted = coil_span + 1 - 0.3
        all_slots = self.all_slots
        boundary_high = all_slots + 0.5

        loop_count = (
            int(self.all_slots / (self.poles * 3))
            if (self.poles * 3) > 0 else 0
        )
        if loop_count == 0:
            json_manager.set_last_wire_points([])
            return

        pole_step = self.all_slots / self.poles
        repeat_count = int(self.poles)
        max_slot = self.all_slots + coil_span_adjusted + 5
        y_offset = self.get_diagram_area_bottom()

        for pole_index in range(repeat_count):
            pole_start = pole_index * pole_step + 1
            coils_in_pole = loop_count
            for coil_index in range(loop_count):
                absolute_index = pole_index * pole_step + coil_index
                if absolute_index + coil_span_adjusted > max_slot:
                    break
                coil_start, coil_end = pattern.get_coil_span_x(
                    pole_start, coil_index, coils_in_pole, coil_span_adjusted
                )
                y_vals = pattern.get_y_vals_two_layer(
                    coil_index, coils_in_pole, coil_span_adjusted
                )
                if coil_index == 0:
                    x_start = coil_start + X_SHIFT
                    if x_start > boundary_high:
                        x_start = x_start - all_slots
                    points.append({
                        'id': 'P%d_s' % (pole_index + 1),
                        'pole': pole_index,
                        'type': 'start',
                        'x': x_start,
                        'y': y_vals[0] + y_offset,
                    })
                if coil_index == loop_count - 1:
                    if pattern_id == 'concentric':
                        outer_coil_end = (pole_start + 1 +
                                           (loop_count - 1) +
                                           coil_span_adjusted)
                        x_end = outer_coil_end + X_SHIFT
                    else:
                        x_end = coil_end + X_SHIFT
                    if x_end > boundary_high:
                        x_end = x_end - all_slots
                    points.append({
                        'id': 'P%d_e' % (pole_index + 1),
                        'pole': pole_index,
                        'type': 'end',
                        'x': x_end,
                        'y': y_vals[-1] + y_offset,
                    })

        json_manager.set_last_wire_points(points)
    ###################################
    ##########end of _emit_wire_points
    ###################################

    ###################################
    ##########draw_diagram#############
    ###################################
    def draw_diagram(self):
        if not self.diagram_enabled:
            return
        if self.all_slots <= 0 or self.poles <= 0:
            return

        pattern = self._get_pattern()
        pattern_id = pattern.pattern_id
        coil_span = self._get_active_coil_span(pattern_id)
        coil_span_adjusted = coil_span + 1 - 0.3
        shift_main = self._diagram_shift()
        shift_phase = self._phase_diagram_shift()

        loop_count = (
            int(self.all_slots / (self.poles * 3))
            if (self.poles * 3) > 0 else 0
        )
        if loop_count == 0:
            return

        pole_step = self.all_slots / self.poles
        repeat_count = int(self.poles)
        phase_step_x = self.all_slots / (self.poles * 3)
        max_slot = self.all_slots + coil_span_adjusted + 5

        x_peak_offset = None
        if pattern_id == 'concentric' and hasattr(pattern, 'get_x_peak_offset'):
            x_peak_offset = pattern.get_x_peak_offset(
                1, loop_count, coil_span_adjusted
            )

        if self._export_mode:
            line_width_main = EXPORT_LINE_WIDTH_MAIN
            line_width_phase_1 = EXPORT_LINE_WIDTH_PHASE_1
            line_width_phase_2 = EXPORT_LINE_WIDTH_PHASE_2
            line_width_phase_3 = EXPORT_LINE_WIDTH_PHASE_3
        else:
            line_width_main = LINE_WIDTH_MAIN_DISPLAY
            line_width_phase_1 = LINE_WIDTH_PHASE_1_DISPLAY
            line_width_phase_2 = LINE_WIDTH_PHASE_2_DISPLAY
            line_width_phase_3 = LINE_WIDTH_PHASE_3_DISPLAY

        from core.rendering.canvas_backend import CanvasBackend
        static_backend = CanvasBackend(self.layers.get('static_diagram'),
                                        self.world_to_screen)
        backends = [static_backend, self.vector_backend]

        # Main winding
        for pole_index in range(repeat_count):
            pole_start = pole_index * pole_step + 1
            x_peak_world = None
            if x_peak_offset is not None:
                x_peak_world = pole_start + x_peak_offset
            for coil_index in range(loop_count):
                absolute_index = pole_index * pole_step + coil_index
                if absolute_index + coil_span_adjusted > max_slot:
                    break
                coil_start, coil_end = pattern.get_coil_span_x(
                    pole_start, coil_index, loop_count, coil_span_adjusted
                )
                y_vals = pattern.get_y_vals_two_layer(
                    coil_index, loop_count, coil_span_adjusted
                )
                self._draw_coil_segments(
                    backends, coil_start, coil_end,
                    COLOR_MAIN_WINDING, line_width_main,
                    y_vals, shift_main, x_peak_world
                )

        # Phase windings
        def draw_phase(phase_offset, color, line_width):
            for pole_index in range(repeat_count):
                base_index = pole_index * pole_step + phase_offset
                pole_start = pole_index * pole_step + 1 + phase_offset
                x_peak_world = None
                if x_peak_offset is not None:
                    x_peak_world = pole_start + x_peak_offset
                for coil_index in range(loop_count):
                    absolute_index = base_index + coil_index
                    if absolute_index + coil_span_adjusted > max_slot:
                        break
                    coil_start, coil_end = pattern.get_coil_span_x(
                        pole_start, coil_index, loop_count, coil_span_adjusted
                    )
                    y_vals = pattern.get_y_vals_phase(
                        coil_index, loop_count, coil_span_adjusted
                    )
                    self._draw_coil_segments(
                        backends, coil_start, coil_end,
                        color, line_width,
                        y_vals, shift_phase, x_peak_world
                    )

        draw_phase(0, COLOR_PHASE_1, line_width_phase_1)
        draw_phase(phase_step_x, COLOR_PHASE_2, line_width_phase_2)
        draw_phase(2 * phase_step_x, COLOR_PHASE_3, line_width_phase_3)
    ###################################
    ##########end of draw_diagram######
    ###################################