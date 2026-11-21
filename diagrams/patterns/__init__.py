"""
================================================================================
File: diagrams/patterns/__init__.py
Purpose: Coil patterns package initializer.
Version: 0.1.1
================================================================================
"""

from diagrams.patterns.base_pattern import CoilPattern
from diagrams.patterns.lap_pattern import LapPattern
from diagrams.patterns.triangle_pattern import TrianglePattern
from diagrams.patterns.concentric_pattern import ConcentricPattern
from diagrams.patterns.registry import PatternRegistry


__all__ = [
    'CoilPattern', 'LapPattern', 'TrianglePattern',
    'ConcentricPattern', 'PatternRegistry',
]