"""
================================================================================
File: dialogs/setup_validation.py
Purpose: Field validation helpers for Project Setup dialog.
Version: 0.1.1
================================================================================
"""

from ui.theme import Theme


def validate_wire_gauges(wire_items):
    is_valid = True
    has_value = False
    for row in wire_items:
        for child in row.children:
            from kivy.uix.textinput import TextInput
            if isinstance(child, TextInput):
                if child.text.strip():
                    child.background_color = Theme.INPUT_BG
                    has_value = True
                else:
                    child.background_color = Theme.INPUT_ERROR_BG
                    is_valid = False
    return is_valid and has_value


def validate_turns_counts(turns_items):
    is_valid = True
    has_value = False
    for row in turns_items:
        for child in row.children:
            from kivy.uix.textinput import TextInput
            if isinstance(child, TextInput):
                if child.text.strip():
                    child.background_color = Theme.INPUT_BG
                    has_value = True
                else:
                    child.background_color = Theme.INPUT_ERROR_BG
                    is_valid = False
    return is_valid and has_value


def validate_motor_fields(all_slots_input):
    try:
        slots = int(all_slots_input.text.strip())
        if slots < 6:
            all_slots_input.background_color = Theme.INPUT_ERROR_BG
            return False
        all_slots_input.background_color = Theme.INPUT_BG
        return True
    except Exception:
        all_slots_input.background_color = Theme.INPUT_ERROR_BG
        return False


def validate_all(name_input, power_input, all_slots_input,
                  wire_items, turns_items):
    is_valid = True

    if not name_input.text.strip():
        name_input.background_color = Theme.INPUT_ERROR_BG
        is_valid = False
    else:
        name_input.background_color = Theme.INPUT_BG

    if not power_input.text.strip():
        power_input.background_color = Theme.INPUT_ERROR_BG
        is_valid = False
    else:
        power_input.background_color = Theme.INPUT_BG

    if not validate_motor_fields(all_slots_input):
        is_valid = False
    if not validate_wire_gauges(wire_items):
        is_valid = False
    if not validate_turns_counts(turns_items):
        is_valid = False

    return is_valid


def validate_json_data(data):
    if not data:
        return False
    required = ['project_name', 'nominal_power', 'connection_type',
                'winding_type', 'paper_size', 'orientation']
    for f in required:
        if f not in data:
            return False
    if not data['project_name'] or not str(data['project_name']).strip():
        return False
    try:
        if float(data['nominal_power']) <= 0:
            return False
    except Exception:
        return False
    if data['connection_type'] not in ['Star', 'Delta', 'Star-Delta']:
        return False
    if data['winding_type'] not in ['two_layer', 'single_layer']:
        return False
    if data['paper_size'] not in ['A0', 'A1', 'A2', 'A3', 'A4', 'A5',
                                    'Letter', 'Legal', 'Tabloid']:
        return False
    if data['orientation'] not in ['Portrait', 'Landscape']:
        return False
    return True