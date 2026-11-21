"""
================================================================================
File: importers/raster_importer.py
Purpose: Raster importer stub (PNG / JPG / EPS).
Version: 0.1.1
================================================================================
"""

from importers.base_importer import BaseImporter


class RasterImporter(BaseImporter):

    format_id = 'raster'
    display_name = 'Raster'

    def supported_formats(self):
        return ['png', 'jpg', 'jpeg', 'eps']

    def load(self, filepath):
        return {'lines': [], 'points': []}