from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mapa_silencio.rio_demo import build_rio_document
from mapa_silencio.analysis import analyze_dataset

class RioDemoTests(unittest.TestCase):
    def test_state_geometry_and_synthetic_observations_are_distinct(self):
        document = build_rio_document()
        self.assertEqual(6, len(document["regions"]))
        self.assertEqual({"RJ"}, {region["state"] for region in document["regions"]})
        self.assertEqual("simulated", document["metadata"]["data_nature"])
        self.assertEqual("FeatureCollection", document["map_geometry"]["type"])
        self.assertTrue(document["map_geometry"]["features"])
        analysis = analyze_dataset(document)
        self.assertEqual(8, len(analysis["timeline"]))
        self.assertTrue(all("expected" in item for frame in analysis["timeline"] for item in frame["measurements"]))
        self.assertTrue(all(item["data_nature"] == "simulated" for frame in document["frames"] for item in frame["measurements"]))
        quiet = {"campos-dos-goytacazes", "cabo-frio"}
        self.assertFalse(any(item["region_id"] in quiet for item in analysis["anomalies"]))
        self.assertTrue(any(item["region_id"] == "petropolis" for item in analysis["anomalies"]))
