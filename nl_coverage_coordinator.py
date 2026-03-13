#!/usr/bin/env python3
import asyncio
import json
import logging
import math
import socket
import time
from dataclasses import dataclass, field


logging.basicConfig(level=logging.INFO, format="[coordinator] %(message)s")
LOG = logging.getLogger("nl_coverage_coordinator")

LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 61000
ASSIGNMENT_MCAST_GRP = "239.255.0.3"
ASSIGNMENT_MCAST_PORT = 30003
FAILURE_TIMEOUT = 10.0
REPLAN_INTERVAL = 3.0
PARTITION_RING_RADIUS_M = 20.0


def latlon_to_local_xy(lat: float, lon: float, lat0: float, lon0: float) -> tuple[float, float]:
    meters_per_deg_lat = 111_320.0
    lat_rad = math.radians(lat0)
    meters_per_deg_lon = 111_320.0 * math.cos(lat_rad)
    return (
        (lon - lon0) * meters_per_deg_lon,
        (lat - lat0) * meters_per_deg_lat,
    )


@dataclass
class DroneInfo:
    drone_id: str
    x_local: float
    y_local: float
    last_seen: float
    ready: bool = False
    plan_id: int = 0


@dataclass
class TaskState:
    task_id: str
    target_lat: float
    target_lon: float
    search_radius_m: float
    cell_size_m: float
    activation_radius_m: float
    selected_drones: list[str]
    grid_side: int
    grid_origin: tuple[float, float]
    explored: set[tuple[int, int]] = field(default_factory=set)
    drones: dict[str, DroneInfo] = field(default_factory=dict)
    pending_replan: bool = True
    last_replan_time: float = 0.0
    plan_counter: int = 0

    def cell_center_xy(self, ix: int, iy: int) -> tuple[float, float]:
        x = self.grid_origin[0] + ix * self.cell_size_m + self.cell_size_m / 2.0
        y = self.grid_origin[1] + iy * self.cell_size_m + self.cell_size_m / 2.0
        return x, y

    def cell_inside_circle(self, ix: int, iy: int) -> bool:
        x, y = self.cell_center_xy(ix, iy)
        return x * x + y * y <= self.search_radius_m * self.search_radius_m

    def available_cells(self) -> list[tuple[int, int]]:
        cells = []
        for ix in range(self.grid_side):
            for iy in range(self.grid_side):
                cell = (ix, iy)
                if self.cell_inside_circle(ix, iy) and cell not in self.explored:
                    cells.append(cell)
        return cells


