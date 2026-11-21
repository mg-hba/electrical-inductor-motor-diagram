"""
================================================================================
File: dialogs/project_setup/setup_wizard.py
Purpose: Wizard controller - manages navigation between pages.
Version: 0.1.4.2
================================================================================
"""

import os
import json
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

from managers.json_manager import json_manager
from managers.debug_logger import debug_logger
from ui.theme import Theme
from ui.notifications import (
    show_error, show_success, show_confirm,
)

from dialogs.project_setup.draft_manager import DraftManager
from dialogs.project_setup.page_project import PageProject
from dialogs.project_setup.page_motor import PageMotor
from dialogs.project_setup.page_paper import PagePaper
from dialogs.project_setup.page_physical import PagePhysical
from dialogs.project_setup.page_save import PageSave


class ProjectSetupWizard(Popup):

    def __init__(self, on_finish=None, on_cancel=None,
                 project_root=None, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.size_hint = (0.95, 0.45)
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        self.on_finish = on_finish
        self.on_cancel = on_cancel

        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            ))
        self.draft = DraftManager(project_root)

        self.collected_data = {}
        self.history = []
        self.current_page_name = None
        self.current_page = None

        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            Color(*Theme.DIALOG_BG)
            self._bg = Rectangle(pos=self.main_layout.pos,
                                 size=self.main_layout.size)
        self.main_layout.bind(
            pos=lambda i, v: setattr(self._bg, 'pos', i.pos),
            size=lambda i, v: setattr(self._bg, 'size', i.size),
        )
        self.add_widget(self.main_layout)

        self._load_draft_if_exists()
        self._goto_page("project")

    # ============================================================
    # ================== DRAFT ===================================
    # ============================================================

    def _load_draft_if_exists(self):
        if self.draft.exists():
            data = self.draft.get_data()
            if data:
                self.collected_data = data

    def _save_draft(self):
        if not self.collected_data:
            return
        self.draft.save(self.collected_data, self._get_page_index())

    def _get_page_index(self):
        order = ["project", "motor", "paper", "physical", "save"]
        if self.current_page_name in order:
            return order.index(self.current_page_name) + 1
        return 1

    # ============================================================
    # ================== NAVIGATION ==============================
    # ============================================================

    def _goto_page(self, page_name, add_to_history=True):
        if self.current_page is not None:
            self.main_layout.remove_widget(self.current_page)

        if add_to_history and page_name not in self.history:
            self.history.append(page_name)

        self.current_page_name = page_name

        # ---- IMPORTANT: pass is_first_page / is_last_page to __init__ ----
        is_first = (page_name == "project")
        is_last = (page_name == "save")

        page = self._create_page(page_name, is_first, is_last)
        if page is None:
            show_error("Unknown page: " + page_name, 3)
            return

        try:
            page.load_data(self.collected_data)
        except Exception as e:
            debug_logger.log_error("WIZARD_LOAD_PAGE_FAIL", e, "Wizard")

        if page_name == "save" and hasattr(page, "set_default_filename"):
            page.set_default_filename(
                self.collected_data.get("project_name", ""),
                self.collected_data.get("nominal_power", ""),
                self.collected_data.get("poles", 4),
            )

        page.on_next = self._on_next
        page.on_back = self._on_back
        page.on_cancel = self._on_cancel
        page.on_save = self._on_save
        page.on_open = self._on_open
        page.on_physical = self._on_physical

        # Special: on OPEN page, the "Open" button loads the file
        if page_name == "open":
            page.on_open = lambda p: self._finalize_open(p)

        self.current_page = page
        self.main_layout.add_widget(page)

    def _create_page(self, page_name, is_first, is_last):
        # Every page gets the flags passed to __init__
        common = {
            'mode': 'wizard',
            'is_first_page': is_first,
            'is_last_page': is_last,
        }
        if page_name == "project":
            return PageProject(**common)
        elif page_name == "motor":
            return PageMotor(**common)
        elif page_name == "paper":
            return PagePaper(**common)
        elif page_name == "physical":
            return PagePhysical(**common)
        elif page_name == "save":
            return PageSave(**common)
        elif page_name == "open":
            # Special: PageSave in open_mode
            return PageSave(open_mode=True, **common)
        return None

    # ============================================================
    # ================== ACTIONS =================================
    # ============================================================

    def _on_next(self, page):
        if not self._validate_and_collect(page):
            return
        self._save_draft()
        name = self.current_page_name
        if name == "project":
            self._goto_page("motor")
        elif name == "motor":
            self._goto_page("paper")
        elif name == "paper":
            self._goto_page("save")
        elif name == "physical":
            self._goto_page("save")

    def _on_back(self, page):
        if not self._collect_data(page):
            return
        if self.history and self.history[-1] == self.current_page_name:
            self.history.pop()
        if self.history:
            prev = self.history[-1]
            self.history.pop()
            self._goto_page(prev)

    def _on_cancel(self, page):
        def do_cancel():
            self.draft.delete()
            self.auto_dismiss = True
            self.dismiss()
            if self.on_cancel:
                self.on_cancel()

        show_confirm(
            'Cancel project creation?\n'
            'All unsaved data will be lost.',
            on_confirm=do_cancel,
            title='CANCEL WIZARD'
        )

    def _on_physical(self, page):
        if not self._validate_and_collect(page):
            return
        self._save_draft()
        self._goto_page("physical")

    def _on_open(self, page):
        """Open button on PROJECT page - switch to open page."""
        # Collect current data first
        self._collect_data(page)
        self._goto_page("open")

    def _on_save(self, page):
        if not self._validate_and_collect(page):
            return

        save_data = page.get_data()
        path = save_data.get('save_path', '').strip()
        filename = save_data.get('save_filename', '').strip()

        if not path or not filename:
            show_error('Please specify path and filename', 2)
            return

        if not filename.endswith('.json'):
            filename += '.json'

        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            show_error('Cannot create folder: ' + str(e), 3)
            return

        folder_name = filename[:-5]
        project_folder = os.path.join(path, folder_name)
        full_path = os.path.join(project_folder, filename)

        if os.path.exists(full_path):
            def do_overwrite():
                self._finalize_save(full_path, filename, project_folder)
            show_confirm(
                f'Project "{folder_name}" already exists.\n'
                'Do you want to overwrite it?',
                on_confirm=do_overwrite,
                title='OVERWRITE'
            )
            return

        self._finalize_save(full_path, filename, project_folder)

    def _finalize_open(self, page):
        """Open button on OPEN page - load the selected project file."""
        if not page.validate():
            show_error('Please specify a valid path and filename', 2)
            return

        data = page.get_data()
        full_path = data.get('full_path', '')
        if not full_path or not os.path.exists(full_path):
            show_error('File not found: ' + full_path, 3)
            return

        loaded = json_manager.load_project_data(full_path)
        if not loaded:
            show_error('Failed to load project', 3)
            return

        filename = os.path.basename(full_path)
        folder = os.path.dirname(full_path)

        json_manager.update_project_settings(
            file_path=full_path,
            file_name=filename,
            directory=folder,
            paper_size=loaded.get('paper_size', 'A4'),
            orientation=loaded.get('orientation', 'Portrait'),
        )

        self.draft.delete()
        show_success('Loaded: ' + filename, 2)
        self.auto_dismiss = True
        self.dismiss()

        if self.on_finish:
            self.on_finish(full_path, loaded)

    def _finalize_save(self, full_path, filename, project_folder):
        self._ensure_full_structure()
        try:
            os.makedirs(project_folder, exist_ok=True)
            self.collected_data['file_path'] = full_path
            self.collected_data['directory'] = project_folder
            self.collected_data['version'] = "0.1.4"

            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, indent=4,
                          ensure_ascii=False)

            self.draft.delete()

            json_manager.load_project_data(full_path)
            json_manager.update_project_settings(
                file_path=full_path,
                file_name=filename,
                directory=project_folder,
                paper_size=self.collected_data.get('paper_size', 'A4'),
                orientation=self.collected_data.get('orientation', 'Portrait'),
            )

            show_success('Saved: ' + filename, 2)
            self.auto_dismiss = True
            self.dismiss()

            if self.on_finish:
                self.on_finish(full_path, self.collected_data)
        except Exception as e:
            show_error('Failed to save: ' + str(e), 3)

    # ============================================================
    # ================== DATA COLLECTION =========================
    # ============================================================

    def _collect_data(self, page):
        try:
            data = page.get_data()
            if data:
                self.collected_data.update(data)
            return True
        except Exception as e:
            debug_logger.log_error("WIZARD_COLLECT_FAIL", e, "Wizard")
            return False

    def _validate_and_collect(self, page):
        try:
            if not page.validate():
                show_error('Please fix the highlighted fields', 2)
                return False
        except Exception as e:
            show_error('Validation error: ' + str(e), 3)
            return False
        return self._collect_data(page)

    def _ensure_full_structure(self):
        data = self.collected_data
        for group_name in ['chained', 'concentric']:
            if group_name not in data:
                data[group_name] = {}
            g = data[group_name]
            defaults = {
                "winding_type": "two_layer",
                "coil_pattern": ("lap" if group_name == "chained"
                                  else "concentric"),
                "coil_span_chained": data.get("coil_span_chained", 11),
                "coil_span_concentric": data.get("coil_span_concentric", 9),
                "coils_per_pole_values": [],
                "wire_points": [],
                "main_diagram_shift_y": 0.0,
                "phase_diagram_shift_y": 0.0,
            }
            for k, v in defaults.items():
                if k not in g:
                    g[k] = v
            conn_key = ("chained_connection" if group_name == "chained"
                        else "concentric_connection")
            if conn_key not in g:
                g[conn_key] = {
                    "junction_points": [],
                    "line_segments": [],
                    "phase_endpoints": {},
                }
