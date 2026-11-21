"""
================================================================================
File: app/app_menu.py
Purpose: Main menu + open dialogs.
         v0.1.4: Wizard + standalone project pages.
Version: 0.1.4
================================================================================
"""

from kivy.clock import Clock

from managers.json_manager import json_manager
from ui.notifications import show_error
from ui.main_menu import show_main_menu

from app.app_actions import handle_draw, handle_export, handle_motor_info


"""
diagnose_coords.py
Add to menu, click it, send output.
"""
import os
import sys


"""
diagnose_coords.py
Writes diagnostic to file — visible after closing app.
"""


def run_diagnose(app):
    """Add to app_menu.py as diagnose action."""
    import os
    from datetime import datetime

    # Write to file
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "diagnose_output.txt"
    )

    lines = []
    lines.append("=" * 70)
    lines.append(f"COORDINATE DIAGNOSTIC — {datetime.now().strftime('%H:%M:%S')}")
    lines.append("=" * 70)

    if not hasattr(app, 'winding_widget'):
        lines.append("ERROR: No winding widget")
        _write_file(report_path, lines)
        return

    w = app.winding_widget

    # Diagram state
    lines.append("\nDIAGRAM STATE:")
    lines.append(f"  SCREEN_scale:      {w.SCREEN_scale:.4f}")
    lines.append(f"  SCREEN_offset_x:   {w.SCREEN_offset_x:.2f}")
    lines.append(f"  SCREEN_offset_y:   {w.SCREEN_offset_y:.2f}")
    lines.append(f"  GRID_cell_size_px: {w.GRID_cell_size_px:.4f}")
    lines.append(f"  GRID_x_min/max:    {w.GRID_x_min} / {w.GRID_x_max}")
    lines.append(f"  GRID_y_min/max:    {w.GRID_y_min:.2f} / {w.GRID_y_max:.2f}")
    lines.append(f"  PAGE_width_px:     {w.PAGE_width_px}")
    lines.append(f"  PAGE_height_px:    {w.PAGE_height_px}")

    # View state
    v = w.zoom_controller.view
    lines.append("\nVIEW STATE:")
    lines.append(f"  screen_scale:      {v.screen_scale:.4f}")
    lines.append(f"  offset_x:          {v.offset_x:.2f}")
    lines.append(f"  offset_y:          {v.offset_y:.2f}")
    lines.append(f"  cell_size_px:      {v.cell_size_px:.4f}")
    lines.append(f"  grid_x_min:        {v.grid_x_min}")
    lines.append(f"  grid_x_max:        {getattr(v, 'grid_x_max', 'MISSING')}")
    lines.append(f"  grid_y_min:        {v.grid_y_min:.2f}")
    lines.append(f"  grid_y_max:        {getattr(v, 'grid_y_max', 'MISSING')}")
    lines.append(f"  margin_px:         {v.margin_px}")
    lines.append(f"  grid_x_px:         {getattr(v, 'grid_x_px', 'MISSING')}")
    lines.append(f"  grid_y_px:         {getattr(v, 'grid_y_px', 'MISSING')}")
    lines.append(f"  grid_w_px:         {getattr(v, 'grid_w_px', 'MISSING')}")
    lines.append(f"  grid_h_px:         {getattr(v, 'grid_h_px', 'MISSING')}")

    # Agreement
    lines.append("\nAGREEMENT:")
    lines.append(f"  scale match:       {abs(w.SCREEN_scale - v.screen_scale) < 0.0001}")
    lines.append(f"  offset_x match:    {abs(w.SCREEN_offset_x - v.offset_x) < 0.01}")
    lines.append(f"  offset_y match:    {abs(w.SCREEN_offset_y - v.offset_y) < 0.01}")
    lines.append(f"  cell_size match:   {abs(w.GRID_cell_size_px - v.cell_size_px) < 0.0001}")

    # Conversion test
    lines.append("\nCONVERSION TEST:")
    test_points = [
        ("GRID origin", w.GRID_x_min, w.GRID_y_min),
        ("Slot 1", 1, w.GRID_y_min + 0.5),
        ("Slot 10", 10, w.GRID_y_min + 5),
    ]

    for name, wx, wy in test_points:
        sx1, sy1 = w.world_to_screen(wx, wy)
        sx2, sy2 = v.world_to_screen(wx, wy)
        lines.append(f"  {name} (world {wx:.2f}, {wy:.2f}):")
        lines.append(f"    diagram.world_to_screen -> ({sx1:.2f}, {sy1:.2f})")
        lines.append(f"    view.world_to_screen    -> ({sx2:.2f}, {sy2:.2f})")
        lines.append(f"    DIFF:                     ({sx1 - sx2:.2f}, {sy1 - sy2:.2f})")

        # Reverse
        rwx1, rwy1 = w.screen_to_world(sx1, sy1)
        rwx2, rwy2 = v.screen_to_world(sx2, sy2)
        lines.append(f"    diagram.screen_to_world -> ({rwx1:.3f}, {rwy1:.3f})")
        lines.append(f"    view.screen_to_world    -> ({rwx2:.3f}, {rwy2:.3f})")

    # Label check
    lines.append("\nLABEL CHECK:")
    if w.SLOT_labels:
        from utils.constants import SLOT_NUMBER_X_SHIFT
        lines.append(f"  Total SLOT labels: {len(w.SLOT_labels)}")
        for i, lbl in enumerate(w.SLOT_labels[:5]):
            slot_text = lbl.text
            try:
                slot_num = int(slot_text)
            except Exception:
                continue
            x_world = slot_num + SLOT_NUMBER_X_SHIFT
            y_world = w.GRID_y_min + 0.5
            ex, ey = w.world_to_screen(x_world, y_world)
            lines.append(f"  Slot {slot_num}:")
            lines.append(f"    expected:  ({ex:.1f}, {ey:.1f})")
            lines.append(f"    actual:    ({lbl.x:.1f}, {lbl.y:.1f})")
            lines.append(f"    DIFF:      ({lbl.x - ex:.1f}, {lbl.y - ey:.1f})")
            lines.append(f"    opacity:   {lbl.opacity}")
    else:
        lines.append("  No SLOT labels!")

    # Table check
    lines.append("\nTABLE CHECK:")
    if w.TABLE_labels:
        lines.append(f"  Total TABLE labels: {len(w.TABLE_labels)}")
        for i, entry in enumerate(w.TABLE_cells[:3]):
            label, col, row, row_type, span_cols = entry
            lines.append(f"  Cell[{i}] col={col} row={row} type={row_type}:")
            lines.append(f"    text:      '{label.text[:20]}'")
            lines.append(f"    actual:    ({label.x:.1f}, {label.y:.1f})")
            lines.append(f"    opacity:   {label.opacity}")
    else:
        lines.append("  No TABLE labels!")

    lines.append("\n" + "=" * 70)

    _write_file(report_path, lines)
    print(f"Diagnostic written to: {report_path}")

    # Also show in notification
    try:
        from ui.notifications import show_success
        show_success(f"Diagnostic saved to diagnose_output.txt", 3)
    except Exception:
        pass


