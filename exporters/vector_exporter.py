"""
================================================================================
File: exporters/vector_exporter.py
Purpose: Export diagrams to SVG/PDF/PNG/JPG/EPS/DXF.
         Includes zarin.png logo at left and right of the info table.
Version: 0.1.2
================================================================================
"""

import os

from managers.json_manager import json_manager
from utils.constants import (
    EXPORT_PAPER_SIZES_MM, PIXEL_PER_MM,
    EXPORT_LOGO_OPACITY,
    EXPORT_LINE_WIDTH_SCALE, EXPORT_FONT_SIZE_SCALE,
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'zarin.png')


class VectorExporter:

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self):
        self.drawing_commands = []
        self.background_color = (1, 1, 1, 1)

        self.paper_width_mm = None
        self.paper_height_mm = None
        self.orientation = None
        self.width = None
        self.height = None

        self.view_state = None
        self.use_view_state = False

        self.grid_x_mm = 0
        self.grid_y_mm = 0
        self.grid_w_mm = 0
        self.grid_h_mm = 0

        self.load_paper_from_config()
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########load_paper_from_config###
    ###################################
    def load_paper_from_config(self):
        try:
            paper_size = json_manager.get_project_paper_size()
            orientation = json_manager.get_project_orientation()

            if paper_size in EXPORT_PAPER_SIZES_MM:
                self.paper_width_mm, self.paper_height_mm = \
                    EXPORT_PAPER_SIZES_MM[paper_size]
            else:
                self.paper_width_mm, self.paper_height_mm = \
                    EXPORT_PAPER_SIZES_MM.get('A4', (210, 297))

            self.orientation = orientation
            if self.orientation == "Landscape":
                self.paper_width_mm, self.paper_height_mm = (
                    self.paper_height_mm, self.paper_width_mm
                )

            self.width = int(self.paper_width_mm * PIXEL_PER_MM)
            self.height = int(self.paper_height_mm * PIXEL_PER_MM)
        except Exception:
            self.paper_width_mm, self.paper_height_mm = \
                EXPORT_PAPER_SIZES_MM.get('A4', (210, 297))
            self.orientation = "Portrait"
            self.width = int(self.paper_width_mm * PIXEL_PER_MM)
            self.height = int(self.paper_height_mm * PIXEL_PER_MM)
    ###################################
    ##########end of load_paper_from_config
    ###################################

    ###################################
    ##########set_view_state###########
    ###################################
    def set_view_state(self, view_state):
        self.view_state = view_state
        self.use_view_state = True
        if view_state:
            layout = view_state.get('layout', None)
            if layout:
                grid_rect = layout['grid']
                self.grid_x_mm = grid_rect[0]
                self.grid_y_mm = grid_rect[1]
                self.grid_w_mm = grid_rect[2]
                self.grid_h_mm = grid_rect[3]
            else:
                self.grid_x_mm = 0
                self.grid_y_mm = 0
                self.grid_w_mm = self.paper_width_mm
                self.grid_h_mm = self.paper_height_mm
    ###################################
    ##########end of set_view_state####
    ###################################

    ###################################
    ##########world_to_screen##########
    ###################################
    def world_to_screen(self, world_x, world_y):
        if not self.use_view_state or not self.view_state:
            return world_x, world_y

        x_range = self.view_state['grid_x_max'] - self.view_state['grid_x_min']
        y_range = self.view_state['grid_y_max'] - self.view_state['grid_y_min']
        if x_range <= 0 or y_range <= 0:
            return world_x, world_y

        fraction_x = (world_x - self.view_state['grid_x_min']) / x_range
        fraction_y = (world_y - self.view_state['grid_y_min']) / y_range

        screen_x_mm = self.grid_x_mm + fraction_x * self.grid_w_mm
        screen_y_mm = self.grid_y_mm + fraction_y * self.grid_h_mm
        return screen_x_mm, screen_y_mm
    ###################################
    ##########end of world_to_screen###
    ###################################

    ###################################
    ##########add_line#################
    ###################################
    def add_line(self, x1, y1, x2, y2, color=(0, 0, 0, 1), line_width=2):
        self.drawing_commands.append({
            'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
            'color': color, 'line_width': line_width,
        })
    ###################################
    ##########end of add_line#########
    ###################################

    ###################################
    ##########add_coil#################
    ###################################
    def add_coil(self, x_start, x_end, y_values, color=(0, 0, 0, 1),
                 line_width=2):
        self.drawing_commands.append({
            'type': 'coil', 'x_start': x_start, 'x_end': x_end,
            'y_vals': list(y_values), 'color': color,
            'line_width': line_width,
        })
    ###################################
    ##########end of add_coil#########
    ###################################

    ###################################
    ##########add_text#################
    ###################################
    def add_text(self, text, x, y, font_size=12, color=(0, 0, 0, 1)):
        self.drawing_commands.append({
            'type': 'text', 'text': text, 'x': x, 'y': y,
            'font_size': font_size, 'color': color,
        })
    ###################################
    ##########end of add_text#########
    ###################################

    ###################################
    ##########add_filled_rect##########
    ###################################
    def add_filled_rect(self, x, y, width, height, color=(1, 1, 1, 1)):
        self.drawing_commands.append({
            'type': 'rect', 'x': x, 'y': y, 'w': width, 'h': height,
            'color': color,
        })
    ###################################
    ##########end of add_filled_rect##
    ###################################

    ###################################
    ##########add_image################
    ###################################
    def add_image(self, filepath, x, y, width, height, opacity=1.0):
        self.drawing_commands.append({
            'type': 'image', 'filepath': filepath, 'x': x, 'y': y,
            'w': width, 'h': height, 'opacity': opacity,
        })
    ###################################
    ##########end of add_image########
    ###################################

    ###################################
    ##########clear####################
    ###################################
    def clear(self):
        self.drawing_commands = []
    ###################################
    ##########end of clear############
    ###################################

    ###################################
    ##########_color_to_hex############
    ###################################
    def _color_to_hex(self, color):
        red_component = int(color[0] * 255)
        green_component = int(color[1] * 255)
        blue_component = int(color[2] * 255)
        return "#%02x%02x%02x" % (red_component, green_component, blue_component)
    ###################################
    ##########end of _color_to_hex####
    ###################################

    ###################################
    ##########_color_to_rgb############
    ###################################
    def _color_to_rgb(self, color):
        return tuple(int(component * 255) for component in color[:3])
    ###################################
    ##########end of _color_to_rgb####
    ###################################

    ###################################
    ##########_get_target_size#########
    ###################################
    def _get_target_size(self, dpi):
        target_width_px = int(self.paper_width_mm * dpi / 25.4)
        target_height_px = int(self.paper_height_mm * dpi / 25.4)
        return target_width_px, target_height_px
    ###################################
    ##########end of _get_target_size##
    ###################################

    ###################################
    ##########_compute_scale###########
    ###################################
    def _compute_scale(self, target_width_px, target_height_px):
        return 1.0
    ###################################
    ##########end of _compute_scale####
    ###################################

    ###################################
    ##########_logo_placements_mm######
    ###################################
    def _logo_placements_mm(self):
        if not os.path.exists(LOGO_PATH):
            return []
        if not self.view_state:
            return []

        layout = self.view_state.get('layout', None)
        if not layout:
            return []

        info_x_mm, info_y_mm, info_width_mm, info_height_mm = layout['info']

        left_logo_x = info_x_mm
        left_logo_y = info_y_mm
        right_logo_x = info_x_mm + info_width_mm - info_height_mm
        right_logo_y = info_y_mm

        return [
            (left_logo_x, left_logo_y, info_height_mm, info_height_mm,
             EXPORT_LOGO_OPACITY),
            (right_logo_x, right_logo_y, info_height_mm, info_height_mm,
             EXPORT_LOGO_OPACITY),
        ]
    ###################################
    ##########end of _logo_placements_mm
    ###################################

    ###################################
    ##########_coil_segments_4pt#######
    ###################################
    def _coil_segments_4pt(self, x_start, x_end, y_values):
        return [
            (x_start, y_values[0], x_start, y_values[1]),
            (x_start, y_values[1], x_end, y_values[2]),
            (x_end, y_values[2], x_end, y_values[3]),
        ]
    ###################################
    ##########end of _coil_segments_4pt
    ###################################

    ###################################
    ##########_coil_segments_5pt#######
    ###################################
    def _coil_segments_5pt(self, x_start, x_end, y_values):
        x_center = x_start + (x_end - x_start) / 2
        return [
            (x_start, y_values[0], x_start, y_values[1]),
            (x_start, y_values[1], x_center, y_values[2]),
            (x_center, y_values[2], x_end, y_values[3]),
            (x_end, y_values[3], x_end, y_values[4]),
        ]
    ###################################
    ##########end of _coil_segments_5pt
    ###################################

    ###################################
    ##########save_svg#################
    ###################################
    def save_svg(self, filepath):
        if not self.drawing_commands:
            return False
        dpi = 300
        target_width_px, target_height_px = self._get_target_size(dpi)
        scale = self._compute_scale(target_width_px, target_height_px)

        def transform_x(world_x):
            screen_x_mm, _ = self.world_to_screen(world_x, 0)
            return screen_x_mm * dpi / 25.4

        def transform_y(world_y):
            _, screen_y_mm = self.world_to_screen(0, world_y)
            return target_height_px - (screen_y_mm * dpi / 25.4)

        svg_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg"',
            '     xmlns:xlink="http://www.w3.org/1999/xlink"',
            '     viewBox="0 0 %d %d"' % (target_width_px, target_height_px),
            '     width="%smm" height="%smm">' % (
                self.paper_width_mm, self.paper_height_mm
            ),
            '  <rect x="0" y="0" width="%d" height="%d" fill="white"/>' % (
                target_width_px, target_height_px
            ),
        ]

        for (logo_x_mm, logo_y_mm, logo_width_mm,
             logo_height_mm, logo_opacity) in self._logo_placements_mm():
            logo_screen_x = logo_x_mm / self.paper_width_mm * target_width_px
            logo_screen_y = (target_height_px -
                             (logo_y_mm + logo_height_mm) /
                             self.paper_height_mm * target_height_px)
            logo_screen_width = logo_width_mm / self.paper_width_mm * target_width_px
            logo_screen_height = logo_height_mm / self.paper_height_mm * target_height_px
            svg_lines.append(
                '  <image x="%.2f" y="%.2f" width="%.2f" height="%.2f" '
                'opacity="%s" xlink:href="%s"/>' % (
                    logo_screen_x, logo_screen_y, logo_screen_width,
                    logo_screen_height, logo_opacity, LOGO_PATH
                )
            )

        svg_lines.append('  <g stroke-linecap="round" stroke-linejoin="round">')

        for command in self.drawing_commands:
            command_type = command['type']
            if command_type == 'line':
                line_color = self._color_to_hex(command['color'])
                line_width_value = (command['line_width'] *
                                     EXPORT_LINE_WIDTH_SCALE)
                svg_lines.append(
                    '    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" '
                    'stroke="%s" stroke-width="%.2f" />' % (
                        transform_x(command['x1']),
                        transform_y(command['y1']),
                        transform_x(command['x2']),
                        transform_y(command['y2']),
                        line_color, line_width_value
                    )
                )
            elif command_type == 'coil':
                coil_color = self._color_to_hex(command['color'])
                y_values = command['y_vals']
                if len(y_values) == 4:
                    segments = self._coil_segments_4pt(
                        command['x_start'], command['x_end'], y_values
                    )
                elif len(y_values) >= 5:
                    segments = self._coil_segments_5pt(
                        command['x_start'], command['x_end'], y_values
                    )
                else:
                    segments = []
                line_width_value = (command['line_width'] *
                                     EXPORT_LINE_WIDTH_SCALE)
                for (segment_x1, segment_y1,
                     segment_x2, segment_y2) in segments:
                    svg_lines.append(
                        '    <line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" '
                        'stroke="%s" stroke-width="%.2f" />' % (
                            transform_x(segment_x1),
                            transform_y(segment_y1),
                            transform_x(segment_x2),
                            transform_y(segment_y2),
                            coil_color, line_width_value
                        )
                    )
            elif command_type == 'text':
                text_color = self._color_to_hex(command['color'])
                text_screen_x = transform_x(command['x'])
                text_screen_y = transform_y(command['y'])
                text_font_size = max(
                    1,
                    command['font_size'] * EXPORT_FONT_SIZE_SCALE
                )
                svg_lines.append(
                    '    <text x="%.2f" y="%.2f" font-size="%.2f" '
                    'fill="%s" text-anchor="middle" '
                    'dominant-baseline="middle">%s</text>' % (
                        text_screen_x, text_screen_y, text_font_size,
                        text_color, command['text']
                    )
                )
            elif command_type == 'rect':
                rect_color = self._color_to_hex(command['color'])
                rect_x = transform_x(command['x'])
                rect_y_top = transform_y(command['y'] + command['h'])
                rect_width = transform_x(command['x'] + command['w']) - rect_x
                rect_height = transform_y(command['y']) - rect_y_top
                svg_lines.append(
                    '    <rect x="%.2f" y="%.2f" width="%.2f" '
                    'height="%.2f" fill="%s" stroke="none" />' % (
                        rect_x, rect_y_top, rect_width,
                        rect_height, rect_color
                    )
                )

        svg_lines.append('  </g>')
        svg_lines.append('</svg>')

        with open(filepath, 'w', encoding='utf-8') as file_handle:
            file_handle.write('\n'.join(svg_lines))
        return True
    ###################################
    ##########end of save_svg########
    ###################################

    ###################################
    ##########_render_to_pil_image#####
    ###################################
    def _render_to_pil_image(self, target_width_px, target_height_px, dpi=300):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            return None

        image = Image.new('RGB', (target_width_px, target_height_px),
                           (255, 255, 255))

        if os.path.exists(LOGO_PATH):
            try:
                logo_image = Image.open(LOGO_PATH).convert('RGBA')
                for (logo_x_mm, logo_y_mm, logo_width_mm,
                     logo_height_mm, logo_opacity) in self._logo_placements_mm():
                    logo_screen_x = int(logo_x_mm / self.paper_width_mm *
                                         target_width_px)
                    logo_screen_y = int(target_height_px -
                                         (logo_y_mm + logo_height_mm) /
                                         self.paper_height_mm * target_height_px)
                    logo_screen_width = int(logo_width_mm / self.paper_width_mm *
                                             target_width_px)
                    logo_screen_height = int(logo_height_mm / self.paper_height_mm *
                                              target_height_px)
                    if logo_screen_width < 2 or logo_screen_height < 2:
                        continue
                    resized_logo = logo_image.resize(
                        (logo_screen_width, logo_screen_height),
                        Image.LANCZOS
                    )
                    alpha_channel = resized_logo.split()[3]
                    alpha_channel = alpha_channel.point(
                        lambda value: int(value * logo_opacity)
                    )
                    resized_logo.putalpha(alpha_channel)
                    image.paste(resized_logo,
                                (logo_screen_x, logo_screen_y),
                                resized_logo)
            except Exception:
                pass

        image_draw = ImageDraw.Draw(image)

        def get_font(font_size):
            font_size = max(1, font_size)
            for path in ["/system/fonts/Roboto-Regular.ttf",
                         "/system/fonts/DroidSans.ttf",
                         "arial.ttf", "DejaVuSans.ttf"]:
                try:
                    return ImageFont.truetype(path, font_size)
                except Exception:
                    continue
            return ImageFont.load_default()

        def transform_x(world_x):
            screen_x_mm, _ = self.world_to_screen(world_x, 0)
            return screen_x_mm * dpi / 25.4

        def transform_y(world_y):
            _, screen_y_mm = self.world_to_screen(0, world_y)
            return target_height_px - (screen_y_mm * dpi / 25.4)

        for command in self.drawing_commands:
            command_type = command['type']
            if command_type == 'line':
                line_color = self._color_to_rgb(command['color'])
                pixel_line_width = max(
                    1,
                    int(command['line_width'] * EXPORT_LINE_WIDTH_SCALE)
                )
                image_draw.line(
                    [(transform_x(command['x1']),
                      transform_y(command['y1'])),
                     (transform_x(command['x2']),
                      transform_y(command['y2']))],
                    fill=line_color, width=pixel_line_width
                )
            elif command_type == 'coil':
                coil_color = self._color_to_rgb(command['color'])
                pixel_line_width = max(
                    1,
                    int(command['line_width'] * EXPORT_LINE_WIDTH_SCALE)
                )
                y_values = command['y_vals']
                if len(y_values) == 4:
                    segments = self._coil_segments_4pt(
                        command['x_start'], command['x_end'], y_values
                    )
                elif len(y_values) >= 5:
                    segments = self._coil_segments_5pt(
                        command['x_start'], command['x_end'], y_values
                    )
                else:
                    segments = []
                for (segment_x1, segment_y1,
                     segment_x2, segment_y2) in segments:
                    image_draw.line(
                        [(transform_x(segment_x1),
                          transform_y(segment_y1)),
                         (transform_x(segment_x2),
                          transform_y(segment_y2))],
                        fill=coil_color, width=pixel_line_width
                    )
            elif command_type == 'text':
                text_color = self._color_to_rgb(command['color'])
                text_screen_x = transform_x(command['x'])
                text_screen_y = transform_y(command['y'])
                font_pixel_size = max(
                    1,
                    int(command['font_size'] * EXPORT_FONT_SIZE_SCALE)
                )
                font = get_font(font_pixel_size)
                try:
                    bbox = image_draw.textbbox((0, 0), command['text'],
                                                font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except Exception:
                    text_width, text_height = 0, 0
                image_draw.text(
                    (text_screen_x - text_width / 2,
                     text_screen_y - text_height / 2),
                    command['text'],
                    fill=text_color, font=font
                )
            elif command_type == 'rect':
                rect_color = self._color_to_rgb(command['color'])
                rect_x1 = transform_x(command['x'])
                rect_x2 = transform_x(command['x'] + command['w'])
                rect_y1 = transform_y(command['y'])
                rect_y2 = transform_y(command['y'] + command['h'])
                image_draw.rectangle(
                    [rect_x1, min(rect_y1, rect_y2),
                     rect_x2, max(rect_y1, rect_y2)],
                    fill=rect_color
                )

        return image
    ###################################
    ##########end of _render_to_pil_image
    ###################################

    ###################################
    ##########save_png#################
    ###################################
    def save_png(self, filepath, dpi=300):
        try:
            self.load_paper_from_config()
            target_width_px, target_height_px = self._get_target_size(dpi)
            image = self._render_to_pil_image(
                target_width_px, target_height_px, dpi
            )
            if image:
                image.save(filepath, 'PNG')
                return True
        except Exception:
            pass
        return False
    ###################################
    ##########end of save_png#########
    ###################################

    ###################################
    ##########save_jpg#################
    ###################################
    def save_jpg(self, filepath, quality=95, dpi=300):
        try:
            self.load_paper_from_config()
            target_width_px, target_height_px = self._get_target_size(dpi)
            image = self._render_to_pil_image(
                target_width_px, target_height_px, dpi
            )
            if image:
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(filepath, 'JPEG', quality=quality)
                return True
        except Exception:
            pass
        return False
    ###################################
    ##########end of save_jpg#########
    ###################################

    ###################################
    ##########save_pdf#################
    ###################################
    def save_pdf(self, filepath, dpi=300):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4, A3, A2, A1, A0, letter, legal
            from reportlab.lib.utils import ImageReader
            import tempfile

            self.load_paper_from_config()
            pagesize_map = {'A0': A0, 'A1': A1, 'A2': A2, 'A3': A3,
                             'A4': A4, 'Letter': letter, 'Legal': legal}
            paper_size = json_manager.get_project_paper_size()
            pagesize = pagesize_map.get(paper_size, A4)
            if self.orientation == "Landscape":
                pagesize = (pagesize[1], pagesize[0])

            target_width_px, target_height_px = self._get_target_size(dpi)
            image = self._render_to_pil_image(
                target_width_px, target_height_px, dpi
            )
            if not image:
                return False

            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png', delete=False
            )
            image.save(temp_file.name, 'PNG')
            temp_file.close()

            pdf_canvas = canvas.Canvas(filepath, pagesize=pagesize)
            page_width, page_height = pagesize
            image_reader = ImageReader(temp_file.name)
            image_width, image_height = image.size
            fit_scale = min(page_width / image_width,
                             page_height / image_height)
            draw_width = image_width * fit_scale
            draw_height = image_height * fit_scale
            offset_x = (page_width - draw_width) / 2
            offset_y = (page_height - draw_height) / 2
            pdf_canvas.setFillColorRGB(1, 1, 1)
            pdf_canvas.rect(0, 0, page_width, page_height, fill=1)
            pdf_canvas.drawImage(image_reader, offset_x, offset_y,
                                   draw_width, draw_height)
            pdf_canvas.save()
            os.unlink(temp_file.name)
            return True
        except Exception:
            return False
    ###################################
    ##########end of save_pdf#########
    ###################################

    ###################################
    ##########save_eps#################
    ###################################
    def save_eps(self, filepath, dpi=300):
        try:
            self.load_paper_from_config()
            target_width_px, target_height_px = self._get_target_size(dpi)
            image = self._render_to_pil_image(
                target_width_px, target_height_px, dpi
            )
            if image:
                image.save(filepath, 'EPS')
                return True
        except Exception:
            pass
        return False
    ###################################
    ##########end of save_eps#########
    ###################################

    ###################################
    ##########save_dxf#################
    ###################################
    def save_dxf(self, filepath):
        dxf_lines = ['0', 'SECTION', '2', 'HEADER', '0', 'ENDSEC',
                      '0', 'SECTION', '2', 'TABLES', '0', 'ENDSEC',
                      '0', 'SECTION', '2', 'BLOCKS', '0', 'ENDSEC',
                      '0', 'SECTION', '2', 'ENTITIES']

        def add_dxf_line(line_x1, line_y1, line_x2, line_y2):
            dxf_lines.extend(['0', 'LINE', '8', '0',
                               '10', '%.3f' % line_x1,
                               '20', '%.3f' % line_y1,
                               '11', '%.3f' % line_x2,
                               '21', '%.3f' % line_y2])

        for command in self.drawing_commands:
            command_type = command['type']
            if command_type == 'line':
                add_dxf_line(command['x1'], command['y1'],
                              command['x2'], command['y2'])
            elif command_type == 'coil':
                y_values = command['y_vals']
                if len(y_values) == 4:
                    segments = self._coil_segments_4pt(
                        command['x_start'], command['x_end'], y_values
                    )
                elif len(y_values) >= 5:
                    segments = self._coil_segments_5pt(
                        command['x_start'], command['x_end'], y_values
                    )
                else:
                    segments = []
                for (segment_x1, segment_y1,
                     segment_x2, segment_y2) in segments:
                    add_dxf_line(segment_x1, segment_y1,
                                  segment_x2, segment_y2)

        dxf_lines.extend(['0', 'ENDSEC', '0', 'EOF'])
        with open(filepath, 'w') as file_handle:
            file_handle.write('\n'.join(dxf_lines))
        return True
    ###################################
    ##########end of save_dxf#########
    ###################################

    ###################################
    ##########save#####################
    ###################################
    def save(self, filepath, format='svg', dpi=300, quality=95, **kwargs):
        format_lower = format.lower()
        self.load_paper_from_config()
        if format_lower == 'svg' or filepath.lower().endswith('.svg'):
            return self.save_svg(filepath)
        elif format_lower == 'pdf' or filepath.lower().endswith('.pdf'):
            return self.save_pdf(filepath, dpi)
        elif format_lower == 'eps' or filepath.lower().endswith('.eps'):
            return self.save_eps(filepath, dpi)
        elif format_lower == 'dxf' or filepath.lower().endswith('.dxf'):
            return self.save_dxf(filepath)
        elif format_lower == 'png' or filepath.lower().endswith('.png'):
            return self.save_png(filepath, dpi)
        elif format_lower in ('jpg', 'jpeg') or filepath.lower().endswith(
                ('.jpg', '.jpeg')):
            return self.save_jpg(filepath, quality, dpi)
        return False
    ###################################
    ##########end of save############
    ###################################