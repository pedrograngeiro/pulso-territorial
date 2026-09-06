"""Cloudflare Radar annotations are contextual reports, not municipal telemetry."""
from __future__ import annotations

from datetime import datetime, timezone
import os
import re
import time
import unicodedata
from urllib.parse import urlencode, urlparse

from .external import SourceError, read_json
from .ioda import iso
from .territory import Territory

BASE = "https://api.cloudflare.com/client/v4/radar/annotations/outages"
SOURCE_URL = "https://radar.cloudflare.com/outage-center"
PAGE_SIZE = 100
MAX_PAGES = 3


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c)).strip()


def epoch(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.timestamp() if parsed.tzinfo else None
    except (ValueError, OverflowError):
        return None


def normalize_event(raw, municipalities, start, end):
    if not isinstance(raw, dict) or not isinstance(raw.get("locations"), list) or "BR" not in raw["locations"]:
        return None
    began, ended = epoch(raw.get("startDate")), epoch(raw.get("endDate"))
    if began is None or began > end or (ended is not None and ended < start):
        return None
    scope = raw.get("scope") if isinstance(raw.get("scope"), str) else ""
    chunks = {normalized(s) for s in re.split(r"[,;|/]", scope)}
    matches = []
    for city in municipalities:
        name = normalized(city["name"])
        if name == "rio de janeiro":
            # "Rio de Janeiro" alone can mean the state; never label it as the city.
            if "municipio de rio de janeiro" in chunks or "cidade do rio de janeiro" in chunks:
                matches.append(city["id"])
        elif name in chunks or "municipio de "+name in chunks:
            matches.append(city["id"])
    state_mention = bool(chunks & {"rio de janeiro", "rj", "estado do rio de janeiro", "br-rj"})
    # A name in a report is an approximate text association, not a measured footprint.
    relevance = "municipality_mention" if matches else "state_mention" if state_mention else "brazil_context"
    linked = raw.get("linkedUrl")
    parsed = urlparse(linked) if isinstance(linked, str) else None
    link = linked if parsed and parsed.scheme in {"https", "http"} and parsed.netloc and not parsed.username else SOURCE_URL
    outage = raw.get("outage") if isinstance(raw.get("outage"), dict) else {}
    return {
        "id": str(raw.get("id", ""))[:100], "start": iso(began), "end": iso(ended) if ended is not None else None,
        "description": str(raw.get("description") or "Ocorrência reportada pelo Cloudflare Radar.")[:1500],
        "scope_reported": scope[:500], "event_type": str(raw.get("eventType", ""))[:80],
        "outage_type": str(outage.get("outageType", ""))[:80],
        "cause_reported": str(outage.get("outageCause", ""))[:150],
        "municipality_mentions": matches, "relevance": relevance, "url": link,
    }


class CloudflareClient:
    def __init__(self, *, transport=read_json, token=None, territory=None, clock=time.time):
        self.transport = transport
        self.token = token
        self.territory = territory or Territory()
        self.clock = clock

    def snapshot(self):
        token = self.token if self.token is not None else os.environ.get("CLOUDFLARE_API_TOKEN", "")
        if not token.strip():
            return {
                "status": "not_configured", "scope": "reported_events",
                "message": "Cloudflare Radar aguarda a credencial de leitura no servidor.",
                "source_url": SOURCE_URL,
            }
        if "\n" in token or "\r" in token:
            raise SourceError("Credencial Cloudflare inválida.")
        end = self.clock()
        start = end - 7*86400
        events, truncated = [], False
        cities = self.territory.municipalities()
        for page in range(MAX_PAGES):
            query = urlencode({"location": "BR", "dateStart": iso(start), "dateEnd": iso(end), "limit": PAGE_SIZE, "offset": page*PAGE_SIZE, "format": "JSON"})
            data = self.transport(BASE+"?"+query, headers={"Authorization": "Bearer "+token})
            if not isinstance(data, dict) or data.get("success") is not True or not isinstance(data.get("result"), dict) or not isinstance(data["result"].get("annotations"), list):
                raise SourceError("Cloudflare retornou erro ou um envelope inválido.")
            raw_events = data["result"]["annotations"]
            if any(not isinstance(raw, dict) or not isinstance(raw.get("locations"), list) or epoch(raw.get("startDate")) is None for raw in raw_events):
                raise SourceError("Lista de ocorrências Cloudflare inválida.")
            for raw in raw_events:
                event = normalize_event(raw, cities, start, end)
                if event:
                    events.append(event)
            if len(raw_events) < PAGE_SIZE:
                break
            truncated = page == MAX_PAGES-1
        events = list({(e["id"], e["start"]): e for e in events}.values())
        events.sort(key=lambda event: event["start"], reverse=True)
        return {
            "status": "ok", "scope": "reported_events", "events": events,
            "window": {"from": iso(start), "until": iso(end), "days": 7},
            "possibly_truncated": truncated, "source_url": SOURCE_URL,
            "interpretation": "Ocorrências reportadas no Brasil. Menções ao RJ e a municípios são associações textuais, não cobertura medida. Ausência de ocorrência não significa normalidade.",
        }
