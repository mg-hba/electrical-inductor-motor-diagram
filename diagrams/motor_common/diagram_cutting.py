"""
================================================================================
File: diagrams/motor_common/diagram_cutting.py
Purpose: Coil wrap + cut operations for winding diagrams.
Version: 0.1.4
================================================================================
"""


def wrap_coil_segments(diagram, coil_start, coil_end, y_values):
    all_slots = diagram.MOTOR_all_slots
    boundary_high = all_slots + 0.5

    result = [(coil_start, coil_end, list(y_values), False)]

    if coil_end > boundary_high:
        copy_start = coil_start - all_slots
        copy_end = coil_end - all_slots
        result.append((copy_start, copy_end, list(y_values), True))

    return result


def cut_coil_points(diagram, points):
    all_slots = diagram.MOTOR_all_slots
    cut_left = 0.5
    cut_right = all_slots + 0.5

    point_count = len(points)
    if point_count < 4:
        return points

    result = list(points)

    x_positions = [p[0] for p in result]
    x_min = min(x_positions)
    x_max = max(x_positions)

    if x_min < cut_left < x_max:
        y_cut = result[0][1]
        for index in range(point_count - 1):
            if x_positions[index] < cut_left < x_positions[index + 1]:
                t = (cut_left - x_positions[index]) / (
                    x_positions[index + 1] - x_positions[index]
                )
                y_cut = result[index][1] + (
                    result[index + 1][1] - result[index][1]
                ) * t
                break
        new_points = []
        for index in range(point_count):
            if x_positions[index] < cut_left:
                new_points.append((cut_left, y_cut))
            else:
                new_points.append(result[index])
        result = new_points

    x_positions2 = [p[0] for p in result]
    x_min2 = min(x_positions2)
    x_max2 = max(x_positions2)

    if x_min2 < cut_right < x_max2:
        y_cut = result[-1][1]
        for index in range(point_count - 1):
            if x_positions2[index] < cut_right < x_positions2[index + 1]:
                t = (cut_right - x_positions2[index]) / (
                    x_positions2[index + 1] - x_positions2[index]
                )
                y_cut = result[index][1] + (
                    result[index + 1][1] - result[index][1]
                ) * t
                break
        new_points = []
        for index in range(point_count):
            if x_positions2[index] > cut_right:
                new_points.append((cut_right, y_cut))
            else:
                new_points.append(result[index])
        result = new_points

    return result