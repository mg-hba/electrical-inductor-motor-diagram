"""
================================================================================
File: diagrams/motor_common/diagram_table.py
Purpose: Info table (geometry, labels, draw, export text).
Version: 0.1.4
================================================================================
"""

import json
from datetime import datetime
from kivy.uix.label import Label

from managers.json_manager import json_manager
from diagrams.base.diagram_base import get_speed
from core.rendering.canvas_backend import CanvasBackend

from utils.constants import (
    TABLE_ROW_COUNT, TABLE_COL_COUNT,
    TABLE_HEADER_FONT_SIZE_LEVEL_0, TABLE_HEADER_FONT_SIZE_LEVEL_1,
    TABLE_HEADER_FONT_SIZE_LEVEL_2,
    TABLE_BODY_FONT_SIZE_LEVEL_0, TABLE_BODY_FONT_SIZE_LEVEL_1,
    TABLE_BODY_FONT_SIZE_LEVEL_2,
    TABLE_COMMENT_FONT_SIZE_LEVEL_0, TABLE_COMMENT_FONT_SIZE_LEVEL_1,
    TABLE_COMMENT_FONT_SIZE_LEVEL_2,
    TABLE_LINE_WIDTH_LEVEL_0, TABLE_LINE_WIDTH_LEVEL_1,
    TABLE_LINE_WIDTH_LEVEL_2,
    TABLE_HEADER_TEXT_COLOR, TABLE_BODY_TEXT_COLOR,
    TABLE_COMMENT_TEXT_COLOR,
    TABLE_HEADER_BG_COLOR, TABLE_BODY_BG_COLOR, TABLE_COMMENT_BG_COLOR,
    TABLE_HEADER_BOLD,
    ENABLE_INFO_TABLE,
    EXPORT_TABLE_HEADER_FONT_SIZE, EXPORT_TABLE_HEADER_COLOR,
    EXPORT_TABLE_BODY_FONT_SIZE, EXPORT_TABLE_BODY_COLOR,
    EXPORT_TABLE_COMMENT_FONT_SIZE, EXPORT_TABLE_COMMENT_COLOR,
    EXPORT_TABLE_HEADER_BG_COLOR, EXPORT_TABLE_BODY_BG_COLOR,
    EXPORT_TABLE_COMMENT_BG_COLOR,
    EXPORT_TABLE_LINE_WIDTH, EXPORT_TABLE_LINE_COLOR,
)


TABLE_ROW_TYPES = ['comment', 'body', 'header', 'body',
                    'header', 'body', 'header']


def mm_to_world_x(diagram, x_mm):
    layout = diagram._layout_mm()
    grid_x_mm = layout['grid'][0]
    grid_w_mm = layout['grid'][2]
    x_range = diagram.GRID_x_max - diagram.GRID_x_min
    if grid_w_mm <= 0 or x_range <= 0:
        return diagram.GRID_x_min
    fraction = (x_mm - grid_x_mm) / grid_w_mm
    return diagram.GRID_x_min + fraction * x_range


def mm_to_world_y(diagram, y_mm):
    layout = diagram._layout_mm()
    grid_y_mm = layout['grid'][1]
    grid_h_mm = layout['grid'][3]
    y_range = diagram.GRID_y_max - diagram.GRID_y_min
    if grid_h_mm <= 0 or y_range <= 0:
        return diagram.GRID_y_min
    fraction = (y_mm - grid_y_mm) / grid_h_mm
    return diagram.GRID_y_min + fraction * y_range


def get_table_geometry(diagram):
    layout = diagram._layout_mm()
    info_x_mm, info_y_mm, info_w_mm, info_h_mm = layout['info']
    mm_factor = diagram._mm_to_world_factor()

    info_x_world = mm_to_world_x(diagram, info_x_mm)
    info_y_world = mm_to_world_y(diagram, info_y_mm)
    info_width_world = info_w_mm / mm_factor
    info_height_world = info_h_mm / mm_factor

    table_left = info_x_world + info_height_world
    table_right = info_x_world + info_width_world - info_height_world
    table_bottom = info_y_world
    table_top = info_y_world + info_height_world
    table_width = table_right - table_left
    cell_height = info_height_world / TABLE_ROW_COUNT
    cell_width = table_width / TABLE_COL_COUNT

    return {
        'bottom': table_bottom,
        'top': table_top,
        'left': table_left,
        'right': table_right,
        'width': table_width,
        'height': info_height_world,
        'cell_height': cell_height,
        'cell_width': cell_width,
        'row_count': TABLE_ROW_COUNT,
        'col_count': TABLE_COL_COUNT,
        'info_height': info_height_world,
    }


