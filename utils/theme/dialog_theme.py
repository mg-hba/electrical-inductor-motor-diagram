"""
================================================================================
File: utils/theme/dialog_theme.py
Purpose: Dialog layout dimensions and colors.
         Used by BaseDialog and all dialogs.
Version: 0.1.5
================================================================================
"""


class DialogTheme:
    """Dialog layout dimensions and colors."""

    # ============================================================
    # ================== DIALOG DIMENSIONS =======================
    # ============================================================
    DEFAULT_WIDTH_RATIO = 0.95
    DEFAULT_HEIGHT_RATIO = 0.85
    SMALL_WIDTH_RATIO = 0.80
    SMALL_HEIGHT_RATIO = 0.50
    LARGE_WIDTH_RATIO = 0.98
    LARGE_HEIGHT_RATIO = 0.92
    MIN_WIDTH_DP = 300
    MIN_HEIGHT_DP = 200

    # ============================================================
    # ================== HEADER ==================================
    # ============================================================
    HEADER_HEIGHT_DP = 44
    HEADER_PADDING = [10, 6, 10, 6]        # [left, top, right, bottom]
    HEADER_BG = (0.15, 0.35, 0.60, 1.0)
    HEADER_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
    HEADER_FONT_SIZE = '14sp'
    HEADER_FONT_BOLD = True

    # Header buttons (minimize, close)
    HEADER_BUTTON_SIZE = (30, 28)
    HEADER_BUTTON_SPACING = 4

    # ============================================================
    # ================== BODY ====================================
    # ============================================================
    BODY_BG = (0.95, 0.95, 0.95, 1.0)
    BODY_PADDING = [10, 8, 10, 8]
    BODY_SPACING_DP = 6

    # ============================================================
    # ================== FOOTER ==================================
    # ============================================================
    FOOTER_HEIGHT_DP = 56
    FOOTER_PADDING = [10, 6, 10, 6]
    FOOTER_SPACING_DP = 8
    FOOTER_BG = (0.96, 0.96, 0.96, 1.0)

    # ============================================================
    # ================== SECTION =================================
    # ============================================================
    SECTION_PADDING = [5, 2, 5, 2]
    SECTION_SPACING_DP = 0
    SECTION_BG = (0.96, 0.96, 0.96, 1.0)
    SECTION_TITLE_COLOR = (0.2, 0.4, 0.6, 1.0)
    SECTION_TITLE_FONT = '11sp'
    SECTION_TITLE_HEIGHT_DP = 9

    # ============================================================
    # ================== CLOSE / MINIMIZE ========================
    # ============================================================
    CLOSE_BUTTON_TYPE = 'header_close'
    MINIMIZE_BUTTON_TYPE = 'header_minimize'

    # ============================================================
    # ================== NOTIFICATION ============================
    # ============================================================
    NOTIFICATION_WIDTH_RATIO = 0.85
    NOTIFICATION_HEIGHT_DP = 200
    NOTIFICATION_HEADER_HEIGHT_DP = 42
    NOTIFICATION_BODY_PADDING = [20, 12, 20, 12]

    # ============================================================
    # ================== RESIZE HANDLE ===========================
    # ============================================================
    RESIZE_HANDLE_SIZE_DP = 20
    RESIZE_HANDLE_COLOR = (0.5, 0.5, 0.5, 0.6)

    # ============================================================
    # ================== DRAG ====================================
    # ============================================================
    DRAG_MIN_MOVE_DP = 4
    DRAG_FROM_HEADER_ONLY = True

    # ============================================================
    # ================== FOCUS ===================================
    # ============================================================
    FOCUS_BORDER_COLOR = (0.2, 0.6, 0.85, 1.0)
    FOCUS_BORDER_WIDTH = 3

    # ============================================================
    # ================== PERSISTENCE =============================
    # ============================================================
    SAVE_SIZE_ON_RESIZE = True
    SAVE_POS_ON_DRAG = False

    # ============================================================
    # ================== POPUP BACKGROUND ========================
    # ============================================================
    POPUP_BG_COLOR = (0.0, 0.0, 0.0, 0.3)

    # ============================================================
    # ================== HELPER METHODS ==========================
    # ============================================================

    @classmethod
    def get_size(cls, size_type='default'):
        """Get dialog size ratios (width_ratio, height_ratio)."""
        if size_type == 'small':
            return (cls.SMALL_WIDTH_RATIO, cls.SMALL_HEIGHT_RATIO)
        elif size_type == 'large':
            return (cls.LARGE_WIDTH_RATIO, cls.LARGE_HEIGHT_RATIO)
        return (cls.DEFAULT_WIDTH_RATIO, cls.DEFAULT_HEIGHT_RATIO)
