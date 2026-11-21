"""
================================================================================
File: diagrams/base/diagram_base.py
Purpose: Base class for all winding diagrams.
         Layout:
           Page_area       = paper - 1mm margin
           Project_area    = Page_area - 5mm margin
           Draw_area       = Project_area top part (2mm inner margin)
             motor_name_label (10mm high)
             grid_area        (rest of Draw_area)
           Info_area       = Project_area bottom part
           Gap between Draw_area and Info_area = 2mm
Version: 0.1.2
================================================================================
"""

from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, InstructionGroup,
    StencilPush, StencilUse, StencilUnUse, StencilPop,
)
from kivy.core.window import Window
from kivy.clock import Clock
from math import hypot

from managers.json_manager import json_manager
from core.view_transform import ViewTransform
from core.rendering.layer_stack import LayerStack
from core.rendering.canvas_backend import CanvasBackend
from core.connection.layer import ConnectionLayer
from backends.vector_backend import VectorBackend

from diagrams.base.zoom_controller import ZoomController
from diagrams.base.touch_handler import TouchHandler
from diagrams.base.layer_renderer import LayerRenderer

from utils.constants import (
    PAPER_SIZES_MM, DISPLAY_DPI, EXPORT_DPI,
)


def get_paper_dimensions(paper_size, orientation):
    if paper_size is None or orientation is None:
        raise ValueError("paper_size=%s, orientation=%s" % (
            paper_size, orientation))
    w, h = PAPER_SIZES_MM[paper_size]
    if orientation == 'Landscape':
        w, h = h, w
    return w, h


def get_speed(poles):
    try:
        return 6000 // int(poles)
    except Exception:
        return 0


def mm_to_px(mm):
    return mm * DISPLAY_DPI / 25.4


