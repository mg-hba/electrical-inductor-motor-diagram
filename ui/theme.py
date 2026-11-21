"""
================================================================================
File: ui/theme.py
Purpose: Complete theme system:
         - Theme: general colors (backgrounds, text, inputs)
         - ButtonTheme: button colors and borders
         - DialogTheme: dialog layout dimensions and colors
Version: 0.1.5
================================================================================
"""


# ============================================================
# ================== THEME (General Colors) ==================
# ============================================================
class Theme:
    """General theme: backgrounds, text, inputs, sections."""

    # ---- Backgrounds ----
    MAIN_BG = (0.92, 0.95, 0.95, 1.0)
    DIALOG_BG = (0.95, 0.95, 0.95, 1.0)
    CONTENT_BG = (1.00, 1.00, 1.00, 1.0)
    SECTION_BG = (0.96, 0.96, 0.96, 1.0)
    SECTION_ALT_BG = (0.94, 0.94, 0.94, 1.0)
    SECTION_ALT2_BG = (0.97, 0.97, 0.97, 1.0)

    # ---- Inputs ----
    INPUT_BG = (1.00, 1.00, 1.00, 1.0)
    INPUT_DISABLED_BG = (0.85, 0.85, 0.85, 1.0)
    INPUT_TEXT = (0.0, 0.0, 0.0, 1.0)
    INPUT_ERROR_BG = (1.0, 0.8, 0.8, 1.0)

    # ---- Header ----
    HEADER_BG = (0.15, 0.35, 0.60, 1.0)
    HEADER_TEXT = (1.0, 1.0, 1.0, 1.0)
    HEADER_HEIGHT_DP = 44

    # ---- Text ----
    TEXT_PRIMARY = (0.0, 0.0, 0.0, 1.0)
    TEXT_SECONDARY = (0.2, 0.4, 0.6, 1.0)
    TEXT_MUTED = (0.5, 0.5, 0.5, 1.0)
    TEXT_DANGER = (0.8, 0.1, 0.1, 1.0)
    TEXT_SUCCESS = (0.0, 0.6, 0.0, 1.0)
    TEXT_WARNING = (0.8, 0.5, 0.1, 1.0)

    # ---- Dividers ----
    DIVIDER_COLOR = (0.7, 0.7, 0.7, 1.0)
    SECTION_DIVIDER_COLOR = (0.8, 0.8, 0.8, 1.0)
    DIVIDER_HEIGHT_DP = 4

    # ---- Status ----
    ERROR_TEXT = (1.0, 0.0, 0.0, 1.0)
    SUCCESS_TEXT = (0.0, 0.6, 0.0, 1.0)
    WARNING_TEXT = (0.9, 0.5, 0.0, 1.0)

    # ---- Fonts ----
    FONT_HEADER = '16sp'
    FONT_TITLE = '14sp'
    FONT_BODY = '13sp'
    FONT_SMALL = '12sp'
    FONT_TINY = '11sp'
    FONT_INFO_LANDSCAPE = '15sp'
    FONT_INFO_PORTRAIT = '13sp'

    # ---- Rounded corners ----
    ROUNDED_RADIUS = [6]

    # ---- Backward compat (used by older code) ----
    BUTTON_PRIMARY_BG = (0.2, 0.6, 0.85, 1.0)
    BUTTON_SUCCESS_BG = (0.2, 0.6, 0.3, 1.0)
    BUTTON_DANGER_BG = (0.7, 0.3, 0.3, 1.0)
    BUTTON_NEUTRAL_BG = (0.5, 0.5, 0.5, 1.0)
    BUTTON_TEXT = (1.0, 1.0, 1.0, 1.0)

    @staticmethod
    def refresh_from_config(json_manager):
        """Refresh theme from config (legacy)."""
        try:
            Theme.MAIN_BG = tuple(json_manager.get_main_bg_color())
            Theme.HEADER_BG = tuple(json_manager.get_header_bg_color())
            Theme.BUTTON_PRIMARY_BG = tuple(json_manager.get_button_bg_color())
            Theme.INPUT_ERROR_BG = tuple(json_manager.get_error_bg_color())
        except Exception:
            pass


