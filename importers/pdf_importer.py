"""
================================================================================
File: importers/pdf_importer.py
Purpose: PDF importer stub.
Version: 0.1.1
================================================================================
"""

from importers.base_importer import BaseImporter


class PdfImporter(BaseImporter):

    format_id = 'pdf'
    display_name = 'PDF'

    def supported_formats(self):
        return ['pdf']

    def load(self, filepath):
        return {'lines': [], 'points': []}