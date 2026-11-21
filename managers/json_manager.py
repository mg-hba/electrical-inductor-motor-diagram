"""
================================================================================
File: managers/json_manager.py
Purpose: Central config + project data manager.
         coils_per_pole_values at ROOT.
         main_diagram_shift_y / phase_diagram_shift_y inside active group.
Version: 0.1.3
================================================================================
"""

import os
import json

from utils.constants import (
    MAIN_DIAGRAM_SHIFT_Y_DEFAULT,
    PHASE_DIAGRAM_SHIFT_Y_DEFAULT,
)


class JSONManager:

    CONFIG_FILE = 'config.json'

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self):
        self.config = self._load_config()
        self.project_data = None
        self.current_project_file = None
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########_load_config#############
    ###################################
    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as file_handle:
                    loaded = json.load(file_handle)
                    return self._cleanup_and_merge(loaded)
            except Exception:
                return self._get_default_config()
        default = self._get_default_config()
        self._write_config(default)
        return default
    ###################################
    ##########end of _load_config#####
    ###################################

    ###################################
    ##########_cleanup_and_merge#######
    ###################################
    def _cleanup_and_merge(self, loaded):
        if 'project_settings' in loaded:
            del loaded['project_settings']
        default = self._get_default_config()
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in loaded[key]:
                        loaded[key][sub_key] = sub_value
        return loaded
    ###################################
    ##########end of _cleanup_and_merge
    ###################################

    ###################################
    ##########_write_config############
    ###################################
    def _write_config(self, data):
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as file_handle:
                json.dump(data, file_handle, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
    ###################################
    ##########end of _write_config####
    ###################################

    ###################################
    ##########_get_default_config######
    ###################################
    def _get_default_config(self):
        return {
            "version": "0.1.3",
            "last_updated": "2026-11-06",
            "spinner_settings": {
                "bg_color": [0.98, 0.98, 0.98, 0.6],
                "text_color": [0, 0, 0, 1],
                "height": 52,
                "font_size": 13,
            },
            "window_settings": {
                "header_bg_color": [0.15, 0.35, 0.6, 1],
                "main_bg_color": [0.95, 0.95, 0.95, 1],
                "button_bg_color": [0.2, 0.6, 0.85, 1],
                "button_text_color": [1, 1, 1, 1],
                "error_bg_color": [1, 0.8, 0.8, 1],
            },
            "app_settings": {
                "default_directory": "",
                "current_file_path": "",
                "current_file_name": "",
                "current_directory": "",
            },
            "grid_settings": {
                "cell_size": 10,
                "zoom_min": 0.02,
                "zoom_max": 100.0,
            },
            "font_settings": {
                "main_font_size": 34,
                "header_font_size": 16,
                "info_font_size": 13,
                "big_button_font": 20,
            },
            "connection_settings": {
                "touch_tolerance": 80,
                "pull_step_default": 1,
                "pull_step_min": 1,
                "pull_step_max": 5,
            },
        }
    ###################################
    ##########end of _get_default_config
    ###################################

    ###################################
    ##########save_config##############
    ###################################
    def save_config(self):
        return self._write_config(self.config)
    ###################################
    ##########end of save_config######
    ###################################

    ###################################
    ##########get_spinner_bg_color#####
    ###################################
    def get_spinner_bg_color(self):
        return self.config.get("spinner_settings", {}).get(
            "bg_color", [0.98, 0.98, 0.98, 0.6]
        )
    ###################################
    ##########end of get_spinner_bg_color
    ###################################

    ###################################
    ##########set_spinner_bg_color#####
    ###################################
    def set_spinner_bg_color(self, color):
        self.config.setdefault("spinner_settings", {})["bg_color"] = color
        self.save_config()
    ###################################
    ##########end of set_spinner_bg_color
    ###################################

    ###################################
    ##########get_spinner_text_color###
    ###################################
    def get_spinner_text_color(self):
        return self.config.get("spinner_settings", {}).get(
            "text_color", [0, 0, 0, 1]
        )
    ###################################
    ##########end of get_spinner_text_color
    ###################################

    ###################################
    ##########set_spinner_text_color###
    ###################################
    def set_spinner_text_color(self, color):
        self.config.setdefault("spinner_settings", {})["text_color"] = color
        self.save_config()
    ###################################
    ##########end of set_spinner_text_color
    ###################################

    ###################################
    ##########get_spinner_height#######
    ###################################
    def get_spinner_height(self):
        return self.config.get("spinner_settings", {}).get("height", 52)
    ###################################
    ##########end of get_spinner_height
    ###################################

    ###################################
    ##########set_spinner_height#######
    ###################################
    def set_spinner_height(self, height):
        self.config.setdefault("spinner_settings", {})["height"] = height
        self.save_config()
    ###################################
    ##########end of set_spinner_height
    ###################################

    ###################################
    ##########get_spinner_font_size####
    ###################################
    def get_spinner_font_size(self):
        return self.config.get("spinner_settings", {}).get("font_size", 13)
    ###################################
    ##########end of get_spinner_font_size
    ###################################

    ###################################
    ##########set_spinner_font_size####
    ###################################
    def set_spinner_font_size(self, size):
        self.config.setdefault("spinner_settings", {})["font_size"] = size
        self.save_config()
    ###################################
    ##########end of set_spinner_font_size
    ###################################

    ###################################
    ##########get_header_bg_color######
    ###################################
    def get_header_bg_color(self):
        return self.config.get("window_settings", {}).get(
            "header_bg_color", [0.15, 0.35, 0.6, 1]
        )
    ###################################
    ##########end of get_header_bg_color
    ###################################

    ###################################
    ##########get_main_bg_color########
    ###################################
    def get_main_bg_color(self):
        return self.config.get("window_settings", {}).get(
            "main_bg_color", [0.95, 0.95, 0.95, 1]
        )
    ###################################
    ##########end of get_main_bg_color
    ###################################

    ###################################
    ##########get_button_bg_color######
    ###################################
    def get_button_bg_color(self):
        return self.config.get("window_settings", {}).get(
            "button_bg_color", [0.2, 0.6, 0.85, 1]
        )
    ###################################
    ##########end of get_button_bg_color
    ###################################

    ###################################
    ##########get_button_text_color####
    ###################################
    def get_button_text_color(self):
        return self.config.get("window_settings", {}).get(
            "button_text_color", [1, 1, 1, 1]
        )
    ###################################
    ##########end of get_button_text_color
    ###################################

    ###################################
    ##########get_error_bg_color#######
    ###################################
    def get_error_bg_color(self):
        return self.config.get("window_settings", {}).get(
            "error_bg_color", [1, 0.8, 0.8, 1]
        )
    ###################################
    ##########end of get_error_bg_color
    ###################################

    ###################################
    ##########get_default_directory####
    ###################################
    def get_default_directory(self):
        return self.config.get("app_settings", {}).get(
            "default_directory", ""
        )
    ###################################
    ##########end of get_default_directory
    ###################################

    ###################################
    ##########set_default_directory####
    ###################################
    def set_default_directory(self, path):
        self.config.setdefault("app_settings", {})["default_directory"] = path
        self.save_config()
    ###################################
    ##########end of set_default_directory
    ###################################

    ###################################
    ##########get_current_project_path#
    ###################################
    def get_current_project_path(self):
        return self.config.get("app_settings", {}).get(
            "current_file_path", ""
        )
    ###################################
    ##########end of get_current_project_path
    ###################################

    ###################################
    ##########get_current_project_name#
    ###################################
    def get_current_project_name(self):
        return self.config.get("app_settings", {}).get(
            "current_file_name", ""
        )
    ###################################
    ##########end of get_current_project_name
    ###################################

    ###################################
    ##########get_current_directory####
    ###################################
    def get_current_directory(self):
        return self.config.get("app_settings", {}).get(
            "current_directory", ""
        )
    ###################################
    ##########end of get_current_directory
    ###################################

    ###################################
    ##########has_project_loaded#######
    ###################################
    def has_project_loaded(self):
        path = self.get_current_project_path()
        return bool(path) and os.path.exists(path)
    ###################################
    ##########end of has_project_loaded
    ###################################

    ###################################
    ##########update_project_settings##
    ###################################
    def update_project_settings(self, file_path, file_name, directory,
                                 paper_size=None, orientation=None):
        app_settings = self.config.setdefault("app_settings", {})
        app_settings["current_file_path"] = file_path
        app_settings["current_file_name"] = file_name
        app_settings["current_directory"] = directory
        self.current_project_file = file_path
        self.save_config()
    ###################################
    ##########end of update_project_settings
    ###################################

    ###################################
    ##########get_project_paper_size###
    ###################################
    def get_project_paper_size(self):
        if self.project_data is None:
            return None
        return self.project_data.get('paper_size', None)
    ###################################
    ##########end of get_project_paper_size
    ###################################

    ###################################
    ##########get_project_orientation##
    ###################################
    def get_project_orientation(self):
        if self.project_data is None:
            return None
        return self.project_data.get('orientation', None)
    ###################################
    ##########end of get_project_orientation
    ###################################

    ###################################
    ##########get_table_bg_alpha#######
    ###################################
    def get_table_bg_alpha(self):
        return self.config.get("table_settings", {}).get("bg_alpha", 25)
    ###################################
    ##########end of get_table_bg_alpha
    ###################################

    ###################################
    ##########set_table_bg_alpha#######
    ###################################
    def set_table_bg_alpha(self, alpha):
        self.config.setdefault("table_settings", {})["bg_alpha"] = alpha
        self.save_config()
    ###################################
    ##########end of set_table_bg_alpha
    ###################################

    ###################################
    ##########get_table_enabled########
    ###################################
    def get_table_enabled(self):
        return self.config.get("table_settings", {}).get("enabled", True)
    ###################################
    ##########end of get_table_enabled
    ###################################

    ###################################
    ##########set_table_enabled########
    ###################################
    def set_table_enabled(self, enabled):
        self.config.setdefault("table_settings", {})["enabled"] = enabled
        self.save_config()
    ###################################
    ##########end of set_table_enabled
    ###################################

    ###################################
    ##########get_slots_bg_alpha#######
    ###################################
    def get_slots_bg_alpha(self):
        return self.config.get("slots_settings", {}).get("bg_alpha", 0)
    ###################################
    ##########end of get_slots_bg_alpha
    ###################################

    ###################################
    ##########set_slots_bg_alpha#######
    ###################################
    def set_slots_bg_alpha(self, alpha):
        self.config.setdefault("slots_settings", {})["bg_alpha"] = alpha
        self.save_config()
    ###################################
    ##########end of set_slots_bg_alpha
    ###################################

    ###################################
    ##########get_slots_enabled########
    ###################################
    def get_slots_enabled(self):
        return self.config.get("slots_settings", {}).get("enabled", True)
    ###################################
    ##########end of get_slots_enabled
    ###################################

    ###################################
    ##########set_slots_enabled########
    ###################################
    def set_slots_enabled(self, enabled):
        self.config.setdefault("slots_settings", {})["enabled"] = enabled
        self.save_config()
    ###################################
    ##########end of set_slots_enabled
    ###################################

    ###################################
    ##########get_active_group_name####
    ###################################
    def get_active_group_name(self):
        if self.project_data is None:
            return "chained"
        pattern = self.project_data.get('active_pattern', 'lap')
        return "concentric" if pattern == "concentric" else "chained"
    ###################################
    ##########end of get_active_group_name
    ###################################

    ###################################
    ##########get_connection_key#######
    ###################################
    def get_connection_key(self):
        return (
            "concentric_connection"
            if self.get_active_group_name() == "concentric"
            else "chained_connection"
        )
    ###################################
    ##########end of get_connection_key
    ###################################

    ###################################
    ##########ensure_group_structure###
    ###################################
    def ensure_group_structure(self):
        if self.project_data is None:
            return
        for group_name in ['chained', 'concentric']:
            if (group_name not in self.project_data or
                    not isinstance(self.project_data[group_name], dict)):
                self.project_data[group_name] = {}
            group_data = self.project_data[group_name]
            defaults = {
                "winding_type": "two_layer",
                "coil_pattern": ("lap" if group_name == "chained"
                                  else "concentric"),
                "coil_span_chained": 11,
                "coil_span_concentric": 9,
                "coils_per_pole_values": [],
                "wire_points": [],
                "main_diagram_shift_y": MAIN_DIAGRAM_SHIFT_Y_DEFAULT,
                "phase_diagram_shift_y": PHASE_DIAGRAM_SHIFT_Y_DEFAULT,
            }
            for key, value in defaults.items():
                if key not in group_data:
                    group_data[key] = value
            connection_key = (
                "chained_connection" if group_name == "chained"
                else "concentric_connection"
            )
            if (connection_key not in group_data or
                    not isinstance(group_data[connection_key], dict)):
                group_data[connection_key] = {
                    "junction_points": [],
                    "line_segments": [],
                    "phase_endpoints": {},
                }
            else:
                connection_data = group_data[connection_key]
                connection_data.setdefault("junction_points", [])
                connection_data.setdefault("line_segments", [])
                connection_data.setdefault("phase_endpoints", {})
    ###################################
    ##########end of ensure_group_structure
    ###################################

    ###################################
    ##########get_project_field########
    ###################################
    def get_project_field(self, key, default=None):
        if self.project_data is None:
            return default
        return self.project_data.get(key, default)
    ###################################
    ##########end of get_project_field
    ###################################

    ###################################
    ##########set_project_field########
    ###################################
    def set_project_field(self, key, value):
        if self.project_data is not None:
            self.project_data[key] = value
    ###################################
    ##########end of set_project_field
    ###################################

    ###################################
    ##########get_group_field##########
    ###################################
    def get_group_field(self, key, default=None):
        if self.project_data is None:
            return default
        return self.project_data.get(
            self.get_active_group_name(), {}
        ).get(key, default)
    ###################################
    ##########end of get_group_field##
    ###################################

    ###################################
    ##########set_group_field##########
    ###################################
    def set_group_field(self, key, value):
        if self.project_data is None:
            return
        group = self.get_active_group_name()
        if group not in self.project_data:
            self.project_data[group] = {}
        self.project_data[group][key] = value
    ###################################
    ##########end of set_group_field##
    ###################################

    ###################################
    ##########get_main_diagram_shift_y
    ###################################
    def get_main_diagram_shift_y(self):
        return self.get_group_field('main_diagram_shift_y',
                                     MAIN_DIAGRAM_SHIFT_Y_DEFAULT)
    ###################################
    ##########end of get_main_diagram_shift_y
    ###################################

    ###################################
    ##########set_main_diagram_shift_y
    ###################################
    def set_main_diagram_shift_y(self, value):
        self.set_group_field('main_diagram_shift_y', float(value))
        self.update_project_field('main_diagram_shift_y', float(value))
    ###################################
    ##########end of set_main_diagram_shift_y
    ###################################

    ###################################
    ##########get_phase_diagram_shift_y
    ###################################
    def get_phase_diagram_shift_y(self):
        return self.get_group_field('phase_diagram_shift_y',
                                     PHASE_DIAGRAM_SHIFT_Y_DEFAULT)
    ###################################
    ##########end of get_phase_diagram_shift_y
    ###################################

    ###################################
    ##########set_phase_diagram_shift_y
    ###################################
    def set_phase_diagram_shift_y(self, value):
        self.set_group_field('phase_diagram_shift_y', float(value))
        self.update_project_field('phase_diagram_shift_y', float(value))
    ###################################
    ##########end of set_phase_diagram_shift_y
    ###################################

    ###################################
    ##########get_coils_per_pole_values
    ###################################
    def get_coils_per_pole_values(self):
        if self.project_data is None:
            return []
        return self.project_data.get('coils_per_pole_values', [])
    ###################################
    ##########end of get_coils_per_pole_values
    ###################################

    ###################################
    ##########set_coils_per_pole_values
    ###################################
    def set_coils_per_pole_values(self, values):
        if self.project_data is None:
            return
        self.project_data['coils_per_pole_values'] = values
        self.update_project_field('coils_per_pole_values', values)
    ###################################
    ##########end of set_coils_per_pole_values
    ###################################

    ###################################
    ##########get_connection_data######
    ###################################
    def get_connection_data(self):
        if self.project_data is None:
            return {}
        group = self.get_active_group_name()
        group_data = self.project_data.get(group, {})
        return group_data.get(self.get_connection_key(), {})
    ###################################
    ##########end of get_connection_data
    ###################################

    ###################################
    ##########set_connection_data######
    ###################################
    def set_connection_data(self, data):
        if self.project_data is None:
            return
        group = self.get_active_group_name()
        if group not in self.project_data:
            self.project_data[group] = {}
        self.project_data[group][self.get_connection_key()] = data
    ###################################
    ##########end of set_connection_data
    ###################################

    ###################################
    ##########get_last_wire_points#####
    ###################################
    def get_last_wire_points(self):
        if self.project_data is None:
            return []
        return self.project_data.get(
            self.get_active_group_name(), {}
        ).get('wire_points', [])
    ###################################
    ##########end of get_last_wire_points
    ###################################

    ###################################
    ##########set_last_wire_points#####
    ###################################
    def set_last_wire_points(self, value):
        if self.project_data is None:
            return
        group = self.get_active_group_name()
        self.project_data.setdefault(group, {})['wire_points'] = value
    ###################################
    ##########end of set_last_wire_points
    ###################################

    ###################################
    ##########get_last_junction_points
    ###################################
    def get_last_junction_points(self):
        return self.get_connection_data().get('junction_points', [])
    ###################################
    ##########end of get_last_junction_points
    ###################################

    ###################################
    ##########set_last_junction_points
    ###################################
    def set_last_junction_points(self, value):
        connection_data = self.get_connection_data()
        connection_data['junction_points'] = value
        self.set_connection_data(connection_data)
    ###################################
    ##########end of set_last_junction_points
    ###################################

    ###################################
    ##########get_last_line_segments##
    ###################################
    def get_last_line_segments(self):
        return self.get_connection_data().get('line_segments', [])
    ###################################
    ##########end of get_last_line_segments
    ###################################

    ###################################
    ##########set_last_line_segments##
    ###################################
    def set_last_line_segments(self, value):
        connection_data = self.get_connection_data()
        connection_data['line_segments'] = value
        self.set_connection_data(connection_data)
    ###################################
    ##########end of set_last_line_segments
    ###################################

    ###################################
    ##########get_last_phase_endpoints
    ###################################
    def get_last_phase_endpoints(self):
        return self.get_connection_data().get('phase_endpoints', {})
    ###################################
    ##########end of get_last_phase_endpoints
    ###################################

    ###################################
    ##########set_last_phase_endpoints
    ###################################
    def set_last_phase_endpoints(self, value):
        connection_data = self.get_connection_data()
        connection_data['phase_endpoints'] = value
        self.set_connection_data(connection_data)
    ###################################
    ##########end of set_last_phase_endpoints
    ###################################

    ###################################
    ##########get_active_pattern#######
    ###################################
    def get_active_pattern(self):
        if self.project_data is None:
            return "lap"
        return self.project_data.get('active_pattern', 'lap')
    ###################################
    ##########end of get_active_pattern
    ###################################

    ###################################
    ##########set_active_pattern#######
    ###################################
    def set_active_pattern(self, pattern):
        if self.project_data is not None:
            self.project_data['active_pattern'] = pattern
    ###################################
    ##########end of set_active_pattern
    ###################################

    ###################################
    ##########get_last_coil_pattern####
    ###################################
    def get_last_coil_pattern(self):
        return self.get_active_pattern()
    ###################################
    ##########end of get_last_coil_pattern
    ###################################

    ###################################
    ##########set_last_coil_pattern####
    ###################################
    def set_last_coil_pattern(self, pattern):
        self.set_active_pattern(pattern)
    ###################################
    ##########end of set_last_coil_pattern
    ###################################

    ###################################
    ##########get_group_coil_span_chained
    ###################################
    def get_group_coil_span_chained(self):
        return self.get_group_field('coil_span_chained', 11)
    ###################################
    ##########end of get_group_coil_span_chained
    ###################################

    ###################################
    ##########set_group_coil_span_chained
    ###################################
    def set_group_coil_span_chained(self, value):
        self.set_group_field('coil_span_chained', value)
    ###################################
    ##########end of set_group_coil_span_chained
    ###################################

    ###################################
    ##########get_group_coil_span_concentric
    ###################################
    def get_group_coil_span_concentric(self):
        return self.get_group_field('coil_span_concentric', 9)
    ###################################
    ##########end of get_group_coil_span_concentric
    ###################################

    ###################################
    ##########set_group_coil_span_concentric
    ###################################
    def set_group_coil_span_concentric(self, value):
        self.set_group_field('coil_span_concentric', value)
    ###################################
    ##########end of set_group_coil_span_concentric
    ###################################

    ###################################
    ##########get_last_coil_span_chained
    ###################################
    def get_last_coil_span_chained(self):
        return str(self.get_group_coil_span_chained())
    ###################################
    ##########end of get_last_coil_span_chained
    ###################################

    ###################################
    ##########set_last_coil_span_chained
    ###################################
    def set_last_coil_span_chained(self, value):
        try:
            self.set_group_coil_span_chained(int(value))
        except Exception:
            pass
    ###################################
    ##########end of set_last_coil_span_chained
    ###################################

    ###################################
    ##########get_last_coil_span_concentric
    ###################################
    def get_last_coil_span_concentric(self):
        return str(self.get_group_coil_span_concentric())
    ###################################
    ##########end of get_last_coil_span_concentric
    ###################################

    ###################################
    ##########set_last_coil_span_concentric
    ###################################
    def set_last_coil_span_concentric(self, value):
        try:
            self.set_group_coil_span_concentric(int(value))
        except Exception:
            pass
    ###################################
    ##########end of set_last_coil_span_concentric
    ###################################

    ###################################
    ##########get_group_winding_type###
    ###################################
    def get_group_winding_type(self):
        return self.get_group_field('winding_type', 'two_layer')
    ###################################
    ##########end of get_group_winding_type
    ###################################

    ###################################
    ##########set_group_winding_type###
    ###################################
    def set_group_winding_type(self, value):
        self.set_group_field('winding_type', value)
    ###################################
    ##########end of set_group_winding_type
    ###################################

    ###################################
    ##########get_last_winding_type####
    ###################################
    def get_last_winding_type(self):
        if self.project_data is None:
            return 'two_layer'
        return self.get_group_winding_type()
    ###################################
    ##########end of get_last_winding_type
    ###################################

    ###################################
    ##########get_current_winding_type
    ###################################
    def get_current_winding_type(self):
        return self.get_last_winding_type()
    ###################################
    ##########end of get_current_winding_type
    ###################################

    ###################################
    ##########set_last_winding_type####
    ###################################
    def set_last_winding_type(self, value):
        self.set_group_winding_type(value)
    ###################################
    ##########end of set_last_winding_type
    ###################################

    ###################################
    ##########load_project_data########
    ###################################
    def load_project_data(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file_handle:
                self.project_data = json.load(file_handle)
            self.current_project_file = filepath
            if 'active_pattern' not in self.project_data:
                self.project_data['active_pattern'] = 'lap'
            self.ensure_group_structure()
            return self.project_data
        except Exception as error:
            print("load_project_data error: " + str(error))
            return None
    ###################################
    ##########end of load_project_data
    ###################################

    ###################################
    ##########update_project_field#####
    ###################################
    def update_project_field(self, key, value):
        filepath = self.get_current_project_path()
        if not filepath or not os.path.exists(filepath):
            return False
        try:
            with open(filepath, 'r', encoding='utf-8') as file_handle:
                data = json.load(file_handle)

            if key == 'coils_per_pole_values':
                data[key] = value
            elif key in ('junction_points', 'line_segments',
                          'phase_endpoints'):
                group = self.get_active_group_name()
                connection_key = (
                    'concentric_connection' if group == 'concentric'
                    else 'chained_connection'
                )
                data.setdefault(group, {})
                data[group].setdefault(connection_key, {})
                data[group][connection_key][key] = value
            elif key == 'wire_points':
                group = self.get_active_group_name()
                data.setdefault(group, {})
                data[group]['wire_points'] = value
            elif key in ('coil_span_chained', 'coil_span_concentric',
                         'coil_pattern', 'winding_type',
                         'main_diagram_shift_y', 'phase_diagram_shift_y'):
                group = self.get_active_group_name()
                data.setdefault(group, {})
                data[group][key] = value
            else:
                data[key] = value

            with open(filepath, 'w', encoding='utf-8') as file_handle:
                json.dump(data, file_handle, indent=4, ensure_ascii=False)
            self.project_data = data
            return True
        except Exception as error:
            print("update_project_field error: " + str(error))
            return False
    ###################################
    ##########end of update_project_field
    ###################################

    ###################################
    ##########save_project_data########
    ###################################
    def save_project_data(self, filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as file_handle:
                json.dump(data, file_handle, indent=4, ensure_ascii=False)
            self.project_data = data
            self.current_project_file = filepath
            return True
        except Exception:
            return False
    ###################################
    ##########end of save_project_data
    ###################################

    ###################################
    ##########clear_project_data#######
    ###################################
    def clear_project_data(self):
        self.project_data = None
        self.current_project_file = None
    ###################################
    ##########end of clear_project_data
    ###################################


json_manager = JSONManager()