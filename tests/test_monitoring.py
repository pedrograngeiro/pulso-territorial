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

from mapa_silencio.cloudflare import CloudflareClient, normalize_event
from mapa_silencio.demo import build_demo_document
from mapa_silencio.external import NoRedirect, SnapshotCache, SourceError, read_json
from mapa_silencio.ioda import iso
from mapa_silencio.ripe import RipeClient, normalize_ping
from mapa_silencio.server import create_server
from mapa_silencio.territory import Territory, contains

NOW = 1788654000


def rectangle(x, y, size):
    return [[x,y],[x+size,y],[x+size,y+size],[x,y+size],[x,y]]


def territory():
    return Territory({"features": [
        {"properties": {"id": "3301702", "name": "Duque de Caxias", "centroid": [-43.25,-22.25]}, "geometry": {"type": "Polygon", "coordinates": [rectangle(-43.5,-22.5,.5)]}},
        {"properties": {"id": "3304557", "name": "Rio de Janeiro", "centroid": [-43.75,-22.25]}, "geometry": {"type": "Polygon", "coordinates": [rectangle(-44,-22.5,.5)]}},
    ]})


def probe(identifier=10, point=None, public=True):
    return {"id": identifier, "country_code": "BR", "is_public": public,
            "geometry": {"type": "Point", "coordinates": point or [-43.25,-22.25]},
            "status": {"id": 1, "since": iso(NOW-86400)}, "asn_v4": 64500,
            "address_v4": "192.0.2.1", "description": "must not be returned"}


def ping(identifier=10, msm=1001, age=60, received=3):
    return {"prb_id": identifier, "msm_id": msm, "type": "ping", "timestamp": NOW-age,
            "sent": 3, "rcvd": received, "avg": 20 if received else -1,
            "src_addr": "192.0.2.1", "from": "192.0.2.1"}


def atlas_transport(url, **kwargs):
    if "/probes/" in url:
        return {"results": [probe(), probe(20,[-43.75,-22.25],False)], "next": None}
    msm = int(urlparse(url).path.split("/")[-3])
    return [ping(msm=msm)]


def annotation(scope="Duque de Caxias", location="BR"):
    return {"id":"1", "locations":[location], "startDate":iso(NOW-3600),
            "scope":scope, "eventType":"OUTAGE", "description":"Reported event",
            "linkedUrl":"https://radar.cloudflare.com/outage-center"}


class TerritoryTests(unittest.TestCase):
    def test_geometry_excludes_holes_and_rejects_border_uncertainty(self):
        shape = {"type":"Polygon","coordinates":[rectangle(0,0,10),rectangle(3,3,2)]}
        self.assertTrue(contains([1,1],shape))
        self.assertFalse(contains([4,4],shape))
        t=territory()
        self.assertEqual("3301702",t.locate([-43.25,-22.25]))
        self.assertIsNone(t.locate([-43.4999,-22.25]))
        self.assertIsNone(t.locate([-40,-22]))

    def test_official_asset_contains_all_92_unique_rj_municipalities(self):
        t=Territory()
        cities=t.municipalities()
        self.assertEqual(92,len(cities))
        self.assertEqual(92,len({c["id"] for c in cities}))
        self.assertTrue(all(c["id"].startswith("33") for c in cities))
        self.assertTrue(all(c["name"] and len(c["centroid"])==2 for c in cities))


