from __future__ import annotations

from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mapa_silencio.demo import build_demo_document
from mapa_silencio.ioda import IodaClient, IodaError, IodaMonitor, get_json, iso, normalize_signal
from mapa_silencio.server import create_server

END = 1_780_000_200
START = END - 3600


def envelope(values, *, source="bgp", origin=START, step=300, code="499"):
    return {"error": None, "copyright": "fixture", "data": [[{
        "entityType": "region", "entityCode": code, "datasource": source,
        "subtype": "", "from": origin, "step": step, "values": values,
    }]]}


def transport(url, timeout):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if parsed.path.endswith("/entities/query"):
        return {"data": [{"type": "region", "code": "499", "name": "Rio de Janeiro", "attrs": {"country_code": "BR"}}]}
    if parsed.path.endswith("/outages/events"):
        return {"data": []}
    return envelope([100] * 12, source=query["datasource"][0])


class SignalTests(unittest.TestCase):
    def test_clips_window_and_preserves_null_and_zero(self):
        result = normalize_signal(envelope([999, None, 0, 25, 999], origin=START-300), "bgp", "499", START, START+900)
        self.assertEqual([None, 0, 25], [p["value"] for p in result["points"]])
        self.assertEqual(iso(START+600), result["latest"]["timestamp"])
        self.assertEqual(66.7, result["coverage_pct"])
        self.assertIsNone(result["change_pct"])

    def test_coverage_counts_missing_edges_of_window(self):
        result = normalize_signal(envelope([100, 100], origin=START+300), "bgp", "499", START, END)
        self.assertEqual(16.7, result["coverage_pct"])
        self.assertEqual("stale", result["status"])

    def test_missing_measurements_are_not_zero_or_outage(self):
        result = normalize_signal(envelope([None]*12), "bgp", "499", START, END)
        self.assertEqual("no_data", result["status"])
        self.assertIsNone(result["latest"])
        self.assertIsNone(result["change_pct"])

    def test_rejects_wrong_entity_source_and_invalid_numbers(self):
        for response in (envelope([10], code="33"), envelope([10], source="merit-nt"), envelope([float("nan")]), envelope([True]), envelope([-1]), envelope([10], step=True)):
            with self.subTest(response=response), self.assertRaises(IodaError):
                normalize_signal(response, "bgp", "499", START, END)

    def test_median_is_descriptive_and_zero_baseline_has_no_percentage(self):
        result = normalize_signal(envelope([100]*12+[50]), "bgp", "499", START, START+3900)
        self.assertEqual(100, result["reference_median"])
        self.assertEqual(-50, result["change_pct"])
        result = normalize_signal(envelope([0]*12+[50]), "bgp", "499", START, START+3900)
        self.assertIsNone(result["change_pct"])


