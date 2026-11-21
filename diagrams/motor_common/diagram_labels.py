"""
================================================================================
File: diagrams/motor_common/diagram_labels.py
Purpose: Slot numbers, phase labels, motor name label.
Version: 0.1.4
================================================================================
"""

from kivy.uix.label import Label

from managers.json_manager import json_manager
from diagrams.base.diagram_base import get_speed, mm_to_px

from utils.constants import (
    SLOT_NUMBER_X_SHIFT,
    SLOT_BASE_FONT_SIZE, SLOT_LABEL_WIDTH, SLOT_LABEL_HEIGHT,
    SLOT_STEP_LEVEL_0_DISPLAY, SLOT_STEP_LEVEL_1_DISPLAY,
    SLOT_STEP_LEVEL_2_DISPLAY, SLOT_STEP_EXPORT,
    ENABLE_SLOT_NUMBERS,
)


def calculate_slot_numbers(diagram, level, is_export=False):
    if is_export:
        if diagram.SLOT_numbers_export_cache is not None:
            return diagram.SLOT_numbers_export_cache
    if not is_export and level in diagram.SLOT_numbers_cache:
        return diagram.SLOT_numbers_cache[level]

    all_slots = diagram.MOTOR_all_slots

    if is_export:
        step = SLOT_STEP_EXPORT
    else:
        if level == 0:
            step = SLOT_STEP_LEVEL_0_DISPLAY
        elif level == 1:
            step = SLOT_STEP_LEVEL_1_DISPLAY
        else:
            step = SLOT_STEP_LEVEL_2_DISPLAY

    numbers = []
    for slot in range(1, all_slots + 1):
        if slot == 1 or slot == all_slots:
            numbers.append(slot)
        elif slot % step == 0:
            numbers.append(slot)

    if is_export:
        diagram.SLOT_numbers_export_cache = numbers
    else:
        diagram.SLOT_numbers_cache[level] = numbers
    return numbers


def get_font_size_for_slot(diagram):
    return int(SLOT_BASE_FONT_SIZE * diagram.SCREEN_scale)


def rebuild_slot_labels(diagram):
    for label in diagram.SLOT_labels:
        diagram.remove_widget(label)
    diagram.SLOT_labels = []

    new_level = diagram.get_zoom_level()
    diagram.current_level = new_level
    slot_numbers = calculate_slot_numbers(diagram, new_level,
                                           is_export=False)
    if not slot_numbers:
        return
    font_size = max(8, min(48, get_font_size_for_slot(diagram)))

    for real_slot in slot_numbers:
        label = Label(text=str(real_slot), font_size=font_size,
                       bold=True, color=[0, 0, 0, 1],
                       size_hint=(None, None),
                       size=(SLOT_LABEL_WIDTH, SLOT_LABEL_HEIGHT),
                       halign='center', valign='middle')
        diagram.add_widget(label)
        diagram.SLOT_labels.append(label)
    update_slot_labels(diagram)


def update_slot_labels(diagram):
    new_level = diagram.get_zoom_level()
    if new_level != diagram.current_level:
        rebuild_slot_labels(diagram)
        return

    slot_numbers = calculate_slot_numbers(diagram, new_level,
                                           is_export=False)
    if not slot_numbers:
        return

    if len(diagram.SLOT_labels) != len(slot_numbers):
        rebuild_slot_labels(diagram)
        return

    font_size = max(8, min(48, get_font_size_for_slot(diagram)))
    for index, real_slot in enumerate(slot_numbers):
        if index < len(diagram.SLOT_labels):
            x_world = real_slot + SLOT_NUMBER_X_SHIFT
            y_world = diagram.GRID_y_min + 0.5
            x_screen, y_screen = diagram.world_to_screen(x_world, y_world)
            label = diagram.SLOT_labels[index]
            label.font_size = font_size
            label.pos = (x_screen - SLOT_LABEL_WIDTH / 2,
                         y_screen - SLOT_LABEL_HEIGHT / 2)


def ensure_slot_labels_visible(diagram):
    if not ENABLE_SLOT_NUMBERS:
        return
    new_level = diagram.get_zoom_level()
    slot_numbers = calculate_slot_numbers(diagram, new_level,
                                           is_export=False)
    if not slot_numbers:
        return
    if len(diagram.SLOT_labels) != len(slot_numbers):
        rebuild_slot_labels(diagram)
    else:
        update_slot_labels(diagram)


