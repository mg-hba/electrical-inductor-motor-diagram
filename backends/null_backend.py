"""
================================================================================
File: backends/null_backend.py
Purpose: No-op RenderBackend.
Version: 0.1.1
================================================================================
"""

from backends.base import RenderBackend


class NullBackend(RenderBackend):

    def __init__(self):
        self._ready = True

    def clear(self):
        pass

    def is_ready(self):
        return self._ready

    def line(self, *args, **kwargs):
        pass

    def coil(self, *args, **kwargs):
        pass

    def rect(self, *args, **kwargs):
        pass

    def text(self, *args, **kwargs):
        pass

    def image(self, *args, **kwargs):
        pass

    def set_view_state(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        return False