"""
================================================================================
File: importers/dxf_importer.py
Purpose: DXF importer stub.
Version: 0.1.1
================================================================================
"""

from importers.base_importer import BaseImporter


class DxfImporter(BaseImporter):

    format_id = 'dxf'
    display_name = 'DXF'

    def supported_formats(self):
        return ['dxf']

    def load(self, filepath):
        return {'lines': [], 'points': []}