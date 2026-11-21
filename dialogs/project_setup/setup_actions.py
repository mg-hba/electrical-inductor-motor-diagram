"""
================================================================================
File: dialogs/project_setup/setup_actions.py
Purpose: Open, Save, Cancel, Comments, header title helpers.
Version: 0.1.2
================================================================================
"""

import os
from kivy.core.window import Window

from managers.json_manager import json_manager
from ui.notifications import show_error, show_success
from version import get_version_suffix

from dialogs.project_setup.setup_validation import (
    validate_json_data, validate_all,
)


##
###### Open existing project file ######
##
def setup_open_action(dialog):
    try:
        from dialogs.open_save import show_open_save_dialog

        def on_complete(action, data, filepath):
            if action == 'open':
                if validate_json_data(data):
                    if dialog.main_app_callback:
                        dialog.main_app_callback(filepath, data)
                    dialog.dismiss()
                    show_success('Loaded: ' + os.path.basename(filepath), 2)
                else:
                    show_error('Invalid project file format', 3)

        show_open_save_dialog(mode='open', project_data=None,
                               on_complete_callback=on_complete)
    except Exception as e:
        show_error('Error: ' + str(e), 2)
# end setup_open_action


##
###### Save project to file ######
##
def setup_save_action(dialog):
    if not validate_all(dialog.name_input, dialog.power_input,
                         dialog.all_slots_input,
                         dialog.wire_items, dialog.turns_items):
        show_error('Please fill all empty fields', 2)
        return
    project_data = dialog.get_current_project_data()
    try:
        from dialogs.open_save import show_open_save_dialog

        def on_complete(action, data, filepath):
            if action == 'save':
                if dialog.main_app_callback:
                    dialog.main_app_callback(filepath, data)
                dialog.dismiss()
                show_success('Saved: ' + os.path.basename(filepath), 2)

        show_open_save_dialog(mode='save', project_data=project_data,
                               on_complete_callback=on_complete)
    except Exception as e:
        show_error('Error: ' + str(e), 2)
# end setup_save_action


##
###### Handle cancel/close action ######
##
def setup_cancel_action(dialog):
    if dialog.is_startup:
        Window.close()
    else:
        dialog.dismiss()
# end setup_cancel_action


##
###### Open comments editor dialog ######
##
def setup_comments_action(dialog):
    from dialogs.comments_dialog import show_comments_dialog

    def on_apply(text):
        if json_manager.project_data is not None:
            json_manager.project_data['comments'] = text

    initial = ''
    if json_manager.project_data:
        initial = json_manager.project_data.get('comments', '')
    show_comments_dialog(initial_text=initial, on_apply=on_apply)
# end setup_comments_action


##
###### Update header title based on form values ######
##
def update_header_title_action(dialog):
    project_name = dialog.name_input.text.strip()
    project_power = dialog.power_input.text.strip()
    if project_name and project_power:
        dialog.header_title.text = ('NEW DIAGRAM - ' + project_name +
                                     '_' + project_power +
                                     get_version_suffix())
    else:
        dialog.header_title.text = 'NEW DIAGRAM' + get_version_suffix()
# end update_header_title_action