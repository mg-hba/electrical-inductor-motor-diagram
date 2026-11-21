"""
================================================================================
File: diagrams/patterns/triangle_pattern.py
Purpose: Triangle coil pattern.
         y_peak = sqrt(coil_span^2 - (coil_span/2)^2) * 2/3
Version: 0.1.2
================================================================================
"""

import math
from diagrams.patterns.base_pattern import CoilPattern
from utils.constants import (
    MAIN_WINDING_SHIFT_TWO,
    MAIN_WINDING_SHIFT_SINGLE,
)


class TrianglePattern(CoilPattern):

    pattern_id = 'triangle'
    display_name = 'Triangle'
    group_id = 'chained'
    group_display = 'Chained'

    def get_coil_span_x(self, pole_start, coil_index,
                         coils_in_pole, coil_span):
        coil_start = pole_start + coil_index
        coil_end = coil_start + coil_span
        return coil_start, coil_end

    def _compute_y_peak(self, coil_span):
        if coil_span <= 0:
            return 1.0
        return (math.sqrt(coil_span ** 2 - (coil_span / 2) ** 2) * 2 / 3)

    def _build_y_vals(self, coil_span, shift):
        y_peak = self._compute_y_peak(coil_span)
        return [0 + shift, 1 + shift, y_peak + shift,
                1 + shift, 0 + shift]

    def _apply_edges(self, y_vals, coil_index, coils_in_pole):
        if coil_index == 0:
            y_vals[0] -= 1
        if coil_index == coils_in_pole - 1:
            y_vals[-1] -= 1
        return y_vals

    def get_y_vals_two_layer(self, coil_index, coils_in_pole,
                              coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        y_vals = self._build_y_vals(span, MAIN_WINDING_SHIFT_TWO)
        return self._apply_edges(y_vals, coil_index, coils_in_pole)

    def get_y_vals_single_layer(self, coil_index, coils_in_pole,
                                 coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        y_vals = self._build_y_vals(span, MAIN_WINDING_SHIFT_SINGLE)
        return self._apply_edges(y_vals, coil_index, coils_in_pole)

    def get_y_vals_phase(self, coil_index, coils_in_pole,
                          coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        y_vals = self._build_y_vals(span, 0)
        return self._apply_edges(y_vals, coil_index, coils_in_pole)