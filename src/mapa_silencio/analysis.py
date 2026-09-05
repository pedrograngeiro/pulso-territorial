from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from statistics import mean, stdev
from typing import Any


_WEIGHTS = {
    "flood_reports": 0.35,
    "digital_activity": 0.25,
    "rainfall_mm_h": 0.30,
    "official_alert": 0.40,
}


def _score(measurement: Mapping[str, Any]) -> float:
    uncertainty = max(float(measurement.get("uncertainty", 0)), 1.0)
    return (float(measurement["observed"]) - float(measurement["expected"])) / uncertainty


def _qualifies(metric: str, score: float) -> bool:
    if metric == "digital_activity":
        return score <= -2.0
    return metric in {"flood_reports", "rainfall_mm_h", "official_alert"} and score >= 2.0


def _time_bucket(timestamp: str) -> str:
    instant = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return f"{instant.strftime('%A').lower()}-{instant.strftime('%H:%M')}"


def _learn_baselines(document: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str], dict[str, Any]]]:
    groups: dict[tuple[str, str, str], list[float]] = {}
    for sample in document.get("calibration", []):
        key = (sample["region_id"], sample["metric"], _time_bucket(sample["timestamp"]))
        groups.setdefault(key, []).append(float(sample["value"]))

    baselines: list[dict[str, Any]] = []
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for (region_id, metric, bucket), values in sorted(groups.items()):
        baseline = {
            "region_id": region_id,
            "metric": metric,
            "time_bucket": bucket,
            "expected_activity": round(mean(values), 3),
            "uncertainty": round(max(stdev(values) if len(values) > 1 else 1.0, 1.0), 3),
            "sample_count": len(values),
            "model_version": "regional-mean-v1",
        }
        baselines.append(baseline)
        index[(region_id, metric, bucket)] = baseline
    return baselines, index


