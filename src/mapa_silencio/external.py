"""Bounded reads and in-memory snapshots for external observation sources."""
from __future__ import annotations

from copy import deepcopy
from gzip import GzipFile
from http.client import HTTPException
from io import BytesIO
import json
from threading import Lock
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener

from .ioda import iso

MAX_BYTES = 8 * 1024 * 1024


class SourceError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_json(url, *, headers=None, timeout=12, sleep=time.sleep):
    # Auth headers must never follow a redirect to a different origin.
    opener = build_opener(NoRedirect())
    for attempt in range(3):
        delay = 2 ** attempt
        try:
            request = Request(url, headers={"Accept": "application/json", "Accept-Encoding": "identity", "User-Agent": "PulsoTerritorial/0.2", **(headers or {})})
            with opener.open(request, timeout=timeout) as response:
                raw = response.read(MAX_BYTES+1)
            if len(raw) > MAX_BYTES:
                raise SourceError("Resposta excedeu o limite de tamanho.")
            if raw[:2] == b"\x1f\x8b":
                with GzipFile(fileobj=BytesIO(raw)) as zipped:
                    raw = zipped.read(MAX_BYTES+1)
                if len(raw) > MAX_BYTES:
                    raise SourceError("Resposta descompactada excedeu o limite.")
            return json.loads(raw)
        except HTTPError as error:
            # Do not echo bodies, headers, URLs or tokens in browser errors.
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise SourceError(f"Fonte respondeu HTTP {error.code}.") from None
            try:
                delay = max(delay, min(15, float(error.headers.get("Retry-After", 0))))
            except (ValueError, TypeError):
                pass
        except (URLError, OSError, HTTPException) as error:
            if attempt == 2:
                raise SourceError("Não foi possível consultar a fonte externa.") from None
        except (ValueError, EOFError):
            raise SourceError("Resposta JSON inválida da fonte externa.") from None
        sleep(delay)
    raise SourceError("Fonte indisponível.")


class SnapshotCache:
    def __init__(self, source, collect, *, clock=time.time):
        self.source, self.collect, self.clock = source, collect, clock
        self.lock = Lock()
        self.result = None
        self.next_attempt = 0

    def snapshot(self):
        with self.lock:
            now = self.clock()
            if self.result is not None and now < self.next_attempt:
                return deepcopy(self.result)
            try:
                result = self.collect()
                result.update(source=self.source, data_nature="real", fetched_at=iso(self.clock()), cache_state="fresh", refresh_seconds=300)
                self.result = result
                self.next_attempt = self.clock() + 300
            except SourceError as error:
                usable = self.result and self.result.get("status") not in {"unavailable", "not_configured"}
                self.result = {
                    **deepcopy(self.result if usable else {}),
                    "source": self.source, "data_nature": "real",
                    "status": "stale" if usable else "unavailable",
                    "cache_state": "stale" if usable else "empty",
                    "checked_at": iso(self.clock()), "error": str(error), "refresh_seconds": 60,
                }
                self.next_attempt = self.clock() + 60
            return deepcopy(self.result)
