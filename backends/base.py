"""
================================================================================
File: backends/base.py
Purpose: Abstract RenderBackend interface.
Version: 0.1.1
================================================================================
"""

from abc import ABC, abstractmethod


class RenderBackend(ABC):

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def line(self, x1, y1, x2, y2, color, width=1):
        pass

    @abstractmethod
    def coil(self, x_start, x_end, y_vals, color, width=2):
        pass

    @abstractmethod
    def rect(self, x, y, w, h, color, filled=True):
        pass

    @abstractmethod
    def text(self, text, x, y, font_size, color, halign='center'):
        pass

    @abstractmethod
    def image(self, filepath, x, y, w, h, opacity=1.0):
        pass

    @abstractmethod
    def set_view_state(self, view_state):
        pass

    @abstractmethod
    def save(self, filepath, format='svg', **kwargs):
        pass

    @abstractmethod
    def is_ready(self):
        pass