class Coordinator:
    def __init__(self):
        self.tasks: dict[str, TaskState] = {}

    def get_or_create_task(self, payload: dict) -> TaskState | None:
        task_id = payload.get("task_id")
        if not task_id:
            return None
        if task_id in self.tasks:
            return self.tasks[task_id]
        try:
            target_lat = float(payload["target_lat"])
            target_lon = float(payload["target_lon"])
            search_radius_m = float(payload["search_radius_m"])
            cell_size_m = float(payload.get("cell_size_m", 80.0))
            activation_radius_m = float(payload.get("activation_radius_m", 140.0))
            selected_drones = sorted(str(d) for d in payload.get("selected_drones", []))
        except Exception:
            return None
        grid_side = int(math.ceil((2 * search_radius_m) / cell_size_m))
        offset = -(grid_side * cell_size_m) / 2.0
        task = TaskState(
            task_id=task_id,
            target_lat=target_lat,
            target_lon=target_lon,
            search_radius_m=search_radius_m,
            cell_size_m=cell_size_m,
            activation_radius_m=activation_radius_m,
            selected_drones=selected_drones,
            grid_side=grid_side,
            grid_origin=(offset, offset),
        )
        self.tasks[task_id] = task
        LOG.info("Created task %s for drones %s", task_id, selected_drones)
        return task

    def handle_registration(self, payload: dict):
        task = self.get_or_create_task(payload)
        if not task:
            return
        drone_id = str(payload.get("drone_id"))
        if drone_id not in task.selected_drones:
            return
        x_local = float(payload.get("x_local", 0.0))
        y_local = float(payload.get("y_local", 0.0))
        now = time.time()
        ready = (x_local * x_local + y_local * y_local) <= task.activation_radius_m * task.activation_radius_m
        task.drones[drone_id] = DroneInfo(drone_id=drone_id, x_local=x_local, y_local=y_local, last_seen=now, ready=ready)
        task.pending_replan = True

    def handle_state(self, payload: dict):
        task = self.get_or_create_task(payload)
        if not task:
            return
        drone_id = str(payload.get("drone_id"))
        if drone_id not in task.selected_drones:
            return
        lat = float(payload["lat"])
        lon = float(payload["lon"])
        x_local, y_local = latlon_to_local_xy(lat, lon, task.target_lat, task.target_lon)
        now = time.time()
        info = task.drones.get(drone_id)
        ready = (x_local * x_local + y_local * y_local) <= task.activation_radius_m * task.activation_radius_m
        if info is None:
            task.drones[drone_id] = DroneInfo(drone_id=drone_id, x_local=x_local, y_local=y_local, last_seen=now, ready=ready)
            task.pending_replan = True
            return
        info.x_local = x_local
        info.y_local = y_local
        info.last_seen = now
        if ready and not info.ready:
            info.ready = True
            task.pending_replan = True

    def handle_coverage(self, payload: dict):
        task_id = payload.get("task_id")
        if not task_id or task_id not in self.tasks:
            return
        task = self.tasks[task_id]
        updated = 0
        for cell in payload.get("cells", []):
            try:
                ix = int(cell[0])
                iy = int(cell[1])
            except Exception:
                continue
            if task.cell_inside_circle(ix, iy) and (ix, iy) not in task.explored:
                task.explored.add((ix, iy))
                updated += 1
        if updated:
            LOG.info("Task %s: +%d covered cells", task_id, updated)

    def prune(self):
        now = time.time()
        for task in self.tasks.values():
            removed = []
            for drone_id, info in list(task.drones.items()):
                if now - info.last_seen > FAILURE_TIMEOUT:
                    removed.append(drone_id)
                    del task.drones[drone_id]
            if removed:
                LOG.info("Task %s: removed inactive drones %s", task.task_id, removed)
                task.pending_replan = True

    def compute_assignments(self, task: TaskState) -> dict[str, list[list[int]]]:
        ready = {
            drone_id: info
            for drone_id, info in task.drones.items()
            if info.ready and drone_id in task.selected_drones
        }
        if not ready or len(ready) < len(task.selected_drones):
            return {}

        if len(task.selected_drones) == 1:
            seed_points = {task.selected_drones[0]: (0.0, 0.0)}
        else:
            seed_points = {}
            for idx, drone_id in enumerate(task.selected_drones):
                angle = (-math.pi / 2.0) + (2.0 * math.pi * idx / len(task.selected_drones))
                seed_points[drone_id] = (
                    PARTITION_RING_RADIUS_M * math.cos(angle),
                    PARTITION_RING_RADIUS_M * math.sin(angle),
                )

        assignments = {drone_id: [] for drone_id in ready}
        for ix, iy in task.available_cells():
            cx, cy = task.cell_center_xy(ix, iy)
            nearest = min(
                ready,
                key=lambda drone_id: math.hypot(cx - seed_points[drone_id][0], cy - seed_points[drone_id][1]),
            )
            assignments[nearest].append([ix, iy])
        return assignments

    def publish_assignments(self, task: TaskState):
        now = time.time()
        if not task.pending_replan:
            return
        if now - task.last_replan_time < REPLAN_INTERVAL:
            return
        assignments = self.compute_assignments(task)
        if not assignments:
            return
        task.plan_counter += 1
        task.last_replan_time = now
        task.pending_replan = False
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
        for drone_id, cells in assignments.items():
            payload = {
                "msg_type": "region_assignment",
                "task_id": task.task_id,
                "drone_id": drone_id,
                "cells": cells,
                "origin_xy": list(task.grid_origin),
                "cell_size": task.cell_size_m,
                "plan_id": task.plan_counter,
                "active_ids": sorted(assignments.keys()),
            }
            sock.sendto(json.dumps(payload).encode("utf-8"), (ASSIGNMENT_MCAST_GRP, ASSIGNMENT_MCAST_PORT))
            LOG.info("Task %s plan %s -> %s: %d cells", task.task_id, task.plan_counter, drone_id, len(cells))
        sock.close()


async def run():
    coordinator = Coordinator()
    loop = asyncio.get_running_loop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    sock.setblocking(True)
    LOG.info("Listening on %s:%d", LISTEN_HOST, LISTEN_PORT)
    while True:
        try:
            # Python 3.10 selector loops do not expose sock_recvfrom().
            data, _ = await loop.run_in_executor(None, sock.recvfrom, 65535)
            payload = json.loads(data.decode("utf-8"))
            msg_type = payload.get("msg_type")
            if msg_type == "search_registration":
                coordinator.handle_registration(payload)
            elif msg_type == "state_update":
                coordinator.handle_state(payload)
            elif msg_type == "coverage_update":
                coordinator.handle_coverage(payload)
            coordinator.prune()
            for task in coordinator.tasks.values():
                coordinator.publish_assignments(task)
        except Exception as exc:
            LOG.info("loop error: %s", exc)
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(run())
