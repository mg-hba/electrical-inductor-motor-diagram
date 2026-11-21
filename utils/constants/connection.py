"""
================================================================================
File: utils/constants/connection.py
Purpose: Connection constants including errors.
Version: 0.1.1.1
================================================================================
"""

# ===== Node and junction sizes =====
SIZE_NODE_WORLD = 0.25
SIZE_JUNCTION_WORLD = 0.20

# ===== Line widths =====
LINE_WIDTH_LINE_BASE = 3
LINE_WIDTH_LINE_SELECTED = 4
LINE_WIDTH_NODE_CONNECTION = 3

# ===== Touch tolerance =====
CONNECTION_TOUCH_TOLERANCE_BASE = 80
CONNECTION_TOUCH_TOLERANCE_MIN = 40
CONNECTION_TOUCH_TOLERANCE_MAX = 160

# ===== Point priority =====
POINT_PRIORITY_FACTOR = 0.9

# ===== Pull step =====
PULL_STEP_DEFAULT = 1
PULL_STEP_MIN = 1
PULL_STEP_MAX = 5

# ===== Split epsilon =====
SPLIT_EPSILON = 0.05

# ===== Pencil snap radius =====
PENCIL_SNAP_RADIUS = 1.2

# ===== Auto-select =====
AUTO_SELECT_RADIUS = 6.0

# ===== Undo stack =====
UNDO_STACK_SIZE = 30

# ===== Error messages =====
ERROR_OVERLAP = "Cannot draw on existing lines"
ERROR_BLOCKED = "Path is blocked"
ERROR_POINT_ON_LINE = "Cannot place point on existing line"
ERROR_CANNOT_DELETE_JUNCTION = (
    "Cannot delete junction - it connects multiple lines. "
    "Delete the lines instead."
)
ERROR_WIRE_POINT_NOT_DELETABLE = "Main wire points cannot be deleted"
ERROR_WIRE_POINT_NOT_MOVABLE = "Main wire points cannot be moved"
ERROR_PENCIL_FLOATING = (
    "A drawn line must connect to an existing point or line "
    "at least at one end."
)
ERROR_NO_PARALLEL_PAIR = (
    "No suitable pair of parallel lines found for this operation."
)
ERROR_SHORT_CIRCUIT = "Short Circuit - R and U cannot be connected"
ERROR_DIAGONAL_NOT_ALLOWED = "Only horizontal or vertical lines are allowed"

# ===== Conflict dialog =====
CONFLICT_TITLE = "Line is in the path"
CONFLICT_MESSAGE = "What do you want to do?"
CONFLICT_BTN_CONNECT = "Connect"
CONFLICT_BTN_PASS_OVER = "Pass Over"
CONFLICT_BTN_STOP_BEFORE = "Stop Before"