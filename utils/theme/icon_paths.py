"""
================================================================================
File: utils/theme/icon_paths.py
Purpose: Icon path resolver. Finds icons in assets/icons/* folders.
Version: 0.1.5
================================================================================
"""

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")

ICON_SUBFOLDERS = [
    'main', 'menu', 'zoom', 'connection', 'conflict',
    'app_info', 'docs', 'setup', 'file_ops', 'common', 'misc',
]


class IconPaths:
    """Resolve icon names to full paths."""

    BASE_DIR = BASE_DIR
    ICONS_DIR = ICONS_DIR
    SUBFOLDERS = ICON_SUBFOLDERS

    @classmethod
    def get_icon_path(cls, icon_name):
        """
        Get full path for an icon name.
        Searches all subfolders, then root.
        Returns '' if not found.
        """
        if not icon_name:
            return ''

        # Try each subfolder
        for sub in cls.SUBFOLDERS:
            path = os.path.join(cls.ICONS_DIR, sub, icon_name + '.png')
            if os.path.exists(path):
                return path

        # Try root
        path = os.path.join(cls.ICONS_DIR, icon_name + '.png')
        if os.path.exists(path):
            return path

        # Try svg
        for sub in cls.SUBFOLDERS:
            path = os.path.join(cls.ICONS_DIR, sub, icon_name + '.svg')
            if os.path.exists(path):
                return path

        return ''

    @classmethod
    def icon_exists(cls, icon_name):
        """Check if icon exists."""
        return bool(cls.get_icon_path(icon_name))

    @classmethod
    def list_all_icons(cls):
        """List all available icons (for debugging)."""
        result = {}
        for sub in cls.SUBFOLDERS:
            folder = os.path.join(cls.ICONS_DIR, sub)
            if os.path.isdir(folder):
                icons = []
                for f in os.listdir(folder):
                    if f.endswith(('.png', '.svg')):
                        icons.append(os.path.splitext(f)[0])
                result[sub] = sorted(icons)
        return result