# ============================================================
# ================== BUTTON THEME ============================
# ============================================================
class ButtonTheme:
    """Button types with colors and border."""

    TYPES = {
        'primary': {
            'bg': (0.20, 0.60, 0.85, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.10, 0.40, 0.65, 1.0),
            'border_width': 2,
            'hover_bg': (0.15, 0.50, 0.75, 1.0),
        },
        'success': {
            'bg': (0.20, 0.60, 0.30, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.10, 0.40, 0.15, 1.0),
            'border_width': 2,
            'hover_bg': (0.15, 0.50, 0.25, 1.0),
        },
        'danger': {
            'bg': (0.70, 0.30, 0.30, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.50, 0.15, 0.15, 1.0),
            'border_width': 2,
            'hover_bg': (0.60, 0.25, 0.25, 1.0),
        },
        'warning': {
            'bg': (0.90, 0.50, 0.10, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.70, 0.35, 0.05, 1.0),
            'border_width': 2,
            'hover_bg': (0.80, 0.45, 0.10, 1.0),
        },
        'neutral': {
            'bg': (0.50, 0.50, 0.50, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.35, 0.35, 0.35, 1.0),
            'border_width': 2,
            'hover_bg': (0.45, 0.45, 0.45, 1.0),
        },
        'toggle_on': {
            'bg': (0.20, 0.60, 0.85, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.10, 0.40, 0.65, 1.0),
            'border_width': 3,
            'hover_bg': (0.15, 0.50, 0.75, 1.0),
        },
        'toggle_off': {
            'bg': (0.50, 0.50, 0.50, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.55, 0.55, 0.55, 1.0),
        },
        'text': {
            'bg': (0.0, 0.0, 0.0, 0.0),
            'fg': (0.2, 0.4, 0.6, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.9, 0.9, 0.9, 1.0),
        },
        'header_close': {
            'bg': (0.0, 0.0, 0.0, 0.0),
            'fg': (1.0, 1.0, 1.0, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.8, 0.2, 0.2, 1.0),
        },
    }

    @classmethod
    def get_style(cls, button_type='primary'):
        return cls.TYPES.get(button_type, cls.TYPES['primary'])

    @classmethod
    def get_bg(cls, button_type='primary'):
        return cls.get_style(button_type)['bg']

    @classmethod
    def get_fg(cls, button_type='primary'):
        return cls.get_style(button_type)['fg']

    @classmethod
    def get_border(cls, button_type='primary'):
        return cls.get_style(button_type)['border']

    @classmethod
    def get_border_width(cls, button_type='primary'):
        return cls.get_style(button_type)['border_width']

    @classmethod
    def get_hover_bg(cls, button_type='primary'):
        return cls.get_style(button_type)['hover_bg']

    @classmethod
    def get_all_types(cls):
        return list(cls.TYPES.keys())


# ============================================================
# ================== DIALOG THEME ============================
# ============================================================
class DialogTheme:
    """Dialog layout dimensions and colors."""

    # ---- Dialog dimensions ----
    DEFAULT_WIDTH_RATIO = 0.95
    DEFAULT_HEIGHT_RATIO = 0.85
    SMALL_WIDTH_RATIO = 0.80
    SMALL_HEIGHT_RATIO = 0.50
    LARGE_WIDTH_RATIO = 0.98
    LARGE_HEIGHT_RATIO = 0.92

    # ---- Header ----
    HEADER_HEIGHT_DP = 44
    HEADER_PADDING = [10, 6, 10, 6]  # [left, top, right, bottom]
    HEADER_BG = (0.15, 0.35, 0.60, 1.0)
    HEADER_TEXT_COLOR = (1.0, 1.0, 1.0, 1.0)
    HEADER_FONT_SIZE = '14sp'

    # ---- Body ----
    BODY_BG = (0.95, 0.95, 0.95, 1.0)
    BODY_PADDING = [10, 8, 10, 8]
    BODY_SPACING_DP = 6

    # ---- Footer ----
    FOOTER_HEIGHT_DP = 56
    FOOTER_PADDING = [10, 6, 10, 6]
    FOOTER_SPACING_DP = 8
    FOOTER_BG = (0.96, 0.96, 0.96, 1.0)

    # ---- Section ----
    SECTION_PADDING = [5, 2, 5, 2]
    SECTION_SPACING_DP = 0
    SECTION_BG = (0.96, 0.96, 0.96, 1.0)
    SECTION_TITLE_COLOR = (0.2, 0.4, 0.6, 1.0)
    SECTION_TITLE_FONT = '11sp'
    SECTION_TITLE_HEIGHT_DP = 9

    # ---- Close button (X) ----
    CLOSE_BUTTON_SIZE = (30, 28)
    CLOSE_BUTTON_TYPE = 'header_close'

    # ---- Notification ----
    NOTIFICATION_WIDTH_RATIO = 0.85
    NOTIFICATION_HEIGHT_DP = 200
    NOTIFICATION_HEADER_HEIGHT_DP = 42
    NOTIFICATION_BODY_PADDING = [20, 12, 20, 12]

    # ---- Popup background ----
    POPUP_BG_COLOR = (0.0, 0.0, 0.0, 0.3)  # semi-transparent black

    @classmethod
    def get_size(cls, size_type='default'):
        """Get dialog size (w_ratio, h_ratio)."""
        if size_type == 'small':
            return (cls.SMALL_WIDTH_RATIO, cls.SMALL_HEIGHT_RATIO)
        elif size_type == 'large':
            return (cls.LARGE_WIDTH_RATIO, cls.LARGE_HEIGHT_RATIO)
        return (cls.DEFAULT_WIDTH_RATIO, cls.DEFAULT_HEIGHT_RATIO)


# ============================================================
# ================== BACKWARD COMPAT =========================
# ============================================================
# Old code that imported make_icon_button etc. from button_theme
# will still work via this shim
def get_button_style(button_type='primary'):
    return ButtonTheme.get_style(button_type)

def get_button_bg(button_type='primary'):
    return ButtonTheme.get_bg(button_type)

def get_button_fg(button_type='primary'):
    return ButtonTheme.get_fg(button_type)

def get_button_border(button_type='primary'):
    return ButtonTheme.get_border(button_type)

def get_button_border_width(button_type='primary'):
    return ButtonTheme.get_border_width(button_type)

def get_button_hover_bg(button_type='primary'):
    return ButtonTheme.get_hover_bg(button_type)

def get_all_button_types():
    return ButtonTheme.get_all_types()
