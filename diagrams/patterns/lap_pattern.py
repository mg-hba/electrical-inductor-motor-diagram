"""
================================================================================
File: diagrams/patterns/lap_pattern.py
Purpose: Lap coil pattern (rectangle coils).
         y_vals has 4 points: [bottom_left, top_left, top_right, bottom_right]
Version: 0.1.2
================================================================================
"""

from diagrams.patterns.base_pattern import CoilPattern
from utils.constants import (
    Y_VALS_PATTERN_LAP_TWO,
    Y_VALS_PATTERN_LAP_SINGLE,
    MAIN_WINDING_SHIFT_TWO,
    MAIN_WINDING_SHIFT_SINGLE,
)


class LapPattern(CoilPattern):

    pattern_id = 'lap'
    display_name = 'Lap'
    group_id = 'chained'
    group_display = 'Chained'

    def get_coil_span_x(self, pole_start, coil_index,
                         coils_in_pole, coil_span):
        coil_start = pole_start + coil_index
        coil_end = coil_start + coil_span
        return coil_start, coil_end

    def _apply_edges(self, y_vals, coil_index, coils_in_pole):
        if coil_index == 0:
            y_vals[0] -= 1
        if coil_index == coils_in_pole - 1:
            y_vals[-1] -= 1
        return y_vals

    def get_y_vals_two_layer(self, coil_index, coils_in_pole,
                              coil_span=None):
        y_vals = [v + MAIN_WINDING_SHIFT_TWO
                   for v in Y_VALS_PATTERN_LAP_TWO]
        return self._apply_edges(y_vals, coil_index, coils_in_pole)

    def get_y_vals_single_layer(self, coil_index, coils_in_pole,
                                 coil_span=None):
        y_vals = [v + MAIN_WINDING_SHIFT_SINGLE
                   for v in Y_VALS_PATTERN_LAP_SINGLE]
        return self._apply_edges(y_vals, coil_index, coils_in_pole)

    def get_y_vals_phase(self, coil_index, coils_in_pole,
                          coil_span=None):
        y_vals = list(Y_VALS_PATTERN_LAP_TWO)
        return self._apply_edges(y_vals, coil_index, coils_in_pole)