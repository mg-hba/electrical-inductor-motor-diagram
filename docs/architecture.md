Architecture - v0.1.3

Layered Structure

main0.1.3.py (entry point)

- app/                                  (application layer)
  - main_app.py                         (coordinator)
  - app_orientation.py
  - app_zoom.py
  - app_diagram_widget.py
  - app_main_ui.py
  - app_actions.py
  - app_menu.py
  - app_app_info.py
  - app_info_labels.py
  - app_edit_diagram.py
  - app_connection.py
  - app_connection_actions.py

- core/                                 (core logic)
  - base_diagram/
    - base_diagram.py
    - diagram_cutting.py
    - diagram_edit_mode.py
    - diagram_labels.py
    - diagram_table.py
    - diagram_connection.py
  - base_diagram_core.py
  - view_transform.py
  - connection/
  - rendering/

- diagrams/                             (winding diagrams)
  - base/
    - diagram_base.py
    - zoom_controller.py
    - touch_handler.py
    - layer_renderer.py
    - drawing_layer.py
  - single_layer/
  - two_layer/
  - patterns/

- dialogs/                              (UI dialogs)
  - project_setup/                      (package)
  - open_save.py
  - app_info.py
  - docs_viewer.py
  - changelog_viewer.py
  - jm_setup.py
  - log_manager.py
  - motor_info.py
  - draw_style_dialog.py
  - coils_per_pole_dialog.py
  - comments_dialog.py
  - coming_soon_dialog.py

- managers/                             (data managers)
  - json_manager.py
  - debug_logger.py
  - docs_manager.py

- ui/                                   (UI components)
  - theme.py
  - notifications.py
  - components.py
  - icon_button.py
  - connection_panel.py
  - conflict_dialog.py
  - main_menu.py
  - zoom_panel.py
  - edit_diagram_panel.py

- backends/                             (render backends)
  - base.py
  - vector_backend.py
  - null_backend.py

- exporters/                            (export)
  - vector_exporter.py
  - export_dialog.py

- importers/                            (import stubs)
  - base_importer.py
  - importer_registry.py
  - svg_importer.py
  - dxf_importer.py
  - pdf_importer.py
  - raster_importer.py

- utils/                                (helpers)
  - errors.py
  - constants/

Key Design Patterns

- Abstract RenderBackend (Export only)
- Pattern Registry (Lap, Triangle, Concentric)
- Layer Stack (6 canvas layers)
- Facade Pattern (ConnectionLayer, Operations)
- Icon System (IconButton + IconTextButton)
- Docs Manager
- Coordinator + helper functions (app/, core/base_diagram/)

Edit Diagram Flow

1. User opens Edit Diagram (from menu)
2. winding_widget.enter_edit_mode()
3. Two diamonds at x = -1 drawn (main + phase)
4. User drags a diamond (rounded to grid)
5. On release, redraw with new shift
6. User clicks Apply:
   - json_manager.set_main_diagram_shift_y(value)
   - json_manager.set_phase_diagram_shift_y(value)
   - connection.shift_y = value
   - _emit_wire_points() (rebuild points without shift)
   - Connection (junctions, lines) auto-shifts via shift_y

Connection Shift Flow

1. Wire points stored WITHOUT shift in JSON
2. In draw_static, shift_y applied to:
   - wire_points (from _emit_wire_points)
   - junctions (from JSON)
   - lines (from JSON)
3. In touch_handler pencil/drag:
   - world_y = screen_to_world(...)[1] - shift_y
   - New points stored without shift

Export Flow

1. VectorExporter.world_to_screen returns mm
2. transform_x/transform_y convert mm -> px (DPI 300)
3. scale = 1.0 (no double scaling)
4. stroke-width and font-size use EXPORT_*_SCALE multipliers
5. Result: full page, correct layout, correct widths
