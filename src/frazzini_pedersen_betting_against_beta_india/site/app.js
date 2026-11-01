/* Betting Against Beta in India: companion page.
   Reads data/snapshot.json and data/grid_<universe>.json, keeps the chosen
   specification in the URL hash, and recomputes every live table and chart. */
'use strict';

const COLOURS = {
  blue: '#4285f4',
  red: '#ea4335',
  yellow: '#fbbc05',
  green: '#34a853',
  grey: '#9aa0a6',
  dark: '#202124',
};
const FONT = "'Times New Roman', Tinos, 'Liberation Serif', serif";
const LAGS = 6;
const UNIVERSE_NAMES = {
  A: 'All NSE shares',
  B: 'Liquid 500',
  C: 'Shares with stock futures',
};
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const LONG_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const US_ALPHA = [0.40, 0.37, 0.30, 0.25, 0.18, 0.20, 0.09, 0.11, 0.01, -0.13];

const state = {
  universe: 'A', vol: 12, corr: 60, k: 1, w: 0.6, weighting: 'rank',
  portfolio: 'bab', costs: 'gross', start: 1999,
  deciles: 'deciles_A_equal', window: '1999-04', sub: 'A',
};
let snapshot = null;
const grids = {};
const charts = {};

/* ---------- small helpers ---------- */

function el(id) {
  return document.getElementById(id);
}

function fmt(value, digits) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '';
  }
  const text = value.toFixed(digits);
  return text.replace('-', '−');
}

function pct(value, digits = 2) {
  return value === null || value === undefined ? '' : fmt(100 * value, digits);
}

function cell(value, t, digits = 2, scale = 100) {
  const main = value === null || value === undefined ? '' : fmt(scale * value, digits);
  const cls = value !== null && value < 0 ? ' class="negative"' : '';
  const tLine = t === null || t === undefined ? '' : `<span class="t">(${fmt(t, 2)})</span>`;
  return `<td${cls}>${main}${tLine}</td>`;
}

function tableValue(name, row, column) {
  const table = snapshot.tables[name];
  const r = table.rows.indexOf(row);
  const c = table.columns.indexOf(column);
  if (r < 0 || c < 0) {
    return null;
  }
  return table.values[r][c];
}

function seriesFor(name) {
  return snapshot.series.values[name];
}

function riskFreeMap() {
  if (!riskFreeMap.cache) {
    const map = {};
    snapshot.risk_free.months.forEach((m, i) => {
      map[m] = snapshot.risk_free.values[i] / 10000;
    });
    riskFreeMap.cache = map;
  }
  return riskFreeMap.cache;
}

/* ---------- statistics, matching the study's Python code ---------- */

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function stdev(values) {
  const m = mean(values);
  const s = values.reduce((a, b) => a + (b - m) * (b - m), 0);
  return Math.sqrt(s / (values.length - 1));
}

function neweyWestT(values, lags = LAGS) {
  const n = values.length;
  if (n < 3) {
    return null;
  }
  const m = mean(values);
  const d = values.map((v) => v - m);
  let variance = d.reduce((a, b) => a + b * b, 0) / n;
  for (let lag = 1; lag <= lags; lag += 1) {
    let g = 0;
    for (let i = lag; i < n; i += 1) {
      g += d[i] * d[i - lag];
    }
    g /= n;
    variance += 2 * (1 - lag / (lags + 1)) * g;
  }
  return m / Math.sqrt(variance / n);
}

function drawdowns(values) {
  let wealth = 1;
  let peak = 1;
  return values.map((v) => {
    wealth *= 1 + v;
    peak = Math.max(peak, wealth);
    return wealth / peak - 1;
  });
}

function summary(values) {
  if (values.length < 3) {
    return null;
  }
  const sd = stdev(values);
  const m = mean(values);
  let wealth = 1;
  values.forEach((v) => {
    wealth *= 1 + v;
  });
  return {
    months: values.length,
    mean: m,
    t: neweyWestT(values),
    volatility: sd * Math.sqrt(12),
    sharpe: (m / sd) * Math.sqrt(12),
    drawdown: Math.min(...drawdowns(values)),
    compound: Math.pow(wealth, 12 / values.length) - 1,
  };
}

/* ---------- the specification ---------- */

