#!/usr/bin/env python3
"""Shared cooperative search helpers for NL_Swarm agents."""

from __future__ import annotations

import math

HOME_POSITIONS = {
    "uav1": (-35.363261, 149.165230),
    "uav2": (-35.363261, 149.166230),
    "uav3": (-35.364261, 149.165230),
    "uav4": (-35.365261, 149.165230),
}


def ensure_search_task_defaults(task: dict) -> dict:
    """Populate default cooperative search settings on incoming tasks."""
    normalized = dict(task)
    task_type = str(normalized.get("type", "")).lower()
    if task_type == "search":
        diameter = normalized.get("search_diameter_m")
        if diameter in (None, "", 0):
            diameter = 300
        diameter = max(200, int(float(diameter)))
        normalized["search_diameter_m"] = diameter
        normalized["search_radius_m"] = diameter / 2.0
        normalized["search_pattern"] = normalized.get("search_pattern") or "lawnmower"
        normalized["partitioning"] = normalized.get("partitioning") or "voronoi"
        normalized["lane_spacing_m"] = max(20.0, float(normalized.get("lane_spacing_m") or 30.0))
    return normalized


def build_team_positions(selected_drones: list[str], self_id: str, self_position, peer_positions: dict) -> dict:
    """Build deterministic team positions for selected drones using live peers with home fallbacks."""
    team_positions = {}
    for drone_id in selected_drones:
        if drone_id == self_id and self_position:
            team_positions[drone_id] = tuple(self_position)
            continue
        peer = peer_positions.get(drone_id)
        if peer and peer.get("lat") is not None and peer.get("lon") is not None:
            team_positions[drone_id] = (peer["lat"], peer["lon"])
        else:
            team_positions[drone_id] = HOME_POSITIONS.get(drone_id, HOME_POSITIONS["uav1"])
    return team_positions


def build_centered_search_positions(
    selected_drones: list[str],
    center_lat: float,
    center_lon: float,
    desired_spacing_m: float = 10.0,
) -> dict:
    """Build deterministic pseudo-seed positions around the center for post-arrival Voronoi partitioning."""
    ordered = list(selected_drones)
    if not ordered:
        return {}
    if len(ordered) == 1:
        return {ordered[0]: (center_lat, center_lon)}

    ring_radius_m = max(5.0, desired_spacing_m / (2.0 * math.sin(math.pi / len(ordered))))
    positions = {}
    for idx, drone_id in enumerate(ordered):
        angle = (-math.pi / 2.0) + (2.0 * math.pi * idx / len(ordered))
        x_m = ring_radius_m * math.cos(angle)
        y_m = ring_radius_m * math.sin(angle)
        positions[drone_id] = local_m_to_latlon(center_lat, center_lon, x_m, y_m)
    return positions


def latlon_to_local_m(center_lat: float, center_lon: float, lat: float, lon: float) -> tuple[float, float]:
    meters_per_deg_lat = 111320.0
    meters_per_deg_lon = max(1.0, 111320.0 * math.cos(math.radians(center_lat)))
    x_m = (lon - center_lon) * meters_per_deg_lon
    y_m = (lat - center_lat) * meters_per_deg_lat
    return (x_m, y_m)


def local_m_to_latlon(center_lat: float, center_lon: float, x_m: float, y_m: float) -> tuple[float, float]:
    meters_per_deg_lat = 111320.0
    meters_per_deg_lon = max(1.0, 111320.0 * math.cos(math.radians(center_lat)))
    lat = center_lat + (y_m / meters_per_deg_lat)
    lon = center_lon + (x_m / meters_per_deg_lon)
    return (lat, lon)


def approx_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    x_m, y_m = latlon_to_local_m(lat2, lon2, lat1, lon1)
    return math.sqrt(x_m * x_m + y_m * y_m)


def _generate_circle_samples(radius_m: float, sample_step_m: float) -> list[tuple[float, float]]:
    samples = [(0.0, 0.0)]
    limit = int(math.ceil(radius_m / sample_step_m))
    for ix in range(-limit, limit + 1):
        x_m = ix * sample_step_m
        for iy in range(-limit, limit + 1):
            y_m = iy * sample_step_m
            if x_m * x_m + y_m * y_m <= radius_m * radius_m:
                samples.append((x_m, y_m))
    return samples


