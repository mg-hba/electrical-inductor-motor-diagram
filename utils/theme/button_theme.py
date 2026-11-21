"""
================================================================================
File: utils/theme/button_theme.py
Purpose: Central button style system.
         All buttons use one of these types.
         Border color/width based on button purpose.
Version: 0.1.5
================================================================================
"""


class ButtonTheme:
    """Button types with background, foreground, border."""

    TYPES = {
        # Primary actions (Open, Draw, Next, OK)
        'primary': {
            'bg': (0.20, 0.60, 0.85, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.10, 0.40, 0.65, 1.0),
            'border_width': 2,
            'hover_bg': (0.15, 0.50, 0.75, 1.0),
        },

        # Success actions (Apply, Save, OK, Finish)
        'success': {
            'bg': (0.20, 0.60, 0.30, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.10, 0.40, 0.15, 1.0),
            'border_width': 2,
            'hover_bg': (0.15, 0.50, 0.25, 1.0),
        },

        # Danger actions (Cancel, Delete, Exit)
        'danger': {
            'bg': (0.70, 0.30, 0.30, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.50, 0.15, 0.15, 1.0),
            'border_width': 2,
            'hover_bg': (0.60, 0.25, 0.25, 1.0),
        },

        # Warning actions (Reset, Undo)
        'warning': {
            'bg': (0.90, 0.50, 0.10, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.70, 0.35, 0.05, 1.0),
            'border_width': 2,
            'hover_bg': (0.80, 0.45, 0.10, 1.0),
        },

        # Neutral actions (Back, Close)
        'neutral': {
            'bg': (0.50, 0.50, 0.50, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (0.35, 0.35, 0.35, 1.0),
            'border_width': 2,
            'hover_bg': (0.45, 0.45, 0.45, 1.0),
        },

        # Toggle ON (active state)
        'toggle_on': {
            'bg': (0.20, 0.75, 0.30, 1.0),
            'fg': (1.00, 1.00, 1.00, 1.0),
            'border': (1.00, 0.85, 0.10, 1.0),
            'border_width': 4,
            'hover_bg': (0.15, 0.65, 0.25, 1.0),
        },

        # Toggle OFF (inactive state)
        'toggle_off': {
            'bg': (0.65, 0.65, 0.65, 1.0),
            'fg': (0.30, 0.30, 0.30, 1.0),
            'border': (0.45, 0.45, 0.45, 1.0),
            'border_width': 1,
            'hover_bg': (0.55, 0.55, 0.55, 1.0),
        },

        # Text-only button (transparent bg)
        'text': {
            'bg': (0.0, 0.0, 0.0, 0.0),
            'fg': (0.2, 0.4, 0.6, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.9, 0.9, 0.9, 1.0),
        },

        # Header close button (X in header)
        'header_close': {
            'bg': (0.0, 0.0, 0.0, 0.0),
            'fg': (1.0, 1.0, 1.0, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.8, 0.2, 0.2, 1.0),
        },

        # Header minimize button (_ in header)
        'header_minimize': {
            'bg': (0.0, 0.0, 0.0, 0.0),
            'fg': (1.0, 1.0, 1.0, 1.0),
            'border': (0.0, 0.0, 0.0, 0.0),
            'border_width': 0,
            'hover_bg': (0.9, 0.7, 0.1, 1.0),
        },

        # Disabled button
        'disabled': {
            'bg': (0.75, 0.75, 0.75, 1.0),
            'fg': (0.5, 0.5, 0.5, 1.0),
            'border': (0.6, 0.6, 0.6, 1.0),
            'border_width': 1,
            'hover_bg': (0.75, 0.75, 0.75, 1.0),
        },
    }

    # ============================================================
    # ================== HELPER METHODS ==========================
    # ============================================================

    @classmethod
    def get_style(cls, button_type='primary'):
        """Get full style dict for a button type."""
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

    @classmethod
    def is_toggle(cls, button_type):
        """Check if a button type is a toggle type."""
        return button_type in ('toggle_on', 'toggle_off')