class DiagramBase(Widget):

    # Layout margins (mm)
    PAGE_MARGIN_MM = 1.0
    PROJECT_MARGIN_MM = 5.0
    INNER_MARGIN_MM = 2.0
    MOTOR_LABEL_HEIGHT_MM = 10.0
    INFO_HEIGHT_PERCENT = 0.18

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        paper_size = json_manager.get_project_paper_size() or 'A4'
        orientation = json_manager.get_project_orientation() or 'Portrait'
        w_mm, h_mm = get_paper_dimensions(paper_size, orientation)

        self.PAGE_width_mm = w_mm
        self.PAGE_height_mm = h_mm
        self.PAGE_orientation = orientation
        self.PAGE_width_px = int(w_mm * DISPLAY_DPI / 25.4)
        self.PAGE_height_px = int(h_mm * DISPLAY_DPI / 25.4)

        self.SCREEN_offset_x = 0.0
        self.SCREEN_offset_y = 0.0
        self.SCREEN_scale = 1.0
        self.GRID_cell_size_px = 10.0

        self.MOTOR_all_slots = 60
        self.MOTOR_coil_span = 11
        self.MOTOR_poles = 4

        # Grid range (in world units, set by _rebuild_grid_bounds)
        self.GRID_x_min = 0
        self.GRID_x_max = 0
        self.GRID_y_min = 0
        self.GRID_y_max = 0
        self.GRID_x_step = 1.0

        self._rebuild_grid_bounds()

        self._export_mode = False

        self._touch_on_point = False
        self._drag_target = None
        self._drag_start_world = None
        self._pencil_start = None
        self._pencil_current = None
        self._box_start = None
        self._box_current = None

        self.zoom_controller = ZoomController(self)
        self.touch_handler = TouchHandler(self)
        self.layer_renderer = LayerRenderer(self)

        self.vector_backend = VectorBackend()
        self.connection = ConnectionLayer(self.zoom_controller.view)

        self.layers = LayerStack()

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.zoom_controller.sync()
        Clock.schedule_once(lambda dt: self.auto_fit(), 0.2)

    # ============================================================
    # ================== LAYOUT (mm) ============================
    # ============================================================

    def _layout_mm(self):
        """
        Compute all layout boxes in mm.
        Returns a dict with page/project/draw/info/grid/label rects
        each as (x, y, w, h) in mm from bottom-left of the paper.
        """
        page_margin = self.PAGE_MARGIN_MM
        project_margin = self.PROJECT_MARGIN_MM
        inner_margin = self.INNER_MARGIN_MM
        label_height = self.MOTOR_LABEL_HEIGHT_MM

        page_w = self.PAGE_width_mm
        page_h = self.PAGE_height_mm

        # Page_area
        page_x = page_margin
        page_y = page_margin
        page_w = page_w - 2 * page_margin
        page_h = page_h - 2 * page_margin

        # Project_area
        proj_x = page_x + project_margin
        proj_y = page_y + project_margin
        proj_w = page_w - 2 * project_margin
        proj_h = page_h - 2 * project_margin

        # Info height = 18% of project height
        info_height = proj_h * self.INFO_HEIGHT_PERCENT

        # Info_area (bottom)
        info_x = proj_x + inner_margin
        info_y = proj_y + inner_margin
        info_w = proj_w - 2 * inner_margin
        info_h = info_height - 2 * inner_margin

        # Draw_area (top), with 2mm gap above Info_area
        gap = inner_margin
        draw_x = proj_x + inner_margin
        draw_y = proj_y + inner_margin + info_height + gap
        draw_w = proj_w - 2 * inner_margin
        draw_h = (proj_y + proj_h - inner_margin) - draw_y

        # motor_name_label (top of Draw_area)
        label_x = draw_x
        label_y = draw_y + draw_h - label_height
        label_w = draw_w
        label_h = label_height

        # grid_area (rest of Draw_area, below label)
        grid_x = draw_x
        grid_y = draw_y
        grid_w = draw_w
        grid_h = draw_h - label_height

        return {
            'page': (page_x, page_y, page_w, page_h),
            'project': (proj_x, proj_y, proj_w, proj_h),
            'info': (info_x, info_y, info_w, info_h),
            'draw': (draw_x, draw_y, draw_w, draw_h),
            'motor_label': (label_x, label_y, label_w, label_h),
            'grid': (grid_x, grid_y, grid_w, grid_h),
            'info_height': info_height,
            'inner_margin': inner_margin,
        }

    def get_info_height_world(self):
        """Info_area height in world units."""
        layout = self._layout_mm()
        return layout['info'][3] / self._mm_to_world_factor()

    def _mm_to_world_factor(self):
        """1 world unit = how many mm."""
        layout = self._layout_mm()
        grid_w_mm = layout['grid'][2]
        x_range = self.GRID_x_max - self.GRID_x_min
        if x_range <= 0:
            return 1.0
        return grid_w_mm / x_range

    # ============================================================
    # ================== HELPERS ================================
    # ============================================================

    @property
    def view(self):
        return self.zoom_controller.view

    @property
    def connection_layer(self):
        return self.connection

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def _rebuild_grid_bounds(self):
        """
        Grid range: -2 .. rounded_up(all_slots + 2)
        The world_to_screen maps this range onto grid_area.
        """
        all_slots = self.MOTOR_all_slots
        total_before_round = all_slots + 2
        rounded_total = ((total_before_round + 9) // 10) * 10

        self.GRID_x_min = -2
        self.GRID_x_max = rounded_total

        # Y range matches the grid_area aspect
        layout = self._layout_mm()
        grid_w_mm = layout['grid'][2]
        grid_h_mm = layout['grid'][3]
        x_range = self.GRID_x_max - self.GRID_x_min
        if grid_w_mm > 0:
            aspect = grid_h_mm / grid_w_mm
        else:
            aspect = 1.0
        y_range = x_range * aspect

        self.GRID_y_min = 0
        self.GRID_y_max = y_range

    def _update_cell_size(self):
        layout = self._layout_mm()
        grid_w_px = mm_to_px(layout['grid'][2])
        grid_h_px = mm_to_px(layout['grid'][3])

        x_range = self.GRID_x_max - self.GRID_x_min
        y_range = self.GRID_y_max - self.GRID_y_min
        if x_range > 0 and y_range > 0:
            self.GRID_cell_size_px = min(
                grid_w_px / x_range,
                grid_h_px / y_range
            )
        self.GRID_cell_size_px = max(1, self.GRID_cell_size_px)

    # ============================================================
    # ================== VIEW TRANSFORM =========================
    # ============================================================

    def auto_fit(self):
        self.zoom_controller.auto_fit()
        self.redraw()

    ###################################
    ##########world_to_screen##########
    ###################################
    def world_to_screen(self, world_x, world_y):
        layout = self._layout_mm()
        grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']
    
        grid_x_px = mm_to_px(grid_x_mm)
        grid_y_px = mm_to_px(grid_y_mm)
        grid_w_px = mm_to_px(grid_w_mm)
        grid_h_px = mm_to_px(grid_h_mm)
    
        x_range = self.GRID_x_max - self.GRID_x_min
        y_range = self.GRID_y_max - self.GRID_y_min
    
        fraction_x = (world_x - self.GRID_x_min) / max(x_range, 0.0001)
        fraction_y = (world_y - self.GRID_y_min) / max(y_range, 0.0001)
    
        screen_x_px = grid_x_px + fraction_x * grid_w_px
        screen_y_px = grid_y_px + fraction_y * grid_h_px
    
        screen_x_px = screen_x_px * self.SCREEN_scale + self.SCREEN_offset_x
        screen_y_px = screen_y_px * self.SCREEN_scale + self.SCREEN_offset_y
        return screen_x_px, screen_y_px
    ###################################
    ##########end of world_to_screen###
    ###################################
    




    def screen_to_world(self, sx, sy):
        layout = self._layout_mm()
        grid_x_mm, grid_y_mm, grid_w_mm, grid_h_mm = layout['grid']

        grid_x_px = mm_to_px(grid_x_mm)
        grid_y_px = mm_to_px(grid_y_mm)
        grid_w_px = mm_to_px(grid_w_mm)
        grid_h_px = mm_to_px(grid_h_mm)

        sx_unscaled = (sx - self.SCREEN_offset_x) / self.SCREEN_scale
        sy_unscaled = (sy - self.SCREEN_offset_y) / self.SCREEN_scale

        fx = (sx_unscaled - grid_x_px) / max(grid_w_px, 0.0001)
        fy = (sy_unscaled - grid_y_px) / max(grid_h_px, 0.0001)

        x_range = self.GRID_x_max - self.GRID_x_min
        y_range = self.GRID_y_max - self.GRID_y_min

        x = self.GRID_x_min + fx * x_range
        y = self.GRID_y_min + fy * y_range
        return x, y

    def get_view_state(self):
        layout = self._layout_mm()
        return {
            'layout': layout,
            'grid_x_min': self.GRID_x_min, 'grid_x_max': self.GRID_x_max,
            'grid_y_min': self.GRID_y_min, 'grid_y_max': self.GRID_y_max,
            'cell_size_px': self.GRID_cell_size_px,
            'screen_scale': self.SCREEN_scale,
            'offset_x': self.SCREEN_offset_x, 'offset_y': self.SCREEN_offset_y,
            'page_width_mm': self.PAGE_width_mm,
            'page_height_mm': self.PAGE_height_mm,
            'page_width_px': self.PAGE_width_px,
            'page_height_px': self.PAGE_height_px,
        }

    def get_export_view_state(self):
        d = self.get_view_state()
        d['screen_scale'] = 1.0
        d['offset_x'] = 0.0
        d['offset_y'] = 0.0
        return d

    def get_zoom_level(self):
        if self.SCREEN_scale < 3:
            return 0
        elif self.SCREEN_scale < 5:
            return 1
        return 2

    def refresh_paper_dimensions(self):
        paper = json_manager.get_project_paper_size()
        orient = json_manager.get_project_orientation()
        if not paper or not orient:
            return
        w_mm, h_mm = get_paper_dimensions(paper, orient)
        self.PAGE_width_mm = w_mm
        self.PAGE_height_mm = h_mm
        self.PAGE_orientation = orient
        self.PAGE_width_px = int(w_mm * DISPLAY_DPI / 25.4)
        self.PAGE_height_px = int(h_mm * DISPLAY_DPI / 25.4)
        self._rebuild_grid_bounds()
        self.vector_backend.load_paper_from_config()
        self.clear_caches()
        self.auto_fit()

    def clear_caches(self):
        pass

    # ============================================================
    # ================== ZOOM API ===============================
    # ============================================================

    def zoom_all(self):
        self.zoom_controller.zoom_all()
        self._rebuild_all()

    def zoom_in(self, anchor=None):
        self.zoom_controller.zoom_in(anchor)
        self._rebuild_all()

    def zoom_out(self, anchor=None):
        self.zoom_controller.zoom_out(anchor)
        self._rebuild_all()

    def zoom_back(self):
        if self.zoom_controller.zoom_back():
            self._rebuild_all()

    def zoom_redo(self):
        if self.zoom_controller.zoom_redo():
            self._rebuild_all()

    def zoom_reset(self):
        self.zoom_controller.zoom_reset()
        self._rebuild_all()

    def zoom_box_activate(self, active=None):
        self.zoom_controller.activate_zoom_box(active)
        self._rebuild_overlay()

    def is_zoom_box_active(self):
        return self.zoom_controller.zoom_box_active

    def _get_zoom_anchor(self):
        return self.zoom_controller.get_zoom_anchor()

    # ============================================================
    # ================== TOUCH ==================================
    # ============================================================

    def on_touch_down(self, touch):
        return self.touch_handler.on_touch_down(touch)

    def on_touch_move(self, touch):
        return self.touch_handler.on_touch_move(touch)

    def on_touch_up(self, touch):
        return self.touch_handler.on_touch_up(touch)

    # ============================================================
    # ================== REBUILD ================================
    # ============================================================

    def _rebuild_all(self):
        self._update_cell_size()
        self.zoom_controller.sync()
        self.redraw()

    def _rebuild_overlay(self):
        self.layer_renderer.draw_overlay()

    # ============================================================
    # ================== REDRAW =================================
    # ============================================================

    def redraw(self):
        self.clear_caches()
        self.canvas.clear()

        from kivy.graphics import (
            Color, Rectangle, InstructionGroup,
            StencilPush, StencilUse, StencilUnUse, StencilPop,
        )

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        for name in self.layers.layers.keys():
            self.layers.set(name, InstructionGroup())

        self._update_cell_size()
        self.zoom_controller.sync()

        with self.canvas:
            StencilPush()
            Rectangle(pos=self.pos, size=self.size)
            StencilUse()
            for g in self.layers.all():
                self.canvas.add(g)
            StencilUnUse()
            StencilPop()

        self.layer_renderer.draw_paper_border()
        self.layer_renderer.draw_grid()
        self.draw_diagram()
        self.draw_table()
        self.layer_renderer.draw_connections()
        self._update_labels()
        self.layer_renderer.draw_overlay()

    # ============================================================
    # ================== ABSTRACT ===============================
    # ============================================================

    def draw_diagram(self):
        pass

    def draw_table(self):
        pass

    def _update_labels(self):
        pass

    def set_parameters(self, *args, **kwargs):
        pass

    def clear_diagram(self):
        self.clear_caches()
        self.redraw()

    def connection_mode_active(self):
        return self.connection.active

    # ============================================================
    # ================== EXPORT =================================
    # ============================================================

    def _rebuild_exporter(self):
        self.vector_backend.clear()
        self.vector_backend.load_paper_from_config()
        self.vector_backend.set_view_state(self.get_export_view_state())
        self._export_mode = True
        try:
            self.layer_renderer.draw_paper_border()
            self.layer_renderer.draw_grid()
            self.draw_diagram()
            self.draw_table()
            self.connection.draw_static(self.vector_backend)
        finally:
            self._export_mode = False

    def save_diagram(self, path, fmt='svg', dpi=EXPORT_DPI, quality=95, **kw):
        self._rebuild_exporter()
        return self.vector_backend.save(path, fmt, dpi=dpi, quality=quality)