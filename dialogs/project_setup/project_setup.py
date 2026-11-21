"""
================================================================================
File: dialogs/project_setup/project_setup.py
Purpose: Project Setup package entry point.
Version: 0.1.4.1
================================================================================
"""

import os

from managers.json_manager import json_manager
from managers.debug_logger import debug_logger


def show_project_setup(main_app_callback=None, is_startup=False):
    try:
        from dialogs.project_setup.setup_wizard import ProjectSetupWizard

        project_root = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        ))

        def on_finish(filepath, data):
            if main_app_callback:
                main_app_callback(filepath, data)

        def on_cancel():
            # بستن کامل اپ - هر دو حالت startup و non-startup
            from kivy.clock import Clock
            from kivy.core.window import Window
            # تأخیر خیلی کم برای فرصت dismiss شدن
            Clock.schedule_once(lambda dt: Window.close(), 0.05)

        wizard = ProjectSetupWizard(
            on_finish=on_finish,
            on_cancel=on_cancel,
            project_root=project_root,
        )
        wizard.open()
        return wizard
    except Exception as e:
        from ui.notifications import show_error
        show_error('Error opening wizard: ' + str(e), 3)
        debug_logger.log_error("SHOW_WIZARD_FAIL", e, "ProjectSetup")
        return None


def update_all_spinners():
    pass


def open_standalone_page(app, page_name):
    if not json_manager.project_data:
        from ui.notifications import show_error
        show_error("Please load a project first", 3)
        return

    try:
        from kivy.uix.popup import Popup
        from kivy.graphics import Color
        from ui.theme import Theme

        page = None
        if page_name == "project":
            from dialogs.project_setup.page_project import PageProject
            page = PageProject()
        elif page_name == "motor":
            from dialogs.project_setup.page_motor import PageMotor
            page = PageMotor()
        elif page_name == "paper":
            from dialogs.project_setup.page_paper import PagePaper
            page = PagePaper()
        elif page_name == "physical":
            from dialogs.project_setup.page_physical import PagePhysical
            page = PagePhysical()
        else:
            return

        page.mode = "standalone"
        page.is_first_page = False
        page.is_last_page = False
        page.load_data(json_manager.project_data)

        popup = Popup(
            title='',
            size_hint=(0.95, 0.7),
            background_color=[0, 0, 0, 0],
            auto_dismiss=False,
        )

        def on_save(page_instance):
            if not page_instance.validate():
                from ui.notifications import show_error
                show_error('Please fix highlighted fields', 2)
                return
            page_data = page_instance.get_data()
            for k, v in page_data.items():
                json_manager.project_data[k] = v
            filepath = json_manager.current_project_file
            if filepath:
                json_manager.save_project_data(
                    filepath, json_manager.project_data
                )
                from ui.notifications import show_success
                show_success('Saved', 2)
            popup.dismiss()

        def on_cancel(page_instance):
            popup.dismiss()

        page.on_save = on_save
        page.on_cancel = on_cancel
        page.on_physical = None

        popup.content = page
        popup.open()
        return popup

    except Exception as e:
        from ui.notifications import show_error
        show_error('Error: ' + str(e), 3)
        return None
