/* Learn to Upholster — reading features (continue reading, bookmarks, progress).
   All state is stored locally in the visitor's browser (per device). No backend. */
(function () {
  'use strict';
  var KEY = 'lu.reader.v1';

  function load() { try { var s = localStorage.getItem(KEY); return s ? JSON.parse(s) : {}; } catch (e) { return {}; } }
  function save(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }
  function norm(p) { try { p = new URL(p, location.origin).pathname; } catch (e) {} if (p.length > 1 && p.charAt(p.length - 1) === '/') p = p.slice(0, -1); return p; }
  function esc(s) { return (s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  var DB = load();
  DB.bookmarks = DB.bookmarks || [];
  DB.read = DB.read || {};
  function isBm(url) { return DB.bookmarks.some(function (b) { return b.url === url; }); }

  /* ---- styles ---- */
  var css = `
.lu-bm-btn{display:inline-flex;align-items:center;gap:.35rem;margin-top:1rem;font-family:'EB Garamond',Georgia,serif;font-size:.95rem;color:var(--green);background:#fff;border:1.5px solid var(--rule);border-radius:999px;padding:.35rem .9rem;cursor:pointer;transition:background .15s,border-color .15s}
.lu-bm-btn:hover{background:var(--cream-deep);border-color:var(--sage)}
.lu-bm-btn.on{background:var(--green);color:var(--cream);border-color:var(--green)}
#lu-continue{max-width:34rem;margin:1.1rem auto 0}
#lu-continue:empty,#lu-reader-panel:empty{display:none}
.lu-panel{font-family:'EB Garamond',Georgia,serif;background:#fff;border:1px solid var(--rule);border-radius:12px;padding:1rem 1.1rem;margin:0 0 1.7rem}
.lu-continue-card{display:block;text-decoration:none;background:var(--green);color:var(--cream);border-radius:10px;padding:.7rem .95rem;margin:0 0 .9rem}
.lu-continue-card:hover{background:var(--green-deep)}
.lu-cont-label{display:block;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;opacity:.82}
.lu-cont-title{display:block;font-family:'Fraunces',Georgia,serif;font-size:1.18rem;line-height:1.2;margin:.12rem 0}
.lu-cont-chno{display:block;font-size:.82rem;opacity:.85}
.lu-prog-text{font-size:.9rem;color:#6b6357}
.lu-prog-bar{display:block;height:4px;background:var(--cream-deep);border-radius:3px;margin-top:.35rem;overflow:hidden}
.lu-prog-bar>span{display:block;height:100%;background:var(--sage);border-radius:3px;transition:width .3s}
.lu-bm{margin-top:.95rem;border-top:1px solid var(--rule);padding-top:.75rem}
.lu-bm-h{font-family:'Fraunces',Georgia,serif;font-weight:600;color:var(--green-deep);margin:0 0 .35rem;font-size:1.02rem}
.lu-bm-list{list-style:none;margin:0;padding:0}
.lu-bm-list li{display:flex;align-items:baseline;gap:.5rem;padding:.2rem 0}
.lu-bm-list a{flex:1;text-decoration:none;color:var(--ink)}
.lu-bm-list a:hover{text-decoration:underline}
.lu-bm-chno{font-size:.71rem;letter-spacing:.03em;text-transform:uppercase;color:var(--sage);margin-right:.15rem}
.lu-bm-x{background:none;border:none;color:#b0a48c;font-size:1.15rem;line-height:1;cursor:pointer;padding:0 .25rem}
.lu-bm-x:hover{color:var(--terracotta)}
.lu-tick{color:var(--sage);font-weight:700;margin-right:.12rem}
.lu-star{color:var(--gold);margin-right:.12rem}`;
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  /* ---- continue-reading card markup ---- */
  function continueCard() {
    if (!DB.last || !DB.last.url) return '';
    var l = DB.last;
    return '<a class="lu-continue-card" href="' + esc(l.url) + '?resume">' +
      '<span class="lu-cont-label">Continue reading</span>' +
      '<span class="lu-cont-title">' + esc(l.title) + '</span>' +
      '<span class="lu-cont-chno">' + esc(l.chno) + ' &#8594;</span></a>';
  }

  /* ---- chapter page: record position, mark read, bookmark button ---- */
  var art = document.querySelector('article.article');
  var chnoEl = document.querySelector('.chapter-head .chno');
  var h1 = document.querySelector('.chapter-head h1');
  var path = norm(location.pathname);
  var isChapter = !!(art && chnoEl && h1);

  if (isChapter) {
    var meta = { url: path, title: h1.textContent.trim(), chno: chnoEl.textContent.trim() };

    if (/[?&]resume\b/.test(location.search) && DB.last && DB.last.url === path && DB.last.scroll) {
      var target = DB.last.scroll;
      window.addEventListener('load', function () { setTimeout(function () { window.scrollTo(0, target); }, 60); });
    }

    var wrap = document.querySelector('.chapter-head .wrap');
    if (wrap) {
      var btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'lu-bm-btn';
      var paint = function () {
        var on = isBm(path);
        btn.classList.toggle('on', on);
        btn.innerHTML = (on ? '\u2605' : '\u2606') + ' ' + (on ? 'Saved' : 'Save this chapter');
        btn.setAttribute('aria-pressed', String(on));
      };
      paint();
      btn.addEventListener('click', function () {
        if (isBm(path)) { DB.bookmarks = DB.bookmarks.filter(function (b) { return b.url !== path; }); }
        else { DB.bookmarks.unshift({ url: path, title: meta.title, chno: meta.chno, ts: Date.now() }); }
        save(DB); paint();
      });
      wrap.appendChild(btn);
    }

    var setLast = function () {
      DB.last = { url: path, title: meta.title, chno: meta.chno, scroll: Math.round(window.scrollY), ts: Date.now() };
    };
    var ticking = false;
    var onScroll = function () {
      if (ticking) return; ticking = true;
      setTimeout(function () {
        ticking = false;
        setLast();
        var dh = document.documentElement.scrollHeight;
        if (dh > 0 && (window.scrollY + window.innerHeight) / dh >= 0.85 && !DB.read[path]) DB.read[path] = Date.now();
        save(DB);
      }, 300);
    };
    setLast(); save(DB);
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('pagehide', function () { setLast(); save(DB); });
    document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') { setLast(); save(DB); } });
  }

  /* ---- home: continue card ---- */
  var contEl = document.getElementById('lu-continue');
  if (contEl) { var c = continueCard(); if (c) contEl.innerHTML = c; }

  /* ---- contents: full panel ---- */
  var panel = document.getElementById('lu-reader-panel');
  if (panel) {
    var live = document.querySelectorAll('.toc-list a[href^="/"]');
    var total = live.length, readCount = 0;
    live.forEach(function (a) { if (DB.read[norm(a.getAttribute('href'))]) readCount++; });
    if ((DB.last && DB.last.url) || DB.bookmarks.length || readCount > 0) {
      var html = '<div class="lu-panel">' + continueCard();
      var pct = total ? Math.round(readCount / total * 100) : 0;
      html += '<div class="lu-prog"><span class="lu-prog-text">You&#8217;ve read ' + readCount + ' of ' + total + ' chapters</span>' +
        '<span class="lu-prog-bar"><span style="width:' + pct + '%"></span></span></div>';
      if (DB.bookmarks.length) {
        html += '<div class="lu-bm"><p class="lu-bm-h">Your bookmarks</p><ul class="lu-bm-list">';
        DB.bookmarks.forEach(function (b) {
          html += '<li><a href="' + esc(b.url) + '"><span class="lu-bm-chno">' + esc(b.chno) + '</span> ' + esc(b.title) + '</a>' +
            '<button type="button" class="lu-bm-x" data-url="' + esc(b.url) + '" aria-label="Remove bookmark">\u00d7</button></li>';
        });
        html += '</ul></div>';
      }
      html += '</div>';
      panel.innerHTML = html;
      panel.querySelectorAll('.lu-bm-x').forEach(function (x) {
        x.addEventListener('click', function () {
          var u = x.getAttribute('data-url');
          DB.bookmarks = DB.bookmarks.filter(function (b) { return b.url !== u; });
          save(DB); location.reload();
        });
      });
    }
  }

  /* ---- decorate contents links with read/bookmark markers ---- */
  document.querySelectorAll('.toc-list a[href^="/"]').forEach(function (a) {
    var u = norm(a.getAttribute('href'));
    if (a.querySelector('.lu-tick') || a.querySelector('.lu-star')) return;
    var marks = '';
    if (DB.read[u]) marks += '<span class="lu-tick" title="Read">\u2713</span>';
    if (isBm(u)) marks += '<span class="lu-star" title="Bookmarked">\u2605</span>';
    if (marks) a.insertAdjacentHTML('afterbegin', marks + ' ');
  });
})();
