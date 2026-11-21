"""
================================================================================
File: diagrams/motor_common/diagram_edit_mode.py
Purpose: Edit Diagram mode (two diamonds at x=-1, drag to shift).
Version: 0.1.4
================================================================================
"""

from managers.json_manager import json_manager
from utils.constants import (
    MAIN_DIAGRAM_BASE_OFFSET_Y, PHASE_DIAGRAM_BASE_OFFSET_Y,
    EDIT_DIAMOND_SIZE_WORLD, EDIT_HIT_RADIUS_WORLD,
    EDIT_MAIN_DIAMOND_COLOR, EDIT_PHASE_DIAMOND_COLOR,
    EDIT_DIAMOND_LINE_WIDTH,
)


def enter_edit_mode(diagram):
    diagram.edit_mode_active = True
    diagram.edit_current_main_shift = json_manager.get_main_diagram_shift_y()
    diagram.edit_current_phase_shift = json_manager.get_phase_diagram_shift_y()
    diagram._rebuild_all()


def exit_edit_mode(diagram):
    diagram.edit_mode_active = False
    diagram.edit_drag_target = None
    diagram.edit_drag_start_y = None
    diagram._rebuild_all()


def apply_edit_shifts(diagram):
    json_manager.set_main_diagram_shift_y(diagram.edit_current_main_shift)
    json_manager.set_phase_diagram_shift_y(diagram.edit_current_phase_shift)
    diagram.connection.shift_y = diagram.edit_current_main_shift
    diagram._emit_wire_points()
    exit_edit_mode(diagram)


def reset_edit_shifts(diagram):
    diagram.edit_current_main_shift = 0.0
    diagram.edit_current_phase_shift = 0.0
    json_manager.set_main_diagram_shift_y(0.0)
    json_manager.set_phase_diagram_shift_y(0.0)
    diagram.connection.shift_y = 0.0
    diagram._emit_wire_points()
    diagram._rebuild_all()


def get_edit_diamonds(diagram):
    x_diamond = -1.0
    main_y = (diagram.GRID_y_min + MAIN_DIAGRAM_BASE_OFFSET_Y +
              diagram.edit_current_main_shift)
    phase_y = (diagram.GRID_y_min + PHASE_DIAGRAM_BASE_OFFSET_Y +
               diagram.edit_current_phase_shift)
    return {
        'main': (x_diamond, main_y),
        'phase': (x_diamond, phase_y),
    }


def draw_edit_diamonds(diagram):
    if not diagram.edit_mode_active:
        return
    from kivy.graphics import Color, Line
    group = diagram.layers.get('connection_overlay')
    if group is None:
        return

    positions = get_edit_diamonds(diagram)
    for target, (world_x, world_y) in positions.items():
        if target == 'main':
            color = EDIT_MAIN_DIAMOND_COLOR
        else:
            color = EDIT_PHASE_DIAMOND_COLOR
        screen_x, screen_y = diagram.world_to_screen(world_x, world_y)
        diamond_size_px = (EDIT_DIAMOND_SIZE_WORLD *
                            diagram.GRID_cell_size_px * diagram.SCREEN_scale)
        if diamond_size_px < 6:
            diamond_size_px = 6
        points = [
            screen_x, screen_y + diamond_size_px,
            screen_x + diamond_size_px, screen_y,
            screen_x, screen_y - diamond_size_px,
            screen_x - diamond_size_px, screen_y,
            screen_x, screen_y + diamond_size_px,
        ]
        group.add(Color(*color))
        group.add(Line(points=points, width=EDIT_DIAMOND_LINE_WIDTH))


def handle_edit_touch_down(diagram, touch):
    if not diagram.edit_mode_active:
        return False
    world_x, world_y = diagram.screen_to_world(*touch.pos)
    positions = get_edit_diamonds(diagram)
    for target, (diamond_x, diamond_y) in positions.items():
        if (abs(world_x - diamond_x) <= EDIT_HIT_RADIUS_WORLD and
                abs(world_y - diamond_y) <= EDIT_HIT_RADIUS_WORLD):
            diagram.edit_drag_target = target
            diagram.edit_drag_start_y = diamond_y
            return True
    return False


def handle_edit_touch_move(diagram, touch):
    if not diagram.edit_mode_active or diagram.edit_drag_target is None:
        return False
    world_x, world_y = diagram.screen_to_world(*touch.pos)
    world_y = round(world_y)

    if diagram.edit_drag_target == 'main':
        new_shift = world_y - diagram.GRID_y_min - MAIN_DIAGRAM_BASE_OFFSET_Y
        diagram.edit_current_main_shift = float(new_shift)
    else:
        new_shift = world_y - diagram.GRID_y_min - PHASE_DIAGRAM_BASE_OFFSET_Y
        diagram.edit_current_phase_shift = float(new_shift)

    diagram._rebuild_all()
    return True


def handle_edit_touch_up(diagram, touch):
    if not diagram.edit_mode_active:
        return False
    if diagram.edit_drag_target is not None:
        diagram.edit_drag_target = None
        diagram._rebuild_all()
        return True
    return False