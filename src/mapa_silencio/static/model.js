// Presentation rules shared by the map, municipality list and evidence panel.
export const statusLabels = {
  normal: 'Atividade esperada', silence: 'Silêncio digital', spike: 'Pico de relatos',
  unavailable: 'Fonte indisponível', unknown: 'Dados insuficientes',
};

export function measurement(scenario, frameIndex, regionId, metric) {
  return scenario.analysis.timeline[frameIndex]?.measurements.find(item => item.region_id === regionId && item.metric === metric);
}

export function regionalSignal(scenario, frameIndex, regionId) {
  const activity = measurement(scenario, frameIndex, regionId, 'digital_activity');
  const source = scenario.sources.find(item => item.id === activity?.source_id);
  const valid = activity && Number.isFinite(activity.observed) && Number.isFinite(activity.expected) && activity.expected > 0;
  const timestamp = scenario.analysis.timeline[frameIndex]?.timestamp;
  const anomaly = scenario.analysis.anomalies.find(item => item.region_id === regionId && item.started_at === timestamp);
  let status = 'normal';
  if (!valid) status = 'unknown';
  else if (source?.health_status !== 'healthy') status = 'unavailable';
  else if (anomaly?.evidence.some(item => item.metric === 'digital_activity' && item.standardized_deviation <= -2)) status = 'silence';
  else if (anomaly?.evidence.some(item => item.metric === 'flood_reports')) status = 'spike';
  const change = valid && source?.health_status === 'healthy' ? Math.round((activity.observed / activity.expected - 1) * 100) : null;
  return { status, change, activity, anomaly };
}

export function silenceSequence(scenario, frameIndex) {
  const sequence = [];
  for (let index = 0; index <= frameIndex; index++) {
    for (const region of scenario.regions) {
      if (!sequence.some(item => item.region.id === region.id) && regionalSignal(scenario, index, region.id).status === 'silence') {
        sequence.push({ region, frameIndex: index, timestamp: scenario.analysis.timeline[index].timestamp });
      }
    }
  }
  return sequence;
}

export function changeLabel(value) {
  return value === null ? '—' : `${value > 0 ? '+' : value < 0 ? '−' : ''}${Math.abs(value)}%`;
}

export function project([longitude, latitude], zoom) {
  const size = 256 * 2 ** zoom;
  const sine = Math.sin(Math.max(-85.0511, Math.min(85.0511, latitude)) * Math.PI / 180);
  return [(longitude + 180) / 360 * size, (0.5 - Math.log((1 + sine) / (1 - sine)) / (4 * Math.PI)) * size];
}

export function unproject([x, y], zoom) {
  const size = 256 * 2 ** zoom;
  return [x / size * 360 - 180, Math.atan(Math.sinh(Math.PI * (1 - 2 * y / size))) * 180 / Math.PI];
}
