"""
================================================================================
File: utils/theme/color_palette.py
Purpose: Color utilities - hex/rgba conversion, darken, lighten, alpha.
Version: 0.1.5
================================================================================
"""


class ColorPalette:
    """Preset color palette for quick access."""

    # ============================================================
    # ================== BASIC COLORS ============================
    # ============================================================
    BLACK = (0.0, 0.0, 0.0, 1.0)
    WHITE = (1.0, 1.0, 1.0, 1.0)
    RED = (1.0, 0.0, 0.0, 1.0)
    GREEN = (0.0, 0.6, 0.0, 1.0)
    BLUE = (0.2, 0.6, 0.85, 1.0)
    YELLOW = (1.0, 0.9, 0.0, 1.0)
    ORANGE = (1.0, 0.55, 0.0, 1.0)
    PURPLE = (0.6, 0.2, 0.8, 1.0)
    PINK = (1.0, 0.4, 0.7, 1.0)
    GRAY = (0.5, 0.5, 0.5, 1.0)

    # ============================================================
    # ================== PHASE COLORS ============================
    # ============================================================
    PHASE_R = (1.0, 0.55, 0.0, 1.0)      # Orange
    PHASE_U = (0.6, 0.2, 0.8, 1.0)        # Purple
    PHASE_1 = (0.0, 0.0, 0.0, 1.0)        # Black
    PHASE_2 = (0.2, 0.6, 0.8, 1.0)        # Blue
    PHASE_3 = (0.9, 0.2, 0.2, 1.0)        # Red

    # ============================================================
    # ================== CONNECTION COLORS =======================
    # ============================================================
    WIRE_BASE = (0.1, 0.4, 0.9, 1.0)
    WIRE_SELECTED = (0.1, 0.8, 0.3, 1.0)
    WIRE_DELETE = (1.0, 0.0, 0.0, 1.0)
    JUNCTION = (0.9, 0.5, 0.0, 1.0)
    LINE_BASE = (0.1, 0.4, 0.9, 1.0)
    LINE_SELECTED = (0.1, 0.8, 0.3, 1.0)


# ============================================================
# ================== CONVERSION HELPERS ======================
# ============================================================

def hex_to_rgba(hex_str, alpha=1.0):
    """
    Convert hex color to RGBA tuple.
    Examples: '#FF0000' → (1.0, 0.0, 0.0, 1.0)
              '#FF000080' → (1.0, 0.0, 0.0, 0.5)
    """
    if not hex_str:
        return (0.0, 0.0, 0.0, alpha)

    hex_str = hex_str.strip().lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c * 2 for c in hex_str)
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return (r, g, b, alpha)
    if len(hex_str) == 8:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        a = int(hex_str[6:8], 16) / 255.0
        return (r, g, b, a)
    return (0.0, 0.0, 0.0, alpha)


def rgba_to_hex(rgba):
    """
    Convert RGBA tuple to hex string.
    Example: (1.0, 0.0, 0.0, 1.0) → '#FF0000'
    """
    if not rgba or len(rgba) < 3:
        return '#000000'
    r = int(round(rgba[0] * 255))
    g = int(round(rgba[1] * 255))
    b = int(round(rgba[2] * 255))
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def darken(rgba, factor=0.2):
    """Make color darker by factor (0.0-1.0)."""
    if not rgba or len(rgba) < 3:
        return rgba
    r = max(0.0, rgba[0] - factor)
    g = max(0.0, rgba[1] - factor)
    b = max(0.0, rgba[2] - factor)
    a = rgba[3] if len(rgba) > 3 else 1.0
    return (r, g, b, a)


def lighten(rgba, factor=0.2):
    """Make color lighter by factor (0.0-1.0)."""
    if not rgba or len(rgba) < 3:
        return rgba
    r = min(1.0, rgba[0] + factor)
    g = min(1.0, rgba[1] + factor)
    b = min(1.0, rgba[2] + factor)
    a = rgba[3] if len(rgba) > 3 else 1.0
    return (r, g, b, a)


def with_alpha(rgba, alpha):
    """Return color with new alpha."""
    if not rgba or len(rgba) < 3:
        return (0.0, 0.0, 0.0, alpha)
    return (rgba[0], rgba[1], rgba[2], alpha)
