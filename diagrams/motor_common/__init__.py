"""
================================================================================
File: diagrams/motor_common/__init__.py
Purpose: Common base for all motor winding diagrams.
         (Previously in core/base_diagram/)
Version: 0.1.4
================================================================================
"""

from diagrams.motor_common.base_diagram import (
    BaseMotorDiagram, BaseMotorCore,
)


__all__ = ['BaseMotorDiagram', 'BaseMotorCore']