function readHash() {
  const hash = window.location.hash.replace('#', '');
  if (!hash) {
    return;
  }
  hash.split('&').forEach((part) => {
    const [key, value] = part.split('=');
    if (!(key in state) || value === undefined) {
      return;
    }
    const numeric = ['vol', 'corr', 'k', 'w', 'start'];
    state[key] = numeric.includes(key) ? Number(value) : decodeURIComponent(value);
  });
}

function writeHash() {
  const keys = ['universe', 'vol', 'corr', 'k', 'w', 'weighting', 'portfolio', 'costs', 'start'];
  const hash = keys.map((k) => `${k}=${state[k]}`).join('&');
  history.replaceState(null, '', `#${hash}`);
}

function setupControls() {
  const start = el('control-start');
  for (let year = 1999; year <= 2022; year += 1) {
    const option = document.createElement('option');
    option.value = String(year);
    option.textContent = year === 1999 ? '1999 (all months)' : String(year);
    start.appendChild(option);
  }
  const bindings = {
    'control-universe': 'universe',
    'control-vol': 'vol',
    'control-corr': 'corr',
    'control-k': 'k',
    'control-w': 'w',
    'control-weighting': 'weighting',
    'control-portfolio': 'portfolio',
    'control-costs': 'costs',
    'control-start': 'start',
  };
  Object.entries(bindings).forEach(([id, key]) => {
    const control = el(id);
    control.value = String(state[key]);
    control.addEventListener('change', () => {
      const numeric = ['vol', 'corr', 'k', 'w', 'start'];
      state[key] = numeric.includes(key) ? Number(control.value) : control.value;
      writeHash();
      drawLive();
    });
  });
}

function variantId(universe, vol, corr, w, k, weighting) {
  const match = snapshot.variants.find((v) => v[1] === universe && v[2] === vol
    && v[3] === corr && Math.abs(v[4] - w) < 1e-9 && v[5] === k && v[6] === weighting);
  return match ? match[0] : null;
}

async function loadGrid(universe) {
  if (!grids[universe]) {
    const response = await fetch(`data/grid_${universe}.json`);
    grids[universe] = await response.json();
  }
  return grids[universe];
}

/* Returns {months, values, market} for a variant: the portfolio's monthly
   excess return and the market's excess return, both decimals, over the
   chosen sample. */
function variantSeries(grid, settings) {
  const id = variantId(settings.universe, settings.vol, settings.corr, settings.w, settings.k, settings.weighting);
  if (id === null) {
    return null;
  }
  let source;
  if (settings.portfolio === 'bab') {
    source = grid.bab[String(id)];
  } else {
    source = grid.long[`${settings.vol}-${settings.corr}-${settings.k}-${settings.weighting}`];
  }
  const rf = riskFreeMap();
  const marketMonths = snapshot.series.months;
  const market = seriesFor('NIFTY 500 TRI');
  const marketMap = {};
  marketMonths.forEach((m, i) => {
    marketMap[m] = market[i];
  });
  const out = { months: [], values: [], total: [], market: [], marketTotal: [] };
  grid.months.forEach((month, i) => {
    const gross = source.g[i];
    if (gross === null || Number(month.slice(0, 4)) < settings.start) {
      return;
    }
    const cost = settings.costs === 'net' ? (source.c[i] || 0) : 0;
    const value = (gross - cost) / 10000;
    const riskFree = rf[month] || 0;
    const marketTotal = marketMap[month] === null || marketMap[month] === undefined ? null : marketMap[month] / 10000;
    if (marketTotal === null) {
      return;
    }
    out.months.push(month);
    if (settings.portfolio === 'bab') {
      out.values.push(value);
      out.total.push(value);
    } else {
      out.values.push(value - riskFree);
      out.total.push(value);
    }
    out.market.push(marketTotal - riskFree);
    out.marketTotal.push(marketTotal);
  });
  return out;
}

/* ---------- live section ---------- */

async function drawLive() {
  const grid = await loadGrid(state.universe);
  const data = variantSeries(grid, state);
  const portfolioName = state.portfolio === 'bab' ? 'BAB long-short' : 'Low-beta half, long only';
  el('spec-summary').innerHTML = `${UNIVERSE_NAMES[state.universe]}; <i>J</i><sub>σ</sub> = ${state.vol}, <i>J</i><sub>ρ</sub> = ${state.corr} months; <i>K</i> = ${state.k}; <i>w</i> = ${state.w}; ${state.weighting} weights; ${portfolioName}; ${state.costs === 'net' ? 'after' : 'before'} costs; from ${state.start}. Link: <code>${window.location.hash}</code>`;
  if (!data || data.values.length < 3) {
    el('table-live').innerHTML = '<tr><td class="loading">No months for this choice.</td></tr>';
    return;
  }
  const own = summary(data.values);
  const market = summary(data.market);
  drawCards(own, market);
  drawLiveTable(own, market, data);
  drawGrowth(data);
  drawDrawdown(data);
  drawCalendar(data);
  drawHeat(grid);
  drawKW(grid);
}