def get_table_data(diagram):
    project_data = json_manager.project_data
    if project_data:
        project_name = project_data.get('project_name', '---')
        power = project_data.get('nominal_power', '---')
        connection_type = project_data.get('connection_type', '---')
        wires = project_data.get('wire_gauges', [])
        turns = project_data.get('turns_counts', [])
        poles_val = project_data.get('poles', diagram.MOTOR_poles)
        slots_val = project_data.get('all_slots', diagram.MOTOR_all_slots)
        span_val = project_data.get('coil_span_chained',
                                      diagram.MOTOR_coil_span)
        poles = str(poles_val)
        slots = str(slots_val)
        span = str(span_val)
        speed = str(get_speed(poles_val))
        unit = project_data.get('unit', '---') or '---'
        slot_length = project_data.get('slot_length', '')
        core_diameter = project_data.get('core_diameter', '')
        comments = project_data.get('comments', '') or ''
        slot_length_str = (str(slot_length) + ' mm'
                           if str(slot_length).strip() else '---')
        core_diameter_str = (str(core_diameter) + ' mm'
                             if str(core_diameter).strip() else '---')
    else:
        project_name = "---"
        power = "---"
        connection_type = "---"
        poles = str(diagram.MOTOR_poles)
        speed = str(get_speed(diagram.MOTOR_poles))
        slots = str(diagram.MOTOR_all_slots)
        span = "---"
        wires = []
        turns = []
        unit = '---'
        slot_length_str = '---'
        core_diameter_str = '---'
        comments = ''

    wire_str = ', '.join(wires) if wires else "---"
    turns_str = ', '.join(str(t) for t in turns) if turns else "---"
    date = datetime.now().strftime("%Y-%m-%d")

    return {
        'headers1': ["PROJECT", "POWER", "CONNECTION", "POLES",
                      "SPEED", "UNIT"],
        'vals1': [project_name, str(power) + " kW", connection_type,
                   poles, speed + " RPM", unit],
        'headers2': ["WIRE GAUGE", "TURNS", "SLOTS", "COIL SPAN",
                      "DATE", "SLOT LENGTH"],
        'vals2': [wire_str, turns_str, slots, span, date,
                   slot_length_str],
        'headers3': ["DRAWN BY", "CHECKED BY", "APPROVED BY",
                      "REVISION", "SCALE", "CORE DIAMETER"],
        'vals3': ["---", "---", "---", "0.1.3", "1:1",
                   core_diameter_str],
        'comments': comments,
    }


def get_table_font_size(diagram, row_type):
    if diagram.current_level == 0:
        if row_type == 'header':
            return TABLE_HEADER_FONT_SIZE_LEVEL_0
        elif row_type == 'comment':
            return TABLE_COMMENT_FONT_SIZE_LEVEL_0
        return TABLE_BODY_FONT_SIZE_LEVEL_0
    elif diagram.current_level == 1:
        if row_type == 'header':
            return TABLE_HEADER_FONT_SIZE_LEVEL_1
        elif row_type == 'comment':
            return TABLE_COMMENT_FONT_SIZE_LEVEL_1
        return TABLE_BODY_FONT_SIZE_LEVEL_1
    else:
        if row_type == 'header':
            return TABLE_HEADER_FONT_SIZE_LEVEL_2
        elif row_type == 'comment':
            return TABLE_COMMENT_FONT_SIZE_LEVEL_2
        return TABLE_BODY_FONT_SIZE_LEVEL_2


def get_table_text_color(row_type):
    if row_type == 'header':
        return TABLE_HEADER_TEXT_COLOR
    elif row_type == 'comment':
        return TABLE_COMMENT_TEXT_COLOR
    return TABLE_BODY_TEXT_COLOR


def get_table_bg_color(row_type):
    if row_type == 'header':
        return TABLE_HEADER_BG_COLOR
    elif row_type == 'comment':
        return TABLE_COMMENT_BG_COLOR
    return TABLE_BODY_BG_COLOR


