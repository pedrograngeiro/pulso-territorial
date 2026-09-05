import { project, unproject, statusLabels, changeLabel } from './model.js';

// Small slippy map: native image tiles and geographic overlays, no framework.
export class TerritorialMap {
  constructor(element, onSelect) {
    this.element = element;
    this.tiles = element.querySelector('#tiles');
    this.markers = element.querySelector('#map-markers');
    this.regions = [];
    this.buttons = new Map();
    this.signals = new Map();
    this.sequence = [];
    this.zoom = 10;
    this.center = [-51.4, -30];
    this.onSelect = onSelect;
    this.drag = null;
    this.pendingFrame = null;
    this.tileCache = new Map();
    this.visibleTiles = [];
    this.bindControls();
    this.resizeObserver = new ResizeObserver(() => this.fit());
    this.resizeObserver.observe(element);
  }

  setRegions(regions, geometry) {
    this.rings = (geometry?.features ?? []).flatMap(feature => feature.geometry.type === 'MultiPolygon' ? feature.geometry.coordinates.flat() : feature.geometry.type === 'Polygon' ? feature.geometry.coordinates : []);
    this.element.classList.toggle('state-view', this.rings.length > 0);
    this.regions = regions.filter(region => Array.isArray(region.centroid) && region.centroid.length === 2 && region.centroid.every(Number.isFinite));
    this.markers.replaceChildren();
    this.buttons.clear();
    const north = [...this.regions].sort((a, b) => b.centroid[1] - a.centroid[1])[0];
    for (const region of this.regions) {
      const button = document.createElement('button');
      button.className = 'map-marker';
      button.innerHTML = '<span class="signal-ring outer"></span><span class="signal-ring"></span><span class="signal-core"></span><span class="marker-index" hidden></span><span class="marker-caption"><span></span><small></small></span>';
      button.querySelector('.marker-caption>span').textContent = region.name;
      if (region.label_offset) {
        const caption = button.querySelector('.marker-caption');
        caption.style.left = `calc(50% + ${region.label_offset[0]}px)`;
        caption.style.top = `calc(50% + ${region.label_offset[1]}px)`;
      } else if (region === north) button.classList.add('label-above');
      button.addEventListener('click', () => this.onSelect(region.id));
      button.addEventListener('pointerdown', event => event.stopPropagation());
      this.buttons.set(region.id, button);
      this.markers.append(button);
    }
    this.fit();
  }