def _assign_samples_to_voronoi_cells(samples, seed_points):
    assigned = {drone_id: [] for drone_id in seed_points}
    for x_m, y_m in samples:
        winner_id = min(
            seed_points,
            key=lambda drone_id: (
                (x_m - seed_points[drone_id][0]) ** 2 + (y_m - seed_points[drone_id][1]) ** 2,
                drone_id,
            ),
        )
        assigned[winner_id].append((x_m, y_m))
    return assigned


def _assign_samples_to_sector_cells(samples, ordered_drones):
    assigned = {drone_id: [] for drone_id in ordered_drones}
    sector_count = len(ordered_drones)
    for x_m, y_m in samples:
        angle = math.atan2(y_m, x_m)
        normalized = (angle + math.pi) / (2.0 * math.pi)
        index = min(sector_count - 1, int(normalized * sector_count))
        assigned[ordered_drones[index]].append((x_m, y_m))
    return assigned


def _choose_balanced_partition(samples, seed_points):
    voronoi_cells = _assign_samples_to_voronoi_cells(samples, seed_points)
    counts = [len(voronoi_cells[drone_id]) for drone_id in seed_points]
    avg_count = sum(counts) / max(1, len(counts))
    min_count = min(counts) if counts else 0
    max_count = max(counts) if counts else 0
    if not counts:
        return "voronoi", voronoi_cells

    if min_count >= 0.55 * avg_count and max_count <= 1.8 * avg_count:
        return "voronoi", voronoi_cells

    # Voronoi is too skewed when all selected drones approach from one side.
    ordered_drones = sorted(seed_points)
    sector_cells = _assign_samples_to_sector_cells(samples, ordered_drones)
    return "sector_fallback", sector_cells


def _cell_waypoints_from_samples(cell_samples, radius_m: float, lane_spacing_m: float):
    if not cell_samples:
        return [(0.0, 0.0)]

    sample_step_m = max(10.0, min(40.0, lane_spacing_m / 2.0))
    min_y = min(y for _, y in cell_samples)
    max_y = max(y for _, y in cell_samples)
    rows = []
    current_y = min_y
    while current_y <= max_y + 0.5 * lane_spacing_m:
        band = [pt for pt in cell_samples if abs(pt[1] - current_y) <= max(sample_step_m, lane_spacing_m / 2.0)]
        if band:
            min_x = min(x for x, _ in band)
            max_x = max(x for x, _ in band)
            if max_x - min_x < 5.0:
                current_y += lane_spacing_m
                continue
            rows.append((current_y, min_x, max_x))
        current_y += lane_spacing_m

    if not rows:
        centroid_x = sum(x for x, _ in cell_samples) / len(cell_samples)
        centroid_y = sum(y for _, y in cell_samples) / len(cell_samples)
        return [(centroid_x, centroid_y)]

    waypoints = []
    for idx, (row_y, min_x, max_x) in enumerate(rows):
        start_x, end_x = (min_x, max_x) if idx % 2 == 0 else (max_x, min_x)
        if not waypoints or waypoints[-1] != (start_x, row_y):
            waypoints.append((start_x, row_y))
        waypoints.append((end_x, row_y))

        if idx + 1 >= len(rows):
            continue

        next_row_y, next_min_x, next_max_x = rows[idx + 1]
        next_start_x = next_max_x if (idx + 1) % 2 == 1 else next_min_x
        corner = (end_x, next_row_y)
        if waypoints[-1] != corner:
            waypoints.append(corner)
        next_entry = (next_start_x, next_row_y)
        if waypoints[-1] != next_entry:
            waypoints.append(next_entry)

    last_x, last_y = waypoints[-1]
    if last_x * last_x + last_y * last_y > radius_m * radius_m:
        scale = radius_m / math.sqrt(last_x * last_x + last_y * last_y)
        waypoints[-1] = (last_x * scale, last_y * scale)
    return waypoints


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    unique_points = sorted(set(points))
    if len(unique_points) <= 2:
        return unique_points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for point in unique_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)

    upper = []
    for point in reversed(unique_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)

    return lower[:-1] + upper[:-1]


