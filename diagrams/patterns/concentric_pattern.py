"""
================================================================================
File: diagrams/patterns/concentric_pattern.py
Purpose: Concentric coil pattern.
         span(ci) = coil_span + 2 * (N - 1 - ci)
         y_peak(ci) = sqrt(span(ci)^2 - (span(ci)/2)^2) * 2/3
         x_peak_offset from first coil of first pole.
Version: 0.1.2
================================================================================
"""

import math
from diagrams.patterns.base_pattern import CoilPattern
from utils.constants import (
    MAIN_WINDING_SHIFT_TWO,
    MAIN_WINDING_SHIFT_SINGLE,
)


class ConcentricPattern(CoilPattern):

    pattern_id = 'concentric'
    display_name = 'Concentric'
    group_id = ''
    group_display = ''

    def get_coil_span_x(self, pole_start, coil_index,
                         coils_in_pole, coil_span):
        coil_start = pole_start + coil_index
        reversed_coil_index = coils_in_pole - 1 - coil_index
        span_for_this_coil = coil_span + 2 * reversed_coil_index
        coil_end = coil_start + span_for_this_coil
        return coil_start, coil_end

    def get_x_peak_offset(self, pole_start, coils_in_pole, coil_span):
        first_coil_start, first_coil_end = self.get_coil_span_x(
            pole_start, 0, coils_in_pole, coil_span
        )
        return (first_coil_end - first_coil_start) / 2

    def _span_for_coil(self, coil_index, coils_in_pole, coil_span):
        reversed_coil_index = coils_in_pole - 1 - coil_index
        return coil_span + 2 * reversed_coil_index

    def _compute_y_peak(self, span_for_this_coil):
        if span_for_this_coil <= 0:
            return 1.0
        return (math.sqrt(span_for_this_coil ** 2 -
                          (span_for_this_coil / 2) ** 2) * 2 / 3)

    def _build_y_vals(self, coil_index, coils_in_pole, coil_span, shift):
        span_i = self._span_for_coil(coil_index, coils_in_pole, coil_span)
        y_peak = self._compute_y_peak(span_i)
        y0 = 0 + shift
        y1 = 1 + shift
        y_vals = [y0, y1, y_peak + shift, y1, y0]

        if coil_index == coils_in_pole - 1:
            y_vals[0] -= 1
        if coil_index == 0:
            y_vals[-1] -= 1
        return y_vals

    def get_y_vals_two_layer(self, coil_index, coils_in_pole,
                              coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        return self._build_y_vals(coil_index, coils_in_pole,
                                   span, MAIN_WINDING_SHIFT_TWO)

    def get_y_vals_single_layer(self, coil_index, coils_in_pole,
                                 coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        return self._build_y_vals(coil_index, coils_in_pole,
                                   span, MAIN_WINDING_SHIFT_SINGLE)

    def get_y_vals_phase(self, coil_index, coils_in_pole,
                          coil_span=None):
        span = coil_span if coil_span is not None else 1.0
        return self._build_y_vals(coil_index, coils_in_pole, span, 0)