  fit() {
    if (!this.regions.length) return;
    const { width, height } = this.element.getBoundingClientRect();
    const mobile = window.innerWidth <= 700;
    const compact = window.innerWidth <= 950;
    const left = mobile ? 70 : 125;
    const right = mobile ? 70 : compact ? 75 : 360;
    const top = 200;
    const bottom = compact ? 650 : 305;
    const coordinates = this.rings?.length ? this.rings.flat() : this.regions.map(region => region.centroid);
    const points = coordinates.map(point => project(point, 0));
    const xs = points.map(point => point[0]), ys = points.map(point => point[1]);
    const bounds = [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
    const scale = Math.min(Math.max(120, width - left - right) / Math.max(.08, bounds[2] - bounds[0]), Math.max(100, height - top - bottom) / Math.max(.08, bounds[3] - bounds[1]));
    this.zoom = Math.max(3, Math.min(13, Math.floor(Math.log2(scale))));
    const center = [(bounds[0] + bounds[2]) / 2 * 2 ** this.zoom, (bounds[1] + bounds[3]) / 2 * 2 ** this.zoom];
    center[0] += (right - left) / 2;
    center[1] += (bottom - top) / 2;
    this.center = unproject(center, this.zoom);
    this.render();
  }

  setSignals(signals, selected, sequence) {
    this.signals = signals;
    this.sequence = sequence;
    for (const region of this.regions) {
      const button = this.buttons.get(region.id);
      const signal = signals.get(region.id);
      if (!signal) continue;
      button.classList.remove('normal', 'silence', 'spike', 'unknown', 'unavailable', 'selected');
      button.classList.add(signal.status);
      button.classList.toggle('selected', region.id === selected);
      button.setAttribute('aria-pressed', String(region.id === selected));
      button.setAttribute('aria-label', `${region.name}: ${statusLabels[signal.status]}, ${changeLabel(signal.change)}`);
      button.querySelector('small').textContent = signal.status === 'silence' ? `${changeLabel(signal.change)} DE ATIVIDADE` : statusLabels[signal.status];
      const index = sequence.findIndex(item => item.region.id === region.id);
      const badge = button.querySelector('.marker-index');
      badge.hidden = index < 0;
      // Simultaneous detections share the same rank; never invent an ordering.
      badge.textContent = index < 0 ? '' : String(1 + new Set(sequence.filter(item => item.frameIndex < sequence[index].frameIndex).map(item => item.frameIndex)).size);
    }
    this.renderOverlays();
  }

  screenPoint(coordinates) {
    const [x, y] = project(coordinates, this.zoom), [cx, cy] = project(this.center, this.zoom);
    return [x - cx + this.element.clientWidth / 2, y - cy + this.element.clientHeight / 2];
  }

  renderOverlays() {
    const boundary = this.element.querySelector('#state-boundary');
    boundary.replaceChildren();
    for (const ring of this.rings ?? []) {
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', ring.map((point, index) => `${index ? 'L' : 'M'}${this.screenPoint(point).join(',')}`).join(' ') + 'Z');
      boundary.append(path);
    }
    for (const region of this.regions) {
      const [x, y] = this.screenPoint(region.centroid);
      const button = this.buttons.get(region.id);
      button.style.left = `${x}px`;
      button.style.top = `${y}px`;
    }
    const layer = this.element.querySelector('#connections');
    layer.replaceChildren();
    const stages = [...new Set(this.sequence.map(item => item.frameIndex))];
    for (let index = 1; index < stages.length; index++) {
      const previous = this.sequence.filter(item => item.frameIndex === stages[index - 1]);
      const current = this.sequence.filter(item => item.frameIndex === stages[index]);
      for (const start of previous) for (const end of current) {
        const [x1, y1] = this.screenPoint(start.region.centroid), [x2, y2] = this.screenPoint(end.region.centroid);
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', `M${x1},${y1} Q${(x1 + x2) / 2 + 25},${(y1 + y2) / 2 - 30} ${x2},${y2}`);
        layer.append(path);
      }
    }
    this.element.querySelector('#connections-glow').replaceChildren(...[...layer.children].map(path => path.cloneNode()));
  }

  render() {
    const width = this.element.clientWidth, height = this.element.clientHeight;
    const [cx, cy] = project(this.center, this.zoom);
    const left = cx - width / 2, top = cy - height / 2;
    const count = 2 ** this.zoom;
    const visible = [];
    for (let y = Math.floor(top / 256); y <= Math.floor((top + height) / 256); y++) {
      if (y < 0 || y >= count) continue;
      for (let x = Math.floor(left / 256); x <= Math.floor((left + width) / 256); x++) {
        const wrappedX = ((x % count) + count) % count;
        const key = `${this.zoom}/${wrappedX}/${y}`;
        let tile = this.tileCache.get(key);
        if (!tile) {
          tile = document.createElement('img');
          tile.alt = '';
          tile.draggable = false;
          tile.decoding = 'async';
          tile.dataset.status = 'loading';
          tile.onload = () => { tile.dataset.status = 'loaded'; this.updateTileStatus(); };
          tile.onerror = () => { tile.dataset.status = 'error'; this.updateTileStatus(); };
          tile.src = `https://tile.openstreetmap.org/${key}.png`;
          this.tileCache.set(key, tile);
        }
        tile.style.left = `${Math.round(x * 256 - left)}px`;
        tile.style.top = `${Math.round(y * 256 - top)}px`;
        visible.push(tile);
      }
    }
    this.visibleTiles = visible;
    const visibleSet = new Set(visible);
    for (const child of [...this.tiles.children]) if (!visibleSet.has(child)) child.remove();
    for (const tile of visible) if (!tile.isConnected) this.tiles.append(tile);
    if (this.tileCache.size > 160) {
      for (const [key, tile] of this.tileCache) {
        if (!visibleSet.has(tile)) this.tileCache.delete(key);
        if (this.tileCache.size <= 100) break;
      }
    }
    this.updateTileStatus();
    this.renderOverlays();
  }

  updateTileStatus() {
    document.querySelector('#tile-status').hidden = !this.visibleTiles.some(tile => tile.dataset.status === 'error');
  }

  zoomBy(delta, anchor) {
    const next = Math.max(3, Math.min(17, this.zoom + delta));
    if (next === this.zoom) return;
    const offset = anchor ?? [this.element.clientWidth / 2, this.element.clientHeight / 2];
    const oldCenter = project(this.center, this.zoom);
    const dx = offset[0] - this.element.clientWidth / 2, dy = offset[1] - this.element.clientHeight / 2;
    const factor = 2 ** (next - this.zoom);
    this.center = unproject([(oldCenter[0] + dx) * factor - dx, (oldCenter[1] + dy) * factor - dy], next);
    this.zoom = next;
    this.render();
  }

  scheduleRender() {
    if (this.pendingFrame !== null) return;
    this.pendingFrame = requestAnimationFrame(() => { this.pendingFrame = null; this.render(); });
  }

  bindControls() {
    this.element.addEventListener('pointerdown', event => {
      if (event.button !== 0 || this.drag) return;
      this.drag = { id: event.pointerId, x: event.clientX, y: event.clientY, center: project(this.center, this.zoom) };
      this.element.setPointerCapture(event.pointerId);
      this.element.classList.add('dragging');
    });
    this.element.addEventListener('pointermove', event => {
      if (!this.drag || event.pointerId !== this.drag.id) return;
      this.center = unproject([this.drag.center[0] - event.clientX + this.drag.x, this.drag.center[1] - event.clientY + this.drag.y], this.zoom);
      this.scheduleRender();
    });
    const endDrag = () => { this.drag = null; this.element.classList.remove('dragging'); };
    this.element.addEventListener('pointerup', endDrag);
    this.element.addEventListener('pointercancel', endDrag);
    this.element.addEventListener('lostpointercapture', endDrag);
    let lastWheel = 0;
    this.element.addEventListener('wheel', event => {
      if (window.innerWidth <= 700 && !event.ctrlKey) return;
      event.preventDefault();
      if (Date.now() - lastWheel < 170) return;
      lastWheel = Date.now();
      const rect = this.element.getBoundingClientRect();
      this.zoomBy(event.deltaY < 0 ? 1 : -1, [event.clientX - rect.left, event.clientY - rect.top]);
    }, { passive: false });
    this.element.addEventListener('keydown', event => {
      if (event.target !== this.element) return;
      const movement = { ArrowLeft: [-80, 0], ArrowRight: [80, 0], ArrowUp: [0, -80], ArrowDown: [0, 80] }[event.key];
      if (movement) {
        event.preventDefault();
        const point = project(this.center, this.zoom);
        this.center = unproject([point[0] + movement[0], point[1] + movement[1]], this.zoom);
        this.render();
      } else if (['+', '=', '-'].includes(event.key)) {
        event.preventDefault(); this.zoomBy(event.key === '-' ? -1 : 1);
      }
    });
    document.querySelector('#zoom-in').addEventListener('click', () => this.zoomBy(1));
    document.querySelector('#zoom-out').addEventListener('click', () => this.zoomBy(-1));
    document.querySelector('#reset-map').addEventListener('click', () => this.fit());
  }
}
