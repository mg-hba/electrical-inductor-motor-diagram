"""
================================================================================
File: backends/vector_backend.py
Purpose: Backend that writes to VectorExporter.
Version: 0.1.1
================================================================================
"""

from backends.base import RenderBackend
from exporters.vector_exporter import VectorExporter


class VectorBackend(RenderBackend):

    def __init__(self):
        self.exporter = VectorExporter()
        self._ready = True

    def clear(self):
        self.exporter.clear()
        self._ready = True

    def is_ready(self):
        return self._ready and self.exporter is not None

    def line(self, x1, y1, x2, y2, color, width=1):
        if not self.is_ready():
            return
        self.exporter.add_line(x1, y1, x2, y2, color, width)

    def coil(self, x_start, x_end, y_vals, color, width=2):
        if not self.is_ready():
            return
        self.exporter.add_coil(x_start, x_end, y_vals, color, width)

    def rect(self, x, y, w, h, color, filled=True):
        if not self.is_ready():
            return
        if filled:
            self.exporter.add_filled_rect(x, y, w, h, color)
        else:
            self.exporter.add_line(x, y, x + w, y, color, 1)
            self.exporter.add_line(x + w, y, x + w, y + h, color, 1)
            self.exporter.add_line(x + w, y + h, x, y + h, color, 1)
            self.exporter.add_line(x, y + h, x, y, color, 1)

    def text(self, text, x, y, font_size, color, halign='center'):
        if not self.is_ready():
            return
        self.exporter.add_text(text, x, y, font_size, color)

    def image(self, filepath, x, y, w, h, opacity=1.0):
        if not self.is_ready():
            return
        self.exporter.add_image(filepath, x, y, w, h, opacity)

    def set_view_state(self, view_state):
        self.exporter.set_view_state(view_state)

    def save(self, filepath, format='svg', **kwargs):
        return self.exporter.save(filepath, format, **kwargs)

    def load_paper_from_config(self):
        self.exporter.load_paper_from_config()