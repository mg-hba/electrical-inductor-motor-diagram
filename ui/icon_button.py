"""
================================================================================
File: ui/icon_button.py
Purpose: Backward-compatible button factory.
         Delegates to button_manager internally.
         All old calls work without change.
Version: 0.1.5
================================================================================
"""

from kivy.metrics import dp

from utils.theme import IconPaths, ButtonTheme
from ui.button_manager import BorderButton, button_manager


# ============================================================
# ================== LEGACY API ==============================
# ============================================================

def get_icon_path(icon_name):
    """Get full path for an icon name."""
    return IconPaths.get_icon_path(icon_name)


def make_icon_button(text, icon_name, on_press,
                     size_hint=(None, None), size=(dp(38), dp(30)),
                     font_size='12sp',
                     bg_color=None,
                     fg_color=None,
                     button_type='primary'):
    """
    Legacy API — creates icon button.
    Delegates to BorderButton directly.
    """
    width, height = size

    # Determine if text should be shown (fallback)
    icon_exists = bool(IconPaths.get_icon_path(icon_name))
    display_text = '' if icon_exists else text

    widget = BorderButton(
        text=display_text,
        icon_name=icon_name,
        on_press_callback=on_press,
        style=button_type,
        size=(width, height),
        size_hint=size_hint,
        # icon_size_dp=None → auto-calc 60% of button height
        font_size=font_size,
        align='center',
        padding=(2, 2, 2, 2),
    )

    # Custom colors (override)
    if bg_color is not None:
        widget.bg_color = bg_color
        widget._bg_color.rgba = bg_color
    if fg_color is not None:
        widget.fg_color = fg_color
        from kivy.uix.label import Label
        from kivy.uix.image import Image
        for child in widget.children:
            if isinstance(child, (Label, Image)):
                child.color = fg_color

    return widget


class IconTextButton(BorderButton):
    """
    Legacy IconTextButton — wraps BorderButton.
    """

    def __init__(self, text='', icon_name='', on_press=None,
                 height=dp(38), icon_size=dp(26),
                 font_size='13sp',
                 bg_color=None,
                 fg_color=None,
                 align='left',
                 padding=(dp(8), dp(2), dp(8), dp(2)),
                 button_type='primary',
                 width=None,
                 **kwargs):

        widget_kwargs = {
            'text': text,
            'icon_name': icon_name,
            'on_press_callback': on_press,
            'style': button_type,
            'size_hint': (None, None) if width else (1, None),
            'size': (dp(width) if width else None, height),
            'icon_size_dp': icon_size,
            'font_size': font_size,
            'align': align,
            'padding': padding,
        }
        widget_kwargs.update(kwargs)

        super().__init__(**widget_kwargs)

        if bg_color is not None:
            self.bg_color = bg_color
            self._bg_color.rgba = bg_color
        if fg_color is not None:
            self.fg_color = fg_color
            from kivy.uix.label import Label
            from kivy.uix.image import Image
            for child in self.children:
                if isinstance(child, (Label, Image)):
                    child.color = fg_color

    def set_text(self, value):
        super().set_text(value)

    def set_bg_color(self, color):
        self.bg_color = color
        self._bg_color.rgba = color


def make_icon_text_button(text, icon_name, on_press,
                          height=dp(38),
                          icon_size=dp(26),
                          font_size='13sp',
                          bg_color=None,
                          fg_color=None,
                          align='left',
                          button_type='primary',
                          width=None,
                          **kwargs):
    """
    Legacy API — creates icon+text button.
    Delegates to BorderButton.
    """
    # Convert icon_size to dp number (avoid double dp())
    from kivy.metrics import Metrics
    density = Metrics.density if Metrics.density > 0 else 1.0
    icon_size_dp_num = (icon_size / density) if icon_size else None

    widget = BorderButton(
        text=text,
        icon_name=icon_name,
        on_press_callback=on_press,
        style=button_type,
        size_hint=(None, None) if width else (1, None),
        size=(dp(width) if width else None, height),
        icon_size_dp=icon_size_dp_num,
        font_size=font_size,
        align=align,
        **kwargs
    )

    if bg_color is not None:
        widget.bg_color = bg_color
        widget._bg_color.rgba = bg_color
    if fg_color is not None:
        widget.fg_color = fg_color
        from kivy.uix.label import Label
        from kivy.uix.image import Image
        for child in widget.children:
            if isinstance(child, (Label, Image)):
                child.color = fg_color

    return widget


__all__ = [
    'get_icon_path',
    'make_icon_button',
    'make_icon_text_button',
    'IconTextButton',
    'button_manager',
    'BorderButton',
]
