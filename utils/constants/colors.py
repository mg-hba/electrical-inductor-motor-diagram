"""
================================================================================
File: utils/constants/colors.py
Purpose: All color constants including R/U phase groups.
Version: 0.1.1.1
================================================================================
"""

# ===== Main diagram =====
COLOR_MAIN_WINDING = (0.1, 0.1, 0.1, 1)
COLOR_PHASE_1 = (0, 0, 0, 1)
COLOR_PHASE_2 = (0.2, 0.6, 0.8, 1)
COLOR_PHASE_3 = (0.9, 0.2, 0.2, 1)
COLOR_PAPER_BORDER = (0.2, 0.4, 0.8, 1)

# ===== Grid (display) =====
COLOR_GRID_10_DISPLAY = (0.1, 0.1, 0.1, 1)
COLOR_GRID_5_DISPLAY = (0.7, 0.7, 0.7, 1)
COLOR_GRID_5V_DISPLAY = (0.7, 0.7, 0.7, 0.8)
COLOR_GRID_OTHER_DISPLAY = (0.7, 0.7, 0.7, 0.6)

# ===== Grid (export) =====
COLOR_GRID_10_EXPORT = (0.1, 0.1, 0.1, 0.15)
COLOR_GRID_5_EXPORT = (0.7, 0.7, 0.7, 0.1)
COLOR_GRID_5V_EXPORT = (0.7, 0.7, 0.7, 0.1)
COLOR_GRID_OTHER_EXPORT = (0.7, 0.7, 0.7, 0.06)

# ===== Connection: Nodes and Junctions =====
COLOR_NODE_BASE = (0.1, 0.4, 0.9, 1)          # آبی پایه
COLOR_NODE_SELECTED = (0.1, 0.8, 0.3, 1)      # سبز روشن (انتخاب)
COLOR_NODE_DELETE_PENDING = (1.0, 0.0, 0.0, 1)

COLOR_JUNCTION = (0.9, 0.5, 0.0, 1)
COLOR_JUNCTION_SELECTED = (0.1, 0.8, 0.3, 1)
COLOR_JUNCTION_DELETE_PENDING = (1.0, 0.0, 0.0, 1)

# ===== Connection: Lines =====
COLOR_LINE_BASE = (0.1, 0.4, 0.9, 1)          # آبی پایه
COLOR_LINE_SELECTED = (0.1, 0.8, 0.3, 1)      # سبز روشن (انتخاب)
COLOR_LINE_DELETE_PENDING = (1.0, 0.0, 0.0, 1)

# ===== Phase endpoints (legacy) =====
COLOR_PHASE_START = (0.1, 0.7, 0.2, 1)
COLOR_PHASE_END = (0.9, 0.1, 0.1, 1)

# ===== Phase Groups R/U (NEW - DISTINCT) =====
COLOR_PHASE_GROUP_R = (1.0, 0.55, 0.0, 1)     # نارنجی آمبر
COLOR_PHASE_GROUP_U = (0.6, 0.2, 0.8, 1)      # بنفش
COLOR_PHASE_GROUP_CONFLICT = (1.0, 0.0, 0.0, 1)  # قرمز - فقط برای safety (رسم نمی‌شود)

# ===== Selection box =====
COLOR_SELECT_BOX_CONTAIN = (0.1, 0.5, 0.9, 0.5)
COLOR_SELECT_BOX_INTERSECT = (0.9, 0.5, 0.1, 0.5)