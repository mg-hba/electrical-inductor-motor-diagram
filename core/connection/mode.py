"""
================================================================================
File: core/connection/mode.py
Purpose: Connection mode enum (mutually exclusive states).
Version: 0.1.4
================================================================================
"""

from enum import Enum


class ConnectionMode(Enum):
    """
    Mutually exclusive connection input modes.
    `active` (whether connection panel is open) is a separate boolean.
    `group_clear_mode` is a sub-flag of DELETE mode, also separate.
    """
    SELECT = "select"
    DELETE = "delete"
    CROSSING = "crossing"
    PENCIL = "pencil"
    SELECT_BOX = "select_box"