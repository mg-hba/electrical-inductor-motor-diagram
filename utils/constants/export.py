"""
================================================================================
File: utils/constants/export.py
Purpose: All export-related constants (paper, grid, diagram, table, labels).
Version: 0.1.2
================================================================================
"""

# ===== Export: formats and defaults =====
EXPORT_FORMATS = ['svg', 'pdf', 'eps', 'dxf', 'png', 'jpg']
DEFAULT_EXPORT_FORMAT = 'svg'
DEFAULT_EXPORT_DPI = 300
DEFAULT_EXPORT_QUALITY = 95
IMPORT_FORMATS = ['svg', 'dxf', 'pdf', 'png', 'jpg', 'eps']

# ===== Export: paper sizes (mm) =====
EXPORT_PAPER_SIZES_MM = {
    'A0': (841, 1189),
    'A1': (594, 841),
    'A2': (420, 594),
    'A3': (297, 420),
    'A4': (210, 297),
    'A5': (148, 210),
    'Letter': (216, 279),
    'Legal': (216, 356),
    'Tabloid': (279, 432),
}

# ===== Export: page layout (mm) =====
EXPORT_PAGE_MARGIN_MM = 1.0
EXPORT_PROJECT_MARGIN_MM = 5.0
EXPORT_INNER_MARGIN_MM = 2.0
EXPORT_MOTOR_LABEL_HEIGHT_MM = 10.0
EXPORT_INFO_HEIGHT_PERCENT = 0.18

# ===== Export: paper border =====
EXPORT_PAPER_BORDER_COLOR = (0.2, 0.4, 0.8, 1)
EXPORT_PAPER_BORDER_WIDTH = 2
EXPORT_PROJECT_BORDER_COLOR = (0.0, 0.0, 0.0, 1)
EXPORT_PROJECT_BORDER_WIDTH = 1
EXPORT_AREA_BORDER_COLOR = (0.5, 0.5, 0.5, 1)
EXPORT_AREA_BORDER_WIDTH = 1

# ===== Export: grid vertical lines =====
EXPORT_GRID_10_COLOR = (0.1, 0.1, 0.1, 0.6)
EXPORT_GRID_10_WIDTH = 1.5
EXPORT_GRID_5_COLOR = (0.4, 0.4, 0.4, 0.5)
EXPORT_GRID_5_WIDTH = 1.0
EXPORT_GRID_OTHER_COLOR = (0.7, 0.7, 0.7, 0.4)
EXPORT_GRID_OTHER_WIDTH = 0.5

# ===== Export: grid horizontal lines =====
EXPORT_GRID_5V_COLOR = (0.4, 0.4, 0.4, 0.5)
EXPORT_GRID_5V_WIDTH = 1.0

# ===== Export: diagram line widths =====
EXPORT_LINE_WIDTH_MAIN = 8
EXPORT_LINE_WIDTH_PHASE_1 = 5
EXPORT_LINE_WIDTH_PHASE_2 = 4 
EXPORT_LINE_WIDTH_PHASE_3 = 6 #red
# ===== Export: line width multipliers =====
EXPORT_LINE_WIDTH_SCALE = 2.0
EXPORT_FONT_SIZE_SCALE = 1.0

# ===== Export: diagram line colors =====
EXPORT_DIAGRAM_MAIN_COLOR = (0.0, 0.0, 0.0, 1)
EXPORT_DIAGRAM_PHASE_1_COLOR = (0.0, 0.0, 0.0, 1)
EXPORT_DIAGRAM_PHASE_2_COLOR = (0.2, 0.6, 0.8, 1)
EXPORT_DIAGRAM_PHASE_3_COLOR = (0.9, 0.2, 0.2, 1)

# ===== Export: connection lines =====
EXPORT_CONNECTION_LINE_WIDTH = 2
EXPORT_CONNECTION_PHASE_R_COLOR = (1.0, 0.55, 0.0, 1)
EXPORT_CONNECTION_PHASE_U_COLOR = (0.6, 0.2, 0.8, 1)
EXPORT_CONNECTION_PHASE_OTHER_COLOR = (0.1, 0.4, 0.9, 1)

# ===== Export: table text (header cells) =====
EXPORT_TABLE_HEADER_FONT_SIZE = 34
EXPORT_TABLE_HEADER_COLOR = (0.2, 0.4, 0.6, 1)
EXPORT_TABLE_HEADER_BOLD = True

# ===== Export: table text (body cells) =====
EXPORT_TABLE_BODY_FONT_SIZE = 38
EXPORT_TABLE_BODY_COLOR = (0.0, 0.0, 0.0, 1)
EXPORT_TABLE_BODY_BOLD = False

# ===== Export: table text (comment row) =====
EXPORT_TABLE_COMMENT_FONT_SIZE = 22
EXPORT_TABLE_COMMENT_COLOR = (0.0, 0.0, 0.0, 1)

# ===== Export: table cell backgrounds =====
EXPORT_TABLE_HEADER_BG_COLOR = (0.88, 0.92, 0.96, 1)
EXPORT_TABLE_BODY_BG_COLOR = (1.0, 1.0, 1.0, 1)
EXPORT_TABLE_COMMENT_BG_COLOR = (0.97, 0.97, 0.97, 1)

# ===== Export: table lines =====
EXPORT_TABLE_LINE_WIDTH = 1
EXPORT_TABLE_LINE_COLOR = (0.0, 0.0, 0.0, 1)

# ===== Export: motor name label =====
EXPORT_MOTOR_LABEL_FONT_SIZE = 30
EXPORT_MOTOR_LABEL_COLOR = (0.0, 0.0, 0.0, 1)

# ===== Export: slot numbers =====
EXPORT_SLOT_FONT_SIZE = 24
EXPORT_SLOT_COLOR = (0.0, 0.0, 0.0, 1)
EXPORT_SLOT_Y_OFFSET = 0.5

# ===== Export: logo =====
EXPORT_LOGO_OPACITY = 1.0