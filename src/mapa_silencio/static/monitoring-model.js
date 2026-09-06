export const observationLabels = {
  observed: 'Com medição recente',
  no_recent_data: 'Sem medição recente',
  no_observation: 'Sem observação',
  unavailable: 'Fonte indisponível',
  stale: 'Coleta anterior',
};

export function observationStatus(snapshot, city) {
  if (!snapshot || snapshot.status === 'unavailable') return 'unavailable';
  if (snapshot.cache_state === 'stale') return 'stale';
  return city?.status || 'unavailable';
}

export function eventGroups(snapshot, selectedId) {
  if (!snapshot?.events) return { selected: [], regional: [], context: [] };
  return {
    selected: snapshot.events.filter(event => event.municipality_mentions.includes(selectedId)),
    regional: snapshot.events.filter(event => event.relevance !== 'brazil_context' && !event.municipality_mentions.includes(selectedId)),
    context: snapshot.events.filter(event => event.relevance === 'brazil_context'),
  };
}

export function safeLink(value, fallback) {
  try {
    const url = new URL(value);
    return ['https:', 'http:'].includes(url.protocol) && !url.username ? url.href : fallback;
  } catch { return fallback; }
}