def _write_file(path, lines):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"Written: {path}")
    except Exception as e:
        print(f"Write failed: {e}")


                
def show_main_menu_for_app(app):
    show_main_menu(
        anchor_widget=app.menu_btn,
        new_open=lambda: open_project_setup(app),
        #
        debug_overlay=lambda: toggle_debug_overlay(app),
        project_info=lambda: open_standalone_page(app, "project"),diagnose=lambda: run_diagnose(app),

        motor_settings=lambda: open_standalone_page(app, "motor"),
        paper_settings=lambda: open_standalone_page(app, "paper"),
        physical_settings=lambda: open_standalone_page(app, "physical"),
        draw_style=lambda: open_draw_style(app),
        edit_diagram=lambda: handle_edit_diagram_menu(app),
        add_pattern=lambda: open_add_pattern(app),
        connection=lambda: handle_connection_toggle_menu(app),
        export=lambda: handle_export(app),
        import_=lambda: open_import(app),
        settings=lambda: open_jm_setup(app),
        log_manager=lambda: open_log_manager(app),
        motor_info=lambda: handle_motor_info(app),
        app_info=lambda: open_app_info(app),
        exit=lambda: close_app_menu(app),
    )


# ============================================================
# ================== WIZARD ==================================
# ============================================================

def open_project_setup(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.project_setup import show_project_setup

        def on_finish(filepath, data):
            set_project_file_path(app, filepath, data)

        # اگر پروژه‌ای لود نشده، startup mode
        # (یعنی cancel = بستن کامل اپ)
        is_startup = (json_manager.project_data is None)

        show_project_setup(
            main_app_callback=on_finish,
            is_startup=is_startup,
        )
    except Exception as error:
        show_error("Error: " + str(error), 3)


def set_project_file_path(app, filepath, data=None):
    app.project_loaded = True

    if data:
        json_manager.project_data = data
        json_manager.ensure_group_structure()

    if hasattr(app, "winding_widget"):
        app.winding_widget.connection.clear_for_new_project()

    from app.app_diagram_widget import recreate_diagram_widget
    recreate_diagram_widget(app)

    from app.app_info_labels import update_info_labels
    update_info_labels(app)

    Clock.schedule_once(lambda dt: handle_draw(app, None), 0.2)


# ============================================================
# ================== STANDALONE PAGES ========================
# ============================================================

def open_standalone_page(app, page_name):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.project_setup import open_standalone_page as _open

        def on_saved():
            from app.app_info_labels import update_info_labels
            update_info_labels(app)
            Clock.schedule_once(lambda dt: handle_draw(app, None), 0.2)

        _open(app, page_name)
    except Exception as error:
        show_error("Error: " + str(error), 3)


# ============================================================
# ================== OTHER ===================================
# ============================================================

def open_draw_style(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.draw_style_dialog import show_draw_style_dialog

        def on_apply():
            Clock.schedule_once(lambda dt: handle_draw(app, None), 0.1)

        show_draw_style_dialog(on_apply_callback=on_apply)
    except Exception as error:
        show_error("Error: " + str(error), 3)


def open_jm_setup(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.jm_setup import show_jm_setup

        def on_save():
            try:
                from dialogs.project_setup import update_all_spinners
                update_all_spinners()
            except Exception:
                pass

        show_jm_setup(on_save)
    except Exception as error:
        show_error("Error: " + str(error), 3)


def open_log_manager(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.log_manager import show_log_manager
        show_log_manager()
    except Exception as error:
        show_error("Error: " + str(error), 3)


def open_add_pattern(app):
    from dialogs.coming_soon_dialog import show_coming_soon
    show_coming_soon(
        "Add Pattern",
        "Custom pattern editor will be available in a later version."
    )


def open_import(app):
    if app.connection_panel is not None:
        return
    if app.edit_diagram_panel is not None:
        return
    try:
        from dialogs.import_dialog import show_import_dialog
        show_import_dialog(on_import=lambda filepath, importer: None)
    except Exception as error:
        show_error("Error: " + str(error), 3)


def handle_edit_diagram_menu(app):
    from app.app_edit_diagram import handle_edit_diagram
    handle_edit_diagram(app)


def handle_connection_toggle_menu(app):
    from app.app_connection import handle_connection_toggle
    handle_connection_toggle(app)


def open_app_info(app):
    from app.app_app_info import open_app_info_dialog
    open_app_info_dialog(app)


def close_app_menu(app):
    from app.app_main_ui import close_app
    close_app(app)

def toggle_debug_overlay(app):
    """Debug overlay disabled (module removed in cleanup)."""
    from ui.notifications import show_info
    show_info("Debug overlay disabled (module removed)", 2)


