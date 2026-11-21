"""
================================================================================
File: importers/importer_registry.py
Purpose: Registry mapping file extensions to importers.
Version: 0.1.1
================================================================================
"""

from importers.svg_importer import SvgImporter
from importers.dxf_importer import DxfImporter
from importers.pdf_importer import PdfImporter
from importers.raster_importer import RasterImporter


class ImporterRegistry:

    _importers = {}

    @classmethod
    def initialize(cls):
        cls._importers = {}
        for imp_class in [SvgImporter, DxfImporter, PdfImporter, RasterImporter]:
            imp = imp_class()
            for ext in imp.supported_formats():
                cls._importers[ext.lower()] = imp

    @classmethod
    def get(cls, extension):
        if not cls._importers:
            cls.initialize()
        return cls._importers.get(extension.lower().lstrip('.'))

    @classmethod
    def all_extensions(cls):
        if not cls._importers:
            cls.initialize()
        return list(cls._importers.keys())


ImporterRegistry.initialize()


def get_importer(extension):
    return ImporterRegistry.get(extension)