def rebuild_table_labels(diagram):
    project_data = json_manager.project_data
    project_hash = (hash(json.dumps(project_data, sort_keys=True,
                                     default=str))
                    if project_data else 0)
    current_hash = hash((
        diagram.GRID_x_min, diagram.GRID_x_max, diagram.GRID_y_min,
        diagram.GRID_y_max, diagram.MOTOR_all_slots,
        diagram.MOTOR_coil_span, diagram.MOTOR_poles,
        diagram.PAGE_width_px, diagram.PAGE_height_px,
        project_hash,
    ))
    diagram.TABLE_last_hash = current_hash

    for label in diagram.TABLE_labels:
        diagram.remove_widget(label)
    diagram.TABLE_labels = []
    diagram.TABLE_cells = []

    data = get_table_data(diagram)
    geom = get_table_geometry(diagram)

    xl, yt = diagram.world_to_screen(geom['left'], geom['top'])
    xr, yb = diagram.world_to_screen(geom['right'], geom['bottom'])
    row_height = (yt - yb) / TABLE_ROW_COUNT
    col_width = (xr - xl) / TABLE_COL_COUNT

    row_data_keys = [
        ('comments', 'comment'),
        ('vals3',    'body'),
        ('headers3', 'header'),
        ('vals2',    'body'),
        ('headers2', 'header'),
        ('vals1',    'body'),
        ('headers1', 'header'),
    ]

    def add_text(text, col, row, row_type, span_cols=1):
        font_size = get_table_font_size(diagram, row_type)
        color = get_table_text_color(row_type)
        cell_w = col_width * span_cols
        xc = xl + col * col_width + cell_w / 2
        yc = yb + row * row_height + row_height / 2
        bold = (row_type == 'header' and TABLE_HEADER_BOLD)
        label = Label(text=str(text), font_size=font_size, color=color,
                       bold=bold,
                       size_hint=(None, None),
                       size=(cell_w - 2, row_height - 2),
                       pos=(xc - (cell_w - 2) / 2,
                            yc - (row_height - 2) / 2),
                       halign='center', valign='middle',
                       text_size=(cell_w - 2, row_height - 2))
        diagram.add_widget(label)
        diagram.TABLE_labels.append(label)
        diagram.TABLE_cells.append((label, col, row, row_type, span_cols))

    for row_index, (data_key, row_type) in enumerate(row_data_keys):
        if row_type == 'comment':
            add_text(data.get('comments', ''), 0, row_index,
                     row_type, span_cols=TABLE_COL_COUNT)
        else:
            values = data.get(data_key, [])
            for col_index in range(TABLE_COL_COUNT):
                text = values[col_index] if col_index < len(values) else ''
                add_text(text, col_index, row_index, row_type)


def update_table_labels(diagram):
    if not diagram.TABLE_cells:
        rebuild_table_labels(diagram)
        return
    geom = get_table_geometry(diagram)
    xl, yt = diagram.world_to_screen(geom['left'], geom['top'])
    xr, yb = diagram.world_to_screen(geom['right'], geom['bottom'])
    row_height = (yt - yb) / TABLE_ROW_COUNT
    col_width = (xr - xl) / TABLE_COL_COUNT

    for entry in diagram.TABLE_cells:
        label, col, row, row_type, span_cols = entry
        font_size = get_table_font_size(diagram, row_type)
        cell_w = col_width * span_cols
        xc = xl + col * col_width + cell_w / 2
        yc = yb + row * row_height + row_height / 2
        label.font_size = font_size
        label.size = (cell_w - 2, row_height - 2)
        label.pos = (xc - (cell_w - 2) / 2,
                     yc - (row_height - 2) / 2)


def draw_table(diagram):
    if not ENABLE_INFO_TABLE:
        return

    # Skip table at high zoom (it's unreadable and off-screen)
    if not diagram._export_mode and diagram.SCREEN_scale > 6:
        return

    # Skip table at high zoom (it's unreadable and off-screen)
    if not diagram._export_mode and diagram.SCREEN_scale > 6:
        return
    project_data = json_manager.project_data
    project_hash = (hash(json.dumps(project_data, sort_keys=True,
                                     default=str))
                    if project_data else 0)
    current_hash = hash((
        diagram.GRID_x_min, diagram.GRID_x_max, diagram.GRID_y_min,
        diagram.GRID_y_max, diagram.MOTOR_all_slots,
        diagram.MOTOR_coil_span, diagram.MOTOR_poles,
        diagram.PAGE_width_px, diagram.PAGE_height_px,
        project_hash,
    ))
    need_rebuild = (current_hash != diagram.TABLE_last_hash) or \
                   (diagram.TABLE_last_level != diagram.current_level) or \
                   (len(diagram.TABLE_labels) == 0)
    if need_rebuild:
        diagram.TABLE_last_hash = current_hash
        diagram.TABLE_last_level = diagram.current_level
        rebuild_table_labels(diagram)
    else:
        update_table_labels(diagram)
    draw_table_lines(diagram)


