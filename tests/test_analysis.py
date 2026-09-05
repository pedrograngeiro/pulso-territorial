from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mapa_silencio.analysis import analyze_dataset
from mapa_silencio.demo import build_demo_document
from mapa_silencio.validation import evaluate_detectors


class AnalyzeDatasetTests(unittest.TestCase):
    def test_compares_four_detectors_against_synthetic_ground_truth(self) -> None:
        report = evaluate_detectors(build_demo_document())

        self.assertEqual(
            ["spike_only", "silence_only", "combined", "combined_with_physical"],
            list(report["detectors"]),
        )
        for metrics in report["detectors"].values():
            self.assertIn("precision", metrics)
            self.assertIn("recall", metrics)
            self.assertIn("false_positives", metrics)
            self.assertIn("detection_delay_minutes", metrics)
            self.assertIn("coverage", metrics)
            self.assertEqual(
                {"without_flood_reports", "without_digital_activity", "without_rainfall_mm_h"},
                set(metrics["partial_source_recall"]),
            )
        outcomes = {
            (metrics["precision"], metrics["recall"], metrics["detection_delay_minutes"])
            for metrics in report["detectors"].values()
        }
        self.assertGreater(len(outcomes), 1)
        self.assertEqual("synthetic_reference", report["reference_nature"])

    def test_estimates_propagation_only_when_multiple_regions_have_distinct_onsets(self) -> None:
        result = analyze_dataset(build_demo_document())

        hypothesis = result["hypotheses"][0]
        self.assertEqual("porto-alegre", hypothesis["probable_origin"])
        self.assertEqual("oeste", hypothesis["propagation_direction"])
        self.assertGreater(hypothesis["propagation_speed_kmh"], 0)
        self.assertIn("propagation_method", hypothesis)

    def test_learns_regional_baseline_for_matching_weekday_and_time_bucket(self) -> None:
        document = {
            "metadata": {"scenario_id": "baseline-example", "data_nature": "simulated"},
            "sources": [
                {"id": "social", "name": "Simulador", "source_type": "simulator", "health_status": "healthy"}
            ],
            "regions": [{"id": "r1", "name": "Município Exemplo", "centroid": [-51.2, -30.0]}],
            "calibration": [
                {"timestamp": "2024-04-05T12:00:00Z", "region_id": "r1", "metric": "flood_reports", "value": 2},
                {"timestamp": "2024-04-12T12:00:00Z", "region_id": "r1", "metric": "flood_reports", "value": 4},
                {"timestamp": "2024-04-19T12:00:00Z", "region_id": "r1", "metric": "flood_reports", "value": 3},
            ],
            "frames": [
                {
                    "timestamp": "2024-05-03T12:00:00Z",
                    "measurements": [
                        {"region_id": "r1", "metric": "flood_reports", "observed": 8, "source_id": "social"}
                    ],
                }
            ],
        }

        result = analyze_dataset(document)

        baseline = result["baselines"][0]
        self.assertEqual("r1", baseline["region_id"])
        self.assertEqual("friday-12:00", baseline["time_bucket"])
        self.assertEqual(3.0, baseline["expected_activity"])
        self.assertEqual(1.0, baseline["uncertainty"])
        self.assertEqual(3, baseline["sample_count"])
        self.assertEqual("regional-mean-v1", baseline["model_version"])
        self.assertEqual(3.0, result["timeline"][0]["measurements"][0]["expected"])

    def test_fuses_spike_silence_and_rain_as_explainable_mixed_anomaly(self) -> None:
        document = {
            "metadata": {"scenario_id": "worked-example", "data_nature": "simulated"},
            "sources": [
                {"id": "social", "name": "Relatos sintéticos", "source_type": "simulator", "health_status": "healthy"},
                {"id": "rain", "name": "Chuva sintética", "source_type": "simulator", "health_status": "healthy"},
            ],
            "regions": [
                {"id": "r1", "name": "Município Exemplo", "centroid": [-51.2, -30.0]}
            ],
            "frames": [
                {
                    "timestamp": "2024-05-03T12:00:00Z",
                    "measurements": [
                        {"region_id": "r1", "metric": "flood_reports", "observed": 18, "expected": 4, "uncertainty": 2, "source_id": "social"},
                        {"region_id": "r1", "metric": "digital_activity", "observed": 3, "expected": 15, "uncertainty": 3, "source_id": "social"},
                        {"region_id": "r1", "metric": "rainfall_mm_h", "observed": 42, "expected": 5, "uncertainty": 5, "source_id": "rain"},
                    ],
                }
            ],
        }

        result = analyze_dataset(document)

        anomaly = result["anomalies"][0]
        self.assertEqual("mixed", anomaly["anomaly_type"])
        self.assertEqual("r1", anomaly["region_id"])
        self.assertGreaterEqual(anomaly["confidence"], 0.8)
        self.assertEqual(
            ["digital_activity", "flood_reports", "rainfall_mm_h"],
            sorted(item["metric"] for item in anomaly["evidence"]),
        )
        self.assertEqual("inferred", anomaly["data_nature"])

        hypothesis = result["hypotheses"][0]
        self.assertEqual("urban_flood", hypothesis["event_type"])
        self.assertEqual("unverified", hypothesis["status"])
        self.assertIn("r1", hypothesis["affected_region_ids"])
        self.assertIsNone(hypothesis["propagation_direction"])
        self.assertTrue(hypothesis["limitations"])


if __name__ == "__main__":
    unittest.main()
