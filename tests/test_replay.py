from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mapa_silencio.demo import build_demo_document
from mapa_silencio.replay import ReplayValidationError, load_replay


class ReplayAdapterTests(unittest.TestCase):
    def test_loads_a_versioned_json_replay_through_the_common_document_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scenario.json"
            path.write_text(json.dumps(build_demo_document()), encoding="utf-8")

            document = load_replay(path)

        self.assertEqual("rs-urban-flood-synthetic-v1", document["metadata"]["scenario_id"])
        self.assertEqual("simulated", document["metadata"]["data_nature"])

    def test_rejects_a_replay_that_hides_its_data_nature(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unknown.json"
            path.write_text('{"metadata": {}, "sources": [], "regions": [], "frames": []}', encoding="utf-8")

            with self.assertRaisesRegex(ReplayValidationError, "data_nature"):
                load_replay(path)


if __name__ == "__main__":
    unittest.main()
