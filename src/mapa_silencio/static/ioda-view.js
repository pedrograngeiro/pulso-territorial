import { TerritorialMap } from './map.js';

const $ = selector => document.querySelector(selector);
const number = value => Number.isFinite(value) ? new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(value) : '—';
const time = timestamp => timestamp ? new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(timestamp)) : '—';
const labels = { available: 'Atualizado', stale: 'Atrasado', no_data: 'Sem dados', error: 'Indisponível' };
const state = { snapshot: null, selected: 'ping-slash24', timer: null, loading: false };
const map = new TerritorialMap($('#map-canvas'), () => selectSignal('ping-slash24'));
const buttons = new Map();

async function loadGeometry() {
  try {
    const response = await fetch('/rio-state.geojson');
    if (!response.ok) throw new Error('Geometry unavailable');
    const geometry = await response.json();
    map.setRegions([{ id: 'state-rj', name: 'Rio de Janeiro', centroid: [-42.65, -22.3] }], geometry);
    $('#map-markers small').textContent = 'COBERTURA ESTADUAL';
    $('#map-markers button').setAttribute('aria-label', 'Rio de Janeiro: consultar redes alcançáveis no estado');
  } catch {
    $('#geometry-status').hidden = false;
  }
}

function selectSignal(id) {
  state.selected = id;
  render();
}

function render() {
  const snapshot = state.snapshot;
  if (!snapshot) return;
  document.body.classList.remove('collection-ok', 'collection-partial', 'collection-stale', 'collection-unavailable');
  document.body.classList.add('collection-' + snapshot.status);
  $('#collection-status').textContent = { ok: 'Dados recebidos', partial: 'Dados parciais ou atrasados', stale: 'Exibindo coleta anterior', unavailable: 'Coleta indisponível' }[snapshot.status] || 'Estado desconhecido';
  $('#collection-time').textContent = snapshot.fetched_at ? 'Coleta: ' + time(snapshot.fetched_at) + ' BRT · atualização a cada ' + (snapshot.refresh_seconds / 60) + ' min.' : 'Nenhuma coleta real disponível.';
  $('#collection-error').hidden = !snapshot.error;
  $('#collection-error').textContent = snapshot.error || '';
  if (!snapshot.signals) return;
  $('#ioda-link').href = 'https://ioda.inetintel.cc.gatech.edu/region/' + encodeURIComponent(snapshot.entity.code) + '?from=' + Math.floor(Date.parse(snapshot.window.from) / 1000) + '&until=' + Math.floor(Date.parse(snapshot.window.until) / 1000);
  for (const signal of snapshot.signals) {
    let button = buttons.get(signal.id);
    if (!button) {
      button = document.createElement('button');
      button.className = 'region-card';
      button.innerHTML = '<span class="region-top"><span class="region-name"></span><span class="signal-count"></span></span><span class="region-bottom"><span class="signal-state"></span><span class="signal-time"></span></span>';
      button.addEventListener('click', () => selectSignal(signal.id));
      buttons.set(signal.id, button);
      $('#signal-list').append(button);
    }
    button.querySelector('.region-name').textContent = signal.name;
    button.querySelector('.signal-count').textContent = number(signal.latest?.value);
    const status = snapshot.cache_state === 'stale' ? 'stale' : signal.status;
    button.querySelector('.signal-state').textContent = labels[status];
    button.querySelector('.signal-state').className = 'signal-state ' + status;
    button.querySelector('.signal-time').textContent = signal.latest ? time(signal.latest.timestamp) : '—';
    button.classList.toggle('selected', signal.id === state.selected);
    button.setAttribute('aria-pressed', String(signal.id === state.selected));
  }
  const signal = snapshot.signals.find(item => item.id === state.selected);
  if (!signal) return;
  const status = snapshot.cache_state === 'stale' ? 'stale' : signal.status;
  $('#signal-name').textContent = signal.name;
  $('#signal-description').textContent = signal.description;
  $('#signal-unit').textContent = signal.unit;
  $('#signal-status').textContent = labels[status];
  $('#signal-status').className = 'status-tag signal-state ' + status;
  $('#latest-value').textContent = number(signal.latest?.value);
  $('#measurement-time').textContent = signal.latest ? 'Medição: ' + time(signal.latest.timestamp) + ' BRT' : 'Nenhuma medição recebida.';
  $('#reference-value').textContent = number(signal.reference_median);
  $('#variation-value').textContent = signal.change_pct === null ? '—' : (signal.change_pct > 0 ? '+' : '') + number(signal.change_pct) + '%';
  $('#coverage-value').textContent = number(signal.coverage_pct) + '%';
  const events = snapshot.events;
  if (snapshot.cache_state === 'stale' || events.status !== 'available') {
    $('#event-count').textContent = 'Eventos: consulta indisponível';
    $('#event-description').textContent = 'A ausência de resposta não significa ausência de interrupções.';
  } else {
    $('#event-count').textContent = events.items.length + (events.possibly_truncated ? '+' : '') + ' eventos retornados pelo IODA';
    $('#event-description').textContent = events.items.length ? 'Eventos de conectividade na janela. Consulte os detalhes e a cronologia no IODA.' : 'Nenhum evento retornado nesta janela. Isso não descarta uma interrupção local.';
  }
  renderChart(signal, snapshot.window);
}

