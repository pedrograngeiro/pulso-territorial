from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


REGIONS = [
    {"id": "porto-alegre", "name": "Porto Alegre", "state": "RS", "centroid": [-51.2300, -30.0331], "geometry_nature": "schematic"},
    {"id": "canoas", "name": "Canoas", "state": "RS", "centroid": [-51.1836, -29.9177], "geometry_nature": "schematic"},
    {"id": "eldorado-do-sul", "name": "Eldorado do Sul", "state": "RS", "centroid": [-51.6187, -30.0847], "geometry_nature": "schematic"},
]

SOURCES = [
    {
        "id": "sim-social",
        "name": "Gerador de atividade digital agregada",
        "source_type": "simulator",
        "license_status": "project_generated",
        "terms_checked_at": "2026-08-30",
        "health_status": "healthy",
        "data_nature": "simulated",
        "usage_restrictions": "Somente demonstração; não representa publicações reais.",
    },
    {
        "id": "sim-rain",
        "name": "Gerador de chuva agregada",
        "source_type": "simulator",
        "license_status": "project_generated",
        "terms_checked_at": "2026-08-30",
        "health_status": "healthy",
        "data_nature": "simulated",
        "usage_restrictions": "Somente demonstração; não representa medição oficial.",
    },
]


def build_demo_document() -> dict[str, Any]:
    """Return a deterministic, aggregate-only urban-flood replay."""
    start = datetime(2024, 5, 3, 8, 0, tzinfo=timezone.utc)
    baseline_values = {
        "porto-alegre": {"flood_reports": 2, "digital_activity": 30, "rainfall_mm_h": 3},
        "canoas": {"flood_reports": 1, "digital_activity": 20, "rainfall_mm_h": 2},
        "eldorado-do-sul": {"flood_reports": 1, "digital_activity": 12, "rainfall_mm_h": 2},
    }
    calibration: list[dict[str, Any]] = []
    variations = (-1, 0, 1, 0)
    for weeks_ago, variation in enumerate(variations, start=1):
        calibration_day = start - timedelta(days=7 * weeks_ago)
        for frame_index in range(8):
            timestamp = calibration_day + timedelta(minutes=30 * frame_index)
            for region in REGIONS:
                for metric, base in baseline_values[region["id"]].items():
                    value = max(0, base + (variation if metric != "rainfall_mm_h" else 0))
                    calibration.append(
                        {"timestamp": _iso(timestamp), "region_id": region["id"], "metric": metric, "value": value}
                    )

    observed = {
        "porto-alegre": {
            "flood_reports": [2, 2, 9, 15, 18, 16, 12, 9],
            "digital_activity": [30, 31, 29, 15, 8, 5, 4, 5],
            "rainfall_mm_h": [3, 18, 35, 42, 39, 28, 20, 12],
        },
        "canoas": {
            "flood_reports": [1, 1, 1, 3, 8, 12, 11, 8],
            "digital_activity": [20, 20, 19, 18, 8, 5, 4, 5],
            "rainfall_mm_h": [2, 4, 12, 25, 38, 35, 25, 16],
        },
        "eldorado-do-sul": {
            "flood_reports": [1, 1, 1, 1, 2, 7, 10, 9],
            "digital_activity": [12, 12, 12, 11, 10, 4, 2, 2],
            "rainfall_mm_h": [2, 2, 4, 10, 21, 34, 31, 22],
        },
    }
    frames: list[dict[str, Any]] = []
    for frame_index in range(8):
        timestamp = start + timedelta(minutes=30 * frame_index)
        measurements: list[dict[str, Any]] = []
        for region in REGIONS:
            region_values = observed[region["id"]]
            for metric in ("flood_reports", "digital_activity", "rainfall_mm_h"):
                measurements.append(
                    {
                        "id": f"obs-{frame_index}-{region['id']}-{metric}",
                        "region_id": region["id"],
                        "metric": metric,
                        "observed": region_values[metric][frame_index],
                        "observed_at": _iso(timestamp),
                        "ingested_at": _iso(timestamp),
                        "source_id": "sim-rain" if metric == "rainfall_mm_h" else "sim-social",
                        "content_category": metric,
                        "data_nature": "simulated",
                        "provenance": "deterministic-demo-v1",
                        "usage_restrictions": "synthetic-demo-only",
                        "location_precision": "municipality",
                        "location_confidence": 1.0,
                        "raw_content_retention_policy": "none-aggregates-only",
                    }
                )
        frames.append({"timestamp": _iso(timestamp), "measurements": measurements})

    return {
        "metadata": {
            "scenario_id": "rs-urban-flood-synthetic-v1",
            "title": "Propagação sintética de enchente urbana — RS",
            "description": "Cenário inteiramente sintético inspirado apenas na dinâmica geral de uma enchente; não reproduz relatos nem medições reais.",
            "data_nature": "simulated",
            "generated_by": "deterministic-demo-v1",
            "timezone_original": "America/Sao_Paulo",
            "warning": "Não usar para resposta operacional ou afirmações sobre pessoas e infraestrutura.",
        },
        "sources": SOURCES,
        "regions": REGIONS,
        "ground_truth": {
            "nature": "synthetic_reference",
            "event_type": "urban_flood",
            "affected_since": {
                "porto-alegre": "2024-05-03T09:00:00Z",
                "canoas": "2024-05-03T10:00:00Z",
                "eldorado-do-sul": "2024-05-03T10:30:00Z",
            },
        },
        "calibration": calibration,
        "frames": frames,
    }


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
