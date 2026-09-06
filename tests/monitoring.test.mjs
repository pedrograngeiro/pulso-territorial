import test from 'node:test';
import assert from 'node:assert/strict';
import { observationStatus, eventGroups, safeLink } from '../src/mapa_silencio/static/monitoring-model.js';

test('source failure and stale cache override a previously observed city', () => {
  const city = { status: 'observed' };
  assert.equal(observationStatus({ status: 'ok', cache_state: 'fresh' }, city), 'observed');
  assert.equal(observationStatus({ status: 'stale', cache_state: 'stale' }, city), 'stale');
  assert.equal(observationStatus({ status: 'unavailable' }, city), 'unavailable');
  assert.equal(observationStatus(null, city), 'unavailable');
});

test('no probes and old measurements remain different from healthy connectivity', () => {
  assert.equal(observationStatus({ status: 'ok' }, { status: 'no_observation' }), 'no_observation');
  assert.equal(observationStatus({ status: 'ok' }, { status: 'no_recent_data' }), 'no_recent_data');
});

test('national events never become events of a selected municipality', () => {
  const local = { municipality_mentions: ['3301702'], relevance: 'municipality_mention' };
  const statewide = { municipality_mentions: [], relevance: 'state_mention' };
  const national = { municipality_mentions: [], relevance: 'brazil_context' };
  const groups = eventGroups({ events: [local, statewide, national] }, '3301702');
  assert.deepEqual(groups.selected, [local]);
  assert.deepEqual(groups.regional, [statewide]);
  assert.deepEqual(groups.context, [national]);
  assert.deepEqual(eventGroups({ status: 'not_configured' }, '3301702').selected, []);
});

test('external event URLs cannot execute script or contain credentials', () => {
  const fallback = 'https://radar.cloudflare.com/outage-center';
  for (const url of ['javascript:alert(1)', 'data:text/html,test', 'https://user:pass@example.org', '/relative']) assert.equal(safeLink(url, fallback), fallback);
  assert.equal(safeLink('https://example.org/event', fallback), 'https://example.org/event');
});

import { TerritorialMap } from '../src/mapa_silencio/static/map.js';

test('municipal geometry remains visible even when no probe can be mapped', () => {
  const previous = globalThis.window;
  globalThis.window = { innerWidth: 1400 };
  try {
    const map = Object.create(TerritorialMap.prototype);
    map.regions = [];
    map.rings = [[[-44,-23],[-41,-23],[-41,-21],[-44,-21]]];
    map.element = { getBoundingClientRect: () => ({ width: 1000, height: 1100 }) };
    let rendered = false;
    map.render = () => { rendered = true; };
    map.fit();
    assert.equal(rendered, true);
    assert.ok(map.center.every(Number.isFinite));
    assert.ok(map.zoom >= 3);
  } finally { globalThis.window = previous; }
});
