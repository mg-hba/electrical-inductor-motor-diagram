"""
================================================================================
File: core/rendering/layer_stack.py
Purpose: Manage multiple InstructionGroup layers.
Version: 0.1.1
================================================================================
"""

from collections import OrderedDict


LAYER_ORDER = [
    'paper_bg',
    'grid',
    'static_diagram',
    'table_lines',         # ← این خط باید باشد
    'connection_static',
    'connection_overlay',
    'drawing_layer',
]


class LayerStack:

    def __init__(self):
        self.layers = OrderedDict()
        for name in LAYER_ORDER:
            self.layers[name] = None

    def set(self, name, group):
        self.layers[name] = group

    def get(self, name):
        return self.layers.get(name)

    def all(self):
        return [g for g in self.layers.values() if g is not None]

    def all_up_to(self, name):
        result = []
        for n in LAYER_ORDER:
            g = self.layers.get(n)
            if g is not None:
                result.append(g)
            if n == name:
                break
        return result

    def clear(self, name):
        g = self.layers.get(name)
        if g is not None:
            g.clear()

    def clear_from(self, name):
        started = False
        for n in LAYER_ORDER:
            if n == name:
                started = True
            if started:
                g = self.layers.get(n)
                if g is not None:
                    g.clear()