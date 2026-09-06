from __future__ import annotations

import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mapa_silencio.demo import build_demo_document
from mapa_silencio.server import create_server


class ApiEndToEndTests(unittest.TestCase):
    def test_serves_replay_analysis_and_map_without_external_services(self) -> None:
        server = create_server(("127.0.0.1", 0), build_demo_document())
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base_url = f"http://127.0.0.1:{server.server_port}"

        with urlopen(f"{base_url}/api/scenario", timeout=2) as response:
            scenario = json.load(response)
        with urlopen(f"{base_url}/", timeout=2) as response:
            html = response.read().decode("utf-8")
        with urlopen(f"{base_url}/api/evidence", timeout=2) as response:
            evidence = json.load(response)

        self.assertEqual("simulated", scenario["metadata"]["data_nature"])
        self.assertGreaterEqual(len(scenario["analysis"]["anomalies"]), 3)
        self.assertIn("Pulso Territorial", html)
        self.assertIn("DADOS SINTÉTICOS", html)
        self.assertIn("Linha do tempo", html)
        self.assertTrue(evidence)
        self.assertEqual("urban-flood-1", evidence[0]["hypothesis_id"])
        self.assertEqual("aggregated_only", evidence[0]["public_visibility"])
        with urlopen(f"{base_url}/scenario.json", timeout=2) as response:
            self.assertEqual(scenario, json.load(response))
        for name in ("app.js", "map.js", "model.js", "styles.css"):
            with self.subTest(asset=name), urlopen(f"{base_url}/{name}", timeout=2) as response:
                self.assertEqual(200, response.status)
                self.assertGreater(len(response.read()), 100)


if __name__ == "__main__":
    unittest.main()
