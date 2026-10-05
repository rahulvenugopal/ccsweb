/* CCS charts: small dependency-free SVG charts for the CCS website.
   Every chart is drawn from assets/data/site-data.json (built from the research activity register).
   Colours follow the site palette; hover shows the exact value; each chart has a "View as table" fallback. */
(function (global) {
  var NS = 'http://www.w3.org/2000/svg';
  var C = { saffron: '#E8830A', teal: '#24A0A0', neutral: '#6B7F96', ink: '#FAF6EF', muted: '#8A9BB0', grid: 'rgba(250,246,239,.12)', surface: '#132030' };

  function s(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  var tip;
  function tipShow(ev, title, lines) {
    if (!tip) { tip = h('div', 'ccs-tip'); document.body.appendChild(tip); }
    tip.textContent = '';
    tip.appendChild(h('strong', null, title));
    (lines || []).forEach(function (l) { tip.appendChild(h('span', null, l)); });
    tip.style.display = 'block';
    var x = Math.min(ev.clientX + 14, window.innerWidth - tip.offsetWidth - 8);
    tip.style.left = Math.max(8, x) + 'px'; tip.style.top = (ev.clientY + 14) + 'px';
  }
  function tipHide() { if (tip) tip.style.display = 'none'; }
  function hover(node, title, lines) {
    node.addEventListener('mousemove', function (e) { tipShow(e, title, lines); });
    node.addEventListener('mouseleave', tipHide);
    node.addEventListener('focus', function () { var r = node.getBoundingClientRect(); tipShow({ clientX: r.left + r.width / 2, clientY: r.top }, title, lines); });
    node.addEventListener('blur', tipHide);
  }

  function niceMax(v) {
    if (v <= 5) return 5; if (v <= 10) return 10; if (v <= 20) return 20;
    var p = Math.pow(10, Math.floor(Math.log10(v))); return Math.ceil(v / p) * p;
  }
  function table(host, head, rows) {
    var d = h('details', 'ccs-table'); d.appendChild(h('summary', null, 'View as table'));
    var t = h('table'), tr = h('tr');
    head.forEach(function (c) { tr.appendChild(h('th', null, c)); });
    t.appendChild(h('thead')).appendChild(tr);
    var tb = h('tbody'); rows.forEach(function (r) { var x = h('tr'); r.forEach(function (c) { x.appendChild(h('td', null, c)); }); tb.appendChild(x); });
    t.appendChild(tb); d.appendChild(t); host.appendChild(d);
  }
  function legend(host, items) {
    var l = h('div', 'ccs-legend');
    items.forEach(function (i) { var li = h('span'); var sw = h('i'); sw.style.background = i.color; li.appendChild(sw); li.appendChild(document.createTextNode(i.label)); l.appendChild(li); });
    host.appendChild(l);
  }
  function svgRoot(host, w, hgt, label) {
    var r = s('svg', { viewBox: '0 0 ' + w + ' ' + hgt, role: 'img', 'aria-label': label, class: 'ccs-svg' });
    host.appendChild(r); return r;
  }
  function txt(parent, x, y, text, o) {
    var t = s('text', { x: x, y: y, fill: (o && o.fill) || C.muted, 'font-size': (o && o.size) || 11, 'text-anchor': (o && o.anchor) || 'middle', 'font-family': "'DM Mono', monospace" }, parent);
    t.textContent = text; return t;
  }

  /* Vertical bars. data: [{label, value, note}] */
  function bars(host, data, o) {
    o = o || {}; host.textContent = '';
    var W = o.width || 640, H = o.height || 290, L = 34, R = 10, T = 28, B = 36, pw = W - L - R, ph = H - T - B;
    var max = niceMax(Math.max.apply(null, data.map(function (d) { return d.value; })));
    var svg = svgRoot(host, W, H, o.label || 'Bar chart');
    for (var i = 0; i <= 4; i++) {
      var y = T + ph - ph * i / 4;
      s('line', { x1: L, x2: W - R, y1: y, y2: y, stroke: C.grid, 'stroke-width': 1 }, svg);
      txt(svg, L - 6, y + 4, Math.round(max * i / 4), { anchor: 'end', size: 12 });
    }
    var step = pw / data.length, bw = Math.min(54, step * 0.62);
    data.forEach(function (d, k) {
      var x = L + step * k + (step - bw) / 2, bh = d.value ? Math.max(3, ph * d.value / max) : 0, y = T + ph - bh;
      var g = s('g', { tabindex: 0 }, svg);
      if (bh) s('path', { d: 'M' + x + ',' + (y + bh) + 'V' + (y + 4) + 'Q' + x + ',' + y + ' ' + (x + 4) + ',' + y + 'H' + (x + bw - 4) + 'Q' + (x + bw) + ',' + y + ' ' + (x + bw) + ',' + (y + 4) + 'V' + (y + bh) + 'Z', fill: o.color || C.saffron }, g);
      else s('line', { x1: x, x2: x + bw, y1: T + ph - 1, y2: T + ph - 1, stroke: C.muted, 'stroke-width': 2 }, g);
      txt(g, x + bw / 2, y - 7, d.value, { fill: C.ink, size: 14 });
      txt(svg, x + bw / 2, H - 12, d.label, { size: 13 });
      var hit = s('rect', { x: L + step * k, y: T, width: step, height: ph + B, fill: 'transparent' }, g);
      hover(g, d.label, [d.value + (o.unit ? ' ' + o.unit : '')].concat(d.note ? [d.note] : []));
    });
    table(host, [o.xName || 'Year', o.yName || 'Count'], data.map(function (d) { return [d.label, String(d.value)]; }));
  }

  /* Horizontal bars. data: [{label, value, sub}] sorted as given */
  function hbars(host, data, o) {
    o = o || {}; host.textContent = '';
    var W = o.width || 640, rowH = o.rowH || 38, L = o.left || 200, R = o.right || 70, T = 6, H = T + rowH * data.length + 8;
    var max = o.max || Math.max.apply(null, data.map(function (d) { return d.value; })) * 1.05;
    var svg = svgRoot(host, W, H, o.label || 'Bar chart');
    data.forEach(function (d, k) {
      var y = T + k * rowH, bw = Math.max(d.value ? 3 : 0, (W - L - R) * d.value / max);
      var g = s('g', { tabindex: 0 }, svg);
      var name = d.label.length > 30 ? d.label.slice(0, 29) + '…' : d.label;
      txt(g, L - 10, y + rowH / 2 + 5, name, { anchor: 'end', fill: C.ink, size: 14 });
      s('rect', { x: L, y: y + 8, width: bw, height: rowH - 16, rx: 3, fill: d.color || o.color || C.saffron }, g);
      txt(g, L + bw + 8, y + rowH / 2 + 5, d.valueText || d.value, { anchor: 'start', fill: C.ink, size: 13 });
      s('rect', { x: 0, y: y, width: W, height: rowH, fill: 'transparent' }, g);
      hover(g, d.label, [d.valueText || String(d.value)].concat(d.sub ? [d.sub] : []));
    });
    table(host, [o.xName || 'Item', o.yName || 'Value'], data.map(function (d) { return [d.label, d.valueText || String(d.value)]; }));
  }

  /* Donut. slices: [{label, value, color}] */
  function donut(host, slices, o) {
    o = o || {}; host.textContent = '';
    var total = slices.reduce(function (a, b) { return a + b.value; }, 0), S = 220, c = S / 2, ro = 100, ri = 62;
    var wrap = h('div', 'ccs-donut'); host.appendChild(wrap);
    var svg = s('svg', { viewBox: '0 0 ' + S + ' ' + S, role: 'img', 'aria-label': o.label || 'Donut chart', class: 'ccs-svg ccs-donut-svg' }); wrap.appendChild(svg);
    var a0 = -Math.PI / 2;
    slices.forEach(function (sl) {
      if (!sl.value) return;
      var a1 = a0 + 2 * Math.PI * sl.value / total, large = a1 - a0 > Math.PI ? 1 : 0;
      function P(r, a) { return (c + r * Math.cos(a)).toFixed(2) + ',' + (c + r * Math.sin(a)).toFixed(2); }
      var d = 'M' + P(ro, a0) + 'A' + ro + ',' + ro + ' 0 ' + large + ' 1 ' + P(ro, a1) + 'L' + P(ri, a1) + 'A' + ri + ',' + ri + ' 0 ' + large + ' 0 ' + P(ri, a0) + 'Z';
      var p = s('path', { d: d, fill: sl.color, stroke: C.surface, 'stroke-width': 2, tabindex: 0 }, svg);
      hover(p, sl.label, [sl.value + ' of ' + total + ' (' + Math.round(100 * sl.value / total) + '%)']);
      var am = (a0 + a1) / 2; if (sl.value / total > 0.06) txt(svg, c + (ro + ri) / 2 * Math.cos(am), c + (ro + ri) / 2 * Math.sin(am) + 4, sl.value, { fill: '#0D1B2A', size: 13 }).setAttribute('font-weight', '700');
      a0 = a1;
    });
    txt(svg, c, c + 2, total, { fill: C.ink, size: 28 });
    txt(svg, c, c + 20, o.centre || 'total', { size: 10 });
    var side = h('div', 'ccs-donut-side'); wrap.appendChild(side);
    legend(side, slices.map(function (x) { return { label: x.label + ' · ' + x.value, color: x.color }; }));
    table(host, ['Outcome', 'Count'], slices.map(function (x) { return [x.label, String(x.value)]; }));
  }

  /* Stacked bars by year. rows: [{label, parts:{key:value}}], series: [{key,label,color}] bottom to top */
  function stacked(host, rows, series, o) {
    o = o || {}; host.textContent = '';
    var W = o.width || 640, H = o.height || 300, L = 34, R = 10, T = 28, B = 36, pw = W - L - R, ph = H - T - B;
    var tots = rows.map(function (r) { return series.reduce(function (a, se) { return a + (r.parts[se.key] || 0); }, 0); });
    var max = niceMax(Math.max.apply(null, tots));
    var svg = svgRoot(host, W, H, o.label || 'Stacked bar chart');
    for (var i = 0; i <= 4; i++) { var y = T + ph - ph * i / 4; s('line', { x1: L, x2: W - R, y1: y, y2: y, stroke: C.grid }, svg); txt(svg, L - 6, y + 4, Math.round(max * i / 4), { anchor: 'end', size: 12 }); }
    var step = pw / rows.length, bw = Math.min(54, step * 0.62);
    rows.forEach(function (r, k) {
      var x = L + step * k + (step - bw) / 2, yb = T + ph, g = s('g', { tabindex: 0 }, svg);
      series.forEach(function (se) {
        var v = r.parts[se.key] || 0; if (!v) return;
        var hh = ph * v / max; yb -= hh;
        s('rect', { x: x, y: yb, width: bw, height: hh, fill: se.color, stroke: C.surface, 'stroke-width': 2, rx: 2 }, g);
      });
      txt(g, x + bw / 2, yb - 7, tots[k], { fill: C.ink, size: 14 });
      txt(svg, x + bw / 2, H - 12, r.label, { size: 13 });
      s('rect', { x: L + step * k, y: T, width: step, height: ph + B, fill: 'transparent' }, g);
      hover(g, r.label, series.slice().reverse().map(function (se) { return se.label + ': ' + (r.parts[se.key] || 0); }));
    });
    legend(host, series.slice().reverse().map(function (se) { return { label: se.label, color: se.color }; }));
    table(host, ['Year'].concat(series.map(function (se) { return se.label; })), rows.map(function (r) { return [r.label].concat(series.map(function (se) { return String(r.parts[se.key] || 0); })); }));
  }

  /* Fill missing years between first and last so gaps read as zero */
  function yearRows(obj) {
    var ks = Object.keys(obj).map(Number).sort(function (a, b) { return a - b; }), out = [];
    for (var y = ks[0]; y <= ks[ks.length - 1]; y++) out.push({ label: String(y), value: obj[y] || 0 });
    return out;
  }

  global.CCSCharts = { bars: bars, hbars: hbars, donut: donut, stacked: stacked, yearRows: yearRows, colors: C, el: h };
})(window);
