"""Export the default synthetic replay and frontend as a standalone static site."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mapa_silencio.analysis import analyze_dataset
from mapa_silencio.rio_demo import build_rio_document


def main() -> None:
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    for name in ("index.html", "styles.css", "app.js", "map.js", "model.js"):
        shutil.copy2(ROOT / "src" / "mapa_silencio" / "static" / name, output / name)
    document = build_rio_document()
    scenario = {**document, "analysis": analyze_dataset(document)}
    (output / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False), encoding="utf-8")
    assert scenario["metadata"]["data_nature"] == "simulated"
    assert len(scenario["analysis"]["timeline"]) == 8
    print(f"Site estático gerado em {output}: 5 arquivos de interface e cenário sintético.")


if __name__ == "__main__":
    main()
