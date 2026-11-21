"""
================================================================================
File: core/connection/layer_history.py
Purpose: Undo / Redo / Reset history management for connection layer.
Version: 0.1.1
================================================================================
"""

from utils.constants import UNDO_STACK_SIZE


class HistoryManager:

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []
        self._initial_snapshot = None

    # ============================================================
    # ================== INITIAL SNAPSHOT =======================
    # ============================================================

    def capture_initial(self, snapshot):
        self._initial_snapshot = snapshot
        self._undo_stack.clear()
        self._redo_stack.clear()

    # ============================================================
    # ================== PUSH / POP =============================
    # ============================================================

    def push(self, before_snapshot, after_snapshot):
        if before_snapshot == after_snapshot:
            return
        self._undo_stack.append(before_snapshot)
        if len(self._undo_stack) > UNDO_STACK_SIZE:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, current_snapshot):
        if not self._undo_stack:
            return None
        self._redo_stack.append(current_snapshot)
        if len(self._redo_stack) > UNDO_STACK_SIZE:
            self._redo_stack.pop(0)
        return self._undo_stack.pop()

    def redo(self, current_snapshot):
        if not self._redo_stack:
            return None
        self._undo_stack.append(current_snapshot)
        if len(self._undo_stack) > UNDO_STACK_SIZE:
            self._undo_stack.pop(0)
        return self._redo_stack.pop()

    def reset_to_initial(self, current_snapshot):
        if self._initial_snapshot is None:
            return None
        self._undo_stack.append(current_snapshot)
        if len(self._undo_stack) > UNDO_STACK_SIZE:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        return self._initial_snapshot

    # ============================================================
    # ================== STATE ==================================
    # ============================================================

    def can_undo(self):
        return len(self._undo_stack) > 0

    def can_redo(self):
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._initial_snapshot = None