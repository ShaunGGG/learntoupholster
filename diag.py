import os,re,html
K=[('walking foot','Walking foot'),('overlock|serger','Overlocker'),
('bonded nylon|bonded thread|upholstery thread','Bonded thread'),
('machine needle|needle size|needle system','Machine needles'),
('zip','Zip'),('piping|welting','Piping cord'),('seam ripper|unpick','Seam ripper'),
('shears','Shears'),('regulator','Regulator'),('tack hammer','Tack hammer'),
('ripping chisel','Ripping chisel'),('staple remover|staple lifter','Staple remover'),
('staple gun','Staple gun'),('strainer|webbing stretcher','Webbing strainer'),
('skewer','Skewers'),('curved needle|mattress needle','Curved needles'),
('button','Button kit'),('webbing','Webbing'),('hessian|burlap','Hessian'),
('scrim','Scrim'),('calico|muslin','Calico'),('dacron|wadding','Dacron'),
('foam','Foam'),('horsehair|coir','Coir/hair'),('twine','Twine'),
('laid cord','Laid cord'),('spring','Springs'),('tack','Tacks'),('gimp','Gimp'),
('decorative nail|stud','Studs'),('adhesive','Adhesive'),('leather','Leather care'),
('velvet','Velvet brush'),('thread','Thread'),('bobbin','Bobbins'),('foot\\b','Presser feet')]
F=[]
for r,ds,ns in os.walk('.'):
    ds[:]=[d for d in ds if not d.startswith('.') and d not in {'node_modules','md'}]
    F+=[os.path.join(r,n)[2:] for n in ns if n.endswith('.html')]
for f in sorted(F):
    if 'sewing' not in f and 'blog/' not in f and 'projects/' not in f: continue
    h=open(f,encoding='utf-8').read()
    if 'class="aff"' in h: print('%-46s ALREADY HAS LINKS'%f); continue
    b=re.search(r'<article[^>]*>(.*?)</article>',h,re.S)
    tagfound='article' if b else 'NO-ARTICLE'
    t=b.group(1) if b else h
    for x in ('script','style','nav','footer','aside','header'):
        t=re.sub('<'+x+r'\b.*?</'+x+'>',' ',t,flags=re.S|re.I)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)).lower()
    hits=sorted([(len(re.findall(p,t)),l) for p,l in K if re.search(p,t)],key=lambda x:-x[0])[:7]
    print('%-46s %-11s %5d chars  %s'%(f,tagfound,len(t),', '.join('%s(%d)'%(l,n) for n,l in hits)))
