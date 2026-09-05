"""Synthetic Rio de Janeiro scenario over an IBGE state outline."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any
from .demo import build_demo_document

RIO_REGIONS = [
    {"id": "rio-de-janeiro", "name": "Rio de Janeiro", "state": "RJ", "centroid": [-43.1729, -22.9068], "label_offset": [-35, 40]},
    {"id": "petropolis", "name": "Petrópolis", "state": "RJ", "centroid": [-43.1787, -22.5112], "label_offset": [-75, -20]},
    {"id": "nova-friburgo", "name": "Nova Friburgo", "state": "RJ", "centroid": [-42.5311, -22.2819], "label_offset": [-15, -45]},
    {"id": "campos-dos-goytacazes", "name": "Campos dos Goytacazes", "state": "RJ", "centroid": [-41.3235, -21.7622], "label_offset": [20, -42]},
    {"id": "cabo-frio", "name": "Cabo Frio", "state": "RJ", "centroid": [-42.0186, -22.8894], "label_offset": [45, 34]},
    {"id": "angra-dos-reis", "name": "Angra dos Reis", "state": "RJ", "centroid": [-44.3181, -23.0067], "label_offset": [-25, 38]},
]
PROFILES = [("porto-alegre", 1, False), ("porto-alegre", 0, False), ("canoas", 1, False), ("canoas", 0, True), ("eldorado-do-sul", 0, True), ("eldorado-do-sul", 0, False)]


def build_rio_document() -> dict[str, Any]:
    original = build_demo_document()
    document = deepcopy(original)
    document["regions"] = [{**region, "geometry_nature": "schematic"} for region in RIO_REGIONS]
    document["metadata"].update(
        scenario_id="rj-silence-synthetic-v1",
        title="Silêncio digital no estado do Rio de Janeiro",
        description="Cenário fictício de seis municípios fluminenses. Não reproduz um desastre real.",
        generated_by="rio-demo-v1",
    )
    document["map_geometry"] = json.loads(Path(__file__).with_name("static").joinpath("rio-state.geojson").read_text(encoding="utf-8"))
    document["map_attribution"] = {
        "name": "IBGE — malha simplificada do estado do Rio de Janeiro",
        "url": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/33?formato=application/vnd.geo%2Bjson&qualidade=minima",
        "retrieved_at": "2026-09-05",
        "usage": "Contorno de referência; não delimita áreas afetadas.",
    }
    shift = datetime.fromisoformat("2026-09-05T11:00:00+00:00") - datetime.fromisoformat(original["frames"][0]["timestamp"].replace("Z", "+00:00"))

    def shifted(timestamp: str) -> str:
        return (datetime.fromisoformat(timestamp.replace("Z", "+00:00")) + shift).isoformat().replace("+00:00", "Z")

    document["calibration"] = []
    for region, (profile, delay, quiet) in zip(document["regions"], PROFILES):
        for sample in original["calibration"]:
            if sample["region_id"] == profile:
                document["calibration"].append({**sample, "region_id": region["id"], "timestamp": shifted(sample["timestamp"])})
    for index, frame in enumerate(document["frames"]):
        frame["timestamp"] = shifted(original["frames"][index]["timestamp"])
        frame["measurements"] = []
        for region, (profile, delay, quiet) in zip(document["regions"], PROFILES):
            source_frame = original["frames"][0 if quiet else max(0, index - delay)]
            for sample in source_frame["measurements"]:
                if sample["region_id"] == profile:
                    frame["measurements"].append({
                        **sample,
                        "id": f"rj-{index}-{region['id']}-{sample['metric']}",
                        "region_id": region["id"],
                        "observed_at": frame["timestamp"],
                        "ingested_at": frame["timestamp"],
                        "provenance": "rio-demo-v1",
                    })
    document["ground_truth"]["affected_since"] = {
        region["id"]: (datetime.fromisoformat(original["ground_truth"]["affected_since"][profile].replace("Z", "+00:00")) + shift + timedelta(minutes=delay * 30)).isoformat().replace("+00:00", "Z")
        for region, (profile, delay, quiet) in zip(document["regions"], PROFILES)
        if not quiet
    }
    return document
