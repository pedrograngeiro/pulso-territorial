"""Public RIPE Atlas inventory + existing IPv4 ping results; no measurement creation."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import math
import time
from urllib.parse import urlencode, urlparse

from .external import SourceError, read_json
from .ioda import iso
from .territory import Territory

BASE = "https://atlas.ripe.net/api/v2"
MEASUREMENTS = {1001: "k.root-servers.net", 1004: "f.root-servers.net"}
FRESH_SECONDS = 900


def finite(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def normalize_ping(raw, measurement, allowed, now):
    if not isinstance(raw, dict) or raw.get("prb_id") not in allowed or raw.get("msm_id") != measurement or raw.get("type") != "ping":
        return None
    timestamp = raw.get("timestamp")
    if not finite(timestamp) or timestamp <= 0 or timestamp > now+60:
        return None
    sent, received = raw.get("sent"), raw.get("rcvd")
    if not finite(sent) or sent <= 0 or not finite(received) or not 0 <= received <= sent:
        return None
    avg = raw.get("avg")
    return {
        "measurement_id": measurement, "target": MEASUREMENTS[measurement],
        "timestamp": iso(timestamp), "age_seconds": max(0, round(now-timestamp)),
        "fresh": now-timestamp <= FRESH_SECONDS,
        "sent": sent, "received": received,
        "loss_pct": round(100*(sent-received)/sent, 1),
        "rtt_ms": round(avg, 2) if received > 0 and finite(avg) and avg >= 0 else None,
    }


class RipeClient:
    def __init__(self, *, transport=read_json, territory=None, clock=time.time):
        self.transport, self.territory, self.clock = transport, territory or Territory(), clock

    def snapshot(self):
        url = BASE + "/probes/?" + urlencode({
            "country_code": "BR", "is_public": "true", "page_size": 500,
            "latitude__gte": -23.5, "latitude__lte": -20.7,
            "longitude__gte": -44.95, "longitude__lte": -40.9,
        })
        probes, seen, pages = [], set(), 0
        unassigned = 0
        while url:
            if url in seen or pages >= 10 or urlparse(url).scheme != "https" or urlparse(url).netloc != "atlas.ripe.net" or urlparse(url).path != "/api/v2/probes/":
                raise SourceError("Paginação inesperada no catálogo RIPE Atlas.")
            seen.add(url)
            data = self.transport(url)
            if not isinstance(data, dict) or not isinstance(data.get("results"), list):
                raise SourceError("Catálogo RIPE Atlas inválido.")
            for p in data["results"]:
                if not isinstance(p, dict) or p.get("is_public") is not True or p.get("country_code") != "BR":
                    continue
                geometry = p.get("geometry") or {}
                point = geometry.get("coordinates")
                if geometry.get("type") != "Point" or not isinstance(point, list) or len(point) != 2 or not all(finite(v) for v in point):
                    continue
                if not (-44.95 <= point[0] <= -40.9 and -23.5 <= point[1] <= -20.7):
                    continue
                city = self.territory.locate(point)
                if city is None:
                    unassigned += 1
                    continue
                identifier = p.get("id")
                if not isinstance(identifier, int) or isinstance(identifier, bool) or identifier <= 0:
                    continue
                status = (p.get("status") or {}).get("id")
                probes.append({
                    "id": identifier, "municipality_id": city,
                    "connection_status": {1: "connected", 2: "disconnected", 3: "abandoned"}.get(status, "unknown"),
                    "status_since": (p.get("status") or {}).get("since"),
                    "asn_v4": p.get("asn_v4"), "measurements": [],
                })
            pages += 1
            url = data.get("next")
            if url is not None and not isinstance(url, str):
                raise SourceError("Próxima página RIPE Atlas inválida.")
        probes = list({p["id"]: p for p in probes}.values())
        allowed = {p["id"] for p in probes}
        by_id = {p["id"]: p for p in probes}
        errors = {}
        jobs = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            identifiers = sorted(allowed)
            for measurement in MEASUREMENTS:
                for start in range(0, len(identifiers), 100):
                    group = identifiers[start:start+100]
                    query = urlencode({"probe_ids": ",".join(map(str, group)), "lookback_days": 1, "public_only": "true"})
                    jobs.append((measurement, set(group), executor.submit(self.transport, BASE+f"/measurements/{measurement}/latest/?"+query)))
            for measurement, group, future in jobs:
                try:
                    results = future.result()
                    if not isinstance(results, list):
                        raise SourceError("Lista de medições RIPE Atlas inválida.")
                    latest = {}
                    for raw in results:
                        ping = normalize_ping(raw, measurement, group, self.clock())
                        if ping is None and isinstance(raw, dict) and raw.get("prb_id") in group and raw.get("msm_id") == measurement:
                            errors[str(measurement)] = "Resultados inválidos ignorados na medição RIPE Atlas."
                        if ping:
                            probe_id = raw["prb_id"]
                            if probe_id not in latest or ping["timestamp"] > latest[probe_id]["timestamp"]:
                                latest[probe_id] = ping
                    for probe_id, ping in latest.items():
                        by_id[probe_id]["measurements"].append(ping)
                except SourceError as error:
                    errors[str(measurement)] = str(error)
        cities = []
        for city in self.territory.municipalities():
            local = [p for p in probes if p["municipality_id"] == city["id"]]
            fresh_probes = [p for p in local if any(m["fresh"] for m in p["measurements"])]
            state = "observed" if fresh_probes else "no_recent_data" if local else "no_observation"
            if local and errors and not fresh_probes:
                state = "unavailable"
            cities.append({
                **city, "status": state, "probe_count": len(local),
                "recent_probe_count": len(fresh_probes),
                "connected_probe_count": sum(p["connection_status"] == "connected" for p in local),
                "asns_observed": sorted({p["asn_v4"] for p in fresh_probes if isinstance(p["asn_v4"], int)}),
                "probes": local,
            })
        return {
            "status": "partial" if errors else "ok", "scope": "municipal_samples",
            "municipalities": cities, "errors": errors,
            "probe_count": len(probes), "municipalities_with_probes": sum(c["probe_count"] > 0 for c in cities),
            "municipalities_with_recent_data": sum(c["recent_probe_count"] > 0 for c in cities),
            "unassigned_in_bounding_box": unassigned,
            "freshness_seconds": FRESH_SECONDS,
            "measurements": [{"id": k, "target": v} for k,v in MEASUREMENTS.items()],
            "source_url": "https://atlas.ripe.net/probes/",
            "interpretation": "Amostras IPv4 de sondas públicas. Associação municipal aproximada; não representa todo o município. Sonda desconectada não confirma falha territorial.",
        }
