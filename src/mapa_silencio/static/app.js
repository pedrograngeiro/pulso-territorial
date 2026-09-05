import { TerritorialMap } from './map.js';
import { measurement, regionalSignal, silenceSequence, statusLabels, changeLabel } from './model.js';

const $ = selector => document.querySelector(selector);
const state = { scenario: null, frameIndex: 0, selected: null, speed: 1, timer: null };
const timeFormatter = new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit' });
const numberFormatter = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 });
const formatTime = timestamp => timeFormatter.format(new Date(timestamp));
const formatNumber = value => Number.isFinite(value) ? numberFormatter.format(value) : '—';
const map = new TerritorialMap($('#map-canvas'), selectRegion);
const regionButtons = new Map();

async function loadScenario() {
  $('#error-panel').hidden = true;
  try {
    const response = await fetch('/scenario.json', { signal: AbortSignal.timeout(12000) });
    if (!response.ok) throw new Error('Scenario request failed');
    const scenario = await response.json();
    if (!scenario.analysis?.timeline?.length || !scenario.regions?.length) throw new Error('Empty scenario');
    state.scenario = scenario;
    state.frameIndex = Math.min(5, scenario.analysis.timeline.length - 1);
    state.selected = scenario.regions.find(region => region.id === 'petropolis')?.id ?? scenario.regions[0].id;
    $('#timeline').max = scenario.analysis.timeline.length - 1;
    $('#timeline').disabled = scenario.analysis.timeline.length < 2;
    $('#play-button').disabled = scenario.analysis.timeline.length < 2;
    buildRegionList();
    renderSources();
    map.setRegions(scenario.regions, scenario.map_geometry);
    render();
  } catch (error) {
    console.error('Não foi possível carregar o cenário:', error);
    $('#error-panel').hidden = false;
    $('#region-list').textContent = 'Cenário indisponível.';
  }
}

function buildRegionList() {
  $('#region-list').replaceChildren();
  regionButtons.clear();
  for (const region of state.scenario.regions) {
    const button = document.createElement('button');
    button.className = 'region-card';
    button.innerHTML = '<span class="region-top"><span class="region-name"></span><svg><use href="#icon-arrow"/></svg></span><span class="region-bottom"><span class="region-status"><i></i><span></span></span><span class="region-change"></span></span>';
    button.querySelector('.region-name').textContent = region.name;
    button.addEventListener('click', () => selectRegion(region.id));
    regionButtons.set(region.id, button);
    $('#region-list').append(button);
  }
}

function renderSources() {
  const { scenario } = state;
  $('#source-list').replaceChildren();
  $('#source-count').textContent = scenario.sources.length;
  for (const source of scenario.sources) {
    const entry = document.createElement('p');
    entry.className = 'source-item';
    const name = document.createElement('strong');
    name.textContent = source.name;
    const detail = document.createElement('span');
    detail.textContent = `${source.data_nature === 'simulated' ? 'Simulada' : 'Fonte do replay'} · ${source.health_status === 'healthy' ? 'disponível' : 'indisponível ou degradada'}`;
    entry.append(name, detail);
    $('#source-list').append(entry);
  }
  const synthetic = scenario.metadata.data_nature === 'simulated';
  $('#data-mode').textContent = synthetic ? 'DEMONSTRAÇÃO' : 'REPLAY';
  $('#data-note').textContent = `${synthetic ? 'DADOS SINTÉTICOS' : 'DADOS DO REPLAY'} · SEM CONEXÃO COM O X`;
  $('#about-data').textContent = synthetic ? 'O replay atual usa dados sintéticos. Não reproduz medições reais de qualquer desastre.' : `O replay usa dados declarados como ${scenario.metadata.data_nature}. Consulte a proveniência das fontes antes de interpretar os sinais.`;
  const states = [...new Set(scenario.regions.map(region => region.state).filter(Boolean))];
  $('#state-label').textContent = states.length === 1 ? ({ RJ: 'RIO DE JANEIRO', RS: 'RIO GRANDE DO SUL' }[states[0]] || states[0]) : states.join(' · ') || 'TERRITÓRIO DO CENÁRIO';
  $('#map-title').textContent = scenario.metadata.scenario_id === 'rj-silence-synthetic-v1' ? 'Um estado. Muitos sinais.' : scenario.metadata.scenario_id === 'rs-urban-flood-synthetic-v1' ? 'Região metropolitana' : 'Território do cenário';
}

function selectRegion(id) {
  if (!state.scenario?.regions.some(region => region.id === id)) return;
  state.selected = id;
  render();
}