def _timeline_with_baselines(document: Mapping[str, Any], baseline_index: Mapping[tuple[str, str, str], Mapping[str, Any]]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    for original_frame in document.get("frames", []):
        frame = {"timestamp": original_frame["timestamp"], "measurements": []}
        bucket = _time_bucket(original_frame["timestamp"])
        for original in original_frame.get("measurements", []):
            measurement = dict(original)
            baseline = baseline_index.get((measurement["region_id"], measurement["metric"], bucket))
            if "expected" not in measurement and baseline:
                measurement["expected"] = baseline["expected_activity"]
                measurement["uncertainty"] = baseline["uncertainty"]
            frame["measurements"].append(measurement)
        timeline.append(frame)
    return timeline


def analyze_dataset(document: Mapping[str, Any]) -> dict[str, Any]:
    """Analyze a normalized replay document through the public analytical seam."""
    baselines, baseline_index = _learn_baselines(document)
    timeline = _timeline_with_baselines(document, baseline_index)
    source_health = {
        source["id"]: source.get("health_status", "unknown")
        for source in document.get("sources", [])
    }
    anomalies: list[dict[str, Any]] = []

    for frame in timeline:
        by_region: dict[str, list[Mapping[str, Any]]] = {}
        for measurement in frame.get("measurements", []):
            by_region.setdefault(measurement["region_id"], []).append(measurement)

        for region_id, measurements in by_region.items():
            evidence: list[dict[str, Any]] = []
            has_spike = False
            has_silence = False
            confidence = 0.0
            severity = 0.0

            for measurement in measurements:
                metric = measurement["metric"]
                score = _score(measurement)
                if not _qualifies(metric, score):
                    continue
                source_id = measurement["source_id"]
                health_factor = 1.0 if source_health.get(source_id) == "healthy" else 0.5
                contribution = _WEIGHTS[metric] * min(abs(score) / 3.0, 1.0) * health_factor
                confidence += contribution
                severity = max(severity, min(abs(score) / 5.0, 1.0))
                has_silence = has_silence or metric == "digital_activity"
                has_spike = has_spike or metric == "flood_reports"
                evidence.append(
                    {
                        "evidence_type": "negative_signal" if metric == "digital_activity" else "positive_signal",
                        "source_id": source_id,
                        "timestamp": frame["timestamp"],
                        "metric": metric,
                        "observed_value": measurement["observed"],
                        "expected_value": measurement["expected"],
                        "standardized_deviation": round(score, 3),
                        "contribution": round(contribution, 3),
                        "confidence": round(min(abs(score) / 3.0, 1.0) * health_factor, 3),
                        "public_visibility": "aggregated_only",
                    }
                )

            if not (has_spike or has_silence):
                continue
            anomaly_type = "mixed" if has_spike and has_silence else "spike" if has_spike else "silence"
            metrics = ", ".join(sorted(item["metric"] for item in evidence))
            observed_values = {item["metric"]: item["observed_value"] for item in evidence}
            expected_values = {item["metric"]: item["expected_value"] for item in evidence}
            anomalies.append(
                {
                    "region_id": region_id,
                    "started_at": frame["timestamp"],
                    "anomaly_type": anomaly_type,
                    "observed_value": observed_values,
                    "expected_value": expected_values,
                    "severity": round(severity, 3),
                    "confidence": round(min(confidence, 0.98), 3),
                    "explanation": f"Desvios agregados detectados em: {metrics}.",
                    "evidence": evidence,
                    "data_nature": "inferred",
                }
            )

    hypotheses = _build_hypotheses(anomalies, document.get("regions", []))
    hypothesis_id = hypotheses[0]["id"] if hypotheses else None
    all_evidence = [
        {**item, "hypothesis_id": hypothesis_id}
        for anomaly in anomalies
        for item in anomaly["evidence"]
    ]
    return {
        "baselines": baselines,
        "timeline": timeline,
        "anomalies": anomalies,
        "hypotheses": hypotheses,
        "evidence": all_evidence,
    }


def _build_hypotheses(anomalies: list[dict[str, Any]], regions: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not anomalies:
        return []
    affected = sorted({anomaly["region_id"] for anomaly in anomalies})
    probable_start = min(anomaly["started_at"] for anomaly in anomalies)
    confidence = round(sum(item["confidence"] for item in anomalies) / len(anomalies), 3)
    origin, direction, speed, interval, method = _estimate_propagation(anomalies, regions)
    return [
        {
            "id": "urban-flood-1",
            "event_type": "urban_flood",
            "probable_origin": origin,
            "probable_start": probable_start,
            "affected_region_ids": affected,
            "affected_geometry": "municipality_set",
            "propagation_direction": direction,
            "propagation_speed_kmh": speed,
            "propagation_speed_interval_kmh": interval,
            "propagation_method": method,
            "confidence": confidence,
            "status": "unverified",
            "data_nature": "inferred",
            "limitations": [
                "Anomalia não confirma desastre nem causalidade.",
                "Silêncio digital também pode refletir falha da fonte ou mudança de comportamento.",
                "Revisão humana e corroboração oficial são obrigatórias.",
            ],
        }
    ]


def _estimate_propagation(
    anomalies: list[dict[str, Any]], regions: list[Mapping[str, Any]]
) -> tuple[str | None, str | None, float | None, list[float] | None, str | None]:
    first_onset: dict[str, datetime] = {}
    for anomaly in anomalies:
        instant = datetime.fromisoformat(anomaly["started_at"].replace("Z", "+00:00"))
        previous = first_onset.get(anomaly["region_id"])
        if previous is None or instant < previous:
            first_onset[anomaly["region_id"]] = instant
    if len(first_onset) < 2:
        return None, None, None, None, None
    ordered = sorted(first_onset.items(), key=lambda item: item[1])
    if ordered[0][1] == ordered[1][1] or ordered[-1][1] == ordered[0][1]:
        return None, None, None, None, None
    region_index = {region["id"]: region for region in regions}
    if ordered[0][0] not in region_index or ordered[-1][0] not in region_index:
        return None, None, None, None, None
    origin_id, origin_time = ordered[0]
    last_id, last_time = ordered[-1]
    origin_point = region_index[origin_id]["centroid"]
    last_point = region_index[last_id]["centroid"]
    hours = (last_time - origin_time).total_seconds() / 3600.0
    distance = _haversine_km(origin_point, last_point)
    speed = round(distance / hours, 1)
    direction = _cardinal_direction(last_point[0] - origin_point[0], last_point[1] - origin_point[1])
    interval = [round(speed * 0.5, 1), round(speed * 1.5, 1)]
    method = "Diferença entre o primeiro início anômalo por município; intervalo heurístico de ±50%, não hidrológico."
    return origin_id, direction, speed, interval, method


def _haversine_km(left: list[float], right: list[float]) -> float:
    lon1, lat1, lon2, lat2 = map(radians, [left[0], left[1], right[0], right[1]])
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(value))


def _cardinal_direction(delta_lon: float, delta_lat: float) -> str:
    if abs(delta_lon) >= abs(delta_lat) * 2:
        return "leste" if delta_lon > 0 else "oeste"
    if abs(delta_lat) >= abs(delta_lon) * 2:
        return "norte" if delta_lat > 0 else "sul"
    return ("nordeste" if delta_lat > 0 else "sudeste") if delta_lon > 0 else ("noroeste" if delta_lat > 0 else "sudoeste")
