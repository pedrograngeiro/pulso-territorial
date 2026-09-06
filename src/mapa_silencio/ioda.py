"""Public IODA connectivity consumer. Regional measurements never become city observations."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from gzip import GzipFile
from io import BytesIO
from http.client import HTTPException
import json
import math
from statistics import median
from threading import Lock
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen

API_BASE = "https://api.ioda.inetintel.cc.gatech.edu/v2"
MAX_BYTES = 5 * 1024 * 1024
REFRESH_SECONDS = 300
EVENT_LIMIT = 25
SIGNALS = {
    "bgp": ("Rotas visíveis", "blocos /24 visíveis", "Visibilidade das redes no roteamento da internet."),
    "ping-slash24": ("Redes alcançáveis", "blocos /24 alcançáveis", "Redes que responderam às sondagens do IODA."),
    "merit-nt": ("Atividade no telescópio", "IPs de origem por intervalo", "Tráfego observado pelo telescópio de rede; não conta publicações ou pessoas."),
}


class IodaError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool = False, retry_after: float = 0):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after = retry_after


def iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_json(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={
        "Accept": "application/json", "Accept-Encoding": "identity",
        "User-Agent": "MapaDoSilencio/0.2 (local research; IODA public API)",
    })
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise IodaError("Resposta IODA excedeu o limite de 5 MiB.")
        if raw[:2] == b"\x1f\x8b":
            with GzipFile(fileobj=BytesIO(raw)) as zipped:
                raw = zipped.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise IodaError("Resposta IODA descompactada excedeu o limite.")
        data = json.loads(raw)
    except HTTPError as error:
        try:
            delay = float(error.headers.get("Retry-After", 0))
        except (ValueError, TypeError):
            delay = 0
        raise IodaError(
            f"IODA respondeu HTTP {error.code}.",
            retryable=error.code == 429 or error.code in {500, 502, 503, 504},
            retry_after=max(0, min(delay, 30)),
        ) from error
    except (URLError, TimeoutError, OSError, HTTPException) as error:
        raise IodaError(f"Não foi possível consultar o IODA: {str(error)[:180]}", retryable=True) from error
    except (ValueError, EOFError) as error:
        raise IodaError("IODA retornou uma resposta JSON inválida.") from error
    if not isinstance(data, dict) or data.get("error") or "data" not in data:
        raise IodaError("IODA retornou um envelope inválido ou informou erro.")
    return data


def _series_objects(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, list):
        raise IodaError("Lista de séries IODA inválida.")
    result = []
    for item in data:
        if isinstance(item, list):
            result.extend(_series_objects(item))
        elif isinstance(item, dict):
            result.append(item)
        else:
            raise IodaError("Série IODA contém um item inválido.")
    return result


def normalize_signal(envelope: dict[str, Any], source: str, entity_code: str, start: int, end: int) -> dict[str, Any]:
    name, unit, description = SIGNALS[source]
    result = {
        "id": source, "name": name, "unit": unit, "description": description,
        "status": "no_data", "points": [], "latest": None, "reference_median": None,
        "change_pct": None, "coverage_pct": 0, "step_seconds": None,
        "copyright": envelope.get("copyright"),
    }
    candidates = _series_objects(envelope["data"])
    if not candidates:
        return result
    matching = [item for item in candidates if item.get("entityType") == "region" and str(item.get("entityCode")) == entity_code and item.get("datasource") == source and item.get("subtype", "") in {"", None}]
    if len(matching) != 1:
        raise IodaError("A série retornada não corresponde unicamente ao estado e à fonte solicitados.")
    series = matching[0]
    origin, step, values = series.get("from"), series.get("step"), series.get("values")
    if isinstance(origin, bool) or isinstance(step, bool) or not isinstance(origin, (int, float)) or not math.isfinite(origin) or not isinstance(step, (int, float)) or not math.isfinite(step) or step <= 0 or not isinstance(values, list):
        raise IodaError("Série IODA sem início, intervalo ou valores válidos.")
    points = []
    for index, value in enumerate(values):
        timestamp = origin + index * step
        if not start <= timestamp < end:
            continue
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
            raise IodaError("Série IODA contém um valor não numérico ou inválido.")
        points.append({"timestamp": iso(timestamp), "value": value})
    valid = [point for point in points if point["value"] is not None]
    expected_slots = math.ceil((end - origin) / step) - math.ceil((start - origin) / step)
    result.update(points=points, step_seconds=step, coverage_pct=round(100 * len(valid) / max(1, expected_slots), 1))
    if not valid:
        return result
    latest = valid[-1]
    latest_epoch = datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00")).timestamp()
    result.update(latest=latest, status="available" if end - latest_epoch <= max(1800, step * 3) else "stale")
    # Descriptive comparison only. This is not IODA's anomaly detector or a seasonal baseline.
    if len(valid) >= 13:
        reference = median(point["value"] for point in valid[:-1])
        result["reference_median"] = reference
        if reference > 0:
            result["change_pct"] = round((latest["value"] / reference - 1) * 100, 2)
    return result


class IodaClient:
    def __init__(self, *, transport: Callable = get_json, timeout: float = 12, sleep: Callable = time.sleep):
        self.transport = transport
        self.timeout = timeout
        self.sleep = sleep
        self._entity: dict[str, Any] | None = None

    def _request(self, path: str, parameters: dict[str, Any]) -> dict[str, Any]:
        url = API_BASE + path + "?" + urlencode(parameters)
        for attempt in range(3):
            try:
                envelope = self.transport(url, self.timeout)
                if not isinstance(envelope, dict) or envelope.get("error") or "data" not in envelope:
                    raise IodaError("IODA retornou erro ou um envelope inválido.")
                return envelope
            except IodaError as error:
                if not error.retryable or attempt == 2:
                    raise
                self.sleep(max(2 ** attempt, error.retry_after))
        raise AssertionError("Unreachable")

    def resolve_rio(self) -> dict[str, Any]:
        if self._entity is None:
            response = self._request("/entities/query", {
                "entityType": "region", "relatedTo": "country/BR", "search": "Rio de Janeiro", "limit": 10,
            })
            if not isinstance(response["data"], list):
                raise IodaError("Consulta de regiões IODA inválida.")
            matches = [
                item for item in response["data"]
                if isinstance(item, dict) and item.get("type") == "region"
                and isinstance(item.get("name"), str) and item["name"].casefold() == "rio de janeiro"
                and isinstance(item.get("attrs"), dict) and item["attrs"].get("country_code") == "BR"
                and isinstance(item.get("code"), str) and item["code"]
            ]
            if len(matches) != 1:
                raise IodaError("Não foi possível identificar unicamente o estado do Rio de Janeiro no IODA.")
            self._entity = {**matches[0], "scope": "state", "country_code": "BR"}
        return deepcopy(self._entity)

    def snapshot(self, *, hours: int = 24, until: int | None = None) -> dict[str, Any]:
        if not isinstance(hours, int) or not 1 <= hours <= 168:
            raise ValueError("A janela precisa ter entre 1 e 168 horas.")
        end = int(time.time() if until is None else until) // 300 * 300
        if end < hours * 3600 or end > time.time() + 300:
            raise ValueError("Instante final inválido ou no futuro.")
        start = end - hours * 3600
        entity = self.resolve_rio()
        code = entity["code"]
        signals = []
        errors = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                source: executor.submit(self._request, f"/signals/raw/region/{quote(code, safe='')}", {
                    "from": start, "until": end, "datasource": source, "maxPoints": 288,
                }) for source in SIGNALS
            }
            event_future = executor.submit(self._request, "/outages/events", {
                "entityType": "region", "entityCode": code, "from": start, "until": end,
                "limit": EVENT_LIMIT, "page": 0,
            })
            for source, future in futures.items():
                try:
                    signals.append(normalize_signal(future.result(), source, code, start, end))
                except IodaError as error:
                    errors[source] = str(error)
                    signal = normalize_signal({"data": []}, source, code, start, end)
                    signals.append({**signal, "status": "error", "error": str(error)})
            try:
                event_response = event_future.result()
                items = event_response["data"]
                if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
                    raise IodaError("Lista de eventos IODA inválida.")
                events = {"status": "available", "items": items[:EVENT_LIMIT], "limit": EVENT_LIMIT, "possibly_truncated": len(items) >= EVENT_LIMIT, "copyright": event_response.get("copyright")}
            except IodaError as error:
                errors["events"] = str(error)
                events = {"status": "error", "items": [], "limit": EVENT_LIMIT, "possibly_truncated": False, "error": str(error)}
        available = sum(signal["status"] == "available" for signal in signals)
        status = "ok" if available == len(SIGNALS) and events["status"] == "available" else "partial" if any(signal["latest"] for signal in signals) else "unavailable"
        return {
            "schema_version": 1, "source": "IODA", "data_nature": "real", "scope": "state",
            "entity": entity, "window": {"from": iso(start), "until": iso(end), "hours": hours},
            "fetched_at": iso(time.time()), "checked_at": iso(time.time()), "status": status,
            "cache_state": "fresh", "refresh_seconds": REFRESH_SECONDS,
            "signals": signals, "events": events, "errors": errors,
            "source_url": f"https://ioda.inetintel.cc.gatech.edu/region/{quote(code, safe='')}?from={start}&until={end}",
            "api_url": API_BASE,
            "interpretation": "Medições estaduais de conectividade. Não medem publicações, pessoas ou municípios e não confirmam desastres.",
        }


class IodaMonitor:
    """Share a bounded refresh across browsers and retain the last usable snapshot on failure."""
    def __init__(self, client: IodaClient | None = None, *, clock: Callable = time.time):
        self.client = client or IodaClient()
        self.clock = clock
        self._lock = Lock()
        self._result: dict[str, Any] | None = None
        self._last_good: dict[str, Any] | None = None
        self._next_attempt = 0.0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            now = self.clock()
            if self._result is not None and now < self._next_attempt:
                return deepcopy({**self._result, "served_at": iso(now)})
            try:
                result = self.client.snapshot()
                if result["status"] == "unavailable":
                    raise IodaError("Nenhuma série de conectividade utilizável retornou do IODA.")
                self._last_good = deepcopy(result)
                self._result = result
                self._next_attempt = now + REFRESH_SECONDS
            except IodaError as error:
                self._result = {
                    **deepcopy(self._last_good or {}),
                    "source": "IODA", "data_nature": "real", "scope": "state",
                    "status": "stale" if self._last_good else "unavailable",
                    "cache_state": "stale" if self._last_good else "empty",
                    "checked_at": iso(now), "refresh_seconds": 60,
                    "error": str(error),
                }
                self._next_attempt = now + 60
            return deepcopy({**self._result, "served_at": iso(now)})
