"""
================================================================================
File: diagrams/base/layer_renderer.py
Purpose: Draw paper border, project border, draw/info areas,
         motor name label border, grid (only inside grid_area),
         overlay, connections.
Version: 0.1.2
================================================================================
"""

from kivy.graphics import Color, Line, Rectangle

from core.rendering.canvas_backend import CanvasBackend

from utils.constants import (
    DISPLAY_DPI,
    COLOR_GRID_10_DISPLAY, COLOR_GRID_5_DISPLAY,
    COLOR_GRID_5V_DISPLAY, COLOR_GRID_OTHER_DISPLAY,
    COLOR_PAPER_BORDER,
    ZOOM_BOX_FILL_COLOR, ZOOM_BOX_LINE_COLOR,
    ZOOM_BOX_LINE_WIDTH,
)


def mm_to_px(mm):
    return mm * DISPLAY_DPI / 25.4


class LayerRenderer:

    def __init__(self, diagram):
        self.diagram = diagram

    def _mm_rect_to_world(self, rect_mm):
        d = self.diagram
        x_mm, y_mm, w_mm, h_mm = rect_mm
        layout = d._layout_mm()
        grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']

        x_range = d.GRID_x_max - d.GRID_x_min
        y_range = d.GRID_y_max - d.GRID_y_min

        fx = (x_mm - grid_x_mm) / max(grid_w_mm, 0.0001)
        fy = (y_mm - grid_y_mm) / max(grid_h_mm, 0.0001)
        fw = w_mm / max(grid_w_mm, 0.0001)
        fh = h_mm / max(grid_h_mm, 0.0001)

        world_x = d.GRID_x_min + fx * x_range
        world_y = d.GRID_y_min + fy * y_range
        world_w = fw * x_range
        world_h = fh * y_range
        return world_x, world_y, world_w, world_h

    def draw_paper_border(self):
        d = self.diagram
        layout = d._layout_mm()

        backends = [
            CanvasBackend(d.layers.get('paper_bg'), d.world_to_screen),
        ]
        if d._export_mode:
            backends.append(d.vector_backend)

        # Page_area (blue)
        page_world = self._mm_rect_to_world(layout['page'])
        for b in backends:
            b.rect(page_world[0], page_world[1],
                   page_world[2], page_world[3],
                   (0.2, 0.4, 0.8, 1), filled=False)

        # Project_area (black)
        proj_world = self._mm_rect_to_world(layout['project'])
        for b in backends:
            b.rect(proj_world[0], proj_world[1],
                   proj_world[2], proj_world[3],
                   (0, 0, 0, 1), filled=False)

        # Motor name label border
        label_world = self._mm_rect_to_world(layout['motor_label'])
        for b in backends:
            b.rect(label_world[0], label_world[1],
                   label_world[2], label_world[3],
                   (0.5, 0.5, 0.5, 1), filled=False)

        # Info_area border
        info_world = self._mm_rect_to_world(layout['info'])
        for b in backends:
            b.rect(info_world[0], info_world[1],
                   info_world[2], info_world[3],
                   (0.5, 0.5, 0.5, 1), filled=False)

    def draw_grid(self):
        d = self.diagram

        layout = d._layout_mm()
        grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']
        gw = self._mm_rect_to_world((grid_x_mm, grid_y_mm,
                                      grid_w_mm, grid_h_mm))
        world_x_min, world_y_min, world_w, world_h = gw
        world_x_max = world_x_min + world_w
        world_y_max = world_y_min + world_h

        backend = CanvasBackend(d.layers.get('grid'), d.world_to_screen)
        backends = [backend]
        if d._export_mode:
            backends.append(d.vector_backend)

        c10 = COLOR_GRID_10_DISPLAY
        c5 = COLOR_GRID_5_DISPLAY
        c5v = COLOR_GRID_5V_DISPLAY
        co = COLOR_GRID_OTHER_DISPLAY

        x_min = d.GRID_x_min
        x_max = d.GRID_x_max
        y_min = d.GRID_y_min
        y_max = d.GRID_y_max

        # ===== CULLING =====
        bounds = getattr(d, '_cached_viewport_bounds', None)
        if bounds is not None and not d._export_mode:
            bx1, by1, bx2, by2 = bounds
            x_start = max(int(x_min), int(bx1) - 1)
            x_end = min(int(x_max), int(bx2) + 2)
            y_start = max(int(y_min), int(by1) - 1)
            y_end = min(int(y_max), int(by2) + 2)
        else:
            x_start = int(x_min)
            x_end = int(x_max)
            y_start = int(y_min)
            y_end = int(y_max)

        # Vertical lines
        for slot in range(x_start, x_end + 1):
            offset = slot - 1
            if offset >= 0 and offset % 10 == 0:
                col = c10
                lw = 1
            elif offset >= 0 and offset % 5 == 0:
                col = c5
                lw = 1
            else:
                col = co
                lw = 1
            for b in backends:
                b.line(slot, y_min, slot, y_max, col, lw)

        # Horizontal lines
        for i in range(y_start, y_end + 1):
            if i % 10 == 0:
                col = c10
                lw = 1
            elif i % 5 == 0:
                col = c5v
                lw = 1
            else:
                col = co
                lw = 1
            for b in backends:
                b.line(x_min, i, x_max, i, col, lw)

    def draw_overlay(self):
        d = self.diagram
        g = d.layers.get('connection_overlay')
        if g is None:
            return
        g.clear()

        zc = d.zoom_controller
        if zc.zoom_box_start and zc.zoom_box_current:
            sx1, sy1 = zc.zoom_box_start
            sx2, sy2 = zc.zoom_box_current
            xmin, xmax = min(sx1, sx2), max(sx1, sx2)
            ymin, ymax = min(sy1, sy2), max(sy1, sy2)
            g.add(Color(*ZOOM_BOX_FILL_COLOR))
            g.add(Rectangle(pos=(xmin, ymin),
                            size=(xmax - xmin, ymax - ymin)))
            g.add(Color(*ZOOM_BOX_LINE_COLOR))
            g.add(Line(points=[xmin, ymin, xmax, ymin,
                                xmax, ymax, xmin, ymax, xmin, ymin],
                        width=ZOOM_BOX_LINE_WIDTH))

        if not d.connection_mode_active():
            return

        backend = CanvasBackend(g, d.world_to_screen)

        # Get shift_y (same as renderer.py draw_static)
        shift = getattr(d.connection, 'shift_y', 0.0)

        if d._box_start and d._box_current:
            x1, y1 = d._box_start
            x2, y2 = d._box_current
            direction = 'left_to_right' if x2 >= x1 else 'right_to_left'
            d.connection.renderer.draw_select_box(
                backend, x1, y1 + shift, x2, y2 + shift, direction
            )

        if d._pencil_start and d._pencil_current:
            x1, y1 = d._pencil_start
            x2, y2 = d._pencil_current
            d.connection.renderer.draw_pencil_preview(
                backend, x1, y1 + shift, x2, y2 + shift
            )

    def draw_connections(self):
        d = self.diagram
        static_g = d.layers.get('connection_static')
        if static_g is None:
            return
        static_g.clear()

        backends = [CanvasBackend(static_g, d.world_to_screen)]
        if d._export_mode:
            backends.append(d.vector_backend)

        for b in backends:
            d.connection.draw_static(b)