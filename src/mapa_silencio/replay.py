from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MAX_REPLAY_BYTES = 10 * 1024 * 1024


class ReplayValidationError(ValueError):
    pass


def load_replay(path: str | Path) -> dict[str, Any]:
    """Load a bounded JSON replay and validate its common document interface."""
    replay_path = Path(path)
    if replay_path.suffix.lower() != ".json":
        raise ReplayValidationError("replay must be a JSON file")
    if replay_path.stat().st_size > MAX_REPLAY_BYTES:
        raise ReplayValidationError("replay exceeds the 10 MiB local safety limit")
    try:
        document = json.loads(replay_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReplayValidationError("replay is not valid UTF-8 JSON") from error
    if not isinstance(document, dict):
        raise ReplayValidationError("replay root must be an object")
    required = {"metadata", "sources", "regions", "frames"}
    missing = sorted(required - document.keys())
    if missing:
        raise ReplayValidationError(f"replay is missing required fields: {', '.join(missing)}")
    nature = document["metadata"].get("data_nature")
    if nature not in {"real", "simulated", "mixed"}:
        raise ReplayValidationError("metadata.data_nature must be real, simulated, or mixed")
    if nature in {"real", "mixed"} and not document["metadata"].get("usage_basis"):
        raise ReplayValidationError("real or mixed replay requires metadata.usage_basis")
    return document