function drawCards(own, market) {
  const cards = [
    ['blue', 'Mean excess return', `${pct(own.mean)}% a month`],
    ['green', 'Newey-West t', fmt(own.t, 2)],
    ['yellow', 'Sharpe ratio', `${fmt(own.sharpe, 2)} (market ${fmt(market.sharpe, 2)})`],
    ['red', 'Worst drawdown', `${pct(own.drawdown, 0)}%`],
  ];
  el('stat-cards').innerHTML = cards.map(([colour, label, value]) => `<div class="stat-card ${colour}"><div class="label">${label}</div><div class="value">${value}</div></div>`).join('');
}

function drawLiveTable(own, market, data) {
  const head = '<thead><tr><th></th><th>Mean</th><th>Volatility</th><th>Sharpe</th><th>Worst drawdown</th><th>Compound a year</th><th>Months</th></tr></thead>';
  const row = (name, s) => `<tr><th>${name}</th>${cell(s.mean, s.t)}<td>${pct(s.volatility, 1)}</td><td>${fmt(s.sharpe, 2)}</td><td class="negative">${pct(s.drawdown, 0)}</td><td>${pct(s.compound, 1)}</td><td>${s.months}</td></tr>`;
  el('table-live').innerHTML = `${head}<tbody>${row('Chosen portfolio', own)}${row('NIFTY 500 TRI', market)}</tbody>`;
  const first = data.months[0];
  const last = data.months[data.months.length - 1];
  el('table-live').insertAdjacentHTML('beforeend', `<caption style="caption-side:bottom;text-align:left;font-size:13px;color:#5f6368;padding-top:4px">${first} to ${last}. The <i>t</i>-statistic is beneath the mean.</caption>`);
}

function chart(id) {
  if (!charts[id]) {
    charts[id] = echarts.init(el(id), null, { renderer: 'svg' });
    window.addEventListener('resize', () => charts[id].resize());
  }
  return charts[id];
}

