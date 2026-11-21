"""
================================================================================
File: core/connection/operations.py
Purpose: All operations with automatic group inheritance and short-circuit
         detection. No diagonal lines allowed.
Version: 0.1.2
================================================================================
"""

from core.connection.models import Junction, LineSegment
from core.connection.geometry import (
    points_equal,
    point_on_segment_interior,
)
from core.connection.topology import Topology
from core.connection.topology_ops import TopologyOps
from core.connection.conflict_ops import ConflictInfo, ConflictOps
from core.connection.pencil_ops import PencilOps
from core.connection.group_ops import GroupOps

from utils.constants import (
    SPLIT_EPSILON,
    PULL_STEP_MIN,
    PULL_STEP_MAX,
    AUTO_SELECT_RADIUS,
    ERROR_OVERLAP,
    ERROR_BLOCKED,
    ERROR_NO_PARALLEL_PAIR,
    ERROR_SHORT_CIRCUIT,
)


class Operations:

    def __init__(self, wires, junctions, lines):
        self.wires = wires
        self.junctions = junctions
        self.lines = lines
        self.topo = Topology(wires, junctions, lines)
        self.topo_ops = TopologyOps(wires, junctions, lines, self.topo)
        self.conflict_ops = ConflictOps(wires, junctions, lines,
                                          self.topo, self.topo_ops)
        self.pencil_ops = PencilOps(wires, junctions, lines,
                                      self.topo, self.topo_ops)
        self.group_ops = GroupOps(wires, junctions, lines, self.topo)
        self._last_error = None

    ##
    ###### برمی‌گرداند آخرین خطای عملیات ######
    ##
    def get_last_error(self):
        return self._last_error
    # end get_last_error

    ##
    ###### پاک می‌کند آخرین خطا را ######
    ##
    def clear_last_error(self):
        self._last_error = None
    # end clear_last_error

    ##
    ###### دوباره مقداردهی می‌کند group_ops را ######
    ##
    def _reinit_groups(self):
        self.group_ops = GroupOps(self.wires, self.junctions,
                                    self.lines, self.topo)
    # end _reinit_groups

    ##
    ###### کشیدن خطوط انتخاب‌شده به سمت پایین ######
    ##
    def pull_selected(self, selected_wire_ids, selected_junction_ids,
                       selected_line_ids, step=1):
        self._last_error = None
        made_change = False
        all_conflicts = []
        processed_positions = set()

        step = max(PULL_STEP_MIN, min(PULL_STEP_MAX, step))

        def position_key(x, y):
            return (round(x, 3), round(y, 3))

        for line in list(self.lines):
            if line.line_id not in selected_line_ids:
                continue
            if line.is_vertical:
                top_x, top_y = self._get_top_of_vertical(line)
                key = position_key(top_x, top_y)
                if key in processed_positions:
                    continue
                processed_positions.add(key)
                result = self._extend_or_create_vertical(
                    top_x, top_y, step, all_conflicts,
                    selected_line_ids, None
                )
                if result is True:
                    made_change = True
            elif line.is_horizontal:
                if line.x1 <= line.x2:
                    left_x, left_y = line.x1, line.y1
                else:
                    left_x, left_y = line.x2, line.y2
                key = position_key(left_x, left_y)
                if key in processed_positions:
                    continue
                processed_positions.add(key)
                result = self._extend_or_create_vertical(
                    left_x, left_y, step, all_conflicts,
                    selected_line_ids, None
                )
                if result is True:
                    made_change = True

        for junction in list(self.junctions):
            if junction.junction_id not in selected_junction_ids:
                continue
            key = position_key(junction.x, junction.y)
            if key in processed_positions:
                continue
            processed_positions.add(key)
            result = self._extend_or_create_vertical(
                junction.x, junction.y, step, all_conflicts,
                selected_line_ids, junction
            )
            if result is True:
                made_change = True

        for wire in list(self.wires):
            if wire.wire_id not in selected_wire_ids:
                continue
            key = position_key(wire.x, wire.y)
            if key in processed_positions:
                continue
            processed_positions.add(key)
            result = self._extend_or_create_vertical(
                wire.x, wire.y, step, all_conflicts,
                selected_line_ids, wire
            )
            if result is True:
                made_change = True

        self.topo.cleanup_invalid_junctions()

        if all_conflicts:
            return all_conflicts
        return made_change
    # end pull_selected

    ##
    ###### برمی‌گرداند بالاترین نقطه یک خط عمودی ######
    ##
    def _get_top_of_vertical(self, line):
        if line.y1 >= line.y2:
            return (line.x1, line.y1)
        return (line.x2, line.y2)
    # end _get_top_of_vertical

    ##
    ###### کشیدن یا ساخت خط عمودی از یک نقطه ######
    ##
    def _extend_or_create_vertical(self, x, y, step, conflicts_acc,
                                     selected_line_ids, start_point):
        y = round(y)

        existing = None
        for line in self.lines:
            if not line.is_vertical:
                continue
            top = self._get_top_of_vertical(line)
            if (abs(top[0] - x) < SPLIT_EPSILON and
                    abs(top[1] - y) < SPLIT_EPSILON):
                existing = line
                break

        if existing is not None:
            old_bottom = min(existing.y1, existing.y2)
            new_bottom = old_bottom - step
        else:
            old_bottom = y
            new_bottom = y - step

        new_bottom = round(new_bottom)

        exclude_ids = {existing.line_id} if existing else set()
        perpendicular = self.topo_ops.lines_on_path(
            x, y, x, new_bottom, exclude_ids=exclude_ids
        )

        if perpendicular:
            for line, point in perpendicular:
                conflicts_acc.append(ConflictInfo(
                    line, point, (x, y), (x, new_bottom), start_point
                ))
            return 'NEED_CONFIRM'

        if existing is not None:
            if existing.y1 <= existing.y2:
                bottom_x, bottom_y = existing.x1, existing.y1
                top_x, top_y = existing.x2, existing.y2
            else:
                bottom_x, bottom_y = existing.x2, existing.y2
                top_x, top_y = existing.x1, existing.y1

            bottom_junction = self.topo.find_junction_at(bottom_x, bottom_y)

            existing.y1 = top_y
            existing.y2 = new_bottom
            existing.x1 = top_x
            existing.x2 = top_x

            if bottom_junction is not None:
                bottom_junction.x = top_x
                bottom_junction.y = new_bottom

            if (self.topo.find_junction_at(top_x, new_bottom) is None and
                    self.topo.find_wire_at(top_x, new_bottom) is None):
                self.junctions.append(Junction(top_x, new_bottom))

            selected_line_ids.add(existing.line_id)
            existing.selected = True
            return True
        else:
            new_line = LineSegment(x, y, x, new_bottom)
            self.lines.append(new_line)

            if (self.topo.find_junction_at(x, new_bottom) is None and
                    self.topo.find_wire_at(x, new_bottom) is None):
                self.junctions.append(Junction(x, new_bottom))

            selected_line_ids.add(new_line.line_id)
            new_line.selected = True
            return True
    # end _extend_or_create_vertical

    ##
    ###### اعمال حل تعارض (connect/pass_over/stop_before) ######
    ##
    def apply_conflict_resolution(self, conflict, action):
        return self.conflict_ops.apply(conflict, action)
    # end apply_conflict_resolution

    ##
    ###### اتصال خطوط عمودی انتخاب‌شده با خط افقی ######
    ##
    def connect_selected(self, selected_line_ids):
        self._last_error = None
        selected_lines = [line for line in self.lines
                            if line.line_id in selected_line_ids]
        if len(selected_lines) < 2:
            return False

        vertical_lines = [line for line in selected_lines if line.is_vertical]
        horizontal_lines = [line for line in selected_lines if line.is_horizontal]

        if (len(vertical_lines) == 0 and
                len(horizontal_lines) >= 2):
            auto = self._auto_select_verticals_between_horizontals(
                horizontal_lines
            )
            if auto:
                for line in auto:
                    selected_line_ids.add(line.line_id)
                    line.selected = True
                for line in horizontal_lines:
                    selected_line_ids.discard(line.line_id)
                    line.selected = False
                return self.connect_selected(selected_line_ids)
            self._last_error = ERROR_NO_PARALLEL_PAIR
            return False

        if len(vertical_lines) < 2:
            return False

        line_bottoms = []
        for line in vertical_lines:
            bottom_y = min(line.y1, line.y2)
            bottom_x = line.x1 if line.y1 <= line.y2 else line.x2
            line_bottoms.append({
                'line': line,
                'bottom_y': bottom_y,
                'bottom_x': bottom_x,
            })

        reference_y = max(item['bottom_y'] for item in line_bottoms)

        all_xs = [item['bottom_x'] for item in line_bottoms]
        x_min_new, x_max_new = min(all_xs), max(all_xs)

        if x_max_new - x_min_new > SPLIT_EPSILON:
            if self.topo_ops.line_overlaps_existing(
                    x_min_new, reference_y, x_max_new, reference_y):
                self._last_error = ERROR_OVERLAP
                return False

        junction_xs = []
        for item in line_bottoms:
            line = item['line']
            bottom_y = item['bottom_y']

            if abs(bottom_y - reference_y) < SPLIT_EPSILON:
                junction_x = item['bottom_x']
                self.topo_ops.ensure_junction_at(junction_x, reference_y)
                junction_xs.append(junction_x)
            elif bottom_y > reference_y:
                self.lines.remove(line)
                new_line = LineSegment(line.x1, line.y1, line.x2, reference_y)
                self.lines.append(new_line)
                selected_line_ids.add(new_line.line_id)
                new_line.selected = True
                self.topo_ops.ensure_junction_at(line.x1, reference_y)
                junction_xs.append(line.x1)
            else:
                junction_x = line.x1
                if line.y1 > line.y2:
                    upper = LineSegment(line.x1, line.y1, line.x1, reference_y)
                    lower = LineSegment(line.x1, reference_y, line.x1, line.y2)
                else:
                    upper = LineSegment(line.x1, reference_y, line.x1, line.y1)
                    lower = LineSegment(line.x1, line.y2, line.x1, reference_y)
                self.lines.remove(line)
                self.lines.append(upper)
                self.lines.append(lower)
                selected_line_ids.add(upper.line_id)
                selected_line_ids.add(lower.line_id)
                upper.selected = True
                lower.selected = True
                self.topo_ops.ensure_junction_at(junction_x, reference_y)
                junction_xs.append(junction_x)

        if junction_xs:
            xmin, xmax = min(junction_xs), max(junction_xs)
            if xmax - xmin > SPLIT_EPSILON:
                new_line = LineSegment(xmin, reference_y, xmax, reference_y)
                self.lines.append(new_line)
                selected_line_ids.add(new_line.line_id)
                new_line.selected = True

        self.topo.cleanup_invalid_junctions()
        return True
    # end connect_selected

    ##
    ###### پیدا کردن خودکار خطوط عمودی بین دو خط افقی ######
    ##
    
    def _auto_select_verticals_between_horizontals(self, horizontal_lines):
        if len(horizontal_lines) < 2:
            return []
        first_horizontal = horizontal_lines[0]
        second_horizontal = horizontal_lines[1]

        endpoints = []
        for line in (first_horizontal, second_horizontal):
            endpoints.append((line.x1, line.y1))
            endpoints.append((line.x2, line.y2))

        candidates = []
        for (ax, ay) in endpoints:
            for (bx, by) in endpoints:
                if (abs(ax - bx) < SPLIT_EPSILON and
                        abs(ay - by) > SPLIT_EPSILON):
                    for line in self.lines:
                        if not line.is_vertical:
                            continue
                        if abs(line.x1 - ax) < SPLIT_EPSILON:
                            ymin = min(line.y1, line.y2)
                            ymax = max(line.y1, line.y2)
                            lo, hi = min(ay, by), max(ay, by)
                            if (ymin - SPLIT_EPSILON <= lo <= ymax + SPLIT_EPSILON and
                                    ymin - SPLIT_EPSILON <= hi <= ymax + SPLIT_EPSILON):
                                distance = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
                                candidates.append((distance, line))

        if not candidates:
            best_pair = None
            best_distance = AUTO_SELECT_RADIUS
            for (ax, ay) in endpoints:
                for (bx, by) in endpoints:
                    if abs(ax - bx) < SPLIT_EPSILON:
                        continue
                    distance = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
                    if distance < best_distance:
                        best_distance = distance
                        best_pair = ((ax, ay), (bx, by))

            if best_pair:
                for line in self.lines:
                    if not line.is_vertical:
                        continue
                    ax, ay = best_pair[0]
                    bx, by = best_pair[1]
                    if (abs(line.x1 - ax) < SPLIT_EPSILON or
                            abs(line.x1 - bx) < SPLIT_EPSILON):
                        return [line]
            return []

        candidates.sort(key=lambda pair: pair[0])
        return [candidates[0][1]]
    # end _auto_select_verticals_between_horizontals

    ##
    ###### اعمال تقاطع (crossing) روی خطوط انتخاب‌شده ######
    ##
    def apply_crossing(self, selected_line_ids):
        selected_lines = [line for line in self.lines
                            if line.line_id in selected_line_ids]
        if len(selected_lines) < 2:
            return False

        intersections = []
        n = len(selected_lines)
        for i in range(n):
            for j in range(i + 1, n):
                point = self._compute_hv_intersection(selected_lines[i],
                                                       selected_lines[j])
                if point is not None:
                    intersections.append(point)

        if not intersections:
            return False

        for (x, y) in intersections:
            to_split = []
            for line in self.lines:
                if point_on_segment_interior(x, y, line.x1, line.y1,
                                               line.x2, line.y2):
                    to_split.append(line)

            if (self.topo.find_junction_at(x, y) is None and
                    self.topo.find_wire_at(x, y) is None):
                self.junctions.append(Junction(x, y))

            for line in to_split:
                if line not in self.lines:
                    continue
                new1 = LineSegment(line.x1, line.y1, x, y)
                new2 = LineSegment(x, y, line.x2, line.y2)
                new1.phase_group = line.phase_group
                new2.phase_group = line.phase_group
                if line.phase_group:
                    new1.rename_with_group(line.phase_group)
                    new2.rename_with_group(line.phase_group)
                self.lines.remove(line)
                self.lines.append(new1)
                self.lines.append(new2)

        self.topo.cleanup_invalid_junctions()
        return True
    # end apply_crossing

    ##
    ###### محاسبه نقطه تقاطع یک خط افقی و یک خط عمودی ######
    ##
    def _compute_hv_intersection(self, line1, line2):
        if line1.is_horizontal and line2.is_vertical:
            horizontal, vertical = line1, line2
        elif line1.is_vertical and line2.is_horizontal:
            horizontal, vertical = line2, line1
        else:
            return None

        horizontal_y = horizontal.y1
        vertical_x = vertical.x1
        hx1, hx2 = min(horizontal.x1, horizontal.x2), max(horizontal.x1, horizontal.x2)
        vy1, vy2 = min(vertical.y1, vertical.y2), max(vertical.y1, vertical.y2)

        if (hx1 + SPLIT_EPSILON) < vertical_x < (hx2 - SPLIT_EPSILON):
            if (vy1 + SPLIT_EPSILON) < horizontal_y < (vy2 - SPLIT_EPSILON):
                return (vertical_x, horizontal_y)
        return None
    # end _compute_hv_intersection

