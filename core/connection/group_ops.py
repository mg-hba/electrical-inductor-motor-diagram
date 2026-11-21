"""
================================================================================
File: core/connection/group_ops.py
Purpose: R/U phase group assignment, inheritance, and clearing.
         Short-circuit conflict is forbidden.
Version: 0.1.1.1
================================================================================
"""

from utils.constants import SPLIT_EPSILON


class GroupOps:

    def __init__(self, wires, junctions, lines, topo):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines
        self.topo = topo

    # ============================================================
    # ================== FIND SEED ==============================
    # ============================================================

    def _find_seed_object(self, seed):
        from core.connection.models import LineSegment, Junction, WirePoint

        if isinstance(seed, LineSegment):
            for ln in self.lines:
                if ln.line_id == seed.line_id:
                    return ('line', ln)
        elif isinstance(seed, Junction):
            for j in self.junctions:
                if j.junction_id == seed.junction_id:
                    return ('junction', j)
        elif isinstance(seed, WirePoint):
            for wp in self.wires:
                if wp.wire_id == seed.wire_id:
                    return ('wire', wp)
        return None

    # ============================================================
    # ================== ASSIGN GROUP ===========================
    # ============================================================

    def assign_group_from_seed(self, seed, group):
        """
        Traverse graph from seed, assign group to all connected.
        Returns True, 'CONFLICT', or False.
        """
        found = self._find_seed_object(seed)
        if not found:
            return False

        kind, obj = found

        opposite = 'U' if group == 'R' else 'R'

        # Check if seed already belongs to opposite group
        if getattr(obj, 'phase_group', None) == opposite:
            return 'CONFLICT'

        visited_lines = set()
        visited_junctions = set()
        visited_wires = set()

        queue = [found]

        while queue:
            k, o = queue.pop(0)

            if k == 'line':
                if o.line_id in visited_lines:
                    continue
                visited_lines.add(o.line_id)

                if o.phase_group == opposite:
                    return 'CONFLICT'

                o.phase_group = group
                if hasattr(o, 'rename_with_group'):
                    o.rename_with_group(group)

                for (ex, ey) in [(o.x1, o.y1), (o.x2, o.y2)]:
                    self._enqueue_point(ex, ey, queue,
                                         visited_junctions,
                                         visited_wires,
                                         visited_lines)

            elif k == 'junction':
                if o.junction_id in visited_junctions:
                    continue
                visited_junctions.add(o.junction_id)

                if o.phase_group == opposite:
                    return 'CONFLICT'

                o.phase_group = group
                if hasattr(o, 'rename_with_group'):
                    o.rename_with_group(group)

                self._enqueue_point(o.x, o.y, queue,
                                     visited_junctions,
                                     visited_wires,
                                     visited_lines)

            elif k == 'wire':
                if o.wire_id in visited_wires:
                    continue
                visited_wires.add(o.wire_id)

                if o.phase_group == opposite:
                    return 'CONFLICT'

                o.phase_group = group

                self._enqueue_point(o.x, o.y, queue,
                                     visited_junctions,
                                     visited_wires,
                                     visited_lines)

        return True

    def _enqueue_point(self, x, y, queue,
                        visited_junctions, visited_wires, visited_lines):
        for j in self.junctions:
            if (abs(j.x - x) < SPLIT_EPSILON and
                    abs(j.y - y) < SPLIT_EPSILON):
                if j.junction_id not in visited_junctions:
                    queue.append(('junction', j))

        for wp in self.wires:
            if (abs(wp.x - x) < SPLIT_EPSILON and
                    abs(wp.y - y) < SPLIT_EPSILON):
                if wp.wire_id not in visited_wires:
                    queue.append(('wire', wp))

        for ln in self.lines:
            if ln.line_id in visited_lines:
                continue
            if ((abs(ln.x1 - x) < SPLIT_EPSILON and
                 abs(ln.y1 - y) < SPLIT_EPSILON) or
                (abs(ln.x2 - x) < SPLIT_EPSILON and
                 abs(ln.y2 - y) < SPLIT_EPSILON)):
                queue.append(('line', ln))

    # ============================================================
    # ================== CLEAR GROUP ============================
    # ============================================================

    def clear_group(self, group):
        """Remove the given group from all objects."""
        for ln in self.lines:
            if ln.phase_group == group:
                ln.phase_group = None
                if hasattr(ln, 'rename_with_group'):
                    ln.rename_with_group(None)
        for j in self.junctions:
            if j.phase_group == group:
                j.phase_group = None
                if hasattr(j, 'rename_with_group'):
                    j.rename_with_group(None)
        for wp in self.wires:
            if wp.phase_group == group:
                wp.phase_group = None

    def clear_group_from_selection(self, selection, group):
        """
        Traverse from all selected items and clear the given group
        from all connected objects.
        """
        seeds = []
        for ln in self.lines:
            if ln.line_id in selection.line_ids and ln.phase_group == group:
                seeds.append(('line', ln))
        for j in self.junctions:
            if (j.junction_id in selection.junction_ids and
                    j.phase_group == group):
                seeds.append(('junction', j))
        for wp in self.wires:
            if wp.wire_id in selection.wire_ids and wp.phase_group == group:
                seeds.append(('wire', wp))

        if not seeds:
            return False

        visited_lines = set()
        visited_junctions = set()
        visited_wires = set()
        queue = list(seeds)

        while queue:
            k, o = queue.pop(0)

            if k == 'line':
                if o.line_id in visited_lines:
                    continue
                visited_lines.add(o.line_id)
                if o.phase_group == group:
                    o.phase_group = None
                    if hasattr(o, 'rename_with_group'):
                        o.rename_with_group(None)
                    for (ex, ey) in [(o.x1, o.y1), (o.x2, o.y2)]:
                        self._enqueue_point(ex, ey, queue,
                                             visited_junctions,
                                             visited_wires,
                                             visited_lines)

            elif k == 'junction':
                if o.junction_id in visited_junctions:
                    continue
                visited_junctions.add(o.junction_id)
                if o.phase_group == group:
                    o.phase_group = None
                    if hasattr(o, 'rename_with_group'):
                        o.rename_with_group(None)
                    self._enqueue_point(o.x, o.y, queue,
                                         visited_junctions,
                                         visited_wires,
                                         visited_lines)

            elif k == 'wire':
                if o.wire_id in visited_wires:
                    continue
                visited_wires.add(o.wire_id)
                if o.phase_group == group:
                    o.phase_group = None
                    self._enqueue_point(o.x, o.y, queue,
                                         visited_junctions,
                                         visited_wires,
                                         visited_lines)

        return True

    # ============================================================
    # ================== INHERIT GROUP ==========================
    # ============================================================

    def inherit_group_for_new_line(self, new_line):
        """
        After a new line is created, look at its endpoints and see
        if they touch grouped elements. If both R and U are touched,
        return 'CONFLICT'.
        """
        touched_groups = set()

        for (ex, ey) in [(new_line.x1, new_line.y1),
                          (new_line.x2, new_line.y2)]:
            for j in self.junctions:
                if (abs(j.x - ex) < SPLIT_EPSILON and
                        abs(j.y - ey) < SPLIT_EPSILON):
                    if j.phase_group is not None:
                        touched_groups.add(j.phase_group)
            for wp in self.wires:
                if (abs(wp.x - ex) < SPLIT_EPSILON and
                        abs(wp.y - ey) < SPLIT_EPSILON):
                    if wp.phase_group is not None:
                        touched_groups.add(wp.phase_group)
            for ln in self.lines:
                if ln.line_id == new_line.line_id:
                    continue
                if ((abs(ln.x1 - ex) < SPLIT_EPSILON and
                     abs(ln.y1 - ey) < SPLIT_EPSILON) or
                    (abs(ln.x2 - ex) < SPLIT_EPSILON and
                     abs(ln.y2 - ey) < SPLIT_EPSILON)):
                    if ln.phase_group is not None:
                        touched_groups.add(ln.phase_group)

        if len(touched_groups) == 0:
            return None
        if len(touched_groups) == 1:
            group = touched_groups.pop()
            new_line.phase_group = group
            if hasattr(new_line, 'rename_with_group'):
                new_line.rename_with_group(group)
            return group
        return 'CONFLICT'