function renderChart(signal, window) {
  $('#chart-title').textContent = signal.name + ' · últimas ' + window.hours + ' horas';
  $('#chart-range').textContent = signal.unit + ' · ' + (state.snapshot.cache_state === 'stale' ? 'coleta anterior' : labels[signal.status].toLowerCase());
  $('#chart-start').textContent = time(window.from);
  $('#chart-end').textContent = time(window.until);
  const chart = $('#ioda-chart');
  chart.replaceChildren();
  const create = (name, attrs) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', name);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    chart.append(element);
    return element;
  };
  for (const y of [12, 48, 85]) create('line', { x1: 0, y1: y, x2: 800, y2: y, stroke: '#29413f', 'stroke-width': 0.7 });
  const valid = signal.points.filter(point => point.value !== null);
  if (!valid.length) {
    const text = create('text', { x: 400, y: 50, fill: '#a9bcb7', 'text-anchor': 'middle', 'font-size': 13 });
    text.textContent = 'Sem medições disponíveis nesta janela';
    chart.setAttribute('aria-label', 'Sem medições disponíveis nesta janela.');
    return;
  }
  const max = Math.max(1, ...valid.map(point => point.value));
  const start = Date.parse(window.from), duration = Date.parse(window.until) - start;
  const x = timestamp => 5 + (Date.parse(timestamp) - start) / duration * 790;
  const y = value => 85 - value / max * 70;
  let path = '', gap = true;
  for (const point of signal.points) {
    if (point.value === null) { gap = true; continue; }
    path += (gap ? 'M' : 'L') + x(point.timestamp) + ',' + y(point.value) + ' ';
    gap = false;
  }
  const color = signal.status === 'stale' || state.snapshot.cache_state === 'stale' ? '#f5b76b' : '#61edbc';
  create('path', { d: path, stroke: color, 'stroke-width': 2, fill: 'none', 'vector-effect': 'non-scaling-stroke' });
  if (signal.reference_median !== null) create('line', { x1: 5, x2: 795, y1: y(signal.reference_median), y2: y(signal.reference_median), stroke: '#a8bcb4', 'stroke-dasharray': '4 5', 'stroke-width': 0.8 });
  const last = valid.at(-1);
  create('circle', { cx: x(last.timestamp), cy: y(last.value), r: 3, fill: color });
  chart.setAttribute('aria-label', signal.name + ': ' + valid.length + ' intervalos com dados. Último valor ' + number(last.value) + ' ' + signal.unit + ', às ' + time(last.timestamp) + ' BRT. Linha tracejada: mediana da janela.');
}

async function refresh() {
  if (state.loading || document.hidden) return;
  clearTimeout(state.timer);
  state.loading = true;
  $('#refresh-button').disabled = true;
  $('#refresh-button').textContent = 'Consultando…';
  try {
    const response = await fetch('/api/ioda', { cache: 'no-store', signal: AbortSignal.timeout(120000) });
    if (response.status === 404) throw new Error('Esta versão estática não possui o consumidor IODA. Abra o site pelo servidor Python local.');
    const snapshot = await response.json();
    if (!['ok', 'partial', 'stale', 'unavailable'].includes(snapshot.status) || snapshot.source !== 'IODA') throw new Error('Resposta inesperada do consumidor IODA.');
    state.snapshot = snapshot;
  } catch (error) {
    state.snapshot = {
      ...(state.snapshot || {}), source: 'IODA',
      status: state.snapshot?.signals ? 'stale' : 'unavailable',
      cache_state: state.snapshot?.signals ? 'stale' : 'empty',
      refresh_seconds: 60,
      error: error.name === 'TimeoutError' ? 'O IODA não respondeu a tempo. Uma nova tentativa será feita.' : error.message,
    };
  } finally {
    state.loading = false;
    $('#refresh-button').disabled = false;
    $('#refresh-button').textContent = 'Atualizar';
    render();
    if (!document.hidden) state.timer = setTimeout(refresh, (state.snapshot?.refresh_seconds || 300) * 1000);
  }
}

$('#refresh-button').addEventListener('click', refresh);
document.addEventListener('visibilitychange', () => {
  if (document.hidden) clearTimeout(state.timer);
  else refresh();
});
loadGeometry();
refresh();
