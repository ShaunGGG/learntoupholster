#!/usr/bin/env python3
"""
Mobile nav, clean rebuild.

Two problems this fixes:

1. Earlier patches each injected their own script and neither knew about the
   other, so pages ended up with two click handlers on Tools. Both toggled the
   same class, so they cancelled out and the tap did nothing. This strips every
   previous injection before installing one marked copy.

2. Making the "Tools" text itself a toggle meant the /tools page was no longer
   reachable by tapping the obvious thing. Now the text stays an ordinary link
   and a real <button> beside it does the expanding -- no ambiguity about what
   a tap will do, and it's keyboard and screen-reader friendly.

Run from the site root:  python3 patch-nav-v3.py
Safe to run repeatedly.
"""
import io, os, re, sys

MARK = 'ltuNav3'

CSS_BLOCK = (
    '.sub-toggle{display:none}'
    '@media(max-width:880px){'
    '.has-sub.collapsible{display:flex;flex-wrap:wrap;align-items:center}'
    '.has-sub.collapsible>a{flex:1 1 auto}'
    '.has-sub.collapsible>a::after{content:none}'
    '.has-sub.collapsible>.sub-toggle{flex:0 0 auto;display:inline-flex;'
    'align-items:center;justify-content:center;width:1.9rem;height:1.9rem;'
    'margin-left:.7rem;padding:0;cursor:pointer;'
    'background:var(--cream-deep);border:1px solid var(--rule);border-radius:5px;'
    'color:var(--green);font-size:.72rem;line-height:1;'
    'transition:transform .18s ease}'
    '.has-sub.collapsible>.sub-menu{flex:1 1 100%;display:none}'
    '.has-sub.collapsible.expanded>.sub-menu{display:block}'
    '.has-sub.collapsible.expanded>.sub-toggle{transform:rotate(180deg)}'
    '.nav-list.open.sub-open{max-height:calc(100vh - 5rem);'
    'max-height:calc(100dvh - 5rem);overflow-y:auto;'
    'overscroll-behavior:contain;-webkit-overflow-scrolling:touch}'
    '}'
)

JS_BLOCK = (
    '<script>/*ltuNav3*/(function(){'
    'if(window.__ltuNav3)return;window.__ltuNav3=1;'
    'var mq=window.matchMedia("(max-width:880px)"),'
    'li=document.querySelector(".nav-list .has-sub"),'
    'list=document.querySelector(".nav-list");'
    'if(!li||!list)return;'
    'var a=li.querySelector(":scope>a"),sub=li.querySelector(".sub-menu");'
    'if(!a||!sub)return;'
    'Array.prototype.forEach.call(sub.querySelectorAll(".all-tools"),function(n){'
    'if(n.parentNode&&n.parentNode.parentNode)n.parentNode.parentNode.removeChild(n.parentNode);});'
    'var w=document.createElement("li"),al=document.createElement("a");'
    'al.href=a.getAttribute("href")||"/tools";al.textContent="All tools";'
    'al.className="all-tools";w.appendChild(al);sub.insertBefore(w,sub.firstChild);'
    'var b=li.querySelector(".sub-toggle");'
    'if(!b){b=document.createElement("button");b.type="button";'
    'b.className="sub-toggle";b.innerHTML="&#9662;";'
    'li.insertBefore(b,sub);}'
    'function label(o){'
    'b.setAttribute("aria-expanded",String(o));'
    'b.setAttribute("aria-label",(o?"Hide":"Show")+" tools menu");}'
    'function sync(){'
    'if(mq.matches){li.classList.add("collapsible");}'
    'else{li.classList.remove("collapsible");}'
    'li.classList.remove("expanded");list.classList.remove("sub-open");label(false);}'
    'b.addEventListener("click",function(e){'
    'e.preventDefault();e.stopPropagation();'
    'var o=li.classList.toggle("expanded");'
    'label(o);list.classList.toggle("sub-open",o);});'
    'sync();'
    'if(mq.addEventListener){mq.addEventListener("change",sync);}'
    'else if(mq.addListener){mq.addListener(sync);}'
    '})();</script>'
)

# stale CSS from the earlier patches, either bare or wrapped in its own media query
OLD_CSS = re.compile(
    r'(?:@media\(max-width:880px\)\{)?'
    r'\.has-sub\.collapsible>\.sub-menu\{display:none\}'
    r'.*?\.nav-list\.open\.sub-open\{[^}]*\}\}?')

# any earlier injection: a script that sets up the 880px media query but isn't this one
OLD_SCRIPT = re.compile(
    r'<script>(?:/\*ltuNavCollapse\*/)?\(function\(\)\{[^<]*?matchMedia\("\(max-width:880px\)"\)[\s\S]*?</script>')

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

        before, did = c, []

        stripped = 0
        while True:
            m = OLD_SCRIPT.search(c)
            if not m or MARK in m.group(0):
                break
            c = c[:m.start()] + c[m.end():]
            stripped += 1
        if stripped:
            did.append('stripped %d old script(s)' % stripped)

        css_gone = 0
        while True:
            m = OLD_CSS.search(c)
            if not m:
                break
            c = c[:m.start()] + c[m.end():]
            css_gone += 1
        if css_gone:
            did.append('cleared %d old css block(s)' % css_gone)

        if MARK not in c:
            if '</style>' in c and '</body>' in c:
                i = c.rindex('</style>')
                c = c[:i] + CSS_BLOCK + c[i:]
                j = c.rindex('</body>')
                c = c[:j] + JS_BLOCK + c[j:]
                did.append('installed')
            else:
                problems.append('%s -- missing </style> or </body>' % p)

        if c != before:
            io.open(p, 'w', encoding='utf-8').write(c)
        rows.append((p, did))

for p, did in rows:
    if did:
        print('  + %-46s %s' % (p, ', '.join(did)))

done = sum(1 for _, d in rows if d)
print('\n%d pages with a nav; %d changed, %d already correct'
      % (len(rows), done, len(rows) - done))

bad = []
for p, _ in rows:
    c = io.open(p, encoding='utf-8').read()
    if c.count('/*' + MARK + '*/') != 1 or 'ltuNavCollapse' in c:
        bad.append(p)
if bad or problems:
    print('\nNeeds a look:')
    for p in bad:
        print('  ! %s' % p)
    for m in problems:
        print('  ! %s' % m)
    sys.exit(1)
print('Every nav page has exactly one copy, and no leftovers.')
