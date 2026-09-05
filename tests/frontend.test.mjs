import test from 'node:test';
import assert from 'node:assert/strict';
import { regionalSignal, silenceSequence, changeLabel, project, unproject } from '../src/mapa_silencio/static/model.js';

function scenario() {
  return {
    regions: [{ id: 'a', centroid: [-51.23, -30.03] }, { id: 'b', centroid: [-51.18, -29.91] }],
    sources: [{ id: 'social', health_status: 'healthy' }],
    analysis: {
      timeline: [0, 1, 2].map(index => ({ timestamp: `t${index}`, measurements: ['a', 'b'].map(id => ({ region_id: id, source_id: 'social', metric: 'digital_activity', observed: index ? 5 : 30, expected: 30 })) })),
      anomalies: [
        { region_id: 'a', started_at: 't1', evidence: [{ metric: 'digital_activity', standardized_deviation: -4 }] },
        { region_id: 'b', started_at: 't2', evidence: [{ metric: 'digital_activity', standardized_deviation: -4 }] },
      ],
    },
  };
}

test('normal activity and a detected fall have distinct, consistent presentations', () => {
  assert.equal(regionalSignal(scenario(), 0, 'a').status, 'normal');
  assert.equal(regionalSignal(scenario(), 1, 'a').status, 'silence');
  assert.equal(changeLabel(regionalSignal(scenario(), 1, 'a').change), '−83%');
});
test('a failing source cannot be presented as territorial silence', () => {
  const data = scenario();
  data.sources[0].health_status = 'degraded';
  assert.equal(regionalSignal(data, 1, 'a').status, 'unavailable');
  assert.equal(regionalSignal(data, 1, 'a').change, null);
  assert.deepEqual(silenceSequence(data, 2), []);
});
test('missing activity or a zero baseline is insufficient data, not silence', () => {
  const data = scenario();
  data.analysis.timeline[1].measurements[0].expected = 0;
  assert.equal(regionalSignal(data, 1, 'a').status, 'unknown');
  data.analysis.timeline[1].measurements = [];
  assert.equal(regionalSignal(data, 1, 'a').status, 'unknown');
});
test('rewinding removes future detections from the geographic sequence', () => {
  assert.deepEqual(silenceSequence(scenario(), 0), []);
  assert.deepEqual(silenceSequence(scenario(), 1).map(item => item.region.id), ['a']);
  assert.deepEqual(silenceSequence(scenario(), 2).map(item => item.region.id), ['a', 'b']);
});
test('geographic projection round-trips at map zoom levels', () => {
  for (const zoom of [3, 10, 13, 17]) {
    const source = [-51.23, -30.0331];
    const restored = unproject(project(source, zoom), zoom);
    assert.ok(Math.abs(restored[0] - source[0]) < 1e-8);
    assert.ok(Math.abs(restored[1] - source[1]) < 1e-8);
  }
});
