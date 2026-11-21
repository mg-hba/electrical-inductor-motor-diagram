"""
================================================================================
File: diagrams/__init__.py
Purpose: Diagrams package initializer.
Version: 0.1.1
================================================================================
"""

from diagrams.two_layer.two_layer import TwoLayerMotorDiagram
from diagrams.single_layer.single_layer import SingleLayerMotorDiagram


__all__ = ['TwoLayerMotorDiagram', 'SingleLayerMotorDiagram']