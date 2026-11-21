"""
================================================================================
File: dialogs/project_setup/setup_wire_turns.py
Purpose: Wire gauge and turns list management.
Version: 0.1.2
================================================================================
"""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.clock import Clock

from ui.theme import Theme
from ui.icon_button import make_icon_button

from utils.constants import PROJECT_SETUP_INPUT_HEIGHT, PROJECT_SETUP_INPUT_FONT


##
###### Add a new wire gauge input row ######
##
def add_wire_item(dialog, instance=None, value=None, focus_new=True):
    row = BoxLayout(orientation='horizontal', spacing=dp(3),
                    size_hint_y=None,
                    height=dp(PROJECT_SETUP_INPUT_HEIGHT + 3))
    input_field = TextInput(
        text=value if value else '',
        multiline=False, font_size=PROJECT_SETUP_INPUT_FONT,
        size_hint_x=0.78, size_hint_y=None,
        height=dp(PROJECT_SETUP_INPUT_HEIGHT),
        background_color=Theme.INPUT_BG,
        foreground_color=Theme.INPUT_TEXT,
        input_filter='float', hint_text='mm'
    )
    input_field.bind(text=lambda i, v: update_wire_sum(dialog))
    input_field.bind(on_text_validate=lambda i: on_enter_in_wire(dialog, i))

    delete_button = make_icon_button(
        text='X', icon_name='delete',
        on_press=lambda x, r=row: remove_wire_item(dialog, r),
        size=(dp(28), dp(PROJECT_SETUP_INPUT_HEIGHT)),
        bg_color=Theme.BUTTON_DANGER_BG,
    )

    row.add_widget(input_field)
    row.add_widget(delete_button)
    dialog.wire_container.add_widget(row)
    dialog.wire_items.append(row)
    update_wire_sum(dialog)
    if focus_new:
        Clock.schedule_once(
            lambda dt, w=input_field: setattr(w, 'focus', True), 0.1
        )
# end add_wire_item


##
###### Remove wire gauge input row ######
##
def remove_wire_item(dialog, row):
    if row in dialog.wire_container.children:
        dialog.wire_container.remove_widget(row)
        dialog.wire_items.remove(row)
        update_wire_sum(dialog)
        focus_first_turns(dialog)
# end remove_wire_item


##
###### Handle Enter key in wire input ######
##
def on_enter_in_wire(dialog, instance):
    current_index = -1
    current_row = None
    for index, row in enumerate(dialog.wire_items):
        for child in row.children:
            if child == instance:
                current_index = index
                current_row = row
                break
        if current_index != -1:
            break
    if instance.text.strip():
        next_empty, _ = get_next_empty_wire(dialog, current_index)
        if next_empty:
            Clock.schedule_once(
                lambda dt, w=next_empty: setattr(w, 'focus', True), 0.05
            )
        else:
            add_wire_item(dialog, focus_new=True)
    else:
        if len(dialog.wire_items) > 1:
            remove_wire_item(dialog, current_row)
        else:
            focus_first_turns(dialog)
# end on_enter_in_wire


##
###### Find first empty wire input after given index ######
##
def get_next_empty_wire(dialog, start_index):
    for index, row in enumerate(dialog.wire_items):
        if index <= start_index:
            continue
        for child in row.children:
            if isinstance(child, TextInput) and not child.text.strip():
                return child, index
    return None, -1
# end get_next_empty_wire


##
###### Calculate RMS of wire gauges ######
##
def calculate_wire_sum(dialog):
    total_squared = 0.0
    for row in dialog.wire_items:
        for child in row.children:
            if isinstance(child, TextInput):
                try:
                    value = float(child.text.strip())
                    total_squared += value * value
                except Exception:
                    pass
    return round(math.sqrt(total_squared), 3)
# end calculate_wire_sum


##
###### Update wire sum display ######
##
def update_wire_sum(dialog):
    if hasattr(dialog, 'wire_sum_input') and dialog.wire_sum_input:
        dialog.wire_sum_input.text = str(calculate_wire_sum(dialog)) + ' mm'
# end update_wire_sum


##
###### Add a new turns input row ######
##
def add_turns_item(dialog, instance=None, value=None, focus_new=True):
    row = BoxLayout(orientation='horizontal', spacing=dp(3),
                    size_hint_y=None,
                    height=dp(PROJECT_SETUP_INPUT_HEIGHT + 3))
    input_field = TextInput(
        text=value if value else '',
        multiline=False, font_size=PROJECT_SETUP_INPUT_FONT,
        size_hint_x=0.78, size_hint_y=None,
        height=dp(PROJECT_SETUP_INPUT_HEIGHT),
        background_color=Theme.INPUT_BG,
        foreground_color=Theme.INPUT_TEXT,
        input_filter='int', hint_text='turns'
    )
    input_field.bind(text=lambda i, v: update_turns_sum(dialog))
    input_field.bind(on_text_validate=lambda i: on_enter_in_turns(dialog, i))

    delete_button = make_icon_button(
        text='X', icon_name='delete',
        on_press=lambda x, r=row: remove_turns_item(dialog, r),
        size=(dp(28), dp(PROJECT_SETUP_INPUT_HEIGHT)),
        bg_color=Theme.BUTTON_DANGER_BG,
    )

    row.add_widget(input_field)
    row.add_widget(delete_button)
    dialog.turns_container.add_widget(row)
    dialog.turns_items.append(row)
    update_turns_sum(dialog)
    if focus_new:
        Clock.schedule_once(
            lambda dt, w=input_field: setattr(w, 'focus', True), 0.1
        )
# end add_turns_item


##
###### Remove turns input row ######
##
def remove_turns_item(dialog, row):
    if row in dialog.turns_container.children:
        dialog.turns_container.remove_widget(row)
        dialog.turns_items.remove(row)
        update_turns_sum(dialog)
# end remove_turns_item


##
###### Handle Enter key in turns input ######
##
def on_enter_in_turns(dialog, instance):
    current_index = -1
    current_row = None
    for index, row in enumerate(dialog.turns_items):
        for child in row.children:
            if child == instance:
                current_index = index
                current_row = row
                break
        if current_index != -1:
            break
    if instance.text.strip():
        next_empty, _ = get_next_empty_turns(dialog, current_index)
        if next_empty:
            Clock.schedule_once(
                lambda dt, w=next_empty: setattr(w, 'focus', True), 0.05
            )
        else:
            add_turns_item(dialog, focus_new=True)
    else:
        if len(dialog.turns_items) > 1:
            remove_turns_item(dialog, current_row)
# end on_enter_in_turns


##
###### Find first empty turns input after given index ######
##
def get_next_empty_turns(dialog, start_index):
    for index, row in enumerate(dialog.turns_items):
        if index <= start_index:
            continue
        for child in row.children:
            if isinstance(child, TextInput) and not child.text.strip():
                return child, index
    return None, -1
# end get_next_empty_turns


##
###### Calculate total turns ######
##
def calculate_turns_sum(dialog):
    total = 0
    for row in dialog.turns_items:
        for child in row.children:
            if isinstance(child, TextInput):
                try:
                    total += int(child.text.strip())
                except Exception:
                    pass
    return total
# end calculate_turns_sum


##
###### Update turns sum display ######
##
def update_turns_sum(dialog):
    if hasattr(dialog, 'turns_sum_input') and dialog.turns_sum_input:
        dialog.turns_sum_input.text = (str(calculate_turns_sum(dialog)) +
                                        ' turns')
# end update_turns_sum