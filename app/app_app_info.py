"""
================================================================================
File: app/app_app_info.py
Purpose: App Info, docs, changelog viewer.
Version: 0.1.3
================================================================================
"""

from kivy.clock import Clock

from dialogs.app_info import show_app_info
from dialogs.docs_viewer import show_docs_viewer
from dialogs.changelog_viewer import show_changelog_viewer


def open_app_info_dialog(app):
    show_app_info(
        app.docs_manager,
        on_open_docs=lambda cat_id: open_docs_category(app, cat_id),
        on_open_changelog=lambda: open_changelog_viewer(app),
    )


def open_docs_category(app, category_id):
    for category in app.docs_manager.get_categories():
        if category.get("id") == category_id:
            file_relative = category.get("file", "")
            text = app.docs_manager.load_markdown(file_relative)
            title = category.get("title", category_id)
            Clock.schedule_once(
                lambda dt: show_docs_viewer(
                    title, text, app.docs_manager
                ),
                0.05
            )
            return


def open_changelog_viewer(app):
    show_changelog_viewer(
        app.docs_manager,
        on_open_version=lambda version_id, filepath:
            open_changelog_version(app, version_id, filepath),
    )


def open_changelog_version(app, version_id, filepath):
    text = app.docs_manager.load_markdown(filepath)
    Clock.schedule_once(
        lambda dt: show_docs_viewer(
            version_id, text, app.docs_manager
        ),
        0.05
    )