function baseOption() {
  return {
    textStyle: { fontFamily: FONT, fontSize: 13 },
    grid: { left: 56, right: 18, top: 36, bottom: 36 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { top: 0, itemGap: 28, textStyle: { fontFamily: FONT } },
  };
}

function cumulative(values) {
  let wealth = 1;
  return values.map((v) => {
    wealth *= 1 + v;
    return Number(wealth.toFixed(4));
  });
}

function drawGrowth(data) {
  const bab = state.portfolio === 'bab';
  const own = cumulative(bab ? data.values : data.total);
  const market = cumulative(bab ? data.market : data.marketTotal);
  const option = baseOption();
  option.xAxis = { type: 'category', data: data.months, boundaryGap: false };
  const all = own.concat(market).filter((v) => v > 0);
  option.yAxis = {
    type: 'log',
    logBase: 10,
    name: '₹',
    min: Number((Math.min(...all) * 0.9).toPrecision(2)),
    max: Number((Math.max(...all) * 1.1).toPrecision(2)),
    axisLabel: { formatter: (v) => (v >= 10 ? v.toFixed(0) : v.toPrecision(2)) },
  };
  option.series = [
    { name: bab ? 'BAB (excess return)' : 'Low-beta half (total return)', type: 'line', data: own, showSymbol: false, lineStyle: { width: 2, color: COLOURS.blue }, itemStyle: { color: COLOURS.blue } },
    { name: bab ? 'NIFTY 500 TRI (excess return)' : 'NIFTY 500 TRI', type: 'line', data: market, showSymbol: false, lineStyle: { width: 1.5, color: COLOURS.grey }, itemStyle: { color: COLOURS.grey } },
  ];
  chart('chart-growth').setOption(option, true);
}

function drawDrawdown(data) {
  const bab = state.portfolio === 'bab';
  const option = baseOption();
  option.xAxis = { type: 'category', data: data.months, boundaryGap: false };
  option.yAxis = { type: 'value', axisLabel: { formatter: (v) => `${Math.round(v * 100)}%` }, max: 0 };
  option.tooltip.valueFormatter = (v) => `${(v * 100).toFixed(1)}%`;
  option.series = [
    { name: 'Chosen portfolio', type: 'line', data: drawdowns(bab ? data.values : data.total).map((v) => Number(v.toFixed(4))), showSymbol: false, areaStyle: { color: 'rgba(234,67,53,0.18)' }, lineStyle: { color: COLOURS.red, width: 1.5 }, itemStyle: { color: COLOURS.red } },
    { name: 'NIFTY 500 TRI', type: 'line', data: drawdowns(bab ? data.market : data.marketTotal).map((v) => Number(v.toFixed(4))), showSymbol: false, lineStyle: { color: COLOURS.grey, width: 1 }, itemStyle: { color: COLOURS.grey } },
  ];
  chart('chart-drawdown').setOption(option, true);
}

function drawCalendar(data) {
  const years = [...new Set(data.months.map((m) => m.slice(0, 4)))];
  const points = data.months.map((m, i) => [Number(m.slice(5, 7)) - 1, years.indexOf(m.slice(0, 4)), Number((100 * data.values[i]).toFixed(1))]);
  const limit = Math.max(5, ...points.map((p) => Math.abs(p[2])).sort((a, b) => a - b).slice(0, Math.floor(points.length * 0.95)));
  const option = {
    textStyle: { fontFamily: FONT, fontSize: 12 },
    grid: { left: 48, right: 18, top: 10, bottom: 60 },
    tooltip: { formatter: (p) => `${years[p.value[1]]} ${MONTH_NAMES[p.value[0]]}: ${fmt(p.value[2], 1)}%` },
    xAxis: { type: 'category', data: MONTH_NAMES, splitArea: { show: false } },
    yAxis: { type: 'category', data: years, inverse: true },
    visualMap: { min: -limit, max: limit, calculable: false, orient: 'horizontal', left: 'center', bottom: 0, itemHeight: 160, inRange: { color: [COLOURS.red, '#f1f3f4', COLOURS.blue] }, textStyle: { fontFamily: FONT } },
    series: [{ type: 'heatmap', data: points, label: { show: false }, itemStyle: { borderColor: '#ffffff', borderWidth: 1 } }],
  };
  el('chart-calendar').style.height = `${Math.max(360, years.length * 16 + 80)}px`;
  chart('chart-calendar').resize();
  chart('chart-calendar').setOption(option, true);
}

function settingStats(grid, overrides) {
  const settings = { ...state, ...overrides };
  const data = variantSeries(grid, settings);
  return data && data.values.length >= 3 ? summary(data.values) : null;
}

function drawHeat(grid) {
  const vols = [6, 12, 24];
  const corrs = [12, 36, 60];
  const points = [];
  vols.forEach((vol, x) => {
    corrs.forEach((corr, y) => {
      const s = settingStats(grid, { vol, corr });
      if (s) {
        points.push([x, y, Number(s.t.toFixed(2)), Number((100 * s.mean).toFixed(2))]);
      }
    });
  });
  const option = {
    textStyle: { fontFamily: FONT, fontSize: 13 },
    grid: { left: 110, right: 18, top: 10, bottom: 70 },
    tooltip: { formatter: (p) => `Volatility ${vols[p.value[0]]}m, correlation ${corrs[p.value[1]]}m: t = ${fmt(p.value[2], 2)}, mean ${fmt(p.value[3], 2)}%` },
    xAxis: { type: 'category', data: vols.map((v) => `${v} months`), name: 'Volatility window', nameLocation: 'middle', nameGap: 28 },
    yAxis: { type: 'category', data: corrs.map((c) => `${c} months`), name: 'Correlation', nameLocation: 'middle', nameGap: 80 },
    visualMap: { min: -4, max: 4, calculable: false, orient: 'horizontal', left: 'center', bottom: 0, itemHeight: 160, inRange: { color: [COLOURS.red, '#f1f3f4', COLOURS.blue] }, textStyle: { fontFamily: FONT } },
    series: [{ type: 'heatmap', data: points, label: { show: true, fontFamily: FONT, fontSize: 14, formatter: (p) => `${fmt(p.value[2], 2)}\n(${fmt(p.value[3], 2)})` }, itemStyle: { borderColor: '#ffffff', borderWidth: 2 } }],
  };
  chart('chart-heat').setOption(option, true);
}

function drawKW(grid) {
  const ks = [1, 3, 6, 12];
  const ws = [0.4, 0.6, 0.8, 1];
  const head = `<thead><tr><th><i>K</i> \\ <i>w</i></th>${ws.map((w) => `<th>${w === 1 ? '1.0' : w}</th>`).join('')}</tr></thead>`;
  const rows = ks.map((k) => {
    const cells = ws.map((w) => {
      const s = settingStats(grid, { k, w });
      return s ? cell(s.mean, s.t) : '<td></td>';
    }).join('');
    const highlight = k === state.k ? ' class="highlight"' : '';
    return `<tr${highlight}><th>${k} month${k > 1 ? 's' : ''}</th>${cells}</tr>`;
  }).join('');
  el('table-kw').innerHTML = `${head}<tbody>${rows}</tbody>`;
}

/* ---------- the static tables ---------- */

function switchButtons(id, options, key, redraw) {
  const box = el(id);
  box.innerHTML = '';
  options.forEach(([value, label]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    if (state[key] === value) {
      button.classList.add('active');
    }
    button.addEventListener('click', () => {
      state[key] = value;
      switchButtons(id, options, key, redraw);
      redraw();
    });
    box.appendChild(button);
  });
}

function drawDeciles() {
  const name = state.deciles;
  const columns = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'BAB'];
  const head = `<thead><tr><th></th>${columns.map((c) => `<th>${c}</th>`).join('')}</tr></thead>`;
  const line = (label, key, tKey, scale = 100, digits = 2) => `<tr><th>${label}</th>${columns.map((c) => cell(tableValue(name, c, key), tKey ? tableValue(name, c, tKey) : null, digits, scale)).join('')}</tr>`;
  const body = [
    line('Excess return', 'excess_mean', 'newey_west_t'),
    line('CAPM α', 'capm_alpha', 'capm_alpha_t'),
    line('3-factor α', 'ff3_alpha', 'ff3_alpha_t'),
    line('4-factor α', 'carhart_alpha', 'carhart_alpha_t'),
    line('β ex ante', 'ex_ante_beta', null, 1),
    line('β realised', 'capm_beta_MF', null, 1),
    line('Volatility, % a year', 'volatility', null, 100, 1),
    line('Sharpe ratio', 'sharpe', null, 1),
    line('Worst drawdown, %', 'max_drawdown', null, 100, 0),
    `<tr class="group-start"><th>US 4-factor α (paper)</th>${US_ALPHA.map((v) => cell(v, null, 2, 1)).join('')}${cell(0.55, 5.59, 2, 1)}</tr>`,
  ].join('');
  el('table-deciles').innerHTML = `${head}<tbody>${body}</tbody>`;
  const option = baseOption();
  option.xAxis = { type: 'category', data: columns.slice(0, 10) };
  option.yAxis = { type: 'value', name: '% a month' };
  option.series = [
    { name: 'India', type: 'bar', data: columns.slice(0, 10).map((c) => Number((100 * tableValue(name, c, 'carhart_alpha')).toFixed(2))), itemStyle: { color: COLOURS.blue } },
    { name: 'United States (paper)', type: 'bar', data: US_ALPHA, itemStyle: { color: COLOURS.grey } },
  ];
  chart('chart-alpha').setOption(option, true);
}

