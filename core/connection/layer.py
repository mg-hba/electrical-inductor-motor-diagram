"""
================================================================================
File: core/connection/layer.py
Purpose: Facade for connection system with R/U groups.
         Adds shift_y for main diagram vertical shift.
         Uses ConnectionMode enum for mutually exclusive states.
Version: 0.1.4
================================================================================
"""

from core.connection.mode import ConnectionMode
from core.connection.models import WirePoint, Junction, LineSegment
from core.connection.topology import Topology
from core.connection.operations import Operations, ConflictInfo
from core.connection.selection import (
    SelectionState, HitTester, compute_tolerance, box_select,
)
from core.connection.renderer import ConnectionRenderer
from core.connection.layer_history import HistoryManager
from core.connection.layer_json import JsonIO
from core.connection.group_ops import GroupOps

from utils.constants import (
    SPLIT_EPSILON,
    ERROR_CANNOT_DELETE_JUNCTION,
    ERROR_WIRE_POINT_NOT_DELETABLE,
    ERROR_SHORT_CIRCUIT,
)


class ConnectionLayer:

    ###################################
    ##########__init__#################
    ###################################
    def __init__(self, view):
        self.view = view

        self.wire_points = []
        self.junctions = []
        self.lines = []
        self.phase_endpoints = {}

        # `active` = panel is open (not a mode)
        self.active = False
        # Single mutually-exclusive input mode
        self._mode = ConnectionMode.SELECT
        # Sub-flag of DELETE mode (group-clear variant)
        self.group_clear_mode = False

        self.selection = SelectionState()

        self._topo = Topology(self.wire_points, self.junctions, self.lines)
        self._ops = Operations(self.wire_points, self.junctions, self.lines)
        self._hit = HitTester(self.wire_points, self.junctions, self.lines)
        self.renderer = ConnectionRenderer(self)
        self._history = HistoryManager()
        self._json = JsonIO(self)
        self._group = GroupOps(self.wire_points, self.junctions,
                                self.lines, self._topo)

        self._last_error = None
        self.shift_y = 0.0
    ###################################
    ##########end of __init__#########
    ###################################

    ###################################
    ##########MODE PROPERTIES##########
    ###################################
    # Read-only backward-compatible properties.
    # Assignment (`connection.delete_mode = True`) is no longer allowed.
    # Use setters: set_delete_mode / set_crossing_mode / ...
    @property
    def delete_mode(self):
        return self._mode == ConnectionMode.DELETE

    @property
    def crossing_mode(self):
        return self._mode == ConnectionMode.CROSSING

    @property
    def pencil_mode(self):
        return self._mode == ConnectionMode.PENCIL

    @property
    def select_box_mode(self):
        return self._mode == ConnectionMode.SELECT_BOX

    def get_mode(self):
        """Return current ConnectionMode (debug / tests)."""
        return self._mode
    ###################################
    ##########end of MODE PROPERTIES###
    ###################################

    ###################################
    ##########selected_wire_ids########
    ###################################
    @property
    def selected_wire_ids(self):
        return self.selection.wire_ids
    ###################################
    ##########end of selected_wire_ids
    ###################################

    ###################################
    ##########selected_junction_ids####
    ###################################
    @property
    def selected_junction_ids(self):
        return self.selection.junction_ids
    ###################################
    ##########end of selected_junction_ids
    ###################################

    ###################################
    ##########selected_line_ids########
    ###################################
    @property
    def selected_line_ids(self):
        return self.selection.line_ids
    ###################################
    ##########end of selected_line_ids
    ###################################

    ###################################
    ##########pending_delete_ids#######
    ###################################
    @property
    def pending_delete_ids(self):
        return self.selection.pending_delete_ids
    ###################################
    ##########end of pending_delete_ids
    ###################################

    ###################################
    ##########set_active###############
    ###################################
    def set_active(self, active):
        self.active = active
        if active:
            self._mode = ConnectionMode.SELECT
            self._history.capture_initial(self.snapshot())
        else:
            self.clear_selection()
            self._mode = ConnectionMode.SELECT
            self.group_clear_mode = False
            self.selection.pending_delete_ids.clear()
    ###################################
    ##########end of set_active#######
    ###################################

    ###################################
    ##########set_delete_mode##########
    ###################################
    def set_delete_mode(self, active):
        if active:
            self._mode = ConnectionMode.DELETE
        else:
            if self._mode == ConnectionMode.DELETE:
                self._mode = ConnectionMode.SELECT
            self.selection.pending_delete_ids.clear()
            self.clear_selection()
    ###################################
    ##########end of set_delete_mode##
    ###################################

    ###################################
    ##########set_crossing_mode########
    ###################################
    def set_crossing_mode(self, active):
        if active:
            self._mode = ConnectionMode.CROSSING
            self.selection.pending_delete_ids.clear()
            self.clear_selection()
        else:
            if self._mode == ConnectionMode.CROSSING:
                self._mode = ConnectionMode.SELECT
    ###################################
    ##########end of set_crossing_mode
    ###################################

    ###################################
    ##########set_pencil_mode##########
    ###################################
    def set_pencil_mode(self, active):
        if active:
            self._mode = ConnectionMode.PENCIL
            self.selection.pending_delete_ids.clear()
        else:
            if self._mode == ConnectionMode.PENCIL:
                self._mode = ConnectionMode.SELECT
    ###################################
    ##########end of set_pencil_mode##
    ###################################

    ###################################
    ##########set_select_box_mode######
    ###################################
    def set_select_box_mode(self, active):
        if active:
            self._mode = ConnectionMode.SELECT_BOX
        else:
            if self._mode == ConnectionMode.SELECT_BOX:
                self._mode = ConnectionMode.SELECT
    ###################################
    ##########end of set_select_box_mode
    ###################################

    ###################################
    ##########set_group_clear_mode#####
    ###################################
    def set_group_clear_mode(self, active):
        self.group_clear_mode = active
    ###################################
    ##########end of set_group_clear_mode
    ###################################

    ###################################
    ##########clear_selection##########
    ###################################
    def clear_selection(self):
        self.selection.clear()
        for wire in self.wire_points:
            wire.selected = False
        for junction in self.junctions:
            junction.selected = False
        for line in self.lines:
            line.selected = False
    ###################################
    ##########end of clear_selection##
    ###################################

    ###################################
    ##########get_selected_names#######
    ###################################
    def get_selected_names(self):
        names = []
        for wire in self.wire_points:
            if wire.wire_id in self.selection.wire_ids:
                names.append(wire.wire_id)
        for junction in self.junctions:
            if junction.junction_id in self.selection.junction_ids:
                names.append(junction.junction_id)
        for line in self.lines:
            if line.line_id in self.selection.line_ids:
                names.append(line.line_id)
        return names
    ###################################
    ##########end of get_selected_names
    ###################################

    ###################################
    ##########get_last_error###########
    ###################################
    def get_last_error(self):
        return self._last_error
    ###################################
    ##########end of get_last_error###
    ###################################

    ###################################
    ##########clear_last_error#########
    ###################################
    def clear_last_error(self):
        self._last_error = None
    ###################################
    ##########end of clear_last_error
    ###################################

    ###################################
    ##########_push_undo###############
    ###################################
    def _push_undo(self, before_snapshot):
        self._history.push(before_snapshot, self.snapshot())
    ###################################
    ##########end of _push_undo#######
    ###################################

    ###################################
    ##########undo#####################
    ###################################
    def undo(self):
        snapshot = self._history.undo(self.snapshot())
        if snapshot is None:
            return False
        self.restore_from_snapshot(snapshot)
        return True
    ###################################
    ##########end of undo############
    ###################################

    ###################################
    ##########redo#####################
    ###################################
    def redo(self):
        snapshot = self._history.redo(self.snapshot())
        if snapshot is None:
            return False
        self.restore_from_snapshot(snapshot)
        return True
    ###################################
    ##########end of redo############
    ###################################

    ###################################
    ##########reset_to_initial#########
    ###################################
    def reset_to_initial(self):
        snapshot = self._history.reset_to_initial(self.snapshot())
        if snapshot is None:
            return False
        self.restore_from_snapshot(snapshot)
        return True
    ###################################
    ##########end of reset_to_initial##
    ###################################

    ###################################
    ##########can_undo##################
    ###################################
    def can_undo(self):
        return self._history.can_undo()
    ###################################
    ##########end of can_undo########
    ###################################

    ###################################
    ##########can_redo##################
    ###################################
    def can_redo(self):
        return self._history.can_redo()
    ###################################
    ##########end of can_redo########
    ###################################

    ###################################
    ##########load_from_json###########
    ###################################
    def load_from_json(self, json_manager):
        self._json.load_from_json(json_manager)
        self._reinit()
    ###################################
    ##########end of load_from_json###
    ###################################

    ###################################
    ##########save_to_json#############
    ###################################
    def save_to_json(self, json_manager):
        self._json.save_to_json(json_manager)
    ###################################
    ##########end of save_to_json#####
    ###################################

    ###################################
    ##########clear_for_new_project####
    ###################################
    def clear_for_new_project(self):
        self.wire_points = []
        self.junctions = []
        self.lines = []
        self.phase_endpoints = {}
        self.selection.clear_all()
        self._history.clear()
        self._reinit()
        self._last_error = None
    ###################################
    ##########end of clear_for_new_project
    ###################################

    ###################################
    ##########snapshot#################
    ###################################
    def snapshot(self):
        return {
            'junctions': [junction.to_dict() for junction in self.junctions],
            'lines': [line.to_dict() for line in self.lines],
            'endpoints': dict(self.phase_endpoints),
        }
    ###################################
    ##########end of snapshot#########
    ###################################

    ###################################
    ##########restore_from_snapshot####
    ###################################
    def restore_from_snapshot(self, snapshot):
        if not snapshot:
            return
        self.junctions = []
        for entry in snapshot.get('junctions', []):
            try:
                self.junctions.append(Junction.from_dict(entry))
            except (ValueError, TypeError):
                continue
        self.lines = []
        for entry in snapshot.get('lines', []):
            try:
                self.lines.append(LineSegment.from_dict(entry))
            except (ValueError, TypeError):
                continue
        self.phase_endpoints = dict(snapshot.get('endpoints', {}))
        self.selection.clear_all()
        self._reinit()
    ###################################
    ##########end of restore_from_snapshot
    ###################################

    ###################################
    ##########_reinit##################
    ###################################
    def _reinit(self):
        self._topo = Topology(self.wire_points, self.junctions, self.lines)
        self._ops = Operations(self.wire_points, self.junctions, self.lines)
        self._hit = HitTester(self.wire_points, self.junctions, self.lines)
        self._group = GroupOps(self.wire_points, self.junctions,
                                self.lines, self._topo)
    ###################################
    ##########end of _reinit##########
    ###################################

    ###################################
    ##########handle_touch_down_world##
    ###################################
    def handle_touch_down_world(self, world_x, world_y,
                                  scale, cell_size_px=10.0):
        if not self.active:
            return None
        tolerance = compute_tolerance(scale, cell_size_px)
        return self._hit.hit_any(world_x, world_y, tolerance)
    ###################################
    ##########end of handle_touch_down_world
    ###################################

    ###################################
    ##########apply_hit################
    ###################################
    def apply_hit(self, hit):
        if hit is None:
            return False
        kind, obj = hit

        if self.delete_mode:
            return self._apply_delete_hit(kind, obj)

        if kind == 'wire':
            changed = self.selection.toggle_wire(obj.wire_id)
            obj.selected = changed
            if changed:
                attached = self._hit.lines_touching_point(obj.x, obj.y)
                if len(attached) == 1:
                    self.selection.add_line(attached[0].line_id)
                    attached[0].selected = True
            else:
                for line in self._hit.lines_touching_point(obj.x, obj.y):
                    self.selection.line_ids.discard(line.line_id)
                    line.selected = False
            return True

        if kind == 'junction':
            changed = self.selection.toggle_junction(obj.junction_id)
            obj.selected = changed
            if changed:
                attached = self._hit.lines_touching_point(obj.x, obj.y)
                if len(attached) == 1:
                    self.selection.add_line(attached[0].line_id)
                    attached[0].selected = True
            else:
                for line in self._hit.lines_touching_point(obj.x, obj.y):
                    self.selection.line_ids.discard(line.line_id)
                    line.selected = False
            return True

        if kind == 'line':
            changed = self.selection.toggle_line(obj.line_id)
            obj.selected = changed
            return True
        return False
    ###################################
    ##########end of apply_hit#######
    ###################################

    ###################################
    ##########_apply_delete_hit########
    ###################################
    def _apply_delete_hit(self, kind, obj):
        if kind == 'wire':
            self._last_error = ERROR_WIRE_POINT_NOT_DELETABLE
            return False
        if kind == 'junction':
            self._last_error = ERROR_CANNOT_DELETE_JUNCTION
            return False
        if kind == 'line':
            lid = obj.line_id
            if lid in self.selection.pending_delete_ids:
                before = self.snapshot()
                if obj.phase_group:
                    self._group.clear_group(obj.phase_group)
                self.lines.remove(obj)
                self.selection.pending_delete_ids.discard(lid)
                self.selection.line_ids.discard(lid)
                self._topo.cleanup_invalid_junctions()
                self._remove_orphan_junctions()
                self._push_undo(before)
            else:
                self.selection.pending_delete_ids.add(lid)
            return True
        return False
    ###################################
    ##########end of _apply_delete_hit
    ###################################

    ###################################
    ##########_remove_orphan_junctions
    ###################################
    def _remove_orphan_junctions(self):
        to_remove = []
        for junction in self.junctions:
            if self._topo.junction_has_wire(junction):
                continue
            if not self._hit.lines_touching_point(junction.x, junction.y):
                to_remove.append(junction)
        for junction in to_remove:
            if junction in self.junctions:
                self.junctions.remove(junction)
                self.selection.junction_ids.discard(junction.junction_id)
                self.selection.pending_delete_ids.discard(
                    junction.junction_id
                )
    ###################################
    ##########end of _remove_orphan_junctions
    ###################################

    ###################################
    ##########pull_selected############
    ###################################
    def pull_selected(self, step=1):
        self._last_error = None
        before = self.snapshot()
        result = self._ops.pull_selected(
            self.selection.wire_ids,
            self.selection.junction_ids,
            self.selection.line_ids,
            step
        )
        if result is False:
            self._last_error = self._ops.get_last_error() or "Cannot pull"
            return result
        if result is True:
            self._push_undo(before)
        return result
    ###################################
    ##########end of pull_selected###
    ###################################

    ###################################
    ##########apply_conflict_resolution
    ###################################
    def apply_conflict_resolution(self, conflict, action):
        before = self.snapshot()
        result = self._ops.apply_conflict_resolution(conflict, action)
        self._topo.cleanup_invalid_junctions()
        self._inherit_groups_after_split()
        self._push_undo(before)
        return result
    ###################################
    ##########end of apply_conflict_resolution
    ###################################

    ###################################
    ##########shrink_selected_lines####
    ###################################
    def shrink_selected_lines(self, step=1):
        before = self.snapshot()
        ok = self._ops.shrink_selected_lines(
            self.selection.pending_delete_ids, step
        )
        self._push_undo(before)
        return ok
    ###################################
    ##########end of shrink_selected_lines
    ###################################

    ###################################
    ##########connect_selected#########
    ###################################
    def connect_selected(self):
        self._last_error = None
        before = self.snapshot()
        result = self._ops.connect_selected(self.selection.line_ids)
        if result is False:
            self._last_error = self._ops.get_last_error()
            return result
        self._inherit_groups_after_split()
        self._push_undo(before)
        return result
    ###################################
    ##########end of connect_selected
    ###################################

    ###################################
    ##########apply_crossing###########
    ###################################
    def apply_crossing(self):
        before = self.snapshot()
        self._reinit()
        result = self._ops.apply_crossing(self.selection.line_ids)
        self._topo.cleanup_invalid_junctions()
        self._inherit_groups_after_split()
        self._push_undo(before)
        return result
    ###################################
    ##########end of apply_crossing###
    ###################################

    ###################################
    ##########_inherit_groups_after_split
    ###################################
    def _inherit_groups_after_split(self):
        for line in self.lines:
            if line.phase_group is not None:
                continue
            try:
                self._group.inherit_group_for_new_line(line)
            except Exception:
                pass
    ###################################
    ##########end of _inherit_groups_after_split
    ###################################

    ###################################
    ##########toggle_select_all########
    ###################################
    def toggle_select_all(self):
        if self.selection.has_any():
            self.clear_selection()
        else:
            for wire in self.wire_points:
                self.selection.add_wire(wire.wire_id)
                wire.selected = True
            for junction in self.junctions:
                if self._topo.junction_has_wire(junction):
                    continue
                self.selection.add_junction(junction.junction_id)
                junction.selected = True
            for line in self.lines:
                self.selection.add_line(line.line_id)
                line.selected = True
    ###################################
    ##########end of toggle_select_all
    ###################################

    ###################################
    ##########mark_all_selected_as_delete
    ###################################
    def mark_all_selected_as_delete(self):
        for line in self.lines:
            if line.line_id in self.selection.line_ids:
                self.selection.pending_delete_ids.add(line.line_id)
    ###################################
    ##########end of mark_all_selected_as_delete
    ###################################

    ###################################
    ##########any_pending_delete#######
    ###################################
    def any_pending_delete(self):
        return len(self.selection.pending_delete_ids) > 0
    ###################################
    ##########end of any_pending_delete
    ###################################

    ###################################
    ##########delete_all_pending#######
    ###################################
    def delete_all_pending(self):
        before = self.snapshot()
        for line in self.lines:
            if line.line_id in self.selection.pending_delete_ids:
                if line.phase_group:
                    self._group.clear_group(line.phase_group)
                    break
        to_remove = [line for line in self.lines
                     if line.line_id in self.selection.pending_delete_ids]
        for line in to_remove:
            self.lines.remove(line)
            self.selection.line_ids.discard(line.line_id)
            self.selection.pending_delete_ids.discard(line.line_id)

        for wire in self.wire_points:
            self.selection.pending_delete_ids.discard(wire.wire_id)

        self._topo.cleanup_invalid_junctions()
        self._remove_orphan_junctions()
        self.clear_selection()
        self._push_undo(before)
    ###################################
    ##########end of delete_all_pending
    ###################################

    ###################################
    ##########move_point###############
    ###################################
    def move_point(self, target, new_x, new_y):
        if isinstance(target, WirePoint):
            self._last_error = "Main wire points cannot be moved"
            return False
        before = self.snapshot()
        ok = self._ops.move_point(target, new_x, new_y)
        self._reinit()
        self._push_undo(before)
        return ok
    ###################################
    ##########end of move_point#######
    ###################################

    ###################################
    ##########draw_pencil_line#########
    ###################################
    def draw_pencil_line(self, x1, y1, x2, y2):
        before = self.snapshot()
        self._reinit()
        result = self._ops.draw_pencil_line(x1, y1, x2, y2)
        if result is None:
            err = self._ops.get_last_error()
            self._last_error = err if err else (
                "A drawn line must connect to an existing point or line"
            )
        self._reinit()
        self._push_undo(before)
        return result
    ###################################
    ##########end of draw_pencil_line
    ###################################

    ###################################
    ##########apply_box_select#########
    ###################################
    def apply_box_select(self, x1, y1, x2, y2):
        if x2 >= x1:
            mode = 'contain'
        else:
            mode = 'intersect'

        wire_ids, junction_ids, line_ids = box_select(
            self.wire_points, self.junctions, self.lines,
            x1, y1, x2, y2, mode
        )

        for wire in self.wire_points:
            if wire.wire_id in wire_ids:
                self.selection.add_wire(wire.wire_id)
                wire.selected = True
        for junction in self.junctions:
            if junction.junction_id in junction_ids:
                self.selection.add_junction(junction.junction_id)
                junction.selected = True
        for line in self.lines:
            if line.line_id in line_ids:
                self.selection.add_line(line.line_id)
                line.selected = True
    ###################################
    ##########end of apply_box_select
    ###################################

    ###################################
    ##########set_group_R##############
    ###################################
    def set_group_R(self):
        self._last_error = None
        before = self.snapshot()
        self._reinit()

        seed = self._get_seed_from_selection()
        if seed is None:
            self._last_error = "Select a line or point first"
            return False

        result = self._group.assign_group_from_seed(seed, 'R')
        if result == 'CONFLICT':
            self._last_error = ERROR_SHORT_CIRCUIT
            return False
        if result is False:
            self._last_error = "Invalid seed"
            return False

        self.clear_selection()
        self._push_undo(before)
        return True
    ###################################
    ##########end of set_group_R#####
    ###################################

    ###################################
    ##########set_group_U##############
    ###################################
    def set_group_U(self):
        self._last_error = None
        before = self.snapshot()
        self._reinit()

        seed = self._get_seed_from_selection()
        if seed is None:
            self._last_error = "Select a line or point first"
            return False

        result = self._group.assign_group_from_seed(seed, 'U')
        if result == 'CONFLICT':
            self._last_error = ERROR_SHORT_CIRCUIT
            return False
        if result is False:
            self._last_error = "Invalid seed"
            return False

        self.clear_selection()
        self._push_undo(before)
        return True
    ###################################
    ##########end of set_group_U#####
    ###################################

    ###################################
    ##########clear_group_from_selection
    ###################################
    def clear_group_from_selection(self, group):
        self._last_error = None
        before = self.snapshot()
        self._reinit()

        if not self.selection.has_any():
            self._last_error = "Select line or point first"
            return False

        result = self._group.clear_group_from_selection(
            self.selection, group
        )
        if result:
            self.clear_selection()
            self._push_undo(before)
        return result
    ###################################
    ##########end of clear_group_from_selection
    ###################################

    ###################################
    ##########_get_seed_from_selection
    ###################################
    def _get_seed_from_selection(self):
        for line in self.lines:
            if line.line_id in self.selection.line_ids:
                return line
        for junction in self.junctions:
            if junction.junction_id in self.selection.junction_ids:
                return junction
        for wire in self.wire_points:
            if wire.wire_id in self.selection.wire_ids:
                return wire
        return None
    ###################################
    ##########end of _get_seed_from_selection
    ###################################

    ###################################
    ##########set_group_label##########
    ###################################
    def set_group_label(self, group):
        target = None
        for wire in self.wire_points:
            if wire.wire_id in self.selection.wire_ids:
                target = wire
                break
        if target is None:
            for junction in self.junctions:
                if junction.junction_id in self.selection.junction_ids:
                    target = junction
                    break

        if target is None:
            self._last_error = "Select a junction or wire point"
            return False

        if target.phase_group != group:
            self._last_error = "This point is not in group " + group
            return False

        tid = (target.wire_id if hasattr(target, 'wire_id')
               else target.junction_id)
        self.phase_endpoints[group] = tid
        self.clear_selection()
        return True
    ###################################
    ##########end of set_group_label##
    ###################################

    ###################################
    ##########draw_static##############
    ###################################
    def draw_static(self, backend):
        self.renderer.draw_static(backend, active=self.active)
    ###################################
    ##########end of draw_static######
    ###################################