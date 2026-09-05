from __future__ import annotations

from datetime import datetime
from typing import Any

from .analysis import analyze_dataset


def evaluate_detectors(document: dict[str, Any]) -> dict[str, Any]:
    """Compare four detector variants against a declared replay reference."""
    analyzed = analyze_dataset(document)
    truth_definition = document["ground_truth"]
    onset = {
        region_id: _instant(timestamp)
        for region_id, timestamp in truth_definition["affected_since"].items()
    }
    truth: set[tuple[str, str]] = set()
    scores: dict[tuple[str, str], dict[str, float]] = {}
    for frame in analyzed["timeline"]:
        timestamp = frame["timestamp"]
        instant = _instant(timestamp)
        by_region: dict[str, dict[str, float]] = {}
        for measurement in frame["measurements"]:
            uncertainty = max(float(measurement.get("uncertainty", 1)), 1.0)
            score = (float(measurement["observed"]) - float(measurement["expected"])) / uncertainty
            by_region.setdefault(measurement["region_id"], {})[measurement["metric"]] = score
        for region_id, metric_scores in by_region.items():
            key = (region_id, timestamp)
            scores[key] = metric_scores
            if region_id in onset and instant >= onset[region_id]:
                truth.add(key)

    variants = {
        "spike_only": lambda item: item.get("flood_reports", 0) >= 2,
        "silence_only": lambda item: item.get("digital_activity", 0) <= -2,
        "combined": lambda item: item.get("flood_reports", 0) >= 2 or item.get("digital_activity", 0) <= -2,
        "combined_with_physical": lambda item: (
            item.get("flood_reports", 0) >= 2 or item.get("digital_activity", 0) <= -2
        ) and item.get("rainfall_mm_h", 0) >= 2,
    }
    reports: dict[str, dict[str, Any]] = {}
    all_regions = {region["id"] for region in document["regions"]}
    for name, detector in variants.items():
        predictions = {key for key, item in scores.items() if detector(item)}
        true_positive = len(predictions & truth)
        false_positive = len(predictions - truth)
        false_negative = len(truth - predictions)
        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        delays = _detection_delays(predictions, onset)
        confidences = {
            key: min(max(abs(scores[key].get("flood_reports", 0)), abs(scores[key].get("digital_activity", 0))) / 5, 0.99)
            for key in predictions
        }
        brier_terms = [
            (confidences.get(key, 0.0) - (1.0 if key in truth else 0.0)) ** 2
            for key in scores
        ]
        covered = {region_id for region_id, _ in scores}
        partial_source_recall = {}
        for missing_metric in ("flood_reports", "digital_activity", "rainfall_mm_h"):
            dropout_predictions = {
                key for key, item in scores.items() if detector({metric: value for metric, value in item.items() if metric != missing_metric})
            }
            dropout_true_positive = len(dropout_predictions & truth)
            partial_source_recall[f"without_{missing_metric}"] = round(dropout_true_positive / max(len(truth), 1), 3)
        reports[name] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(2 * precision * recall / max(precision + recall, 1e-9), 3),
            "false_positives": false_positive,
            "detection_delay_minutes": round(sum(delays) / len(delays), 1) if delays else None,
            "start_time_error_minutes": round(sum(abs(delay) for delay in delays) / len(delays), 1) if delays else None,
            "geographic_error_km": 0.0 if true_positive else None,
            "confidence_brier": round(sum(brier_terms) / len(brier_terms), 3),
            "coverage": round(len(covered) / max(len(all_regions), 1), 3),
            "partial_source_recall": partial_source_recall,
            "evaluated_buckets": len(scores),
        }
    return {
        "reference_nature": truth_definition["nature"],
        "scenario_id": document["metadata"]["scenario_id"],
        "detectors": reports,
        "limitations": [
            "Referência e observações são sintéticas; métricas não demonstram validade externa.",
            "Erro geográfico é zero apenas porque a referência usa os mesmos municípios discretos.",
            "Calibração requer múltiplos eventos históricos autorizados antes de uso operacional.",
        ],
    }


def _detection_delays(predictions: set[tuple[str, str]], onset: dict[str, datetime]) -> list[float]:
    delays: list[float] = []
    for region_id, true_start in onset.items():
        predicted = sorted(_instant(timestamp) for region, timestamp in predictions if region == region_id)
        if predicted:
            delays.append((predicted[0] - true_start).total_seconds() / 60.0)
    return delays


def _instant(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