function statsTable(id, name, rows, labels) {
  const head = '<thead><tr><th></th><th>Excess return</th><th>4-factor α</th><th>Volatility</th><th>Sharpe</th><th>Worst drawdown</th><th>Months</th></tr></thead>';
  const body = rows.map((row, i) => {
    const v = (c) => tableValue(name, row, c);
    const months = v('months');
    return `<tr${labels[i].startsWith('|') ? ' class="group-start"' : ''}><th>${labels[i].replace('|', '')}</th>${cell(v('excess_mean'), v('newey_west_t'))}${cell(v('carhart_alpha'), v('carhart_alpha_t'))}<td>${pct(v('volatility'), 1)}</td><td>${fmt(v('sharpe'), 2)}</td><td class="negative">${pct(v('max_drawdown'), 0)}</td><td>${months === null ? '' : Math.round(months)}</td></tr>`;
  }).join('');
  el(id).innerHTML = `${head}<tbody>${body}</tbody>`;
}

function drawUniverses() {
  const rows = [];
  const labels = [];
  ['A', 'B', 'C'].forEach((u, i) => {
    rows.push(`${u} BAB`, `${u} BAB after costs`);
    labels.push(`${i ? '|' : ''}${UNIVERSE_NAMES[u]}, before costs`, `${UNIVERSE_NAMES[u]}, after costs`);
  });
  statsTable('table-universes', 'bab_summary', rows, labels);
}