class RipeTests(unittest.TestCase):
    def test_only_public_probes_and_whitelisted_output(self):
        result=RipeClient(transport=atlas_transport,territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual(1,result["probe_count"])
        self.assertEqual(1,result["municipalities_with_recent_data"])
        self.assertEqual("observed",result["municipalities"][0]["status"])
        self.assertEqual("no_observation",result["municipalities"][1]["status"])
        output=json.dumps(result)
        for field in ("192.0.2.1","must not be returned","src_addr","address_v4"):
            self.assertNotIn(field,output)
        self.assertNotIn("geometry",result["municipalities"][0]["probes"][0])

    def test_inventory_is_not_recent_observation(self):
        def no_results(url,**kwargs):
            return atlas_transport(url) if "/probes/" in url else []
        result=RipeClient(transport=no_results,territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual("no_recent_data",result["municipalities"][0]["status"])
        self.assertEqual(0,result["municipalities_with_recent_data"])

    def test_missing_results_are_not_packet_loss(self):
        self.assertIsNone(normalize_ping({},1001,{10},NOW))
        lost=normalize_ping(ping(received=0),1001,{10},NOW)
        self.assertEqual(100,lost["loss_pct"])
        self.assertIsNone(lost["rtt_ms"])
        self.assertFalse(normalize_ping(ping(age=901),1001,{10},NOW)["fresh"])
        self.assertIsNone(normalize_ping(ping(age=-100),1001,{10},NOW))
        self.assertIsNone(normalize_ping(ping(identifier=99),1001,{10},NOW))
        self.assertIsNone(normalize_ping(ping(msm=1004),1001,{10},NOW))

    def test_partial_failure_and_total_measurement_failure_are_explicit(self):
        def partial(url,**kwargs):
            if "/1004/" in url: raise SourceError("failed target")
            return atlas_transport(url)
        result=RipeClient(transport=partial,territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual("partial",result["status"])
        self.assertEqual(1,result["municipalities_with_recent_data"])
        def failed(url,**kwargs):
            if "/measurements/" in url: raise SourceError("offline")
            return atlas_transport(url)
        result=RipeClient(transport=failed,territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual("unavailable",result["municipalities"][0]["status"])
        self.assertEqual([],result["municipalities"][0]["probes"][0]["measurements"])

    def test_pagination_and_untrusted_next_url(self):
        calls=[]
        def paged(url,**kwargs):
            calls.append(url)
            if "/probes/" in url:
                if "page=2" in url:
                    return {"results":[probe(11)],"next":None}
                return {"results":[probe()],"next":"https://atlas.ripe.net/api/v2/probes/?page=2"}
            return []
        result=RipeClient(transport=paged,territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual(2,result["probe_count"])
        with self.assertRaises(SourceError):
            RipeClient(transport=lambda *a,**k:{"results":[],"next":"https://evil.invalid/"},territory=territory()).snapshot()

    def test_empty_catalog_does_not_request_global_measurements(self):
        transport=Mock(return_value={"results":[],"next":None})
        result=RipeClient(transport=transport,territory=territory()).snapshot()
        transport.assert_called_once()
        self.assertEqual(0,result["probe_count"])


class CloudflareTests(unittest.TestCase):
    def test_missing_token_does_not_fetch_or_invent_empty_events(self):
        transport=Mock()
        result=CloudflareClient(transport=transport,token="",territory=territory()).snapshot()
        self.assertEqual("not_configured",result["status"])
        self.assertNotIn("events",result)
        transport.assert_not_called()

    def test_brazil_filter_authentication_and_safe_output(self):
        transport=Mock(return_value={"success":True,"result":{"annotations":[annotation()]}})
        result=CloudflareClient(transport=transport,token="secret-fixture",territory=territory(),clock=lambda:NOW).snapshot()
        args,kwargs=transport.call_args
        query=parse_qs(urlparse(args[0]).query)
        self.assertEqual(["BR"],query["location"])
        self.assertEqual("Bearer secret-fixture",kwargs["headers"]["Authorization"])
        self.assertNotIn("secret-fixture",json.dumps(result))
        self.assertEqual(["3301702"],result["events"][0]["municipality_mentions"])

    def test_state_name_is_not_capital_and_country_or_asn_is_not_city(self):
        cities=territory().municipalities()
        def parse(event):return normalize_event(event,cities,NOW-7*86400,NOW)
        self.assertIsNone(parse(annotation(location="US")))
        state=parse(annotation("Rio de Janeiro"))
        self.assertEqual("state_mention",state["relevance"])
        self.assertEqual([],state["municipality_mentions"])
        self.assertEqual("brazil_context",parse(annotation("AS64500"))["relevance"])
        self.assertEqual(["3304557"],parse(annotation("Município de Rio de Janeiro"))["municipality_mentions"])

    def test_bad_links_and_event_window(self):
        event=annotation()
        event["linkedUrl"]="javascript:alert(1)"
        result=normalize_event(event,territory().municipalities(),NOW-86400,NOW)
        self.assertTrue(result["url"].startswith("https://radar.cloudflare.com/"))
        event["startDate"]=iso(NOW+1000)
        self.assertIsNone(normalize_event(event,[],NOW-86400,NOW))
        event["startDate"]=iso(NOW-900000)
        event["endDate"]=iso(NOW-800000)
        self.assertIsNone(normalize_event(event,[],NOW-86400,NOW))

    def test_pagination_preserves_limit_warning(self):
        transport=Mock(return_value={"success":True,"result":{"annotations":[annotation()]*100}})
        result=CloudflareClient(transport=transport,token="fixture",territory=territory(),clock=lambda:NOW).snapshot()
        self.assertEqual(3,transport.call_count)
        self.assertTrue(result["possibly_truncated"])
        self.assertEqual(1,len(result["events"]))
        offsets=[parse_qs(urlparse(call.args[0]).query)["offset"][0] for call in transport.call_args_list]
        self.assertEqual(["0","100","200"],offsets)

    def test_malformed_event_is_not_an_empty_success(self):
        with self.assertRaises(SourceError):
            CloudflareClient(transport=lambda *a,**k:{"success":True,"result":{"annotations":[{}]}},token="fixture",territory=territory()).snapshot()

    def test_bad_envelope_is_error_not_zero_outages(self):
        with self.assertRaises(SourceError):
            CloudflareClient(transport=lambda *a,**k:{"success":False,"errors":[{"message":"private token context"}]},token="secret-fixture",territory=territory()).snapshot()


class ExternalTests(unittest.TestCase):
    def test_cache_failure_keeps_prior_collection_and_recovers(self):
        clock=Mock(return_value=NOW)
        collect=Mock(side_effect=[{"status":"ok","events":[{"id":"1"}]},SourceError("offline"),{"status":"ok","events":[]}])
        cache=SnapshotCache("fixture",collect,clock=clock)
        first=cache.snapshot()
        first["events"].clear()
        self.assertEqual(1,len(cache.snapshot()["events"]))
        self.assertEqual(1,collect.call_count)
        clock.return_value+=300
        stale=cache.snapshot()
        self.assertEqual("stale",stale["status"])
        self.assertEqual(iso(NOW),stale["fetched_at"])
        clock.return_value+=60
        self.assertEqual("ok",cache.snapshot()["status"])

    def test_http_auth_error_does_not_leak_server_body_and_redirects_are_blocked(self):
        opener=Mock()
        opener.open.side_effect=HTTPError("https://api.cloudflare.com",403,"secret-fixture",{},io.BytesIO(b"secret-fixture"))
        with patch("mapa_silencio.external.build_opener",return_value=opener):
            with self.assertRaises(SourceError) as raised:
                read_json("https://api.cloudflare.com",headers={"Authorization":"Bearer secret-fixture"})
        self.assertNotIn("secret-fixture",str(raised.exception))
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,"",{},"https://other.invalid"))


class MonitoringHttpTests(unittest.TestCase):
    def test_endpoints_and_assets_without_external_network(self):
        ripe=Mock()
        ripe.snapshot.return_value={"source":"RIPE Atlas","status":"ok","municipalities":[]}
        cloudflare=Mock()
        cloudflare.snapshot.return_value={"source":"Cloudflare Radar","status":"not_configured"}
        server=create_server(("127.0.0.1",0),build_demo_document(),ripe_monitor=ripe,cloudflare_monitor=cloudflare)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base=f"http://127.0.0.1:{server.server_port}"
        for path,source in (("ripe","RIPE Atlas"),("cloudflare","Cloudflare Radar")):
            with urlopen(base+"/api/"+path,timeout=2) as response:
                self.assertEqual(source,json.load(response)["source"])
        for asset in ("monitoring.html","monitoring.css","monitoring.js","monitoring-model.js","rio-municipalities.geojson"):
            with urlopen(base+"/"+asset,timeout=2) as response:
                self.assertEqual(200,response.status)
        ripe.snapshot.return_value={"source":"RIPE Atlas","status":"stale"}
        with self.assertRaises(HTTPError) as raised:
            urlopen(base+"/api/ripe",timeout=2)
        self.assertEqual(503,raised.exception.code)


if __name__=="__main__":
    unittest.main()
