"""
================================================================================
File: ui/button_manager.py
Purpose: Central button factory. Creates all buttons in the app.
         Uses ButtonTheme, IconPaths, and supports toggle/persistent styles.
Version: 0.1.5
================================================================================
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp

from utils.theme import ButtonTheme, IconPaths, Theme, ColorPalette


# ============================================================
# ================== PRIMITIVE BUTTON WIDGETS ================
# ============================================================

class BorderButton(ButtonBehavior, BoxLayout):
    """
    Button with background, border, icon, text.
    Hover/pressed shows overlay.
    Toggle shows semi-transparent overlay when active.
    """

    def __init__(self,
                 text='',
                 icon_name='',
                 on_press_callback=None,
                 style='primary',
                 mode='normal',
                 is_active=False,
                 size=(None, None),
                 size_hint=(None, None),
                 height_dp=None,
                 width_dp=None,
                 icon_size_dp=None,   # None = auto-calculate
                 font_size='13sp',
                 align='center',
                 padding=(6, 4, 6, 4),
                 bold=False,
                 **kwargs):

        # ============================================================
        # RESOLVE SIZE
        # ============================================================
        w, h = size
        if h is None:
            h = dp(height_dp) if height_dp is not None else dp(38)
        if w is None and width_dp is not None:
            w = dp(width_dp)

        # Default size_hint
        if size_hint == (None, None):
            if w is None:
                size_hint = (1, None)
            else:
                size_hint = (None, None)

        # Auto-calc icon size: 60% of button height
        if icon_size_dp is None:
            h_px = h
            from kivy.metrics import Metrics
            density = Metrics.density if Metrics.density > 0 else 1.0
            h_dp_actual = h_px / density
            icon_size_dp = max(12, min(28, h_dp_actual * 0.6))

        super().__init__(
            orientation='horizontal',
            size_hint=size_hint,
            size=(w if w is not None else 0, h),
            padding=[dp(p) for p in padding],
            spacing=dp(4),
            **kwargs
        )

        # Store
        self.text = text
        self.icon_name = icon_name
        self.style_name = style
        self.mode = mode
        self.is_active = is_active
        self.align = align
        self.font_size = font_size
        self.bold = bold
        self._on_press_callback = on_press_callback
        self.icon_size_dp = icon_size_dp

        # Apply theme
        self._apply_style()

        # Build widget
        self._build()

        # Initial toggle state
        if self.mode == 'toggle':
            self._update_colors()

    # ============================================================
    # ================== STYLE ===================================
    # ============================================================

    def _apply_style(self):
        if self.mode == 'toggle':
            style_key = 'toggle_on' if self.is_active else 'toggle_off'
        else:
            style_key = self.style_name

        style = ButtonTheme.get_style(style_key)
        self.bg_color = style['bg']
        self.fg_color = style['fg']
        self.border_color = style['border']
        self.border_width = style['border_width']
        self.hover_bg = style['hover_bg']

    # ============================================================
    # ================== BUILD ===================================
    # ============================================================

    def _build(self):
        self.clear_widgets()
        self.canvas.before.clear()
        self.canvas.after.clear()

        # ============================================================
        # LAYER 1 (canvas.before): background + overlay
        # Overlay is BETWEEN background and content
        # ============================================================
        with self.canvas.before:
            # Background
            self._bg_color = Color(*self.bg_color)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

            # Overlay (semi-transparent — for hover/toggle)
            self._overlay_color = Color(0, 0, 0, 0)
            self._overlay_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_bg, size=self._update_bg)

        # ============================================================
        # LAYER 2 (children): icon + text
        # ============================================================
        has_icon = bool(self.icon_name)
        has_text = bool(self.text and self.text.strip())

        if has_icon and has_text:
            # [spacer-small] [icon] [text flex] [spacer-small]
            self.add_widget(Label(size_hint=(None, 1), width=dp(2)))
            self._add_icon()
            self._add_text(flex=True)
            self.add_widget(Label(size_hint=(None, 1), width=dp(2)))
        elif has_icon:
            # [spacer] [icon] [spacer]
            self.add_widget(Label(size_hint=(1, 1), text=''))
            self._add_icon()
            self.add_widget(Label(size_hint=(1, 1), text=''))
        elif has_text:
            # [spacer-small] [text flex] [spacer-small]
            self.add_widget(Label(size_hint=(None, 1), width=dp(4)))
            self._add_text(flex=True)
            self.add_widget(Label(size_hint=(None, 1), width=dp(4)))
        else:
            self.add_widget(Label(text=''))

        # ============================================================
        # LAYER 3 (canvas.after): border line (on top)
        # ============================================================
        with self.canvas.after:
            self._border_color = Color(*self.border_color)
            self._border_line = Line(
                rectangle=(self.x, self.y, self.width, self.height),
                width=max(1, self.border_width),
            )
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        if self._border_line is None:
            return
        self._border_line.rectangle = (
            self.x, self.y, self.width, self.height
        )

    def _add_icon(self):
        icon_path = IconPaths.get_icon_path(self.icon_name)
        size_px = dp(self.icon_size_dp)
        if icon_path:
            img = Image(
                source=icon_path,
                size_hint=(None, None),
                size=(size_px, size_px),
                allow_stretch=True,
                keep_ratio=True,
                color=self.fg_color,
            )
            self.add_widget(img)
        else:
            fallback = Label(
                text='?',
                font_size='14sp',
                color=self.fg_color,
                size_hint=(None, None),
                size=(size_px, size_px),
            )
            self.add_widget(fallback)

    def _add_text(self, flex=True):
        """Add text label — single line, ellipsis if too long."""
        lbl = Label(
            text=self.text,
            font_size=self.font_size,
            bold=self.bold,
            color=self.fg_color,
            halign='center',
            valign='middle',
            size_hint_x=1 if flex else None,
            size_hint_y=1,
            shorten=True,
            shorten_from='right',
            max_lines=1,
            markup=False,
        )

        def _update_text_size(instance, *args):
            instance.text_size = (instance.width, None)

        lbl.bind(width=_update_text_size)
        lbl.bind(size=_update_text_size)

        self.add_widget(lbl)

        # Force initial text_size
        from kivy.clock import Clock
        Clock.schedule_once(
            lambda dt: _update_text_size(lbl), 0
        )

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _update_overlay(self, *args):
        self._overlay_rect.pos = self.pos
        self._overlay_rect.size = self.size
        self._border_line.rectangle = (
            self.x, self.y, self.width, self.height
        )

    # ============================================================
    # ================== STATE ===================================
    # ============================================================

    def set_active(self, active):
        self.is_active = active
        if self.mode == 'toggle':
            self._apply_style()
            self._update_colors()

    def set_style(self, style_name):
        self.style_name = style_name
        self._apply_style()
        self._update_colors()

    def set_text(self, text):
        self.text = text
        for child in self.children:
            if isinstance(child, Label) and child.text not in ('', '?'):
                child.text = text
                return

    def set_enabled(self, enabled):
        self.disabled = not enabled
        if not enabled:
            self.style_name = 'disabled'
        self._apply_style()
        self._update_colors()

    def _update_colors(self):
        """Update bg, border, overlay, fg."""
        self._bg_color.rgba = self.bg_color

        # Border
        if self.border_width > 0:
            self._border_color.rgba = self.border_color
            self._border_line.width = max(1, self.border_width)
        else:
            self._border_color.rgba = (0, 0, 0, 0)
            self._border_line.width = 1

        # ============================================================
        # Overlay logic:
        #   - Toggle ACTIVE: strong orange overlay (0.4) — persistent
        #   - Toggle INACTIVE: none
        #   - Normal: none (hover adds temporarily)
        # ============================================================
        if self.mode == 'toggle' and self.is_active:
            self._overlay_color.rgba = (1.0, 0.55, 0.0, 0.40)
        else:
            self._overlay_color.rgba = (0, 0, 0, 0)

        # Children
        for child in self.children:
            if isinstance(child, Label):
                child.color = self.fg_color
            elif isinstance(child, Image):
                child.color = self.fg_color

    # ============================================================
    # ================== EVENTS ==================================
    # ============================================================

    def on_press(self):
        if self.mode == 'normal':
            # Hover effect: orange tint (30%)
            self._overlay_color.rgba = (1.0, 0.6, 0.2, 0.3)
            if self.border_width > 0:
                self._border_line.width = max(2, self.border_width + 1)
        elif self.mode == 'toggle':
            # Toggle switch
            self.set_active(not self.is_active)
            if self._on_press_callback:
                self._on_press_callback(self)

    def on_release(self):
        if self.mode == 'normal':
            # Clear hover overlay
            self._overlay_color.rgba = (0, 0, 0, 0)
            if self.border_width > 0:
                self._border_line.width = max(1, self.border_width)
            if self._on_press_callback:
                self._on_press_callback(self)
        # For toggle mode: DO NOTHING here
        # (set_active already handled colors)


# ============================================================
# ================== BUTTON MANAGER ==========================
# ============================================================

class ButtonManager:
    """
    Central factory for buttons.
    Keeps track of all created buttons.
    """

    def __init__(self):
        self._buttons = {}   # name → widget

    # ============================================================
    # ================== FACTORY METHODS =========================
    # ============================================================

    def create_icon_button(self,
                           icon_name,
                           on_press=None,
                           name=None,
                           style='primary',
                           size=(38, 30),
                           **kwargs):
        """
        Create a button with icon only.
        """
        widget = BorderButton(
            text='',
            icon_name=icon_name,
            on_press_callback=on_press,
            style=style,
            size=(dp(size[0]), dp(size[1])),
            size_hint=(None, None),
            height_dp=size[1],
            width_dp=size[0],
            icon_size_dp=min(size[0], size[1]) - 6,
            padding=(2, 2, 2, 2),
            **kwargs
        )
        if name:
            self._buttons[name] = widget
        return widget

    def create_text_button(self,
                           text,
                           on_press=None,
                           name=None,
                           style='primary',
                           width=80,
                           height=36,
                           font_size='13sp',
                           **kwargs):
        """
        Create a button with text only.
        """
        widget = BorderButton(
            text=text,
            icon_name='',
            on_press_callback=on_press,
            style=style,
            size=(dp(width), dp(height)),
            size_hint=(None, None),
            height_dp=height,
            width_dp=width,
            font_size=font_size,
            align='center',
            **kwargs
        )
        if name:
            self._buttons[name] = widget
        return widget

    def create_icon_text_button(self,
                                text,
                                icon_name,
                                on_press=None,
                                name=None,
                                style='primary',
                                height=38,
                                width=None,
                                icon_size=24,
                                font_size='13sp',
                                align='left',
                                mode='normal',
                                is_active=False,
                                **kwargs):
        """
        Create a button with icon + text.
        """
        widget = BorderButton(
            text=text,
            icon_name=icon_name,
            on_press_callback=on_press,
            style=style,
            size_hint=(None, None) if width else (1, None),
            size=(dp(width), dp(height)) if width else (None, dp(height)),
            height_dp=height,
            width_dp=width,
            icon_size_dp=icon_size,
            font_size=font_size,
            align=align,
            mode=mode,
            is_active=is_active,
            **kwargs
        )
        if name:
            self._buttons[name] = widget
        return widget

    def create_toggle_button(self,
                             text,
                             icon_name='',
                             on_press=None,
                             name=None,
                             is_active=False,
                             height=38,
                             width=None,
                             icon_size=24,
                             font_size='13sp',
                             **kwargs):
        """
        Create a toggle button (persistent active state).
        """
        widget = BorderButton(
            text=text,
            icon_name=icon_name,
            on_press_callback=on_press,
            style='toggle_off',
            mode='toggle',
            is_active=is_active,
            size_hint=(None, None) if width else (1, None),
            size=(dp(width), dp(height)) if width else (None, dp(height)),
            height_dp=height,
            width_dp=width,
            icon_size_dp=icon_size,
            font_size=font_size,
            **kwargs
        )
        if name:
            self._buttons[name] = widget
        return widget

    # ============================================================
    # ================== ACCESS ==================================
    # ============================================================

    def get_button(self, name):
        """Get button by name."""
        return self._buttons.get(name)

    def get_all_buttons(self):
        """Get all buttons."""
        return dict(self._buttons)

    def set_active(self, name, active):
        """Set active state for a toggle button by name."""
        btn = self._buttons.get(name)
        if btn is not None:
            btn.set_active(active)

    def set_enabled(self, name, enabled):
        """Enable/disable button by name."""
        btn = self._buttons.get(name)
        if btn is not None:
            btn.set_enabled(enabled)

    # ============================================================
    # ================== BATCH OPERATIONS ========================
    # ============================================================

    def disable_all(self):
        """Disable all buttons (e.g. during loading)."""
        for btn in self._buttons.values():
            btn.disabled = True

    def enable_all(self):
        """Enable all buttons."""
        for btn in self._buttons.values():
            btn.disabled = False


# ============================================================
# ================== GLOBAL INSTANCE =========================
# ============================================================
button_manager = ButtonManager()
