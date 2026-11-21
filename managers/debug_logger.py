"""
================================================================================
File: managers/debug_logger.py
Purpose: Logging built on Python's standard logging with immediate flush
         and global exception hooks (Python + Kivy).
Version: 0.1.3.3
================================================================================
"""

import os
import sys
import json
import traceback
from datetime import datetime
from enum import Enum
import logging
from logging.handlers import RotatingFileHandler


class LogCategory(Enum):
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"
    TOUCH = "TOUCH"
    DRAW = "DRAW"
    EXPORT = "EXPORT"
    CONFIG = "CONFIG"
    PAPER = "PAPER"
    TABLE = "TABLE"
    PERFORMANCE = "PERFORMANCE"


class DebugLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        self._log_path = os.path.join(
            log_dir,
            'debug_' + datetime.now().strftime('%Y%m%d') + '.log'
        )
        self._config_path = os.path.join(log_dir, 'log_config.json')
        self._enabled = self._load_config()
        self._hooks_installed = False

        self._logger = logging.getLogger('MWD')
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._logger.handlers.clear()
        self._logger.filters.clear()

        fmt = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        self._file_handler = RotatingFileHandler(
            self._log_path,
            maxBytes=5000000,
            backupCount=5,
            encoding='utf-8'
        )
        self._file_handler.setLevel(logging.DEBUG)
        self._file_handler.setFormatter(fmt)
        self._logger.addHandler(self._file_handler)

        self._write_raw(logging.INFO, "=== DEBUG SESSION STARTED ===")

    def _flush(self):
        for h in self._logger.handlers:
            try:
                h.flush()
            except Exception:
                pass

    def _write_raw(self, level, msg):
        self._logger.log(level, msg)
        self._flush()

    def _load_config(self):
        default = {c.value: True for c in LogCategory}
        default[LogCategory.TOUCH.value] = False
        default[LogCategory.PERFORMANCE.value] = False
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    loaded = cfg.get('enabled_categories', {})
                    default.update(loaded)
                    return default
            except Exception:
                return default
        self._save_config(default)
        return default

    def _save_config(self, data=None):
        if data is None:
            data = self._enabled
        try:
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump({'enabled_categories': data}, f, indent=4)
        except Exception:
            pass

    def set_category_enabled(self, category, enabled):
        if isinstance(category, LogCategory):
            category = category.value
        self._enabled[category] = bool(enabled)
        self._save_config()

    def is_category_enabled(self, category):
        if isinstance(category, LogCategory):
            category = category.value
        return self._enabled.get(category, True)

    def get_enabled_categories(self):
        return dict(self._enabled)

    def _log(self, category, level, message, source=""):
        if isinstance(category, LogCategory):
            category = category.value
        if not self.is_category_enabled(category):
            return
        prefix = f"[{category}]"
        if source:
            prefix += f" [{source}]"
        self._write_raw(level, f"{prefix} {message}")

    def log_system(self, message, source=""):
        self._log(LogCategory.SYSTEM, logging.INFO, message, source)

    def log_error(self, message, exception=None, source=""):
        self._log(LogCategory.ERROR, logging.ERROR, message, source)
        if exception is not None:
            if isinstance(exception, BaseException):
                tb = "".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                ).strip()
                if tb and tb != "NoneType: None":
                    self._log(LogCategory.ERROR, logging.ERROR,
                              "TRACEBACK:\n" + tb, source)
                else:
                    self._log(LogCategory.ERROR, logging.ERROR,
                              "EX: " + repr(exception), source)
            else:
                self._log(LogCategory.ERROR, logging.ERROR,
                          "EX: " + str(exception), source)

    def log_touch(self, action, touch_pos, source=""):
        self._log(LogCategory.TOUCH, logging.DEBUG,
                  f"{action}: {touch_pos}", source)

    def log_draw(self, component, details, source=""):
        self._log(LogCategory.DRAW, logging.DEBUG,
                  f"{component}: {details}", source)

    def log_export(self, fmt, filepath, success, source=""):
        status = "OK" if success else "FAIL"
        self._log(LogCategory.EXPORT, logging.INFO,
                  f"{fmt} {status}: {filepath}", source)

    def log_config(self, action, key, value=None, source=""):
        v = f" = {value}" if value is not None else ""
        self._log(LogCategory.CONFIG, logging.INFO,
                  f"{action}: {key}{v}", source)

    def log_paper(self, paper, orient, w, h, source=""):
        self._log(LogCategory.PAPER, logging.INFO,
                  f"{paper} {orient} ({w}x{h} mm)", source)

    def log_table(self, action, details, source=""):
        self._log(LogCategory.TABLE, logging.DEBUG,
                  f"{action}: {details}", source)

    def log_performance(self, op, ms, source=""):
        self._log(LogCategory.PERFORMANCE, logging.INFO,
                  f"{op}: {ms:.2f}ms", source)

    def install_exception_hooks(self):
        """Capture uncaught Python exceptions and Kivy error logs."""
        if self._hooks_installed:
            return
        self._hooks_installed = True

        orig_excepthook = sys.excepthook

        def _global_excepthook(exc_type, exc_value, exc_tb):
            tb_str = "".join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            ).strip()
            self._log(
                LogCategory.ERROR,
                logging.ERROR,
                f"UNCAUGHT_EXCEPTION:\n{tb_str}",
                "GlobalHook"
            )
            if orig_excepthook:
                orig_excepthook(exc_type, exc_value, exc_tb)

        sys.excepthook = _global_excepthook

        try:
            from kivy.logger import Logger as KivyLogger

            class _KivyErrorForwarder(logging.Handler):
                def __init__(self, target_logger):
                    super().__init__(level=logging.ERROR)
                    self.target_logger = target_logger

                def emit(self, record):
                    try:
                        msg = self.format(record)
                        self.target_logger.log_error(msg, source="Kivy")
                    except Exception:
                        pass

            KivyLogger.addHandler(_KivyErrorForwarder(self))
        except Exception:
            pass

    def get_log_file_path(self):
        return self._log_path

    def get_log_content(self):
        try:
            with open(self._log_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return "Unable to read log file"

    def close(self):
        self._write_raw(logging.INFO, "=== DEBUG SESSION ENDED ===")
        for h in self._logger.handlers:
            try:
                h.close()
            except Exception:
                pass


debug_logger = DebugLogger()
debug_logger.install_exception_hooks()
