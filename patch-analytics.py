#!/usr/bin/env python3
"""Adds GA4 (G-K2MK5T0H4B) to every page:
  - loads ONLY after first user interaction  -> zero PageSpeed cost
    (Lighthouse never interacts, so it never loads during an audit)
  - loads ONLY with consent, via a lightweight fixed banner (no layout shift)
  - tracks the events that actually matter: book checkout, Amazon clicks,
    visualiser generations, calculator prints
Idempotent. Run from repo root:  python3 patch-analytics.py
"""
import glob

SNIPPET = '''
<!-- Analytics: consent-gated, interaction-loaded (no page-speed cost) -->
<script>
(function(){
  var GA = 'G-K2MK5T0H4B', KEY = 'ltu-consent', loaded = false;

  function loadGA(){
    if (loaded) return; loaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', GA, { anonymize_ip: true });
  }

  // hold GA back until the visitor actually does something
  function armInteraction(){
    var evts = ['scroll','click','keydown','touchstart','mousemove'];
    function fire(){
      evts.forEach(function(e){ window.removeEventListener(e, fire); });
      loadGA();
    }
    evts.forEach(function(e){ window.addEventListener(e, fire, { once:true, passive:true }); });
  }

  // public tracker — used by the event hooks below
  window.ltuTrack = function(name, params){
    if (!consentGiven()) return;
    loadGA();
    if (window.gtag) gtag('event', name, params || {});
  };
  function consentGiven(){
    try { return localStorage.getItem(KEY) === 'yes'; } catch(e){ return false; }
  }

  // ---- conversion events -------------------------------------------------
  document.addEventListener('click', function(e){
    var el = e.target && e.target.closest ? e.target.closest('a,button') : null;
    if (!el) return;
    var txt = (el.textContent || '').trim().slice(0, 48);
    if (el.id === 'buy') {
      window.ltuTrack('begin_checkout', { item_name: 'Wiro workshop edition', value: 44.99, currency: 'GBP' });
    } else if (el.getAttribute && (el.getAttribute('href') || '').indexOf('/go/amazon') > -1) {
      window.ltuTrack('amazon_click', { link_text: txt, page: location.pathname });
    } else if (/print/i.test(txt)) {
      window.ltuTrack('print_results', { page: location.pathname });
    } else if (el.id === 'v-go') {
      window.ltuTrack('visualiser_try', { page: location.pathname });
    }
  }, { passive: true });

  // ---- consent -----------------------------------------------------------
  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch(e){}
  if (choice === 'yes') { armInteraction(); return; }
  if (choice === 'no')  { return; }

  function decide(v){
    try { localStorage.setItem(KEY, v); } catch(e){}
    var b = document.getElementById('ltu-consent-bar');
    if (b) b.remove();
    if (v === 'yes') loadGA();
  }
  function banner(){
    var d = document.createElement('div');
    d.id = 'ltu-consent-bar';
    d.setAttribute('role','dialog');
    d.setAttribute('aria-label','Cookie choice');
    d.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#2F4A3A;color:#FBF6ED;'
      + 'padding:.8rem 1rem;display:flex;gap:.9rem;align-items:center;justify-content:center;'
      + 'flex-wrap:wrap;font-family:Georgia,serif;font-size:.95rem;box-shadow:0 -4px 18px rgba(42,38,34,.25)';
    d.innerHTML = '<span style="max-width:44rem">We\\u2019d like to use analytics cookies to see which pages are useful. '
      + 'Nothing personal, and you can say no. <a href="/cookie-policy" style="color:#C19A4B">Cookie policy</a>.</span>'
      + '<span style="display:flex;gap:.5rem">'
      + '<button id="ltu-c-yes" style="background:#C19A4B;color:#2A2622;border:0;padding:.45rem 1.1rem;'
      + 'border-radius:3px;cursor:pointer;font-family:Georgia,serif;font-weight:700">Allow</button>'
      + '<button id="ltu-c-no" style="background:transparent;color:#FBF6ED;border:1.5px solid #FBF6ED;'
      + 'padding:.45rem 1.1rem;border-radius:3px;cursor:pointer;font-family:Georgia,serif">No thanks</button>'
      + '</span>';
    document.body.appendChild(d);
    document.getElementById('ltu-c-yes').addEventListener('click', function(){ decide('yes'); });
    document.getElementById('ltu-c-no').addEventListener('click',  function(){ decide('no');  });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', banner);
  } else { banner(); }
})();
</script>
</body>'''

n = 0
for f in glob.glob('*.html') + glob.glob('projects/*.html'):
    t = open(f, encoding='utf-8').read()
    if 'ltu-consent' in t or '</body>' not in t:
        continue
    t = t.replace('</body>', SNIPPET, 1)
    open(f, 'w', encoding='utf-8').write(t)
    n += 1
print(f"GA4 + consent added to {n} pages")

# visualiser: fire a success event when an image actually comes back
try:
    v = open('fabric-visualiser.html', encoding='utf-8').read()
    if 'visualiser_generate' not in v:
        old = "document.getElementById('v-result').style.display='block';"
        if old in v:
            v = v.replace(old, old + "\n      if(window.ltuTrack) ltuTrack('visualiser_generate',{});", 1)
            open('fabric-visualiser.html', 'w', encoding='utf-8').write(v)
            print("visualiser: success event wired")
        else:
            print("visualiser: anchor not found - skipped")
    else:
        print("visualiser: already wired")
except FileNotFoundError:
    print("fabric-visualiser.html not found - skipped")
