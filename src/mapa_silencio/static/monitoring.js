import { TerritorialMap } from './map.js';
import { observationLabels, observationStatus, eventGroups, safeLink } from './monitoring-model.js';

const $ = selector => document.querySelector(selector);
const date = value => value ? new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value)) : '—';
const number = value => Number.isFinite(value) ? new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 }).format(value) : '—';
const state = { ripe: null, cloudflare: null, geometry: null, selected: null };
const timers = {}, loading = {};
const map = new TerritorialMap($('#map-canvas'), selectCity);
const cities = () => state.ripe?.municipalities || state.geometry?.features.map(feature => ({ ...feature.properties, status: 'unavailable', probes: [] })) || [];

function selectCity(id) {
  state.selected = id;
  renderRipe();
  renderRadar();
}

async function loadGeometry() {
  try {
    const response = await fetch('/rio-municipalities.geojson');
    if (!response.ok) throw new Error();
    state.geometry = await response.json();
    updateMap();
    renderRipe();
  } catch { $('#geometry-error').hidden = false; }
}

function updateMap() {
  if (!state.geometry) return;
  // Markers represent municipality summaries, never residential probe positions.
  const markers = cities().filter(city => city.probe_count > 0);
  map.setRegions(markers, state.geometry);
  applyCoverage();
}

function applyCoverage() {
  const coverage = new Map(cities().map(city => [city.id, observationStatus(state.ripe, city)]));
  map.setCoverage(coverage, state.selected);
  for (const city of cities()) {
    const marker = map.buttons.get(city.id);
    if (!marker) continue;
    const status = coverage.get(city.id);
    marker.querySelector('.signal-core').style.background = status === 'observed' ? '#61edbc' : status === 'no_recent_data' ? '#f5b76b' : '#91a4a7';
    marker.setAttribute('aria-label', city.name + ': ' + observationLabels[status]);
    marker.setAttribute('aria-pressed', String(city.id === state.selected));
  }
}

function renderRipe() {
  const snapshot = state.ripe;
  if (snapshot) {
    $('#ripe-status').textContent = { ok: 'RIPE Atlas consultado', partial: 'RIPE Atlas: consulta parcial', stale: 'RIPE Atlas: coleta anterior', unavailable: 'RIPE Atlas indisponível' }[snapshot.status];
    $('#ripe-time').textContent = snapshot.fetched_at ? 'Coleta: ' + date(snapshot.fetched_at) + ' BRT · atualização em ' + snapshot.refresh_seconds / 60 + ' min.' : 'Nenhuma coleta disponível.';
    const errors = snapshot.error || Object.values(snapshot.errors || {}).join(' ');
    $('#ripe-error').textContent = errors;
    $('#ripe-error').hidden = !errors;
    $('#coverage-total').textContent = snapshot.cache_state === 'stale' || snapshot.status === 'unavailable' ? '— / 92' : snapshot.municipalities_with_recent_data + ' / 92';
  }
  let list = cities();
  if (!state.selected && list.length) state.selected = list.find(city => city.recent_probe_count > 0)?.id || list[0].id;
  const filter = $('#city-search').value.toLocaleLowerCase('pt-BR').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  list = [...list].sort((a,b) => (b.recent_probe_count || 0)-(a.recent_probe_count || 0) || (b.probe_count || 0)-(a.probe_count || 0) || a.name.localeCompare(b.name, 'pt-BR'));
  $('#municipality-list').replaceChildren();
  for (const city of list) {
    if (!city.name.toLocaleLowerCase('pt-BR').normalize('NFD').replace(/[\u0300-\u036f]/g, '').includes(filter)) continue;
    const button = document.createElement('button');
    const title = document.createElement('strong'), subtitle = document.createElement('small');
    title.textContent = city.name;
    subtitle.textContent = observationLabels[observationStatus(snapshot, city)];
    button.append(title, subtitle);
    button.classList.toggle('selected', city.id === state.selected);
    button.setAttribute('aria-pressed', String(city.id === state.selected));
    button.addEventListener('click', () => selectCity(city.id));
    $('#municipality-list').append(button);
  }
  const city = cities().find(city => city.id === state.selected);
  if (!city) return;
  $('#city-name').textContent = city.name;
  $('#city-status').textContent = observationLabels[observationStatus(snapshot, city)];
  $('#city-summary').textContent = city.probe_count === undefined ? 'Aguardando o catálogo da fonte.' : city.probe_count + ' sondas públicas associadas aproximadamente; ' + city.recent_probe_count + ' com medição recente na coleta. ' + city.connected_probe_count + ' constam conectadas ao Atlas.';
  $('#probe-list').replaceChildren();
  for (const probe of city.probes || []) {
    const card = document.createElement('article');
    card.className = 'probe-item';
    const link = document.createElement('a');
    link.href = 'https://atlas.ripe.net/probes/' + encodeURIComponent(probe.id) + '/';
    link.target = '_blank'; link.rel = 'noreferrer';
    link.textContent = 'Sonda ' + probe.id + ' ↗';
    const status = document.createElement('p');
    status.textContent = ({ connected: 'Conectada ao Atlas', disconnected: 'Desconectada do Atlas', abandoned: 'Abandonada no catálogo', unknown: 'Estado desconhecido' }[probe.connection_status]) + (probe.asn_v4 ? ' · AS' + probe.asn_v4 : '');
    card.append(link, status);
    if (!probe.measurements.length) {
      const text = document.createElement('p');
      text.textContent = 'Sem resultado recebido dos dois testes nas últimas 24 horas.';
      card.append(text);
    }
    for (const measurement of probe.measurements) {
      const text = document.createElement('p');
      const fresh = measurement.fresh && snapshot.cache_state !== 'stale';
      text.textContent = measurement.target + ': ' + number(measurement.loss_pct) + '% de perda · RTT ' + number(measurement.rtt_ms) + ' ms · ' + date(measurement.timestamp) + ' BRT' + (fresh ? '' : ' · resultado antigo');
      text.classList.toggle('packet-loss', measurement.loss_pct > 0);
      card.append(text);
    }
    $('#probe-list').append(card);
  }
  if (!city.probe_count) {
    const note = document.createElement('p');
    note.className = 'coverage-note';
    note.textContent = snapshot?.municipalities ? 'Nenhuma sonda pública foi associada a este município com os critérios atuais. Isso não demonstra ausência de internet.' : 'O catálogo não foi recebido; a cobertura deste município é desconhecida.';
    $('#probe-list').append(note);
  }
  applyCoverage();
}