def compute_search_plan(task: dict, selected_drones: list[str], team_positions: dict, drone_id: str) -> dict:
    """Build a bounded Voronoi cell approximation and lawnmower coverage path for one drone."""
    search_task = ensure_search_task_defaults(task)
    center_lat, center_lon = search_task.get("location", HOME_POSITIONS["uav1"])
    radius_m = float(search_task["search_radius_m"])
    lane_spacing_m = float(search_task["lane_spacing_m"])
    sample_step_m = max(15.0, min(40.0, lane_spacing_m / 2.0))

    seed_points = {}
    for selected_id in selected_drones:
        lat, lon = team_positions[selected_id]
        seed_points[selected_id] = latlon_to_local_m(center_lat, center_lon, lat, lon)

    samples = _generate_circle_samples(radius_m, sample_step_m)
    partition_name, assigned_cells = _choose_balanced_partition(samples, seed_points)
    cell_samples = assigned_cells.get(drone_id, [])
    if not cell_samples:
        cell_samples = [(0.0, 0.0)]

    local_waypoints = _cell_waypoints_from_samples(cell_samples, radius_m, lane_spacing_m)
    seed_x, seed_y = seed_points[drone_id]
    if len(local_waypoints) >= 2:
        first_x, first_y = local_waypoints[0]
        last_x, last_y = local_waypoints[-1]
        first_distance = math.hypot(first_x - seed_x, first_y - seed_y)
        last_distance = math.hypot(last_x - seed_x, last_y - seed_y)
        if last_distance < first_distance:
            local_waypoints.reverse()
    latlon_waypoints = [
        local_m_to_latlon(center_lat, center_lon, waypoint_x, waypoint_y)
        for waypoint_x, waypoint_y in local_waypoints
    ]
    approx_area = len(cell_samples) * (sample_step_m ** 2)
    centroid_x = sum(x for x, _ in cell_samples) / len(cell_samples)
    centroid_y = sum(y for _, y in cell_samples) / len(cell_samples)
    centroid_lat, centroid_lon = local_m_to_latlon(center_lat, center_lon, centroid_x, centroid_y)

    return {
        "partitioning": partition_name,
        "coverage_pattern": "lawnmower",
        "search_radius_m": radius_m,
        "lane_spacing_m": lane_spacing_m,
        "cell_area_m2": round(approx_area, 1),
        "cell_centroid": [centroid_lat, centroid_lon],
        "waypoints": [[lat, lon] for lat, lon in latlon_waypoints],
    }


def compute_search_partition_overview(task: dict, selected_drones: list[str], team_positions: dict) -> dict:
    """Return full partition geometry for visualization across all selected drones."""
    search_task = ensure_search_task_defaults(task)
    center_lat, center_lon = search_task.get("location", HOME_POSITIONS["uav1"])
    radius_m = float(search_task["search_radius_m"])
    lane_spacing_m = float(search_task["lane_spacing_m"])
    sample_step_m = max(15.0, min(40.0, lane_spacing_m / 2.0))

    seed_points = {}
    for drone_id in selected_drones:
        lat, lon = team_positions[drone_id]
        seed_points[drone_id] = latlon_to_local_m(center_lat, center_lon, lat, lon)

    samples = _generate_circle_samples(radius_m, sample_step_m)
    partition_name, assigned_cells = _choose_balanced_partition(samples, seed_points)

    drones = {}
    for drone_id in selected_drones:
        cell_samples = assigned_cells.get(drone_id, [])
        if not cell_samples:
            cell_samples = [(0.0, 0.0)]

        hull_points = _convex_hull(cell_samples)
        local_waypoints = _cell_waypoints_from_samples(cell_samples, radius_m, lane_spacing_m)
        centroid_x = sum(x for x, _ in cell_samples) / len(cell_samples)
        centroid_y = sum(y for _, y in cell_samples) / len(cell_samples)
        centroid_lat, centroid_lon = local_m_to_latlon(center_lat, center_lon, centroid_x, centroid_y)
        approx_area = len(cell_samples) * (sample_step_m ** 2)

        drones[drone_id] = {
            "seed_latlon": list(team_positions[drone_id]),
            "cell_centroid": [centroid_lat, centroid_lon],
            "cell_centroid_local": [centroid_x, centroid_y],
            "cell_area_m2": round(approx_area, 1),
            "sample_step_m": sample_step_m,
            "cells_local": [[x_m, y_m] for x_m, y_m in cell_samples],
            "waypoints_local": [[x_m, y_m] for x_m, y_m in local_waypoints],
            "outline": [
                list(local_m_to_latlon(center_lat, center_lon, x_m, y_m))
                for x_m, y_m in hull_points
            ],
            "waypoints": [
                list(local_m_to_latlon(center_lat, center_lon, x_m, y_m))
                for x_m, y_m in local_waypoints
            ],
        }

    return {
        "center": [center_lat, center_lon],
        "search_radius_m": radius_m,
        "lane_spacing_m": lane_spacing_m,
        "partitioning": partition_name,
        "selected_drones": list(selected_drones),
        "drones": drones,
    }
