"""
================================================================================
File: utils/errors.py
Purpose: Legacy compatibility wrapper.
Version: 0.1.1
================================================================================
"""

from ui.notifications import (
    show_error, show_success, show_warning, show_info, show_confirm,
)


def show_temporary_error(message, duration=3):
    show_error(message, duration)


def show_temporary_success(message, duration=2):
    show_success(message, duration)


def show_temporary_warning(message, duration=4):
    show_warning(message, duration)


def show_temporary_info(message, duration=3):
    show_info(message, duration)