function render() {
  const { scenario, frameIndex, selected } = state;
  if (!scenario) return;
  const signals = new Map(scenario.regions.map(region => [region.id, regionalSignal(scenario, frameIndex, region.id)]));
  const sequence = silenceSequence(scenario, frameIndex);
  const count = [...signals.values()].filter(signal => signal.status === 'silence').length;
  $('#silence-count').textContent = String(count).padStart(2, '0');
  $('#region-count').textContent = String(scenario.regions.length).padStart(2, '0');
  $('#frame-label').textContent = `${String(frameIndex + 1).padStart(2, '0')} / ${String(scenario.analysis.timeline.length).padStart(2, '0')}`;
  $('#map-summary').textContent = `${scenario.regions.length} municípios · ${count ? `${count} com silêncio detectado` : 'nenhum silêncio detectado'}`;
  for (const [id, button] of regionButtons) {
    const signal = signals.get(id);
    button.classList.toggle('selected', id === selected);
    button.setAttribute('aria-pressed', String(id === selected));
    button.querySelector('.region-status').className = `region-status ${signal.status}`;
    button.querySelector('.region-status>span').textContent = signal.status === 'normal' ? 'Esperado' : signal.status === 'silence' ? 'Silêncio' : statusLabels[signal.status];
    button.querySelector('.region-change').textContent = changeLabel(signal.change);
    button.querySelector('.region-change').className = `region-change ${signal.status}`;
  }
  map.setSignals(signals, selected, sequence);
  renderDetail(signals.get(selected), sequence);
  renderTimeline(sequence);
}

function renderDetail(signal, sequence) {
  const { scenario, frameIndex, selected } = state;
  const region = scenario.regions.find(item => item.id === selected);
  $('#selected-name').textContent = region.name;
  const [longitude, latitude] = region.centroid;
  $('#selected-coordinates').textContent = `${Math.abs(latitude).toFixed(4)}° ${latitude < 0 ? 'S' : 'N'} / ${Math.abs(longitude).toFixed(4)}° ${longitude < 0 ? 'O' : 'L'}`;
  $('#selected-status').textContent = signal.status === 'normal' ? 'Esperado' : signal.status === 'silence' ? 'Silêncio' : statusLabels[signal.status];
  $('#selected-status').className = `status-tag ${signal.status}`;
  $('#activity-change').textContent = changeLabel(signal.change);
  $('#activity-change').style.color = signal.status === 'silence' ? 'var(--amber)' : signal.status === 'normal' ? 'var(--mint)' : 'var(--muted)';
  $('#activity-numbers').textContent = `${formatNumber(signal.activity?.observed)} / ${formatNumber(signal.activity?.expected)}`;
  const rain = measurement(scenario, frameIndex, selected, 'rainfall_mm_h');
  $('#rain-value').textContent = rain ? `${formatNumber(rain.observed)} mm/h` : '—';
  $('#reports-value').textContent = formatNumber(measurement(scenario, frameIndex, selected, 'flood_reports')?.observed);
  const first = sequence.find(item => item.region.id === selected);
  $('#detail-explanation').textContent = signal.status === 'silence'
    ? `Queda incomum desde ${formatTime(first.timestamp)}. Causa não verificada.`
    : signal.status === 'unavailable' ? 'A coleta está degradada. Não é possível atribuir a queda ao território.'
    : signal.status === 'unknown' ? 'Sem dados suficientes para comparar a atividade com o padrão esperado.'
    : signal.status === 'spike' ? 'Aumento incomum de relatos. Confira as outras evidências do cenário.'
    : 'Atividade dentro da faixa esperada nesta etapa.';
  renderLocalChart();
}

