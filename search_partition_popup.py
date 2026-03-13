#!/usr/bin/env python3
"""Standalone Tkinter popup for search partition visualization."""

from __future__ import annotations

import json
import math
import sys
import tkinter as tk
from pathlib import Path


def _load_payload(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_popup(payload: dict):
    radius_m = float(payload["search_radius_m"])
    lane_spacing_m = float(payload["lane_spacing_m"])
    task_id = payload["task_id"]
    drones = payload["drones"]
    selected = payload["selected_drones"]

    width = 980
    height = 980
    margin = 70
    scale = (min(width, height) - 2 * margin) / max(1.0, 2 * (radius_m + 25))

    def sx(x_m: float) -> float:
        return width / 2 + x_m * scale

    def sy(y_m: float) -> float:
        return height / 2 - y_m * scale

    root = tk.Tk()
    root.title(f"Search Partition Map - {task_id}")
    root.geometry(f"{width}x{height}")
    root.configure(bg="white")

    header = tk.Label(
        root,
        text=f"Search Area Assignment\nTask: {task_id} | Radius: {radius_m:.0f} m | Lane Spacing: {lane_spacing_m:.0f} m",
        bg="white",
        fg="#111111",
        font=("Arial", 13, "bold"),
        justify="center",
    )
    header.pack(pady=(10, 0))

    canvas = tk.Canvas(root, width=width, height=height - 70, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.create_oval(
        sx(-radius_m),
        sy(radius_m),
        sx(radius_m),
        sy(-radius_m),
        outline="#111111",
        width=2,
        fill="#f4efe5",
    )

    for grid_m in range(-int(radius_m), int(radius_m) + 1, 25):
        canvas.create_line(sx(grid_m), sy(radius_m), sx(grid_m), sy(-radius_m), fill="#e5e2da", width=1)
        canvas.create_line(sx(-radius_m), sy(grid_m), sx(radius_m), sy(grid_m), fill="#e5e2da", width=1)

    canvas.create_oval(sx(-2), sy(2), sx(2), sy(-2), fill="#111111", outline="#111111")
    canvas.create_text(sx(0) + 20, sy(0) - 10, text="Center", fill="#111111", font=("Arial", 10, "bold"))

    for drone_id in selected:
        info = drones[drone_id]
        color = info["color"]
        cell_size = float(info.get("sample_step_m", 20.0))
        half = cell_size / 2.0

        for x_m, y_m in info.get("cells_local", []):
            canvas.create_rectangle(
                sx(x_m - half),
                sy(y_m + half),
                sx(x_m + half),
                sy(y_m - half),
                outline=color,
                fill=color,
                stipple="gray25",
                width=1,
            )

        waypoints = info.get("waypoints_local", [])
        if len(waypoints) >= 2:
            coords = []
            for x_m, y_m in waypoints:
                coords.extend([sx(x_m), sy(y_m)])
            canvas.create_line(*coords, fill=color, width=3)

        centroid_x, centroid_y = info.get("cell_centroid_local", [0.0, 0.0])
        canvas.create_oval(
            sx(centroid_x - 3),
            sy(centroid_y + 3),
            sx(centroid_x + 3),
            sy(centroid_y - 3),
            fill=color,
            outline="white",
            width=2,
        )
        canvas.create_text(
            sx(centroid_x) + 20,
            sy(centroid_y) - 12,
            text=drone_id,
            fill=color,
            font=("Arial", 10, "bold"),
        )

    legend_y = 18
    for drone_id in selected:
        color = drones[drone_id]["color"]
        canvas.create_rectangle(20, legend_y - 8, 34, legend_y + 6, fill=color, outline=color)
        canvas.create_text(42, legend_y, text=drone_id, anchor="w", fill="#111111", font=("Arial", 10, "bold"))
        legend_y += 22

    root.mainloop()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: search_partition_popup.py <payload.json>")
    payload_path = Path(sys.argv[1]).expanduser().resolve()
    payload = _load_payload(str(payload_path))
    _build_popup(payload)


if __name__ == "__main__":
    main()