function eventCard(event, label) {
  const card = document.createElement('article'), title = document.createElement('h3'), description = document.createElement('p'), dates = document.createElement('p'), link = document.createElement('a');
  title.textContent = label + ' · ' + (event.scope_reported || 'Escopo local não informado');
  description.textContent = event.description;
  dates.textContent = date(event.start) + ' BRT → ' + (event.end ? date(event.end) + ' BRT' : 'término não informado');
  link.href = safeLink(event.url, 'https://radar.cloudflare.com/outage-center');
  link.textContent = 'Consultar relato original ↗'; link.target = '_blank'; link.rel = 'noreferrer';
  card.append(title, description, dates, link);
  return card;
}

function renderRadar() {
  const snapshot = state.cloudflare;
  if (!snapshot) return;
  $('#radar-status').textContent = snapshot.status === 'not_configured' ? snapshot.message : { ok: 'Ocorrências consultadas · Brasil · últimos 7 dias', stale: 'Exibindo ocorrências da coleta anterior', unavailable: 'Consulta de ocorrências indisponível' }[snapshot.status];
  $('#radar-time').textContent = snapshot.fetched_at && snapshot.status !== 'not_configured' ? 'Coleta: ' + date(snapshot.fetched_at) + ' BRT' : '';
  $('#radar-error').textContent = snapshot.error || '';
  $('#radar-error').hidden = !snapshot.error;
  $('#event-list').replaceChildren();
  if (snapshot.status === 'not_configured') {
    $('#radar-note').textContent = 'O consumidor está instalado. Falta configurar a credencial Cloudflare no servidor para receber ocorrências reais.';
    return;
  }
  if (!snapshot.events) {
    $('#radar-note').textContent = 'Sem resposta da fonte, não é possível avaliar a presença de ocorrências.';
    return;
  }
  $('#radar-note').textContent = (snapshot.possibly_truncated ? 'Lista possivelmente incompleta. ' : '') + 'Menções municipais são associações de nomes no escopo reportado. Não delimitam cobertura e não confirmam desastres.';
  const groups = eventGroups(snapshot, state.selected);
  for (const event of groups.selected) $('#event-list').append(eventCard(event, 'Menção ao município selecionado'));
  for (const event of groups.regional) $('#event-list').append(eventCard(event, 'Menção ao RJ'));
  if (!groups.selected.length && !groups.regional.length) {
    const note = document.createElement('p');
    note.className = 'coverage-note';
    note.textContent = 'Nenhuma menção explícita ao RJ reconhecida nesta coleta. Isso não descarta interrupções locais.';
    $('#event-list').append(note);
  }
  if (groups.context.length) {
    const details = document.createElement('details'), summary = document.createElement('summary');
    summary.textContent = groups.context.length + ' ocorrências no Brasil sem associação confirmada ao RJ';
    details.append(summary);
    for (const event of groups.context) details.append(eventCard(event, 'Contexto nacional'));
    $('#event-list').append(details);
  }
}

async function refresh(source) {
  if (loading[source] || document.hidden) return;
  clearTimeout(timers[source]);
  loading[source] = true;
  $('#refresh-button').disabled = true;
  try {
    const response = await fetch('/api/' + source, { cache: 'no-store', signal: AbortSignal.timeout(120000) });
    if (response.status === 404) throw new Error('Esta tela requer o servidor Python local para consultar as fontes.');
    const result = await response.json();
    const expected = source === 'ripe' ? 'RIPE Atlas' : 'Cloudflare Radar';
    if (result.source !== expected || !['ok', 'partial', 'stale', 'unavailable', 'not_configured'].includes(result.status)) throw new Error('Resposta inesperada da fonte.');
    state[source] = result;
  } catch (error) {
    const previous = state[source];
    const retained = previous?.municipalities || previous?.events;
    state[source] = { ...(retained ? previous : {}), status: retained ? 'stale' : 'unavailable', cache_state: retained ? 'stale' : 'empty', refresh_seconds: 60, error: error.name === 'TimeoutError' ? 'A fonte demorou a responder.' : error.message };
  } finally {
    loading[source] = false;
    $('#refresh-button').disabled = Object.values(loading).some(Boolean);
    if (source === 'ripe') { updateMap(); renderRipe(); }
    renderRadar();
    if (!document.hidden) timers[source] = setTimeout(() => refresh(source), (state[source]?.refresh_seconds || 300)*1000);
  }
}

$('#city-search').addEventListener('input', renderRipe);
$('#refresh-button').addEventListener('click', () => { refresh('ripe'); refresh('cloudflare'); });
document.addEventListener('visibilitychange', () => {
  if (document.hidden) Object.values(timers).forEach(clearTimeout);
  else { refresh('ripe'); refresh('cloudflare'); }
});
loadGeometry();
refresh('ripe');
refresh('cloudflare');
