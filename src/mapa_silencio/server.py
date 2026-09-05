from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .analysis import analyze_dataset
from .rio_demo import build_rio_document
from .replay import load_replay
from .validation import evaluate_detectors


STATIC_DIR = Path(__file__).with_name("static")


def create_server(address: tuple[str, int], document: dict[str, Any]) -> ThreadingHTTPServer:
    analysis = analyze_dataset(document)
    validation = evaluate_detectors(document) if "ground_truth" in document else None
    scenario = {**document, "analysis": analysis}
    api_payloads = {
        "/scenario.json": scenario,
        "/api/scenario": scenario,
        "/api/regions": document["regions"],
        "/api/timeline": analysis["timeline"],
        "/api/anomalies": analysis["anomalies"],
        "/api/hypotheses": analysis["hypotheses"],
        "/api/evidence": analysis["evidence"],
        "/api/sources": document["sources"],
        "/api/health": {
            "status": "ok",
            "mode": "local-replay",
            "source_health": {source["id"]: source["health_status"] for source in document["sources"]},
        },
        "/api/validation": validation,
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib interface
            path = urlparse(self.path).path
            if path in api_payloads:
                self._send_json(api_payloads[path])
                return
            static_name = "index.html" if path == "/" else path.removeprefix("/")
            if static_name not in {"index.html", "app.js", "map.js", "model.js", "styles.css"}:
                self.send_error(404)
                return
            file_path = STATIC_DIR / static_name
            content_type = {
                ".html": "text/html; charset=utf-8",
                ".js": "text/javascript; charset=utf-8",
                ".css": "text/css; charset=utf-8",
            }[file_path.suffix]
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return ThreadingHTTPServer(address, Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mapa do Silêncio — replay local")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--replay", type=Path, help="Caminho de replay JSON autorizado ou sintético")
    args = parser.parse_args()
    document = load_replay(args.replay) if args.replay else build_rio_document()
    server = create_server((args.host, args.port), document)
    print(f"Mapa do Silêncio em http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
