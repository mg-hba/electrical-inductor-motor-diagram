"""
================================================================================
File: version.py
Purpose: Central version information.
Version: 0.1.3
================================================================================
"""

__version__ = "0.1.3"
__release_date__ = "2026-11-06"
__app_name__ = "Motor Winding Diagram"
__author__ = "Zarin Tile Factory"
__developer_senior__ = "Eng. Moteshare"
__developer_junior__ = "Mahdi Ghasemi"


def get_version_suffix():
    return " - v" + __version__


def get_app_title():
    return __app_name__ + get_version_suffix()


def get_window_title(name):
    return name + get_version_suffix()
