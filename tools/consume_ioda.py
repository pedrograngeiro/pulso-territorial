"""Fetch and save a real, statewide IODA snapshot; no account or API key is needed."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mapa_silencio.ioda import IodaClient, IodaError


def main() -> int:
    parser = argparse.ArgumentParser(description="Consumir conectividade estadual do Rio de Janeiro no IODA")
    parser.add_argument("--hours", type=int, default=24, help="Janela entre 1 e 168 horas (padrão: 24)")
    parser.add_argument("--output", type=Path, default=ROOT / ".cache" / "ioda" / "latest.json")
    args = parser.parse_args()
    try:
        snapshot = IodaClient().snapshot(hours=args.hours)
    except (IodaError, ValueError) as error:
        print(f"Falha na consulta: {error}", file=sys.stderr)
        return 1
    if snapshot["status"] == "unavailable":
        print("IODA não retornou séries utilizáveis. A coleta anterior foi preservada.", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(args.output)
    print(f"IODA: {snapshot['entity']['name']} ({snapshot['entity']['code']}) | escopo estadual | {snapshot['status']}")
    for signal in snapshot["signals"]:
        latest = signal["latest"]
        print(f"  {signal['id']}: {signal['status']} | último valor: {latest['value'] if latest else 'sem dados'} | {latest['timestamp'] if latest else '-'}")
    print(f"Arquivo: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
