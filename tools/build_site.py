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
    for name in ("index.html", "styles.css", "app.js", "map.js", "model.js", "ioda.html", "ioda.css", "ioda-view.js", "rio-state.geojson", "monitoring.html", "monitoring.css", "monitoring.js", "monitoring-model.js", "rio-municipalities.geojson"):
        shutil.copy2(ROOT / "src" / "mapa_silencio" / "static" / name, output / name)
    for name in ("LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / name, output / name)
    legal_dir = output / "docs" / "third-party"
    legal_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "docs" / "third-party" / "ibge-malha-notas.pdf", legal_dir / "ibge-malha-notas.pdf")
    document = build_rio_document()
    scenario = {**document, "analysis": analyze_dataset(document)}
    (output / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False), encoding="utf-8")
    assert scenario["metadata"]["data_nature"] == "simulated"
    assert len(scenario["analysis"]["timeline"]) == 8
    print(f"Site estático gerado em {output}: interface e cenário sintético. As telas de dados reais requerem o servidor Python.")


if __name__ == "__main__":
    main()
