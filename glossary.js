/* Learn to Upholster — glossary tooltips.
   Marks the first mention of each glossary term in a chapter and shows the
   definition on hover / focus / tap, with a link to the full A–Z entry. */
var __ltInit = (function () { return function () {
  'use strict';
  var root = document.querySelector('article.article');
  if (!root) return;
  if (location.pathname.replace(/\/$/, '') === '/a-z-glossary') return;

  fetch('/glossary.json').then(function (r) { return r.json(); }).then(build).catch(function () {});

  function build(entries) {
    if (!entries || !entries.length) return;

    var map = {};
    entries.forEach(function (e) {
      var forms = [e.term];
      if (!/[\s-]/.test(e.term)) {
        if (/y$/i.test(e.term)) forms.push(e.term.replace(/y$/i, 'ies'));
        if (!/s$/i.test(e.term)) forms.push(e.term + 's');
      }
      forms.forEach(function (f) { map[f.toLowerCase()] = e; });
    });
    var forms = Object.keys(map).sort(function (a, b) { return b.length - a.length; });
    var esc = forms.map(function (f) { return f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    var re = new RegExp('\\b(' + esc.join('|') + ')\\b', 'gi');

    var used = {};
    var SKIP = { A: 1, H1: 1, H2: 1, H3: 1, H4: 1, BUTTON: 1, CODE: 1, SCRIPT: 1, STYLE: 1, FIGURE: 1, FIGCAPTION: 1 };
    function skip(node) {
      var p = node.parentNode;
      while (p && p !== document.body) {
        if (p.tagName && SKIP[p.tagName]) return true;
        var c = p.className;
        if (typeof c === 'string' && /\bgloss\b|\bchno\b|\blu-bm-btn\b|\bepigraph\b/.test(c)) return true;
        p = p.parentNode;
      }
      return false;
    }

    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    var nodes = [], n;
    while ((n = walker.nextNode())) {
      if (n.nodeValue && n.nodeValue.trim() && !skip(n)) nodes.push(n);
    }

    nodes.forEach(function (node) {
      var text = node.nodeValue, m, last = 0, frag = null;
      re.lastIndex = 0;
      while ((m = re.exec(text))) {
        var surf = m[0], base = map[surf.toLowerCase()];
        if (!base || used[base.term]) continue;
        used[base.term] = 1;
        if (!frag) frag = document.createDocumentFragment();
        if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        var span = document.createElement('span');
        span.className = 'gloss';
        span.tabIndex = 0;
        span.setAttribute('role', 'button');
        span.setAttribute('data-term', base.term);
        span.setAttribute('data-def', base.def);
        span.setAttribute('data-href', base.href);
        span.setAttribute('aria-label', base.term + ': ' + base.def);
        span.textContent = surf;
        frag.appendChild(span);
        last = m.index + surf.length;
      }
      if (frag) {
        if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
        node.parentNode.replaceChild(frag, node);
      }
    });

    injectCSS();
    initTooltip();
  }

  function injectCSS() {
    var css =
      '.gloss{border-bottom:1px dotted var(--sage);cursor:help}' +
      '.gloss:hover,.gloss:focus{background:var(--cream-deep);outline:none}' +
      '#gloss-tip{position:absolute;z-index:9999;max-width:300px;background:#fff;border:1px solid var(--rule);' +
      'border-radius:10px;box-shadow:0 8px 26px rgba(42,38,34,.17);padding:.65rem .8rem;' +
      "font-family:'EB Garamond',Georgia,serif;color:var(--ink);font-size:.95rem;line-height:1.42;" +
      'opacity:0;transform:translateY(4px);transition:opacity .12s,transform .12s;pointer-events:none}' +
      '#gloss-tip.show{opacity:1;transform:translateY(0);pointer-events:auto}' +
      "#gloss-tip strong{display:block;font-family:'Fraunces',Georgia,serif;color:var(--green-deep);margin-bottom:.15rem}" +
      '#gloss-tip a{display:inline-block;margin-top:.4rem;color:var(--green);text-decoration:none;font-size:.84rem}' +
      '#gloss-tip a:hover{text-decoration:underline}';
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
  }

  function initTooltip() {
    var tip = document.createElement('div');
    tip.id = 'gloss-tip';
    tip.innerHTML = '<strong></strong><span class="d"></span><br><a>Full entry &#8594;</a>';
    document.body.appendChild(tip);
    var elTerm = tip.querySelector('strong'), elDef = tip.querySelector('.d'), elLink = tip.querySelector('a');
    var hideT, current = null;

    function position(span) {
      var r = span.getBoundingClientRect();
      tip.style.left = '0px'; tip.style.top = '0px';
      var tw = tip.offsetWidth, th = tip.offsetHeight;
      var sx = window.pageXOffset, sy = window.pageYOffset;
      var cw = document.documentElement.clientWidth;
      var left = r.left + sx + r.width / 2 - tw / 2;
      left = Math.max(sx + 8, Math.min(left, sx + cw - tw - 8));
      var top = r.top + sy - th - 8;
      if (top < sy + 4) top = r.bottom + sy + 8;
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
    }
    function show(span) {
      current = span;
      elTerm.textContent = span.getAttribute('data-term');
      elDef.textContent = span.getAttribute('data-def');
      elLink.href = span.getAttribute('data-href');
      position(span);
      tip.classList.add('show');
    }
    function hide() { tip.classList.remove('show'); current = null; }
    function scheduleHide() { clearTimeout(hideT); hideT = setTimeout(hide, 180); }
    function cancelHide() { clearTimeout(hideT); }

    function closestGloss(t) { return t && t.closest ? t.closest('.gloss') : null; }

    document.addEventListener('mouseover', function (e) {
      var g = closestGloss(e.target);
      if (g) { cancelHide(); show(g); }
    });
    document.addEventListener('mouseout', function (e) {
      if (closestGloss(e.target)) scheduleHide();
    });
    tip.addEventListener('mouseenter', cancelHide);
    tip.addEventListener('mouseleave', scheduleHide);

    document.addEventListener('focusin', function (e) {
      if (e.target.classList && e.target.classList.contains('gloss')) show(e.target);
    });
    document.addEventListener('focusout', function (e) {
      if (e.target.classList && e.target.classList.contains('gloss')) scheduleHide();
    });

    document.addEventListener('click', function (e) {
      var g = closestGloss(e.target);
      if (g) { if (current === g) hide(); else show(g); e.stopPropagation(); return; }
      if (!(e.target.closest && e.target.closest('#gloss-tip'))) hide();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(); });
    window.addEventListener('scroll', function () { if (current) position(current); }, { passive: true });
    window.addEventListener('resize', hide);
  }
}})();
(window.requestIdleCallback || function (f) { setTimeout(f, 200); })(__ltInit);
