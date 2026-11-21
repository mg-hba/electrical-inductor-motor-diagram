"""
================================================================================
File: diagrams/patterns/registry.py
Purpose: Central coil pattern registry.
Version: 0.1.1
================================================================================
"""

from diagrams.patterns.lap_pattern import LapPattern
from diagrams.patterns.triangle_pattern import TrianglePattern
from diagrams.patterns.concentric_pattern import ConcentricPattern


class PatternRegistry:

    _patterns = {}

    @classmethod
    def initialize(cls):
        cls._patterns = {}
        cls.register(LapPattern)
        cls.register(TrianglePattern)
        cls.register(ConcentricPattern)

    @classmethod
    def register(cls, pattern_class):
        cls._patterns[pattern_class.pattern_id] = pattern_class

    @classmethod
    def get(cls, pattern_id):
        if not cls._patterns:
            cls.initialize()
        if pattern_id in cls._patterns:
            return cls._patterns[pattern_id]()
        return LapPattern()

    @classmethod
    def get_all(cls):
        if not cls._patterns:
            cls.initialize()
        return list(cls._patterns.values())

    @classmethod
    def get_ids(cls):
        if not cls._patterns:
            cls.initialize()
        return list(cls._patterns.keys())

    @classmethod
    def get_grouped(cls):
        if not cls._patterns:
            cls.initialize()
        groups = {}
        ungrouped = []
        for pid, pclass in cls._patterns.items():
            if pclass.group_id:
                if pclass.group_id not in groups:
                    groups[pclass.group_id] = {
                        'display': pclass.group_display,
                        'items': [],
                    }
                groups[pclass.group_id]['items'].append(pclass)
            else:
                ungrouped.append(pclass)
        return groups, ungrouped


PatternRegistry.initialize()