function drawTradeable() {
  const table = snapshot.tables.tradeable_vs_benchmarks;
  const prefix = `from ${state.window}: `;
  const rows = table.rows.filter((r) => r.startsWith(prefix));
  const labels = rows.map((r, i) => {
    const label = r.replace(prefix, '');
    const isBench = label.startsWith('NIFTY');
    const prevBench = i > 0 && rows[i - 1].replace(prefix, '').startsWith('NIFTY');
    return (isBench && !prevBench ? '|' : '') + label;
  });
  statsTable('table-tradeable', 'tradeable_vs_benchmarks', rows, labels);
}

function drawSize() {
  const sizeRows = snapshot.tables.size_terciles_A.rows;
  const screenRows = snapshot.tables.liquidity_screens_A.rows;
  const head = '<thead><tr><th></th><th>Excess return</th><th>4-factor α</th><th>Volatility</th><th>Sharpe</th><th>Worst drawdown</th><th>Months</th></tr></thead>';
  const line = (name, row, label, group) => {
    const v = (c) => tableValue(name, row, c);
    return `<tr${group ? ' class="group-start"' : ''}><th>${label}</th>${cell(v('excess_mean'), v('newey_west_t'))}${cell(v('carhart_alpha'), v('carhart_alpha_t'))}<td>${pct(v('volatility'), 1)}</td><td>${fmt(v('sharpe'), 2)}</td><td class="negative">${pct(v('max_drawdown'), 0)}</td><td>${Math.round(v('months'))}</td></tr>`;
  };
  const names = ['Least traded third', 'Middle third', 'Most traded third'];
  const body = sizeRows.map((r, i) => line('size_terciles_A', r, names[i], false)).join('')
    + screenRows.map((r, i) => line('liquidity_screens_A', r, r.replace('drop bottom 0% by traded value, price >= Rs ', 'All shares; price ≥ ₹').replace('drop bottom', 'Drop the bottom').replace('by traded value, price >= Rs ', 'by traded value; price ≥ ₹'), i === 0)).join('');
  el('table-size').innerHTML = `${head}<tbody>${body}</tbody>`;
}

function drawSub() {
  const name = `sub_periods_${state.sub}`;
  const rows = snapshot.tables[name].rows;
  statsTable('table-sub', name, rows, rows);
}

function drawCompression() {
  const head = '<thead><tr><th>Stress measure</th><th>Third</th><th>Beta dispersion</th><th>BAB market beta</th><th>Months</th></tr></thead>';
  const parts = [['compression_realised_vol', 'NIFTY 500 realised volatility'], ['compression_india_vix', 'India VIX']];
  const body = parts.map(([name, label], p) => snapshot.tables[name].rows.map((row, i) => {
    const v = (c) => tableValue(name, row, c);
    const dispersion = row === 'high minus low' ? cell(v('dispersion'), v('dispersion_t'), 3, 1) : `<td>${fmt(v('dispersion'), 3)}</td>`;
    const beta = row === 'high minus low' ? `<td>${fmt(v('bab_beta'), 2)}</td>` : cell(v('bab_beta'), v('bab_beta_t'), 2, 1);
    const months = v('months');
    return `<tr${p && i === 0 ? ' class="group-start"' : ''}><th>${i === 0 ? label : ''}</th><th>${row}</th>${dispersion}${beta}<td>${months === null ? '' : Math.round(months)}</td></tr>`;
  }).join('')).join('');
  el('table-compression').innerHTML = `${head}<tbody>${body}</tbody>`;
}

