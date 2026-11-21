"""
================================================================================
File: diagrams/base/drawing_layer.py
Purpose: Placeholder for future free-hand pencil strokes.
Version: 0.1.1
================================================================================
"""

from kivy.graphics import InstructionGroup


class DrawingLayer:

    def __init__(self):
        self.group = InstructionGroup()

    def clear(self):
        self.group.clear()

    def add_stroke(self, points, color, width=2):
        pass