##
###### جابه‌جایی یک نقطه (junction) - فقط اگر خطوط عمودی/افقی بمانند ######
##
    def move_point(self, target, new_x, new_y):
        from core.connection.models import WirePoint
        if isinstance(target, WirePoint):
            self._last_error = "Main wire points cannot be moved"
            return False
    
        new_x = round(new_x)
        new_y = round(new_y)
    
        old_x, old_y = target.x, target.y
    
        # Collect attached lines
        attached_lines = []
        for line in self.lines:
            if points_equal(line.x1, line.y1, old_x, old_y):
                attached_lines.append((line, 'start'))
            elif points_equal(line.x2, line.y2, old_x, old_y):
                attached_lines.append((line, 'end'))
    
        if not attached_lines:
            self._last_error = "No lines attached to this point"
            return False
    
        # Verify each attached line remains H or V after move
        for line, endpoint in attached_lines:
            if endpoint == 'start':
                other_x, other_y = line.x2, line.y2
            else:
                other_x, other_y = line.x1, line.y1
    
            is_h = abs(new_y - other_y) < SPLIT_EPSILON
            is_v = abs(new_x - other_x) < SPLIT_EPSILON
    
            if not is_h and not is_v:
                self._last_error = (
                    "Move would make a line diagonal - only H or V allowed"
                )
                return False
    
        # Apply move
        for line, endpoint in attached_lines:
            if endpoint == 'start':
                line.x1, line.y1 = new_x, new_y
            else:
                line.x2, line.y2 = new_x, new_y
    
        target.x = new_x
        target.y = new_y
    
        self.lines[:] = [line for line in self.lines
                          if line.length() > SPLIT_EPSILON]
        self.topo.cleanup_invalid_junctions()
        return True
