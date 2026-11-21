"""
================================================================================
File: core/connection/renderer.py
Purpose: Draw wires, junctions, lines with group colors.
         Shift applied to ALL items (wire_points, junctions, lines).
         Wire points stored WITHOUT shift in JSON.
Version: 0.1.3
================================================================================
"""

from kivy.graphics import Color, Line, Rectangle

from utils.constants import (
    COLOR_NODE_BASE, COLOR_NODE_SELECTED,
    COLOR_JUNCTION, COLOR_JUNCTION_SELECTED, COLOR_JUNCTION_DELETE_PENDING,
    COLOR_LINE_BASE, COLOR_LINE_SELECTED, COLOR_LINE_DELETE_PENDING,
    COLOR_PHASE_GROUP_R, COLOR_PHASE_GROUP_U,
    LINE_WIDTH_LINE_BASE, LINE_WIDTH_LINE_SELECTED,
    SIZE_NODE_WORLD, SIZE_JUNCTION_WORLD,
    COLOR_SELECT_BOX_CONTAIN, COLOR_SELECT_BOX_INTERSECT,
)


class ConnectionRenderer:

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, layer):
        self.layer = layer
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########_line_color##############
    ###################################
    def _line_color(self, line, active, selected, pending):
        if active and line.line_id in pending:
            return COLOR_LINE_DELETE_PENDING, LINE_WIDTH_LINE_SELECTED
        if active and line.line_id in selected:
            return COLOR_LINE_SELECTED, LINE_WIDTH_LINE_SELECTED
        if line.phase_group == 'R':
            return COLOR_PHASE_GROUP_R, LINE_WIDTH_LINE_BASE
        if line.phase_group == 'U':
            return COLOR_PHASE_GROUP_U, LINE_WIDTH_LINE_BASE
        return COLOR_LINE_BASE, LINE_WIDTH_LINE_BASE
    ###################################
    ##########end of _line_color######
    ###################################

    ###################################
    ##########_junction_color##########
    ###################################
    def _junction_color(self, junction, active, selected, pending):
        if active and junction.junction_id in pending:
            return COLOR_JUNCTION_DELETE_PENDING
        if active and junction.junction_id in selected:
            return COLOR_JUNCTION_SELECTED
        if junction.phase_group == 'R':
            return COLOR_PHASE_GROUP_R
        if junction.phase_group == 'U':
            return COLOR_PHASE_GROUP_U
        return COLOR_JUNCTION
    ###################################
    ##########end of _junction_color##
    ###################################

    ###################################
    ##########_wire_color##############
    ###################################
    def _wire_color(self, wire, active, selected):
        if active and wire.wire_id in selected:
            return COLOR_NODE_SELECTED
        if wire.phase_group == 'R':
            return COLOR_PHASE_GROUP_R
        if wire.phase_group == 'U':
            return COLOR_PHASE_GROUP_U
        return COLOR_NODE_BASE
    ###################################
    ##########end of _wire_color######
    ###################################

    ###################################
    ##########draw_static##############
    ###################################
    def draw_static(self, backend, active=True):
        wires = self.layer.wire_points
        junctions = self.layer.junctions
        lines = self.layer.lines
        selection = self.layer.selection
        pending = selection.pending_delete_ids
        shift = getattr(self.layer, 'shift_y', 0.0)

        for line in lines:
            color, width = self._line_color(line, active,
                                             selection.line_ids, pending)
            backend.line(line.x1, line.y1 + shift,
                          line.x2, line.y2 + shift,
                          color, width)

        for junction in junctions:
            color = self._junction_color(junction, active,
                                          selection.junction_ids, pending)
            self._draw_hollow_square(backend, junction.x,
                                      junction.y + shift,
                                      SIZE_JUNCTION_WORLD, color)

        if not active:
            return

        for wire in wires:
            color = self._wire_color(wire, active, selection.wire_ids)
            self._draw_hollow_square(backend, wire.x, wire.y + shift,
                                      SIZE_NODE_WORLD, color)
    ###################################
    ##########end of draw_static######
    ###################################

    ###################################
    ##########_draw_hollow_square######
    ###################################
    def _draw_hollow_square(self, backend, center_x, center_y,
                             size, color):
        x1, y1 = center_x - size, center_y - size
        x2, y2 = center_x + size, center_y + size
        backend.line(x1, y1, x2, y1, color, 2)
        backend.line(x2, y1, x2, y2, color, 2)
        backend.line(x2, y2, x1, y2, color, 2)
        backend.line(x1, y2, x1, y1, color, 2)
    ###################################
    ##########end of _draw_hollow_square
    ###################################

    ###################################
    ##########draw_select_box##########
    ###################################
    def draw_select_box(self, backend, x1, y1, x2, y2, direction):
        color = (COLOR_SELECT_BOX_CONTAIN if direction == 'left_to_right'
                 else COLOR_SELECT_BOX_INTERSECT)
        sx1, sy1 = backend.world_to_screen(x1, y1)
        sx2, sy2 = backend.world_to_screen(x2, y2)
        backend.group.add(Color(*color))
        backend.group.add(Rectangle(
            pos=(min(sx1, sx2), min(sy1, sy2)),
            size=(abs(sx2 - sx1), abs(sy2 - sy1))
        ))
    ###################################
    ##########end of draw_select_box##
    ###################################

    ###################################
    ##########draw_pencil_preview######
    ###################################
    def draw_pencil_preview(self, backend, x1, y1, x2, y2):
        sx1, sy1 = backend.world_to_screen(x1, y1)
        sx2, sy2 = backend.world_to_screen(x2, y2)
        backend.group.add(Color(0.9, 0.5, 0.1, 0.8))
        backend.group.add(Line(points=[sx1, sy1, sx2, sy2], width=3))
    ###################################
    ##########end of draw_pencil_preview
    ###################################