def update_phase_labels(diagram):
    for label in diagram.PHASE_labels:
        diagram.remove_widget(label)
    diagram.PHASE_labels = []

    if not diagram.connection.active:
        return

    connection = diagram.connection
    if not connection.phase_endpoints:
        return

    r_id = connection.phase_endpoints.get('R')
    u_id = connection.phase_endpoints.get('U')
    offset = diagram.GRID_cell_size_px * diagram.SCREEN_scale

    for label_text, target_id in [('R', r_id), ('U', u_id)]:
        if not target_id:
            continue
        x_world = None
        y_world = None
        for wire in connection.wire_points:
            if wire.wire_id == target_id:
                x_world = wire.x
                y_world = wire.y
                break
        if x_world is None:
            for junction in connection.junctions:
                if junction.junction_id == target_id:
                    x_world = junction.x
                    y_world = junction.y
                    break
        if x_world is None:
            continue
        x_screen, y_screen = diagram.world_to_screen(x_world, y_world)
        color = ([0.0, 0.6, 0.0, 1] if label_text == 'R'
                 else [0.8, 0.0, 0.0, 1])

        label = Label(
            text=label_text, font_size='32sp', bold=True, color=color,
            size_hint=(None, None), size=(60, 60),
            halign='center', valign='middle',
            outline_width=3, outline_color=[0, 0, 0, 1]
        )
        label.pos = (x_screen + offset, y_screen + offset)
        diagram.add_widget(label)
        diagram.PHASE_labels.append(label)


def get_motor_name_text(diagram):
    project_data = json_manager.project_data
    if not project_data:
        return ''
    name = project_data.get('project_name', '')
    power = project_data.get('nominal_power', '')
    slots = project_data.get('all_slots', '')
    poles = project_data.get('poles', '')
    unit = project_data.get('unit', '')
    try:
        speed = get_speed(int(poles))
    except Exception:
        speed = '---'
    return (
        str(name) + ' _ ' + str(power) + ' kW _ ' +
        str(slots) + ' slots _ ' + str(speed) + ' RPM _ ' +
        str(unit)
    )


def update_motor_name_label(diagram):
    if diagram.MOTOR_NAME_label is not None:
        diagram.remove_widget(diagram.MOTOR_NAME_label)
        diagram.MOTOR_NAME_label = None

    if not json_manager.project_data:
        return

    text = get_motor_name_text(diagram)
    if not text:
        return

    layout = diagram._layout_mm()
    label_x_mm, label_y_mm, label_w_mm, label_h_mm = layout['motor_label']

    grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']
    grid_x_px = mm_to_px(grid_x_mm)
    grid_y_px = mm_to_px(grid_y_mm)
    grid_w_px = mm_to_px(grid_w_mm)
    grid_h_px = mm_to_px(grid_h_mm)

    fx = (mm_to_px(label_x_mm) - grid_x_px) / max(grid_w_px, 0.0001)
    fy = (mm_to_px(label_y_mm) - grid_y_px) / max(grid_h_px, 0.0001)
    fw = mm_to_px(label_w_mm) / max(grid_w_px, 0.0001)
    fh = mm_to_px(label_h_mm) / max(grid_h_px, 0.0001)

    sx = (grid_x_px + fx * grid_w_px) * diagram.SCREEN_scale + diagram.SCREEN_offset_x
    sy = (grid_y_px + fy * grid_h_px) * diagram.SCREEN_scale + diagram.SCREEN_offset_y
    sw = fw * grid_w_px * diagram.SCREEN_scale
    sh = fh * grid_h_px * diagram.SCREEN_scale

    label = Label(text=text, font_size='16sp', bold=True,
                   color=[0, 0, 0, 1], size_hint=(None, None),
                   size=(sw, sh), pos=(sx, sy),
                   halign='center', valign='middle',
                   text_size=(sw, sh))
    diagram.add_widget(label)
    diagram.MOTOR_NAME_label = label


def update_labels(diagram):
    if ENABLE_SLOT_NUMBERS:
        update_slot_labels(diagram)
    update_phase_labels(diagram)
    update_motor_name_label(diagram)