# end move_point
    ##
    ###### رسم خط جدید با مداد (pencil) ######
    ##
    def draw_pencil_line(self, x1, y1, x2, y2):
        x1 = round(x1)
        y1 = round(y1)
        x2 = round(x2)
        y2 = round(y2)

        if (abs(x2 - x1) < SPLIT_EPSILON and
                abs(y2 - y1) < SPLIT_EPSILON):
            return None

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        if dx >= dy:
            y2 = y1
        else:
            x2 = x1

        if (abs(x2 - x1) < SPLIT_EPSILON and
                abs(y2 - y1) < SPLIT_EPSILON):
            return None

        snap = 1.2
        x1n, y1n, attached1 = self._snap_endpoint(x1, y1, snap)
        x2n, y2n, attached2 = self._snap_endpoint(x2, y2, snap)

        if abs(x2n - x1n) >= abs(y2n - y1n):
            y2n = y1n
        else:
            x2n = x1n

        if not attached1 and not attached2:
            return None

        if (abs(x2n - x1n) < SPLIT_EPSILON and
                abs(y2n - y1n) < SPLIT_EPSILON):
            return None

        new_line = LineSegment(x1n, y1n, x2n, y2n)
        self.lines.append(new_line)

        self.topo_ops.ensure_junction_at(x1n, y1n)
        self.topo_ops.ensure_junction_at(x2n, y2n)

        self._reinit_groups()
        result = self.group_ops.inherit_group_for_new_line(new_line)
        if result == 'CONFLICT':
            self.lines.remove(new_line)
            self._last_error = ERROR_SHORT_CIRCUIT
            return None

        return new_line
    # end draw_pencil_line

    ##
    ###### اسنپ کردن یک نقطه به نزدیک‌ترین المان موجود ######
    ##
    def _snap_endpoint(self, x, y, radius):
        best_distance = radius
        best = None
        for wire in self.wires:
            distance = ((wire.x - x) ** 2 + (wire.y - y) ** 2) ** 0.5
            if distance <= best_distance:
                best_distance = distance
                best = (wire.x, wire.y)
        if best is not None:
            return (best[0], best[1], True)

        best_distance = radius
        best = None
        for junction in self.junctions:
            distance = ((junction.x - x) ** 2 + (junction.y - y) ** 2) ** 0.5
            if distance <= best_distance:
                best_distance = distance
                best = (junction.x, junction.y)
        if best is not None:
            return (best[0], best[1], True)

        for line in list(self.lines):
            if point_on_segment_interior(x, y, line.x1, line.y1,
                                           line.x2, line.y2):
                self.topo_ops.split_line_at(line, x, y)
                self.topo_ops.ensure_junction_at(x, y)
                return (x, y, True)

        best_distance = radius
        best = None
        for line in self.lines:
            for (ex, ey) in [(line.x1, line.y1), (line.x2, line.y2)]:
                distance = ((ex - x) ** 2 + (ey - y) ** 2) ** 0.5
                if distance <= best_distance:
                    best_distance = distance
                    best = (ex, ey)
        if best is not None:
            return (best[0], best[1], True)

        return (x, y, False)
    # end _snap_endpoint

    ##
    ###### تنظیم نقطه شروع فاز (R) ######
    ##
    def set_phase_start(self, selected_wire_ids, selected_junction_ids,
                         phase_endpoints):
        for wire in self.wires:
            if wire.wire_id in selected_wire_ids:
                wire.is_phase_start = True
                wire.is_phase_end = False
                phase_endpoints['R'] = wire.wire_id
        for junction in self.junctions:
            if junction.junction_id in selected_junction_ids:
                junction.is_phase_start = True
                junction.is_phase_end = False
                phase_endpoints['R'] = junction.junction_id
    # end set_phase_start

    ##
    ###### تنظیم نقطه پایان فاز (U) ######
    ##
    def set_phase_end(self, selected_wire_ids, selected_junction_ids,
                       phase_endpoints):
        for wire in self.wires:
            if wire.wire_id in selected_wire_ids:
                wire.is_phase_end = True
                wire.is_phase_start = False
                phase_endpoints['U'] = wire.wire_id
        for junction in self.junctions:
            if junction.junction_id in selected_junction_ids:
                junction.is_phase_end = True
                junction.is_phase_start = False
                phase_endpoints['U'] = junction.junction_id
    # end set_phase_end
    