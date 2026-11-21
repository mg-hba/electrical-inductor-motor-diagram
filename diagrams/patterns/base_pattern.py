"""
================================================================================
File: diagrams/patterns/base_pattern.py
Purpose: Abstract base for all coil patterns.
Version: 0.1.2
================================================================================
"""

from abc import ABC, abstractmethod


class CoilPattern(ABC):

    pattern_id = 'base'
    display_name = 'Base'
    group_id = ''
    group_display = ''

    @abstractmethod
    def get_coil_span_x(self, pole_start, coil_index,
                         coils_in_pole, coil_span):
        pass

    @abstractmethod
    def get_y_vals_two_layer(self, coil_index, coils_in_pole,
                              coil_span=None):
        pass

    @abstractmethod
    def get_y_vals_single_layer(self, coil_index, coils_in_pole,
                                 coil_span=None):
        pass

    @abstractmethod
    def get_y_vals_phase(self, coil_index, coils_in_pole,
                          coil_span=None):
        pass