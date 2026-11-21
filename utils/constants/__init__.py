"""
================================================================================
File: utils/constants/__init__.py
Purpose: Central re-export of all constants + defensive fallbacks.
Version: 0.1.1
================================================================================
"""

from utils.constants.paper import *
from utils.constants.colors import *
from utils.constants.layout import *
from utils.constants.patterns import *
from utils.constants.connection import *
from utils.constants.project_setup import *
from utils.constants.export import *


def _ensure(name, value):
    import sys
    mod = sys.modules[__name__]
    if not hasattr(mod, name):
        setattr(mod, name, value)


# Zoom fallbacks
_ensure('ZOOM_MIN', 0.02)
_ensure('ZOOM_MAX', 100.0)
_ensure('ZOOM_STEP', 1.35)
_ensure('ZOOM_HISTORY_SIZE', 4)
_ensure('ZOOM_BOX_MIN_SIZE', 30.0)
_ensure('ZOOM_BOX_FILL_COLOR', (0.95, 0.6, 0.1, 0.25))
_ensure('ZOOM_BOX_LINE_COLOR', (0.95, 0.5, 0.1, 0.9))
_ensure('ZOOM_BOX_LINE_WIDTH', 2)
_ensure('PAN_BOUNDS_MARGIN_PX', 60)

# Connection error fallbacks
_ensure('ERROR_OVERLAP', "Cannot draw on existing lines")
_ensure('ERROR_BLOCKED', "Path is blocked")
_ensure('ERROR_POINT_ON_LINE', "Cannot place point on existing line")
_ensure('ERROR_CANNOT_DELETE_JUNCTION',
        "Cannot delete junction - it connects multiple lines. "
        "Delete the lines instead.")
_ensure('ERROR_WIRE_POINT_NOT_DELETABLE',
        "Main wire points cannot be deleted")
_ensure('ERROR_WIRE_POINT_NOT_MOVABLE',
        "Main wire points cannot be moved")
_ensure('ERROR_PENCIL_FLOATING',
        "A drawn line must connect to an existing point or line at "
        "least at one end.")
_ensure('ERROR_NO_PARALLEL_PAIR',
        "No suitable pair of parallel lines found for this operation.")

_ensure('SIZE_NODE_WORLD', 0.55)
_ensure('SIZE_JUNCTION_WORLD', 0.45)
_ensure('LINE_WIDTH_LINE_BASE', 3)
_ensure('LINE_WIDTH_LINE_SELECTED', 4)
_ensure('CONNECTION_TOUCH_TOLERANCE_BASE', 80)
_ensure('CONNECTION_TOUCH_TOLERANCE_MIN', 40)
_ensure('CONNECTION_TOUCH_TOLERANCE_MAX', 160)
_ensure('POINT_PRIORITY_FACTOR', 0.9)
_ensure('PULL_STEP_DEFAULT', 1)
_ensure('PULL_STEP_MIN', 1)
_ensure('PULL_STEP_MAX', 5)
_ensure('SPLIT_EPSILON', 0.05)
_ensure('PENCIL_SNAP_RADIUS', 1.2)
_ensure('AUTO_SELECT_RADIUS', 6.0)
_ensure('UNDO_STACK_SIZE', 30)

_ensure('CONFLICT_TITLE', "Line is in the path")
_ensure('CONFLICT_MESSAGE', "What do you want to do?")
_ensure('CONFLICT_BTN_CONNECT', "Connect")
_ensure('CONFLICT_BTN_PASS_OVER', "Pass Over")
_ensure('CONFLICT_BTN_STOP_BEFORE', "Stop Before")


del _ensure