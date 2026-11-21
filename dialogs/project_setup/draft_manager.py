"""
================================================================================
File: dialogs/project_setup/draft_manager.py
Purpose: Manage temporary draft file during wizard workflow.
         Draft is created on first Next click and deleted either on
         final Save (transferred to project file) or on Cancel.
Version: 0.1.4
================================================================================
"""

import os
import json
from datetime import datetime

from managers.debug_logger import debug_logger


class DraftManager:
    """Handles the draft.json file during wizard workflow."""

    DRAFTS_FOLDER = "drafts"
    DRAFT_FILENAME = "project_draft.json"

    def __init__(self, project_root):
        self.project_root = project_root
        self.drafts_dir = os.path.join(project_root, self.DRAFTS_FOLDER)
        self.draft_path = os.path.join(self.drafts_dir, self.DRAFT_FILENAME)

    # ============================================================
    # ================== SAVE / LOAD / DELETE ====================
    # ============================================================

    def save(self, data, current_page=1):
        """Save draft data with metadata."""
        try:
            os.makedirs(self.drafts_dir, exist_ok=True)
            now = datetime.now().isoformat(timespec='seconds')

            existing = self.load() or {}
            created = existing.get('created_at', now)

            payload = {
                'created_at': created,
                'updated_at': now,
                'current_page': int(current_page),
                'data': dict(data),
            }

            with open(self.draft_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)

            debug_logger.log_config("DRAFT_SAVE", self.draft_path,
                                    f"page={current_page}")
            return True
        except Exception as e:
            debug_logger.log_error("DRAFT_SAVE_FAIL", e, "DraftManager")
            return False

    def load(self):
        """Load draft dict, or None if not found/invalid."""
        if not os.path.exists(self.draft_path):
            return None
        try:
            with open(self.draft_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            debug_logger.log_error("DRAFT_LOAD_FAIL", e, "DraftManager")
            return None

    def get_data(self):
        """Return only the 'data' portion."""
        payload = self.load()
        if not payload:
            return {}
        return payload.get('data', {})

    def get_current_page(self):
        """Return saved page index (1-based), default 1."""
        payload = self.load()
        if not payload:
            return 1
        return payload.get('current_page', 1)

    def delete(self):
        """Delete the draft file."""
        if os.path.exists(self.draft_path):
            try:
                os.remove(self.draft_path)
                debug_logger.log_config("DRAFT_DELETE", self.draft_path)
                return True
            except Exception as e:
                debug_logger.log_error("DRAFT_DELETE_FAIL", e,
                                       "DraftManager")
                return False
        return True

    def exists(self):
        return os.path.exists(self.draft_path)

    # ============================================================
    # ================== TRANSFER TO PROJECT =====================
    # ============================================================

    def transfer_to_project(self, final_path):
        """
        Move draft data to the final project file.
        Returns True on success, then deletes the draft.
        """
        payload = self.load()
        if not payload:
            debug_logger.log_error("DRAFT_TRANSFER_NO_DRAFT",
                                   None, "DraftManager")
            return False

        data = payload.get('data', {})
        if not data:
            debug_logger.log_error("DRAFT_TRANSFER_EMPTY",
                                   None, "DraftManager")
            return False

        try:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            debug_logger.log_config("DRAFT_TRANSFER", final_path)
            self.delete()
            return True
        except Exception as e:
            debug_logger.log_error("DRAFT_TRANSFER_FAIL", e,
                                   "DraftManager")
            return False
