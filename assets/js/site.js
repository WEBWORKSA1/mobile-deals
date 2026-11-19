/* Mobile.Deals core UI: theme, nav, search, forms, deals helpers. No dependencies. */
(function () {
  'use strict';
  var d = document, H = d.documentElement, R = H.getAttribute('data-root') || '';
  var C = window.MD_CONFIG || {};
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  var store = {
    get: function (k, def) { try { var v = localStorage.getItem(k); return v === null ? def : JSON.parse(v); } catch (e) { return def; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  window.MD = { $: $, $$: $$, store: store, root: R, toast: toast };

  function toast(msg) {
    var t = $('#toast'); if (!t) return;
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(function () { t.classList.remove('show'); }, 2600);
  }

  /* theme */
  var tt = $('#themeToggle');
  if (tt) tt.addEventListener('click', function () {
    var cur = H.getAttribute('data-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    var next = cur === 'dark' ? 'light' : 'dark';
    H.setAttribute('data-theme', next); store.set('md-theme', next);
  });

  /* mobile nav */
  var nt = $('#navToggle');
  function closeNav() { d.body.classList.remove('nav-open'); if (nt) nt.setAttribute('aria-expanded', 'false'); }
  if (nt) nt.addEventListener('click', function () {
    var open = d.body.classList.toggle('nav-open'); nt.setAttribute('aria-expanded', String(open));
  });
  d.addEventListener('click', function (e) {
    if (d.body.classList.contains('nav-open') && !e.target.closest('#mainNav') && !e.target.closest('#navToggle')) closeNav();
    $$('details.more[open]').forEach(function (m) { if (!m.contains(e.target)) m.removeAttribute('open'); });
  });
  $$('#mainNav a').forEach(function (a) { a.addEventListener('click', closeNav); });

  /* search */
  var dlg = $('#searchDialog'), si = $('#searchInput'), sr = $('#searchResults'), index = null;
  function openSearch() {
    if (!dlg) return;
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    si.value = ''; sr.innerHTML = ''; si.focus();
    if (!index) fetch(R + 'data/search.json').then(function (r) { return r.json(); }).then(function (j) { index = j; render(''); }).catch(function () { index = []; });
    else render('');
  }
  function render(q) {
    if (!index) return;
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    var res = index.filter(function (x) {
      var hay = (x.t + ' ' + x.d).toLowerCase();
      return terms.every(function (t) { return hay.indexOf(t) > -1; });
    });
    if (!terms.length) res = index.filter(function (x) { return x.k !== 'deal'; });
    else res.sort(function (a, b) { var ta = terms.every(function (t) { return a.t.toLowerCase().indexOf(t) > -1; }) ? 0 : 1, tb = terms.every(function (t) { return b.t.toLowerCase().indexOf(t) > -1; }) ? 0 : 1; return ta - tb; });
    sr.innerHTML = res.slice(0, 14).map(function (x) {
      var ext = /^https?:/.test(x.u);
      return '<li><a href="' + (ext ? x.u : R + x.u) + '"' + (ext ? ' target="_blank" rel="nofollow noopener"' : '') + '><span class="k">' + x.k + '</span>' +
        esc(x.t) + '<small>' + esc(x.d) + '</small></a></li>';
    }).join('') || '<li class="muted" style="padding:.8rem">No matches. Try "unlimited", "trade-in" or a phone name.</li>';
  }
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  if ($('#searchOpen')) $('#searchOpen').addEventListener('click', openSearch);
  if (si) {
    si.addEventListener('input', function () { render(si.value); });
    si.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); var a = $('a', sr); if (a) a.click(); } });
  }
  d.addEventListener('keydown', function (e) {
    if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !/input|textarea|select/i.test(e.target.tagName))) { e.preventDefault(); openSearch(); }
    if (e.key === 'Escape') closeNav();
  });
  if (dlg) dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });

  /* cookie notice */
  var cb = $('#cookieBar');
  if (cb && !store.get('md-cookie', false)) { cb.hidden = false; $('#cookieAccept').addEventListener('click', function () { store.set('md-cookie', true); cb.hidden = true; }); }

  /* forms: delivered through a form relay; inbox address is never placed in markup */
  var K = 'bW9jLmxpYW1nQDFhc2tyb3diZXc=';
  function endpoint() { return 'https://formsubmit.co/ajax/' + atob(K).split('').reverse().join(''); }
  $$('form[data-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var st = $('.form-status', f), btn = $('button[type=submit]', f);
      var hp = f.querySelector('[name=_honey]');
      if (hp && hp.value) return;
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var data = {};
      new FormData(f).forEach(function (v, k) { if (k === '_honey') return; data[k] = data[k] ? data[k] + ', ' + v : v; });
      data._subject = f.getAttribute('data-subject') || 'Mobile.Deals form';
      data._template = 'table'; data._captcha = 'false';
      data.form_type = f.getAttribute('data-form'); data.page = location.href; data.submitted = new Date().toISOString();
      if (data.email) data._replyto = data.email;
      if (btn) btn.disabled = true;
      if (st) { st.className = 'form-status'; st.textContent = 'Sending…'; }
      fetch(endpoint(), { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().catch(function () { return { success: r.ok }; }); })
        .then(function (j) {
          var ok = j && (j.success === true || j.success === 'true' || /activat/i.test(j.message || ''));
          if (!ok) throw new Error((j && j.message) || 'failed');
          f.innerHTML = '<div class="form-success"><div class="tick">✓</div><h3>Sent!</h3><p class="muted">' + esc(f.getAttribute('data-success') || 'Thanks, we received your message.') + '</p></div>';
          if (typeof window.gtag === 'function') window.gtag('event', 'generate_lead', { form: data.form_type });
        })
        .catch(function () {
          if (btn) btn.disabled = false;
          if (st) { st.className = 'form-status err'; st.textContent = 'Sorry, that didn’t go through. Please check your connection and try again.'; }
        });
    });
  });

  /* affiliate links (optional) */
  var aff = C.affiliates || {};
  $$('a[data-aff]').forEach(function (a) { var k = a.getAttribute('data-aff'); if (aff[k]) a.href = aff[k]; });

  /* AdSense manual units: render only when a slot ID is configured, otherwise remove the placeholder */
  var slots = C.adSlots || {};
  $$('.ad-slot').forEach(function (el) {
    var id = slots[el.getAttribute('data-slot')];
    if (!id) { el.remove(); return; }
    el.innerHTML = '<ins class="adsbygoogle" style="display:block" data-ad-client="' + (C.adsenseClient || '') + '" data-ad-slot="' + id + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) {}
  });

  /* donations */
  var don = C.donate || {}, pb = $('#payButtons');
  if (pb) {
    var labels = { paypal: 'PayPal', stripe: 'Card (Stripe)', kofi: 'Ko-fi', buymeacoffee: 'Buy Me a Coffee' };
    pb.innerHTML = Object.keys(labels).filter(function (k) { return don[k]; }).map(function (k) {
      return '<a class="btn btn-primary btn-sm" target="_blank" rel="noopener" href="' + esc(don[k]) + '">Give with ' + labels[k] + '</a>';
    }).join('');
  }
  $$('[data-donate]').forEach(function (b) {
    b.addEventListener('click', function () { var a = $('#pledgeAmount'); if (a) a.value = b.getAttribute('data-donate'); });
  });

  /* contest */
  if (C.contest && C.contest.prize) $$('[data-prize]').forEach(function (p) { p.textContent = C.contest.prize; });
  $$('[data-countdown]').forEach(function (el) {
    var out = $('strong', el);
    function tick() {
      var n = new Date(), end = new Date(Date.UTC(n.getUTCFullYear(), n.getUTCMonth() + 1, 1, 4, 59, 59));
      var s = Math.max(0, Math.floor((end - n) / 1000));
      var dd = Math.floor(s / 86400), hh = Math.floor(s % 86400 / 3600), mm = Math.floor(s % 3600 / 60), ss = s % 60;
      out.textContent = dd + 'd ' + pad(hh) + 'h ' + pad(mm) + 'm ' + pad(ss) + 's';
    }
    function pad(x) { return (x < 10 ? '0' : '') + x; }
    tick(); setInterval(tick, 1000);
  });

  /* relative times on deal cards */
  function ago(iso) {
    var t = Date.parse(iso); if (!t) return '';
    var m = Math.round((Date.now() - t) / 60000);
    if (m < 60) return Math.max(1, m) + 'm ago';
    var h = Math.round(m / 60); if (h < 48) return h + 'h ago';
    return Math.round(h / 24) + 'd ago';
  }
  $$('.deal-card time[datetime]').forEach(function (t) { var a = ago(t.getAttribute('datetime')); if (a) t.textContent = a; });

  /* save + share deals */
  var saved = store.get('md-saved', []);
  function paintSaved() { $$('[data-save]').forEach(function (b) { b.setAttribute('aria-pressed', String(saved.indexOf(b.getAttribute('data-save')) > -1)); }); }
  paintSaved();
  d.addEventListener('click', function (e) {
    var s = e.target.closest('[data-save]');
    if (s) {
      var id = s.getAttribute('data-save'), i = saved.indexOf(id);
      if (i > -1) saved.splice(i, 1); else saved.push(id);
      store.set('md-saved', saved); paintSaved(); toast(i > -1 ? 'Removed from saved deals' : 'Saved. Find it with “Saved only” on the deals page.');
      d.dispatchEvent(new CustomEvent('md:saved'));
    }
    var sh = e.target.closest('[data-share]');
    if (sh) {
      var url = sh.getAttribute('data-share'), title = sh.getAttribute('data-title') || 'Mobile deal';
      if (navigator.share) navigator.share({ title: title, url: url }).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { toast('Link copied'); });
    }
    var y = e.target.closest('.yt-lite');
    if (y && !y.querySelector('iframe')) {
      var id2 = y.getAttribute('data-id'), list = y.getAttribute('data-list');
      var src = 'https://www.youtube-nocookie.com/embed/' + (id2 ? encodeURIComponent(id2) + '?autoplay=1&rel=0' : 'videoseries?list=' + encodeURIComponent(list) + '&autoplay=1');
      y.innerHTML = '<iframe src="' + src + '" title="YouTube video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>';
    }
  });
  window.MD.saved = function () { return saved; };

  /* reveal on scroll */
  var rv = $$('[data-reveal]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) { en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -40px 0px' });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('is-in'); });

  $$('[data-year]').forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();
