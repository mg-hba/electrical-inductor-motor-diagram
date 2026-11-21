"""
================================================================================
File: diagrams/single_layer/single_layer.py
Purpose: Single Layer motor winding diagram.
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
    LINE_WIDTH_MAIN_DISPLAY,
    EXPORT_LINE_WIDTH_MAIN,
)


class SingleLayerMotorDiagram(BaseMotorDiagram):

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, **kwargs):
        self.all_slots = 24
        self.poles = 2
        self.computed_coil_span_chained = 0
        self.computed_coil_span_concentric = 0
        self.custom_coils_per_pole = None
        super().__init__(**kwargs)
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########_compute_spans###########
    ###################################
    def _compute_spans(self, all_slots, poles):
        slots_per_phase = all_slots / 3
        base_span = (all_slots - slots_per_phase) / poles
        coils_per_phase = slots_per_phase / 2
        coils_per_pole = coils_per_phase / poles
        return base_span + coils_per_pole, base_span + 1
    ###################################
    ##########end of _compute_spans###
    ###################################

    ###################################
    ##########set_parameters###########
    ###################################
    def set_parameters(self, all_slots, poles, **kwargs):
        self.all_slots = all_slots
        self.poles = poles

        span_chained, span_concentric = self._compute_spans(all_slots, poles)
        self.computed_coil_span_chained = span_chained
        self.computed_coil_span_concentric = span_concentric

        pattern_id = json_manager.get_last_coil_pattern() or 'lap'
        active_span = (span_concentric if pattern_id == 'concentric'
                       else span_chained)

        self.MOTOR_all_slots = all_slots
        self.MOTOR_coil_span = int(round(active_span))
        self.MOTOR_poles = poles

        self.connection.shift_y = self._diagram_shift()

        self._rebuild_grid_bounds()
        self._emit_wire_points()
        self.restore_connections_from_project()
        self.diagram_enabled = True
        self.redraw()
    ###################################
    ##########end of set_parameters####
    ###################################

    ###################################
    ##########load_custom_values#######
    ###################################
    def load_custom_values(self):
        project_data = json_manager.project_data
        if not project_data:
            self.custom_coils_per_pole = None
            return
        values = project_data.get('coils_per_pole_values', None)
        if values and isinstance(values, list):
            filtered = [int(v) for v in values[:int(self.poles)]]
            if sum(filtered) > 0:
                self.custom_coils_per_pole = filtered
                return
        self.custom_coils_per_pole = None
    ###################################
    ##########end of load_custom_values
    ###################################

    ###################################
    ##########_compute_coils_distribution
    ###################################
    def _compute_coils_distribution(self):
        pattern = self._get_pattern()
        pattern_id = pattern.pattern_id
        coil_span = (self.computed_coil_span_concentric
                     if pattern_id == 'concentric'
                     else self.computed_coil_span_chained)
        slots_per_phase = self.all_slots / 3
        coils_per_phase = slots_per_phase / 2
        coils_per_pole = coils_per_phase / self.poles

        self.load_custom_values()
        if self.custom_coils_per_pole:
            distribution = list(self.custom_coils_per_pole)
        else:
            coils_per_pole_int = int(coils_per_pole)
            if coils_per_pole_int < 1:
                return None, None, None
            distribution = [coils_per_pole_int] * int(self.poles)
        return distribution, coil_span, pattern
    ###################################
    ##########end of _compute_coils_distribution
    ###################################

    ###################################
    ##########_emit_wire_points########
    ###################################
    def _emit_wire_points(self):
        result = self._compute_coils_distribution()
        if result[0] is None:
            json_manager.set_last_wire_points([])
            return

        distribution, coil_span, pattern = result
        pole_step = self.all_slots / self.poles
        y_offset = self.get_diagram_area_bottom()
        all_slots = self.all_slots
        boundary_high = all_slots + 0.5

        points = []
        for pole_index in range(int(self.poles)):
            pole_start = 1 + pole_index * pole_step
            coils_in_pole = distribution[pole_index]
            if coils_in_pole <= 0:
                continue
            for coil_index in range(coils_in_pole):
                coil_start, coil_end = pattern.get_coil_span_x(
                    pole_start, coil_index, coils_in_pole, coil_span
                )
                y_vals = pattern.get_y_vals_single_layer(
                    coil_index, coils_in_pole, coil_span
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
                if coil_index == coils_in_pole - 1:
                    if pattern.pattern_id == 'concentric':
                        outer_coil_end = (pole_start + 1 +
                                           (coils_in_pole - 1) +
                                           coil_span)
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

        result = self._compute_coils_distribution()
        if result[0] is None:
            return

        distribution, coil_span, pattern = result
        pole_step = self.all_slots / self.poles
        shift_main = self._diagram_shift()

        x_peak_offset = None
        if (pattern.pattern_id == 'concentric' and
                hasattr(pattern, 'get_x_peak_offset')):
            first_coils = distribution[0] if distribution else 0
            if first_coils > 0:
                x_peak_offset = pattern.get_x_peak_offset(
                    1, first_coils, coil_span
                )

        if self._export_mode:
            line_width_main = EXPORT_LINE_WIDTH_MAIN
        else:
            line_width_main = LINE_WIDTH_MAIN_DISPLAY

        from core.rendering.canvas_backend import CanvasBackend
        static_backend = CanvasBackend(self.layers.get('static_diagram'),
                                        self.world_to_screen)
        backends = [static_backend, self.vector_backend]

        for pole_index in range(int(self.poles)):
            pole_start = 1 + pole_index * pole_step
            coils_in_pole = distribution[pole_index]
            if coils_in_pole <= 0:
                continue
            x_peak_world = None
            if x_peak_offset is not None:
                x_peak_world = pole_start + x_peak_offset
            for coil_index in range(coils_in_pole):
                coil_start, coil_end = pattern.get_coil_span_x(
                    pole_start, coil_index, coils_in_pole, coil_span
                )
                y_vals = pattern.get_y_vals_single_layer(
                    coil_index, coils_in_pole, coil_span
                )
                self._draw_coil_segments(
                    backends, coil_start, coil_end,
                    COLOR_MAIN_WINDING, line_width_main,
                    y_vals, shift_main, x_peak_world
                )
    ###################################
    ##########end of draw_diagram######
    ###################################