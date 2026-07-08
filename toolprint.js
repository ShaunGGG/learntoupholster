/* Learn to Upholster — printable results for the calculator / tool pages.
   Adds a "Print / Save as PDF" button beside each tool's result and prints a
   clean, branded copy of just that result — matching the fire-safety-checker's
   @media print isolation. One shared script; a <script> tag per tool page. */
(function () {
  'use strict';
  var MAP = {
    '/fabric-yardage'               : '.calc-result',
    '/reupholstery-cost-calculator' : '.ce-result',
    '/deep-buttoning-calculator'    : '#results',
    '/foam-cushion-calculator'      : '#results',
    '/leather-hide-calculator'      : '#results'
  };

  function init() {
    if (document.getElementById('tp-btn')) return;                 // already added
    var path = location.pathname.replace(/\/+$/, '') || '/';
    var sel  = MAP[path];
    if (!sel) return;
    var results = document.querySelector(sel);
    if (!results) return;

    var css =
      '.tp-btn{font-family:var(--display);font-weight:600;font-size:1.02rem;padding:.6rem 1.2rem;' +
        'border:none;border-radius:10px;background:var(--terracotta);color:var(--cream);cursor:pointer;margin:1.1rem 0 .2rem;display:inline-block}' +
      '.tp-btn:hover{filter:brightness(.94)}' +
      '#tp-print{display:none}' +
      '#tp-print .tp-doc{background:#fff;color:var(--ink);border:2px solid var(--ink);border-radius:6px;padding:1.2rem 1.4rem}' +
      '#tp-print .tp-head{border-bottom:1.5px solid var(--ink);padding-bottom:.6rem;margin-bottom:.85rem}' +
      "#tp-print .tp-head h4{font-family:var(--display);margin:0 0 .15rem;font-size:1.25rem;color:var(--ink)}" +
      '#tp-print .tp-head p{margin:0;font-size:.92rem;color:#555}' +
      "#tp-print .tp-foot{margin-top:1rem;padding-top:.6rem;border-top:1px solid var(--ink);font-style:italic;font-size:.85rem;color:#333}" +
      '@media print{body *{visibility:hidden}#tp-print,#tp-print *{visibility:visible}' +
        '#tp-print{position:absolute;left:0;top:0;width:100%;display:block!important}}';
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

    var box = document.createElement('div'); box.id = 'tp-print'; document.body.appendChild(box);

    var btn = document.createElement('button');
    btn.type = 'button'; btn.id = 'tp-btn'; btn.className = 'tp-btn';
    btn.textContent = 'Print / Save as PDF';
    btn.setAttribute('aria-label', 'Print this result or save it as a PDF');
    results.insertAdjacentElement('afterend', btn);

    var title = ((document.querySelector('h1') || {}).textContent || 'Upholstery calculation').trim();

    function esc(s){ var t = document.createElement('span'); t.textContent = s; return t.innerHTML; }

    btn.addEventListener('click', function () {
      var d = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
      var inner = results.innerHTML.replace(/\sid="[^"]*"/g, '');   // drop ids so no duplicates while printing
      box.innerHTML =
        '<div class="tp-doc">' +
          '<div class="tp-head"><h4>' + esc(title) + '</h4>' +
            '<p>learntoupholster.com &middot; ' + d + '</p></div>' +
          '<div class="tp-res">' + inner + '</div>' +
          '<p class="tp-foot">Worked out with the free calculators at learntoupholster.com. ' +
            'An estimate, not a guarantee &#8212; always confirm before you cut or quote.</p>' +
        '</div>';
      window.print();
    });
    window.addEventListener('afterprint', function () { box.innerHTML = ''; });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
