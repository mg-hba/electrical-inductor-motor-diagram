"""
================================================================================
File: importers/base_importer.py
Purpose: Abstract base for importers (stub).
Version: 0.1.1
================================================================================
"""

from abc import ABC, abstractmethod


class BaseImporter(ABC):

    format_id = 'base'
    display_name = 'Base'

    @abstractmethod
    def supported_formats(self):
        pass

    @abstractmethod
    def load(self, filepath):
        pass