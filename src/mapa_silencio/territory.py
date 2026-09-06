"""Municipal assignment is approximate; never infer geography from an ASN."""
from __future__ import annotations

import json
import math
from pathlib import Path


def polygons(geometry):
    return geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]


def in_ring(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:] + ring[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0]) * (y-a[1]) / (b[1]-a[1]) + a[0]:
            inside = not inside
    return inside


def contains(point, geometry):
    return any(in_ring(point, poly[0]) and not any(in_ring(point, hole) for hole in poly[1:]) for poly in polygons(geometry))


def boundary_distance_km(point, geometry):
    scale = 111.32 * math.cos(math.radians(point[1]))
    best = float("inf")
    for poly in polygons(geometry):
        for ring in poly:
            for a, b in zip(ring, ring[1:] + ring[:1]):
                ax, ay = (a[0]-point[0])*scale, (a[1]-point[1])*111.32
                bx, by = (b[0]-point[0])*scale, (b[1]-point[1])*111.32
                dx, dy = bx-ax, by-ay
                t = max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx or dy else 0
                best = min(best, math.hypot(ax+t*dx, ay+t*dy))
    return best


class Territory:
    def __init__(self, collection=None):
        self.collection = collection or json.loads(Path(__file__).with_name("static").joinpath("rio-municipalities.geojson").read_text(encoding="utf-8"))
        self.features = self.collection["features"]

    def locate(self, point):
        matches = [f for f in self.features if contains(point, f["geometry"])]
        # Public probe coordinates are obfuscated; simplified boundaries add uncertainty.
        if len(matches) != 1 or boundary_distance_km(point, matches[0]["geometry"]) < 1:
            return None
        return matches[0]["properties"]["id"]

    def municipalities(self):
        return [{k: f["properties"][k] for k in ("id", "name", "centroid")} for f in self.features]
