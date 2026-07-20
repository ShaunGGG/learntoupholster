#!/usr/bin/env python3
"""
Install the collapsible Tools submenu on EVERY page.

The earlier patch anchored its JavaScript on the exact text of the existing nav
script, so any page formatted differently got the CSS but no JS -- and with no JS
the .collapsible class is never applied, so the submenu stays open. That is why
it worked on the home page and nowhere else.

This version anchors on </style> and </body>, which every page has, and appends a
self-contained @media block so it doesn't matter where the existing nav rules sit.
Being last in the cascade, it also wins any specificity ties.

Run from the site root:  python3 patch-nav-fix.py
Safe to run repeatedly. Reports exactly what each page got.
"""
import io, os, sys

CSS_MARK = 'has-sub.collapsible'
JS_MARK  = 'ltuNavCollapse'

CSS_BLOCK = (
    '@media(max-width:880px){'
    '.has-sub.collapsible>.sub-menu{display:none}'
    '.has-sub.collapsible.expanded>.sub-menu{display:block}'
    '.has-sub.collapsible>a{display:flex;justify-content:space-between;align-items:center}'
    '.has-sub.collapsible>a::after{content:"\\25BE";font-size:.8em;line-height:1;'
    'color:var(--green);background:var(--cream-deep);border:1px solid var(--rule);'
    'border-radius:5px;width:1.85rem;height:1.85rem;display:inline-flex;'
    'align-items:center;justify-content:center;flex:0 0 auto;margin-left:.7rem;'
    'transition:transform .18s ease}'
    '.has-sub.collapsible.expanded>a::after{transform:rotate(180deg)}'
    '.nav-list.open.sub-open{max-height:calc(100vh - 5rem);'
    'max-height:calc(100dvh - 5rem);overflow-y:auto;'
    'overscroll-behavior:contain;-webkit-overflow-scrolling:touch}'
    '}'
)

JS_BLOCK = (
    '<script>/*ltuNavCollapse*/(function(){'
    'var mq=window.matchMedia("(max-width:880px)"),'
    'li=document.querySelector(".nav-list .has-sub"),'
    'list=document.querySelector(".nav-list");'
    'if(!li||!list)return;'
    'var a=li.querySelector("a"),sub=li.querySelector(".sub-menu");'
    'if(!a||!sub)return;'
    'if(!sub.querySelector(".all-tools")){'
    'var w=document.createElement("li"),al=document.createElement("a");'
    'al.href=a.getAttribute("href")||"/tools";al.textContent="All tools";'
    'al.className="all-tools";w.appendChild(al);sub.insertBefore(w,sub.firstChild);}'
    'function sync(){'
    'if(mq.matches){li.classList.add("collapsible");li.classList.remove("expanded");'
    'a.setAttribute("aria-expanded","false");}'
    'else{li.classList.remove("collapsible","expanded");a.removeAttribute("aria-expanded");}'
    'list.classList.remove("sub-open");}'
    'a.addEventListener("click",function(e){'
    'if(!mq.matches)return;'
    'e.preventDefault();'
    'var o=li.classList.toggle("expanded");'
    'a.setAttribute("aria-expanded",String(o));'
    'list.classList.toggle("sub-open",o);});'
    'sync();'
    'if(mq.addEventListener){mq.addEventListener("change",sync);}'
    'else if(mq.addListener){mq.addListener(sync);}'
    '})();</script>'
)

SKIP_DIRS = {'.git', 'node_modules', 'md'}
rows, problems = [], []

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in sorted(files):
        if not f.endswith('.html'):
            continue
        p = os.path.join(root, f)
        try:
            c = io.open(p, encoding='utf-8').read()
        except Exception as e:
            problems.append('%s -- unreadable: %s' % (p, e))
            continue

        if 'nav-list' not in c:
            continue

        did = []

        if CSS_MARK not in c:
            if '</style>' in c:
                i = c.rindex('</style>')
                c = c[:i] + CSS_BLOCK + c[i:]
                did.append('css')
            else:
                problems.append('%s -- no </style> to attach CSS' % p)

        if JS_MARK not in c:
            if '</body>' in c:
                i = c.rindex('</body>')
                c = c[:i] + JS_BLOCK + c[i:]
                did.append('js')
            else:
                problems.append('%s -- no </body> to attach JS' % p)

        if did:
            io.open(p, 'w', encoding='utf-8').write(c)
        rows.append((p, did))

added = [r for r in rows if r[1]]
for p, did in added:
    print('  + %-46s %s' % (p, '+'.join(did)))

print('\n%d pages with a nav; %d needed work, %d already complete'
      % (len(rows), len(added), len(rows) - len(added)))

# final audit: every nav page must now carry BOTH halves
bad = []
for p, _ in rows:
    c = io.open(p, encoding='utf-8').read()
    if CSS_MARK not in c or JS_MARK not in c:
        bad.append(p)
if bad or problems:
    print('\nNeeds a look:')
    for p in bad:
        print('  ! %s -- still incomplete' % p)
    for m in problems:
        print('  ! %s' % m)
    sys.exit(1)
print('Every page with a nav now has both the CSS and the JS.')
