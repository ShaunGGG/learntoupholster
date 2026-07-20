#!/usr/bin/env python3
"""
Mobile nav: collapse the Tools submenu behind a tap.

At the moment the submenu is forced open on phones, so eight top-level items
become nineteen rows and the bottom of the list sits under the fold where a
sticky header can't be scrolled to. Collapsed, the menu is eight rows and fits
any phone without scrolling at all.

Desktop is untouched -- it keeps the hover dropdown.

Because "Tools" becomes a toggle on mobile, the JS inserts an "All tools" link
at the top of the submenu so the /tools page stays reachable. And if the submenu
is expanded on a short screen, the list becomes scrollable just for that state,
so the plain menu never looks boxed in.

No JS? The submenu stays open exactly as it does today. Nothing breaks.

Run from the site root:  python3 patch-nav-collapse.py
Safe to run twice.
"""
import io, os, sys

CSS_ANCHOR = '.sub-menu a{padding:.55rem .1rem;font-size:1.02rem}'
CSS_ADD = (
    '.has-sub.collapsible>.sub-menu{display:none}'
    '.has-sub.collapsible.expanded>.sub-menu{display:block}'
    '.has-sub.collapsible>a{display:flex;justify-content:space-between;align-items:center}'
    '.has-sub.collapsible>a::after{content:"\\25B8";font-size:.78em;opacity:.6;padding-left:.6rem}'
    '.has-sub.collapsible.expanded>a::after{content:"\\25BE"}'
    '.nav-list.open.sub-open{max-height:calc(100vh - 5rem);'
    'max-height:calc(100dvh - 5rem);overflow-y:auto;'
    'overscroll-behavior:contain;-webkit-overflow-scrolling:touch}'
)

JS_ANCHOR = 'l.classList.toggle("open");});}})();</script>'
JS_ADD = (
    'l.classList.toggle("open");});}})();</script>'
    '<script>(function(){'
    'var mq=window.matchMedia("(max-width:880px)"),'
    'li=document.querySelector(".nav-list .has-sub"),'
    'list=document.querySelector(".nav-list");'
    'if(!li||!list)return;'
    'var a=li.querySelector("a"),sub=li.querySelector(".sub-menu");'
    'if(!a||!sub)return;'
    'var all=document.createElement("li"),al=document.createElement("a");'
    'al.href=a.getAttribute("href")||"/tools";al.textContent="All tools";'
    'all.appendChild(al);sub.insertBefore(all,sub.firstChild);'
    'function sync(){'
    'if(mq.matches){li.classList.add("collapsible");li.classList.remove("expanded");'
    'a.setAttribute("aria-expanded","false");list.classList.remove("sub-open");}'
    'else{li.classList.remove("collapsible","expanded");'
    'a.removeAttribute("aria-expanded");list.classList.remove("sub-open");}}'
    'a.addEventListener("click",function(e){'
    'if(!mq.matches)return;'
    'e.preventDefault();'
    'var open=li.classList.toggle("expanded");'
    'a.setAttribute("aria-expanded",String(open));'
    'list.classList.toggle("sub-open",open);});'
    'sync();'
    'if(mq.addEventListener){mq.addEventListener("change",sync);}else if(mq.addListener){mq.addListener(sync);}'
    '})();</script>'
)

SKIP_DIRS = {'.git', 'node_modules', 'md'}
css_done = js_done = skipped = 0

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in sorted(files):
        if not (f.endswith('.html') or f == 'styles.css'):
            continue
        p = os.path.join(root, f)
        try:
            c = io.open(p, encoding='utf-8').read()
        except Exception:
            continue

        orig = c
        if CSS_ANCHOR in c and 'has-sub.collapsible' not in c:
            c = c.replace(CSS_ANCHOR, CSS_ANCHOR + CSS_ADD)
            css_done += 1
        if JS_ANCHOR in c and 'All tools' not in c:
            c = c.replace(JS_ANCHOR, JS_ADD)
            js_done += 1

        if c != orig:
            io.open(p, 'w', encoding='utf-8').write(c)
            print('  ok   %s' % p)
        elif 'nav-list' in orig and 'has-sub.collapsible' not in orig:
            skipped += 1
            print('  ?    %s -- nav present but anchors not found' % p)

print('\nCSS added to %d files, JS added to %d files' % (css_done, js_done))
if skipped:
    print('%d file(s) need a look' % skipped)
    sys.exit(1)