function drawStress() {
  const sources = [
    ['borrow_sensitivity', (r) => r.replace('A fee', 'All NSE after costs, lending fee').replace('B fee', 'Liquid 500 after costs, lending fee').replace('.00%', '%')],
    ['roll_sensitivity', (r) => r.replace('after costs, roll impact', 'after costs, roll impact')],
    ['delisting_stress', (r) => r.replace('BAB A', 'BAB, all NSE').replace('shock -', 'delisting loss ').replace('shock 0%', 'no delisting loss')],
  ];
  const head = '<thead><tr><th></th><th>Excess return</th><th>4-factor α</th><th>Sharpe</th><th>Worst drawdown</th><th>Months</th></tr></thead>';
  const body = sources.map(([name, label], s) => snapshot.tables[name].rows.map((row, i) => {
    const v = (c) => tableValue(name, row, c);
    return `<tr${s && i === 0 ? ' class="group-start"' : ''}><th>${label(row)}</th>${cell(v('excess_mean'), v('newey_west_t'))}${cell(v('carhart_alpha'), v('carhart_alpha_t'))}<td>${fmt(v('sharpe'), 2)}</td><td class="negative">${pct(v('max_drawdown'), 0)}</td><td>${Math.round(v('months'))}</td></tr>`;
  }).join('')).join('');
  el('table-stress').innerHTML = `${head}<tbody>${body}</tbody>`;
}

function drawYears() {
  const table = snapshot.tables.calendar_years_A;
  const years = table.rows;
  const names = [['BAB', COLOURS.blue], ['MKT', COLOURS.grey], ['SMB', COLOURS.yellow], ['HML', COLOURS.green], ['WML', COLOURS.red]];
  const option = baseOption();
  option.xAxis = { type: 'category', data: years };
  option.yAxis = { type: 'value', axisLabel: { formatter: (v) => `${Math.round(v * 100)}%` } };
  option.tooltip.valueFormatter = (v) => (v === null ? '' : `${(v * 100).toFixed(1)}%`);
  option.series = names.map(([name, colour]) => ({
    name,
    type: name === 'BAB' ? 'bar' : 'line',
    data: years.map((y) => tableValue('calendar_years_A', y, name)),
    itemStyle: { color: colour },
    lineStyle: { color: colour, width: 1 },
    showSymbol: false,
  }));
  chart('chart-years').setOption(option, true);
}

/* ---------- filling the text ---------- */

function fillText() {
  const months = snapshot.series.months;
  const bab = seriesFor('BAB A');
  let last = months[months.length - 1];
  for (let i = months.length - 1; i >= 0; i -= 1) {
    if (bab[i] !== null) {
      last = months[i];
      break;
    }
  }
  const fills = {
    end_year: last.slice(0, 4),
    end_label: `${LONG_MONTHS[Number(last.slice(5, 7)) - 1]} ${last.slice(0, 4)}`,
    bab_a: pct(tableValue('bab_summary', 'A BAB', 'excess_mean')),
    bab_a_t: fmt(tableValue('bab_summary', 'A BAB', 'newey_west_t'), 2),
    bab_a_sharpe: fmt(tableValue('bab_summary', 'A BAB', 'sharpe'), 2),
    bab_b: pct(tableValue('bab_summary', 'B BAB', 'excess_mean')),
    bab_c: pct(tableValue('bab_summary', 'C BAB', 'excess_mean')),
    t1_net: pct(tableValue('tradeable', 'T1 after costs', 'excess_mean')),
  };
  document.querySelectorAll('[data-fill]').forEach((node) => {
    const value = fills[node.dataset.fill];
    if (value !== undefined) {
      node.textContent = value;
    }
  });
}

function setupCitation() {
  el('copy-citation').addEventListener('click', () => {
    navigator.clipboard.writeText(el('citation-text').textContent).then(() => {
      el('copy-citation').textContent = 'Copied';
    });
  });
}

async function main() {
  readHash();
  const response = await fetch('data/snapshot.json');
  snapshot = await response.json();
  fillText();
  setupControls();
  setupCitation();
  switchButtons('decile-switch', [
    ['deciles_A_equal', 'All NSE, equal'], ['deciles_A_value', 'All NSE, traded value'],
    ['deciles_B_equal', 'Liquid 500, equal'], ['deciles_B_value', 'Liquid 500, traded value'],
    ['deciles_C_equal', 'Futures shares, equal'],
  ], 'deciles', drawDeciles);
  switchButtons('window-switch', [['1999-04', 'From April 1999'], ['2006-01', 'From 2006']], 'window', drawTradeable);
  switchButtons('sub-switch', [['A', 'All NSE'], ['B', 'Liquid 500'], ['C', 'Futures shares']], 'sub', drawSub);
  drawDeciles();
  drawUniverses();
  drawTradeable();
  drawSize();
  drawSub();
  drawCompression();
  drawStress();
  drawYears();
  writeHash();
  await drawLive();
}

main();