function renderLocalChart() {
  const { scenario, frameIndex, selected } = state;
  const series = scenario.analysis.timeline.slice(0, frameIndex + 1).map((_, index) => measurement(scenario, index, selected, 'digital_activity'));
  const max = Math.max(1, ...series.flatMap(item => [item?.observed ?? 0, item?.expected ?? 0]));
  const x = index => 7 + index / Math.max(1, scenario.analysis.timeline.length - 1) * 246;
  const y = value => 68 - value / max * 57;
  const chart = $('#local-chart');
  chart.replaceChildren();
  const svg = (tag, attrs) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attrs)) element.setAttribute(key, value);
    chart.append(element);
    return element;
  };
  for (const height of [12, 40, 68]) svg('line', { x1: 0, y1: height, x2: 260, y2: height, class: 'chart-grid' });
  for (const [metric, className] of [['expected', 'expected-line'], ['observed', 'observed-line']]) {
    let path = '', gap = true;
    series.forEach((item, index) => {
      if (!Number.isFinite(item?.[metric])) { gap = true; return; }
      path += `${gap ? 'M' : 'L'}${x(index)} ${y(item[metric])} `;
      gap = false;
    });
    svg('path', { d: path, class: className, fill: 'none' });
  }
  const last = series.at(-1);
  if (Number.isFinite(last?.observed)) svg('circle', { cx: x(frameIndex), cy: y(last.observed), r: 4.5, class: 'chart-point' });
  chart.setAttribute('aria-label', `Atividade digital de ${scenario.regions.find(region => region.id === selected).name} até ${formatTime(scenario.analysis.timeline[frameIndex].timestamp)}: ${formatNumber(last?.observed)} observado, ${formatNumber(last?.expected)} esperado.`);
}

function renderTimeline(sequence) {
  const { scenario, frameIndex } = state;
  const frames = scenario.analysis.timeline;
  const timestamp = frames[frameIndex].timestamp;
  $('#current-time').textContent = formatTime(timestamp);
  $('#current-time').dateTime = timestamp;
  $('#current-date').textContent = new Intl.DateTimeFormat('pt-BR', { timeZone: 'America/Sao_Paulo', day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(timestamp)).replace('.', '');
  const slider = $('#timeline');
  slider.value = frameIndex;
  slider.style.setProperty('--progress', `${frameIndex / Math.max(1, frames.length - 1) * 100}%`);
  slider.setAttribute('aria-valuetext', `${formatTime(timestamp)}, etapa ${frameIndex + 1} de ${frames.length}`);
  $('#activity-chart').replaceChildren();
  const totals = frames.map(frame => frame.measurements.filter(item => item.metric === 'digital_activity').reduce((sum, item) => sum + item.observed, 0));
  const max = Math.max(...totals, 1);
  // Each bar is an observed frame; no invented samples between observations.
  totals.forEach((total, index) => {
    const bar = document.createElement('span');
    bar.className = `activity-bar ${index === frameIndex ? 'current' : index < frameIndex ? 'past' : ''}`;
    bar.style.height = `${total / max * 32}px`;
    $('#activity-chart').append(bar);
  });
  $('#timeline-labels').replaceChildren();
  frames.forEach((frame, index) => {
    if (frames.length > 9 && index !== frames.length - 1 && index % Math.ceil(frames.length / 8)) return;
    const label = document.createElement('span');
    label.textContent = formatTime(frame.timestamp);
    $('#timeline-labels').append(label);
  });
  $('#sequence-note').textContent = sequence.length > 1 ? 'Conexões: ordem de detecção, sem trajetória confirmada.' : 'Arraste a linha do tempo para investigar.';
}

function pause() {
  clearInterval(state.timer);
  state.timer = null;
  $('#play-button').classList.remove('playing');
  $('#play-button').setAttribute('aria-label', 'Reproduzir cenário');
}

function play() {
  if (!state.scenario) return;
  if (state.frameIndex === state.scenario.analysis.timeline.length - 1) { state.frameIndex = 0; render(); }
  $('#play-button').classList.add('playing');
  $('#play-button').setAttribute('aria-label', 'Pausar cenário');
  state.timer = setInterval(() => {
    state.frameIndex++;
    render();
    if (state.frameIndex >= state.scenario.analysis.timeline.length - 1) pause();
  }, 1800 / state.speed);
}

$('#timeline').addEventListener('input', event => { pause(); state.frameIndex = Number(event.target.value); render(); });
$('#play-button').addEventListener('click', () => state.timer === null ? play() : pause());
$('#speed-button').addEventListener('click', () => {
  state.speed = state.speed === 4 ? 1 : state.speed * 2;
  $('#speed-button').textContent = `${state.speed}×`;
  $('#speed-button').setAttribute('aria-label', `Velocidade de reprodução: ${state.speed} ${state.speed === 1 ? 'vez' : 'vezes'}`);
  if (state.timer !== null) { pause(); play(); }
});
document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
$('#retry-button').addEventListener('click', loadScenario);
$('#about-button').addEventListener('click', () => $('#about-dialog').showModal());
$('#close-about').addEventListener('click', () => $('#about-dialog').close());
$('#about-dialog').addEventListener('click', event => { if (event.target === $('#about-dialog')) { const rect = event.target.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.target.close(); } });
loadScenario();
