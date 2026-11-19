/* Mobile.Deals tools: plan finder, data calculator, bill audit, quick save, true cost, deal check, trade-in, eSIM, deals filter. */
(function () {
  'use strict';
  var d = document, M = window.MD || {}, R = M.root || '';
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  function num(id, def) { var el = d.getElementById(id); var v = el ? parseFloat(el.value) : NaN; return isNaN(v) ? (def || 0) : v; }
  function money(v, dp) { return '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: dp || 0, maximumFractionDigits: dp || 0 }); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function on(els, ev, fn) { els.forEach(function (el) { if (el) el.addEventListener(ev, fn); }); }
  var aff = (window.MD_CONFIG || {}).affiliates || {};

  var PLANS = [];
  try { PLANS = JSON.parse(($('#plansData') || {}).textContent || '[]'); } catch (e) { PLANS = []; }

  /* monthly total for N lines; needGB = per-line data need (0 = any) */
  function total(p, lines, needGB) {
    var m = p.multi && p.multi[String(lines)];
    var base = (m != null) ? m : p.price * lines;
    if (p.perGB) base += p.perGB * Math.max(1, needGB || 3) * lines;
    return Math.round(base * 100) / 100;
  }
  function fits(p, o) {
    if (o.need >= 999 && (p.data < 999 || p.perGB)) return false;
    if (o.need > 0 && o.need < 999 && !p.perGB && p.data < o.need) return false;
    if (o.network && o.network !== 'any' && p.network !== o.network) return false;
    if (o.hotspot && !p.hotspot) return false;
    return true;
  }
  function dataLabel(p) { return p.data >= 999 ? 'Unlimited data' : (p.perGB ? 'Pay per GB ($' + p.perGB + '/GB)' : p.data + 'GB data'); }
  function link(p) { return aff[p.aff] || p.url; }
  function nm(p) { return p.plan === p.carrier ? p.carrier : p.carrier + ' ' + p.plan; }

  /* ---------------- Plan Finder */
  var pf = $('#planFinder');
  if (pf && PLANS.length) {
    var q = new URLSearchParams(location.search);
    if (q.get('data') && $('#pfData')) $('#pfData').value = q.get('data');
    if (q.get('lines') && $('#pfLines')) $('#pfLines').value = q.get('lines');
    var runPF = function () {
      var o = { budget: num('pfBudget', 100), need: num('pfData', 0), lines: num('pfLines', 1), network: $('#pfNetwork').value, hotspot: $('#pfHotspot').checked, sort: $('#pfSort').value };
      $('#pfBudgetOut').textContent = money(o.budget);
      var rows = PLANS.filter(function (p) { return fits(p, o); }).map(function (p) {
        var t = total(p, o.lines, o.need), per = t / o.lines;
        var gb = p.data >= 999 ? 50 : (p.perGB ? Math.max(1, o.need || 3) : p.data);
        return { p: p, t: t, per: per, cpg: per / gb, t24: t * 24 };
      }).filter(function (r) { return r.per <= o.budget + 0.001; });
      rows.sort(function (a, b) { return o.sort === 'price' ? a.per - b.per : o.sort === 'cpg' ? a.cpg - b.cpg : a.t24 - b.t24; });
      $('#pfCount').textContent = rows.length + ' plan' + (rows.length === 1 ? '' : 's') + ' match · ' + o.lines + ' line' + (o.lines > 1 ? 's' : '') + ' · sorted by ' + { total: '24-month total', price: 'monthly price', cpg: 'cost per GB' }[o.sort];
      $('#pfResults').innerHTML = rows.map(function (r, i) {
        var p = r.p;
        var feats = [dataLabel(p), p.hotspot ? 'Hotspot included' : 'No hotspot listed', p.term, p.perks].filter(Boolean).map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('');
        return '<article class="card plan-card">' + (i === 0 ? '<span class="plan-rank">Best match</span>' : '') +
          '<div class="plan-top"><div><p class="plan-carrier">' + esc(p.carrier) + '</p><h3 class="plan-name">' + esc(p.plan) + '</h3></div><span class="net">' + esc(p.network) + '</span></div>' +
          '<p class="plan-price"><b>' + money(r.per, r.per % 1 ? 2 : 0) + '</b><span>/mo per line' + (o.lines > 1 ? ' (' + money(r.t, r.t % 1 ? 2 : 0) + ' total)' : '') + '</span></p>' +
          '<ul class="plan-feats">' + feats + '</ul>' +
          '<p class="plan-total">24-mo total, ' + o.lines + ' line' + (o.lines > 1 ? 's' : '') + ': <b>' + money(r.t24) + '</b> &middot; $' + r.cpg.toFixed(2) + '/GB</p>' +
          '<p class="plan-best">Best for: ' + esc(p.best) + '</p>' +
          '<a class="btn btn-primary btn-sm btn-block" href="' + esc(link(p)) + '" target="_blank" rel="nofollow noopener sponsored">See plan <span aria-hidden="true">&#8599;</span></a></article>';
      }).join('') || '<div class="card"><h3>No plans match those filters</h3><p class="muted">Try a higher budget or fewer requirements.</p></div>';
    };
    on($$('input,select', pf), 'input', runPF); on($$('input,select', pf), 'change', runPF);
    runPF();
  }

  /* ---------------- Data calculator */
  var dc = $('#dataCalc');
  if (dc) {
    var runDC = function () {
      var gb = 0;
      $$('input[type=range]', dc).forEach(function (r) { var o = r.parentNode.querySelector('output'); if (o) o.textContent = r.value; gb += parseFloat(r.value) * parseFloat(r.getAttribute('data-rate')); });
      gb = gb * 30;
      var rec = gb <= 4 ? [5, 'a 5GB plan'] : gb <= 12 ? [15, 'a 15GB plan'] : gb <= 18 ? [20, 'a 20GB plan'] : [999, 'an unlimited plan'];
      $('#dcResult').textContent = '≈ ' + (gb < 10 ? gb.toFixed(1) : Math.round(gb)) + ' GB / month';
      $('#dcRec').innerHTML = 'Recommended: <strong>' + rec[1] + '</strong> (leaves headroom). <a href="' + R + 'plans/?data=' + rec[0] + '#planFinder">Show matching plans →</a>';
    };
    on($$('input', dc), 'input', runDC); runDC();
  }

  /* ---------------- Quick save (home) */
  var qs = $('#quickSave');
  if (qs && PLANS.length) {
    var runQS = function () {
      var bill = num('qsBill', 0), lines = num('qsLines', 1);
      var best = PLANS.filter(function (p) { return fits(p, { need: 999 }); }).map(function (p) { return { p: p, t: total(p, lines, 999) }; }).sort(function (a, b) { return a.t - b.t; })[0];
      var save = best ? Math.max(0, (bill - best.t) * 12) : 0;
      $('#qsOut').textContent = money(save) + '/yr';
      $('#qsPlan').textContent = best ? (save > 0 ? 'vs ' + nm(best.p) + ' at ' + money(best.t, best.t % 1 ? 2 : 0) + '/mo for ' + lines + ' line' + (lines > 1 ? 's' : '') : 'Your bill already looks competitive.') : '';
      $('#qsGo').href = R + 'save/?bill=' + encodeURIComponent(bill) + '&lines=' + lines;
    };
    on([$('#qsBill'), $('#qsLines')], 'input', runQS); on([$('#qsLines')], 'change', runQS); runQS();
  }

  /* ---------------- Bill Audit */
  var au = $('#audit');
  if (au && PLANS.length) {
    var step = 1, steps = $$('.audit-step', au);
    var p0 = new URLSearchParams(location.search);
    if (p0.get('bill')) $('#auBill').value = p0.get('bill');
    if (p0.get('lines')) $('#auLines').value = p0.get('lines');
    var go = function (n) {
      step = Math.max(1, Math.min(3, n));
      steps.forEach(function (s) { s.classList.toggle('is-on', +s.getAttribute('data-step') === step); });
      $('#auProgress').style.width = (step / 3 * 100) + '%';
      $('#auStepLabel').textContent = step === 3 ? 'Your results' : 'Step ' + step + ' of 3';
      if (step === 3) audit();
      var top = au.getBoundingClientRect().top + scrollY - 90; if (top < scrollY) scrollTo({ top: top, behavior: 'smooth' });
    };
    on($$('[data-next]', au), 'click', function () {
      if (step === 1 && !(num('auBill') > 0)) { $('#auBill').focus(); $('#auBill').reportValidity && $('#auBill').setCustomValidity('Enter your monthly bill'); $('#auBill').reportValidity(); $('#auBill').setCustomValidity(''); return; }
      go(step + 1);
    });
    on($$('[data-prev]', au), 'click', function () { go(step - 1); });
    var audit = function () {
      var bill = num('auBill'), lines = num('auLines', 1), device = Math.max(0, num('auDevice', 0)), need = num('auData', 15);
      var o = { need: need, network: $('#auNetwork').value, hotspot: $('#auHotspot').checked };
      var intl = $('#auIntl').checked, carrier = $('#auCarrier').value;
      var service = Math.max(0, bill - device);
      var rows = PLANS.filter(function (p) { return fits(p, o); }).map(function (p) { return { p: p, t: total(p, lines, need) }; }).sort(function (a, b) { return a.t - b.t; });
      if (intl) rows.sort(function (a, b) { var ia = /international|global|countries|roaming|mexico|canada/i.test(a.p.perks) ? 0 : 1, ib = /international|global|countries|roaming|mexico|canada/i.test(b.p.perks) ? 0 : 1; return ia - ib || a.t - b.t; });
      var top = rows.slice(0, 3), best = top[0];
      var mSave = best ? service - best.t : 0, ySave = Math.round(mSave * 12);
      var html = '';
      if (best && mSave > 1) {
        html += '<div class="savings"><span>Estimated savings</span><strong class="big">' + money(ySave) + ' / year</strong>' +
          '<p>' + money(mSave, mSave % 1 ? 2 : 0) + ' less per month: ' + money(service, service % 1 ? 2 : 0) + ' for service today vs ' + money(best.t, best.t % 1 ? 2 : 0) + ' with ' + esc(nm(best.p)) + '.</p></div>';
      } else {
        html += '<div class="savings"><span>Good news</span><strong class="big">You’re already on a sharp deal</strong><p>Your service cost is at or below the cheapest matching plans we track. The report can still flag perks or promos you may be missing.</p></div>';
      }
      if (device > 0) html += '<p class="micro">We excluded ' + money(device, device % 1 ? 2 : 0) + '/mo of phone payments. Check your remaining device balance before switching (see <a href="' + R + 'guides/switching-carriers-checklist/">switching checklist</a>).</p>';
      html += '<h3 class="h4">Top matches for ' + lines + ' line' + (lines > 1 ? 's' : '') + '</h3><ul class="mini-plans">' + top.map(function (r) {
        return '<li><span><b>' + esc(r.p.carrier) + '</b> ' + (r.p.plan === r.p.carrier ? '' : esc(r.p.plan)) + '<br><small class="muted">' + esc(dataLabel(r.p)) + ' · ' + esc(r.p.network) + '</small></span><span><b>' + money(r.t, r.t % 1 ? 2 : 0) + '</b><small class="muted">/mo</small></span></li>';
      }).join('') + '</ul>';
      if (!top.length) html += '<p class="muted">No tracked plan meets every requirement. Your report will include wider options.</p>';
      $('#auResult').innerHTML = html;
      $('#auSummary').value = 'Carrier: ' + carrier + ' | Bill: $' + bill + ' (device $' + device + ') | Lines: ' + lines + ' | Data/line: ' + (need >= 999 ? '20GB+' : '<=' + need + 'GB') +
        ' | Network: ' + o.network + ' | Hotspot: ' + (o.hotspot ? 'yes' : 'no') + ' | Intl: ' + (intl ? 'yes' : 'no') + ' | Est. yearly savings: $' + Math.max(0, ySave) +
        ' | Top: ' + top.map(function (r) { return nm(r.p) + ' $' + r.t; }).join('; ');
    };
  }

  /* ---------------- True cost */
  var tc = $('#trueCost');
  if (tc) {
    var runTC = function () {
      var retail = num('tcRetail'), months = num('tcMonths', 36), qual = num('tcQual'), up = num('tcUpfront'), alt = num('tcAltPhone'), altPlan = num('tcAltPlan');
      var leave = Math.max(1, Math.min(months, num('tcLeave', months)));
      var owed = leave < months ? retail * (months - leave) / months : 0;
      var A = qual * leave + up + owed, B = alt + altPlan * leave, diff = A - B;
      $('#tcResult').innerHTML = '<span>Over ' + leave + ' months</span>' +
        '<p><b>Carrier offer:</b> ' + money(A) + (owed ? ' <small class="muted">(incl. ' + money(owed) + ' device balance due when you leave)</small>' : '') + '<br><b>Buy + cheaper plan:</b> ' + money(B) + '</p>' +
        '<strong class="big" style="color:' + (diff > 0 ? 'var(--brand-strong)' : 'var(--sky)') + '">' + (diff > 0 ? 'Buying unlocked saves ' + money(diff) : diff < 0 ? 'Carrier offer saves ' + money(-diff) : 'It’s a tie') + '</strong>' +
        '<p class="micro">That is ' + money(Math.abs(diff) / leave, 2) + ' per month. Taxes, trade-in values and promos can shift the result.</p>';
    };
    on($$('input,select', tc), 'input', runTC); on($$('select', tc), 'change', runTC); runTC();
  }

  /* ---------------- Good-deal checker */
  var dk = $('#dealCheck');
  if (dk) {
    var runDK = function () {
      var msrp = num('dkMsrp', 1), price = num('dkPrice'), age = num('dkAge'), cond = $('#dkCond').value;
      var disc = msrp > 0 ? (msrp - price) / msrp : 0;
      var exp = age < 2 ? 0.03 : age < 6 ? 0.10 : age < 12 ? 0.18 : age < 24 ? 0.30 : 0.40;
      exp += cond === 'refurb' ? 0.15 : cond === 'used' ? 0.25 : 0;
      var v = disc >= exp + 0.10 ? ['Great deal', 'v-great', 'This beats typical discounts for a phone of this age. Buy with confidence if it fits your needs.']
        : disc >= exp ? ['Good deal', 'v-good', 'In line with or slightly better than typical discounts. A solid buy.']
          : disc >= exp - 0.08 ? ['Fair price', 'v-fair', 'Slightly above what similar phones usually sell for. Wait for a sale if you can.']
            : ['Wait', 'v-wait', 'Higher than typical for this age and condition. A better price is likely soon.'];
      $('#dkResult').innerHTML = '<span class="verdict ' + v[1] + '">' + v[0] + '</span><p><b>' + Math.round(disc * 100) + '% off</b> launch price vs a typical <b>' + Math.round(exp * 100) + '%</b> for a ' + (cond === 'new' ? 'new' : cond) + ' phone ' + age + ' months after launch.</p><p class="muted">' + v[2] + '</p>';
    };
    on($$('input,select', dk), 'input', runDK); on($$('select', dk), 'change', runDK); runDK();
  }

  /* ---------------- Trade-in estimator */
  var ti = $('#tradeIn');
  if (ti) {
    var curve = [[0, .82], [3, .75], [6, .68], [12, .56], [18, .47], [24, .40], [36, .29], [48, .20], [60, .14], [84, .08]];
    var interp = function (a) { for (var i = 1; i < curve.length; i++) { if (a <= curve[i][0]) { var x0 = curve[i - 1], x1 = curve[i]; return x0[1] + (x1[1] - x0[1]) * (a - x0[0]) / (x1[0] - x0[0]); } } return curve[curve.length - 1][1]; };
    var runTI = function () {
      var launch = num('tiLaunch'), age = Math.max(0, num('tiAge')), brand = num('tiBrand', 1), st = num('tiStorage', 1), cond = num('tiCond', 1);
      var v = Math.min(launch * 0.9, launch * interp(age) * brand * st * cond);
      var lo = Math.max(0, Math.round(v * 0.88 / 5) * 5), hi = Math.round(v * 1.12 / 5) * 5;
      $('#tiResult').innerHTML = '<span>Estimated fair value</span><strong class="big">' + money(lo) + ' – ' + money(hi) + '</strong><p class="muted">Buyback sites typically pay toward the lower end; private sales toward the upper end. Carrier launch promos can pay more as bill credits.</p>';
      var s = $('#tiSummary'); if (s) s.value = 'Brand factor ' + brand + ', launch $' + launch + ', age ' + age + ' mo, storage x' + st + ', condition x' + cond + ' => est. $' + lo + '-$' + hi;
    };
    on($$('input,select', ti), 'input', runTI); on($$('select', ti), 'change', runTI); runTI();
  }

  /* ---------------- eSIM vs roaming */
  var es = $('#esimCalc');
  if (es) {
    var runES = function () {
      var days = Math.max(1, num('esDays', 1)), gb = num('esGb'), pass = num('esPass'), per = num('esPerGb'), local = num('esLocal');
      var roam = days * pass, esim = Math.max(5, Math.ceil(days * gb) * per);
      var opts = [['Carrier roaming pass', roam], ['Travel eSIM', esim], ['Local SIM', local]].sort(function (a, b) { return a[1] - b[1]; });
      $('#esResult').innerHTML = '<span>Cheapest for ' + days + ' days (' + (days * gb).toFixed(1) + ' GB total)</span><strong class="big">' + opts[0][0] + ': ' + money(opts[0][1]) + '</strong>' +
        '<ul class="mini-plans" style="margin-top:.8rem">' + opts.map(function (o) { return '<li><span>' + o[0] + '</span><b>' + money(o[1]) + '</b></li>'; }).join('') + '</ul>' +
        (opts[0][0] !== 'Carrier roaming pass' ? '<p class="muted">You save ' + money(roam - opts[0][1]) + ' vs roaming.</p>' : '');
    };
    on($$('input', es), 'input', runES); runES();
  }

  /* ---------------- Deals filter */
  var app = $('#dealsApp');
  if (app) {
    var grid = $('#dealGrid'), cards = $$('.deal-card', grid);
    var st2 = { region: 'all', cat: 'all', q: '', sort: 'new', saved: false, shown: 24 };
    var qp = new URLSearchParams(location.search);
    if (qp.get('q')) { st2.q = qp.get('q').toLowerCase(); $('#dealSearch').value = qp.get('q'); }
    ['region', 'cat'].forEach(function (k) {
      var v = qp.get(k);
      if (v) { st2[k] = v; $$('[data-' + k + ']', app).forEach(function (c) { c.classList.toggle('is-on', c.getAttribute('data-' + k) === v); }); }
    });
    var apply = function () {
      var saved = (M.saved && M.saved()) || [];
      var list = cards.filter(function (c) {
        return (st2.region === 'all' || c.getAttribute('data-region') === st2.region) &&
          (st2.cat === 'all' || c.getAttribute('data-cat') === st2.cat) &&
          (!st2.q || c.textContent.toLowerCase().indexOf(st2.q) > -1) &&
          (!st2.saved || saved.indexOf(c.getAttribute('data-id')) > -1);
      });
      list.sort(function (a, b) {
        if (st2.sort === 'hot') return (+b.getAttribute('data-heat') - +a.getAttribute('data-heat')) || (b.getAttribute('data-date') > a.getAttribute('data-date') ? 1 : -1);
        if (st2.sort === 'az') return $('.deal-title', a).textContent.localeCompare($('.deal-title', b).textContent);
        return b.getAttribute('data-date') > a.getAttribute('data-date') ? 1 : -1;
      });
      cards.forEach(function (c) { c.hidden = true; });
      list.forEach(function (c, i) { grid.appendChild(c); c.hidden = i >= st2.shown; });
      $('#dealCount').textContent = list.length + ' deal' + (list.length === 1 ? '' : 's');
      $('#dealMore').hidden = list.length <= st2.shown;
      var empty = $('#dealEmpty');
      if (!list.length && !empty) { empty = d.createElement('p'); empty.id = 'dealEmpty'; empty.className = 'muted'; empty.textContent = 'No deals match. Try another region or category.'; grid.appendChild(empty); }
      if (empty) empty.hidden = !!list.length;
    };
    $$('[data-region]', app).forEach(function (c) { c.addEventListener('click', function () { st2.region = c.getAttribute('data-region'); st2.shown = 24; $$('[data-region]', app).forEach(function (x) { x.classList.toggle('is-on', x === c); }); apply(); }); });
    $$('[data-cat]', app).forEach(function (c) { c.addEventListener('click', function () { st2.cat = c.getAttribute('data-cat'); st2.shown = 24; $$('[data-cat]', app).forEach(function (x) { x.classList.toggle('is-on', x === c); }); apply(); }); });
    var t; $('#dealSearch').addEventListener('input', function (e) { clearTimeout(t); t = setTimeout(function () { st2.q = e.target.value.trim().toLowerCase(); st2.shown = 24; apply(); }, 120); });
    $('#dealSort').addEventListener('change', function (e) { st2.sort = e.target.value; apply(); });
    $('#dealSavedOnly').addEventListener('change', function (e) { st2.saved = e.target.checked; apply(); });
    $('#dealMore').addEventListener('click', function () { st2.shown += 24; apply(); });
    d.addEventListener('md:saved', function () { if (st2.saved) apply(); });
    apply();
  }
})();