class ClientTests(unittest.TestCase):
    def test_snapshot_resolves_state_and_keeps_partial_failure(self):
        calls = []
        def partial(url, timeout):
            calls.append(url)
            if "datasource=merit-nt" in url:
                raise IodaError("source failed")
            return transport(url, timeout)
        client = IodaClient(transport=partial)
        result = client.snapshot(hours=1, until=END)
        self.assertEqual(("real", "state", "499", "partial"), (result["data_nature"], result["scope"], result["entity"]["code"], result["status"]))
        self.assertEqual(["available", "available", "error"], [s["status"] for s in result["signals"]])
        self.assertIsNone(result["signals"][2]["latest"])
        self.assertEqual("available", result["events"]["status"])
        client.resolve_rio()
        self.assertEqual(1, sum("/entities/query" in url for url in calls))
        self.assertTrue(any("relatedTo=country%2FBR" in url for url in calls))

    def test_event_failure_does_not_claim_zero_events(self):
        def failed_events(url, timeout):
            if "/outages/events" in url:
                raise IodaError("events unavailable")
            return transport(url, timeout)
        result = IodaClient(transport=failed_events).snapshot(hours=1, until=END)
        self.assertEqual("error", result["events"]["status"])
        self.assertEqual("partial", result["status"])

    def test_http_rate_limit_and_retry_cap(self):
        with patch("mapa_silencio.ioda.urlopen", side_effect=HTTPError("https://example.invalid", 429, "rate limit", {"Retry-After": "5"}, io.BytesIO())):
            with self.assertRaises(IodaError) as raised:
                get_json("https://example.invalid", 1)
        self.assertTrue(raised.exception.retryable)
        sleeper = Mock()
        request = Mock(side_effect=[raised.exception, {"data": []}])
        IodaClient(transport=request, sleep=sleeper)._request("/test", {})
        sleeper.assert_called_once_with(5)
        failed = Mock(side_effect=IodaError("down", retryable=True))
        with self.assertRaises(IodaError):
            IodaClient(transport=failed, sleep=lambda _: None)._request("/test", {})
        self.assertEqual(3, failed.call_count)
        invalid = Mock(side_effect=IodaError("invalid"))
        with self.assertRaises(IodaError):
            IodaClient(transport=invalid)._request("/test", {})
        self.assertEqual(1, invalid.call_count)

    def test_region_resolution_rejects_wrong_country_and_ambiguity(self):
        for data in ([{"type": "region", "code": "499", "name": "Rio de Janeiro", "attrs": {"country_code": "US"}}], transport("https://example/entities/query", 1)["data"] * 2):
            with self.subTest(data=data), self.assertRaises(IodaError):
                IodaClient(transport=lambda *_: {"data": data}).resolve_rio()


class MonitorTests(unittest.TestCase):
    def test_cache_ttl_failure_preserves_original_timestamp_and_recovers(self):
        good = {"status": "ok", "fetched_at": iso(END), "signals": [{"latest": {"value": 10}}]}
        clock = Mock(return_value=END)
        client = Mock()
        client.snapshot.side_effect = [deepcopy(good), IodaError("offline"), deepcopy(good)]
        monitor = IodaMonitor(client, clock=clock)
        first = monitor.snapshot()
        first["signals"][0]["latest"]["value"] = -1
        self.assertEqual(10, monitor.snapshot()["signals"][0]["latest"]["value"])
        self.assertEqual(1, client.snapshot.call_count)
        clock.return_value = END + 300
        stale = monitor.snapshot()
        self.assertEqual(("stale", "stale", iso(END)), (stale["status"], stale["cache_state"], stale["fetched_at"]))
        clock.return_value += 59
        monitor.snapshot()
        self.assertEqual(2, client.snapshot.call_count)
        clock.return_value += 1
        self.assertEqual("ok", monitor.snapshot()["status"])

    def test_first_failure_never_invents_a_measurement(self):
        client = Mock()
        client.snapshot.side_effect = IodaError("offline")
        result = IodaMonitor(client).snapshot()
        self.assertEqual("unavailable", result["status"])
        self.assertNotIn("signals", result)
        self.assertNotIn("fetched_at", result)


class IodaHttpTests(unittest.TestCase):
    def test_real_endpoint_and_failure_status_are_separate_from_simulation(self):
        monitor = Mock()
        monitor.snapshot.return_value = {"source": "IODA", "status": "partial", "data_nature": "real", "scope": "state"}
        server = create_server(("127.0.0.1", 0), build_demo_document(), ioda_monitor=monitor)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base+"/api/ioda", timeout=2) as response:
            self.assertEqual(monitor.snapshot.return_value, json.load(response))
        for asset in ("ioda", "ioda.html", "ioda.css", "ioda-view.js", "rio-state.geojson"):
            with self.subTest(asset=asset), urlopen(base+"/"+asset, timeout=2) as response:
                self.assertEqual(200, response.status)
                self.assertGreater(len(response.read()), 100)
        monitor.snapshot.return_value = {"source": "IODA", "status": "unavailable"}
        with self.assertRaises(HTTPError) as raised:
            urlopen(base+"/api/ioda", timeout=2)
        self.assertEqual(503, raised.exception.code)
        self.assertEqual("unavailable", json.load(raised.exception)["status"])


if __name__ == "__main__":
    unittest.main()
