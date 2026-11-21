"""
================================================================================
File: managers/docs_manager.py
Purpose: Read docs/index.json and load markdown files on demand.
Version: 0.1.1
================================================================================
"""

import os
import json


class DocsManager:

    def __init__(self, docs_dir):
        self.docs_dir = docs_dir
        self.index = None
        self._load_index()

    def _load_index(self):
        path = os.path.join(self.docs_dir, 'index.json')
        if not os.path.exists(path):
            self.index = {'categories': [], 'versions': []}
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        except Exception:
            self.index = {'categories': [], 'versions': []}

    def get_categories(self):
        return self.index.get('categories', [])

    def get_versions(self):
        return self.index.get('versions', [])

    def get_current_version(self):
        return self.index.get('current_version', '')

    def load_markdown(self, relative_path):
        path = os.path.join(self.docs_dir, relative_path)
        if not os.path.exists(path):
            return ''
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ''

    def markdown_to_items(self, text):
        """
        Convert simple markdown to a list of label-dicts for the viewer.
        Supported: # H1, ## H2, ### H3, - item, **bold** (strip markers),
        blank lines.
        """
        items = []
        if not text:
            return items
        for raw in text.split('\n'):
            line = raw.rstrip()
            if not line:
                items.append({'text': '', 'font_size': '6sp',
                              'color': [0, 0, 0, 1]})
                continue
            if line.startswith('### '):
                items.append({
                    'text': line[4:],
                    'font_size': '14sp', 'bold': True,
                    'color': [0.1, 0.3, 0.55, 1],
                })
            elif line.startswith('## '):
                items.append({
                    'text': line[3:],
                    'font_size': '15sp', 'bold': True,
                    'color': [0.1, 0.3, 0.55, 1],
                })
            elif line.startswith('# '):
                items.append({
                    'text': line[2:],
                    'font_size': '17sp', 'bold': True,
                    'color': [0, 0, 0, 1],
                })
            elif line.startswith('- ') or line.startswith('* '):
                text_line = line[2:].replace('**', '')
                items.append({
                    'text': '   ' + chr(0x2022) + ' ' + text_line,
                    'font_size': '13sp',
                    'color': [0, 0, 0, 1],
                })
            else:
                items.append({
                    'text': line.replace('**', ''),
                    'font_size': '13sp',
                    'color': [0, 0, 0, 1],
                })
        return items