def draw_table_lines(diagram):
    if not ENABLE_INFO_TABLE:
        return
    geom = get_table_geometry(diagram)
    if diagram.current_level == 0:
        line_width = TABLE_LINE_WIDTH_LEVEL_0
    elif diagram.current_level == 1:
        line_width = TABLE_LINE_WIDTH_LEVEL_1
    else:
        line_width = TABLE_LINE_WIDTH_LEVEL_2

    backends = [
        CanvasBackend(diagram.layers.get('table_lines'),
                      diagram.world_to_screen),
    ]
    if diagram._export_mode:
        backends.append(diagram.vector_backend)

    left = geom['left']
    right = geom['right']
    bottom = geom['bottom']
    top = geom['top']
    row_height = (top - bottom) / TABLE_ROW_COUNT

    for row_index in range(TABLE_ROW_COUNT):
        row_type = TABLE_ROW_TYPES[row_index]
        if diagram._export_mode:
            if row_type == 'header':
                bg_color = EXPORT_TABLE_HEADER_BG_COLOR
            elif row_type == 'comment':
                bg_color = EXPORT_TABLE_COMMENT_BG_COLOR
            else:
                bg_color = EXPORT_TABLE_BODY_BG_COLOR
        else:
            bg_color = get_table_bg_color(row_type)
        y = bottom + row_index * row_height
        for backend in backends:
            backend.rect(left, y, right - left, row_height,
                          bg_color, filled=True)

    if diagram._export_mode:
        line_color = EXPORT_TABLE_LINE_COLOR
        export_line_width = EXPORT_TABLE_LINE_WIDTH
    else:
        line_color = (0, 0, 0, 1)
        export_line_width = line_width

    for i in range(TABLE_COL_COUNT + 1):
        x = left + i * (right - left) / TABLE_COL_COUNT
        for backend in backends:
            backend.line(x, bottom, x, top, line_color,
                          export_line_width)
    for i in range(TABLE_ROW_COUNT + 1):
        y = bottom + i * row_height
        for backend in backends:
            backend.line(left, y, right, y, line_color,
                          export_line_width)

    if diagram._export_mode:
        export_table_text(diagram)


def export_table_text(diagram):
    data = get_table_data(diagram)
    geom = get_table_geometry(diagram)
    cell_height = geom['cell_height']
    cell_width = geom['cell_width']
    table_left = geom['left']
    table_bottom = geom['bottom']

    row_data_keys = [
        ('comments', 'comment'),
        ('vals3',    'body'),
        ('headers3', 'header'),
        ('vals2',    'body'),
        ('headers2', 'header'),
        ('vals1',    'body'),
        ('headers1', 'header'),
    ]

    def add_text(text, col, row, row_type, span_cols=1):
        if row_type == 'header':
            font_size = EXPORT_TABLE_HEADER_FONT_SIZE
            color = EXPORT_TABLE_HEADER_COLOR
        elif row_type == 'comment':
            font_size = EXPORT_TABLE_COMMENT_FONT_SIZE
            color = EXPORT_TABLE_COMMENT_COLOR
        else:
            font_size = EXPORT_TABLE_BODY_FONT_SIZE
            color = EXPORT_TABLE_BODY_COLOR
        cell_w = cell_width * span_cols
        xc = table_left + col * cell_width + cell_w / 2
        yc = table_bottom + row * cell_height + cell_height / 2
        diagram.vector_backend.text(str(text), xc, yc, font_size, color)

    for row_index, (data_key, row_type) in enumerate(row_data_keys):
        if row_type == 'comment':
            add_text(data.get('comments', ''), 0, row_index,
                     row_type, span_cols=TABLE_COL_COUNT)
        else:
            values = data.get(data_key, [])
            for col_index in range(TABLE_COL_COUNT):
                text = (values[col_index]
                        if col_index < len(values) else '')
                add_text(text, col_index, row_index, row_type)