#!/usr/bin/env python3
"""Assemble the static pages: src/*.html + src/partials → project root.
Partials: {{SPRITE}}, {{HEADER}}, {{FOOTER}}; {{MARK_BODY}}/{{MARK_DOTS}} come
from assets/mark.json (the outlined ü of the logo). Run: python3 build.py"""
import json, pathlib
root = pathlib.Path(__file__).parent
src = root / 'src'
mark = json.loads((root / 'assets/mark.json').read_text())
part = {k: (src / 'partials' / f'{k.lower()}.html').read_text().rstrip('\n')
        for k in ('SPRITE', 'HEADER', 'FOOTER')}
for page in sorted(src.glob('*.html')):
    html = page.read_text()
    for k, v in part.items():
        html = html.replace('{{%s}}' % k, v)
    home = '' if page.name == 'index.html' else 'index.html'
    html = (html.replace('{{HOME}}', home)
                .replace('{{MARK_BODY}}', mark['body'])
                .replace('{{MARK_DOTS}}', mark['dots']))
    assert '{{' not in html, f'unresolved placeholder in {page.name}'
    (root / page.name).write_text(html)
    print('built', page.name)
