#!/usr/bin/env python3
"""Add ContactPage + BreadcrumbList JSON-LD to contact.html.
Matches the house schema style used on about.html. Idempotent.
"""
import json, os, re

F = 'contact.html'
BASE = 'https://www.learntoupholster.com'

CONTACT = {
    "@context": "https://schema.org",
    "@type": "ContactPage",
    "name": "Contact",
    "url": f"{BASE}/contact",
    "isPartOf": {"@type": "WebSite", "name": "Learn to Upholster", "url": f"{BASE}/"},
    "about": {
        "@type": "Organization",
        "name": "Learn to Upholster",
        "url": f"{BASE}/",
        "email": "shaun@greenwoodupholstery.com",
        "parentOrganization": {
            "@type": "Organization",
            "name": "Greenwood Upholstery",
            "url": "https://www.greenwoodupholstery.com/"
        },
        "contactPoint": [{
            "@type": "ContactPoint",
            "contactType": "customer support",
            "email": "shaun@greenwoodupholstery.com",
            "availableLanguage": ["English"],
            "areaServed": "Worldwide"
        }]
    }
}

CRUMBS = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Learn to Upholster", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "Contact", "item": f"{BASE}/contact"}
    ]
}


def main():
    if not os.path.exists(F):
        print(f'!! {F} not found - skipping')
        return

    h = open(F, encoding='utf-8').read()

    if 'ContactPage' in h:
        print(f'{F}: ContactPage schema already present - nothing to do')
        return

    blocks = ''
    blocks += '<script type="application/ld+json">' + json.dumps(CONTACT) + '</script>\n'
    if 'BreadcrumbList' not in h:
        blocks += '<script type="application/ld+json">' + json.dumps(CRUMBS) + '</script>\n'

    if '</head>' not in h:
        print(f'!! {F}: no </head> found - left untouched')
        return

    h = h.replace('</head>', blocks + '</head>', 1)
    open(F, 'w', encoding='utf-8').write(h)
    n = blocks.count('<script')
    print(f'{F}: added {n} JSON-LD block{"s" if n != 1 else ""} (ContactPage'
          + (' + BreadcrumbList' if n == 2 else '') + ')')


if __name__ == '__main__':
    main()
