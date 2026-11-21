"""
================================================================================
File: importers/svg_importer.py
Purpose: SVG importer stub.
Version: 0.1.1
================================================================================
"""

from importers.base_importer import BaseImporter


class SvgImporter(BaseImporter):

    format_id = 'svg'
    display_name = 'SVG'

    def supported_formats(self):
        return ['svg']

    def load(self, filepath):
        return {'lines': [], 'points': []}