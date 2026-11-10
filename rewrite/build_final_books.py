#!/usr/bin/env python3
"""Build the five final MYP coursebooks.

Part A: apply verified corrections surgically (redact + re-insert in the
        book's own extracted fonts at original sizes).
Part B: render and append the supplementary section.
Part C: verification renders.

Run:  python build_final_books.py A | B | C | all
"""
import pymupdf as f
import os, sys

REPO = '/home/user/MYP-Texbook-1'
FIN = f'{REPO}/rewrite/final'
FD = '/tmp/fonts'
os.makedirs(FIN, exist_ok=True)

BOOKS = {
    1: f'{REPO}/MYP-Mathematics-1-Student-Coursebook.pdf',
    2: f'{REPO}/MYP-Mathematics-2-Student-Coursebook.pdf',
    3: f'{REPO}/MYP-Mathematics-3-Student-Coursebook.pdf',
    4: f'{REPO}/MYP_Mathematics_4_Student_Coursebook.pdf',
    5: f'{REPO}/MYP_Mathematics_5_Student_Coursebook.pdf',
}
OUT = {n: f'{FIN}/{os.path.basename(p)}' for n, p in BOOKS.items()}

# ---------------------------------------------------------------- fonts
def find_font_file(substr):
    for fn in os.listdir(FD):
        if substr in fn:
            return f'{FD}/{fn}'
    raise FileNotFoundError(substr)

FONT_FILES = {
    'SS4':  f'{FD}/SourceSerif4-Regularttf',
    'SS4I': find_font_file('SourceSerif4-Italic'),
    'KT':   f'{FD}/m5_KaTeX_Main-Regularttf',
    'KTMI': f'{FD}/m5_KaTeX_Math-Italicttf',
    'KT1':  f'{FD}/m1_KaTeX_Main-Regularttf',
    'DS':   '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    'DSB':  '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
}
_fcache = {}
def FNT(key):
    if key not in _fcache:
        _fcache[key] = f.Font(fontfile=FONT_FILES[key])
    return _fcache[key]

def txtw(key, text, size):
    return FNT(key).text_length(text, size)

def span_font_at(page, x, y):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                x0, y0, x1, y1 = s['bbox']
                if x0 - 0.5 <= x <= x1 + 0.5 and y0 - 1.2 <= y <= y1 + 1.2:
                    name = s['font']
                    if 'SourceSerif4-Italic' in name: key = 'SS4I'
                    elif 'SourceSerif4' in name: key = 'SS4'
                    elif 'KaTeX_Math' in name: key = 'KTMI'
                    elif 'KaTeX_Main' in name: key = 'KT'
                    elif 'KaTeX' in name: key = 'KT'
                    else: return None, s['size']
                    return key, s['size']
    return None, None

def word_rect(page, needle, xmin=0, xmax=1e9, ymin=0, ymax=1e9):
    for r in page.search_for(needle):
        if xmin <= r.x0 <= xmax and ymin <= r.y0 <= ymax:
            return r
    raise AssertionError(f'word not found: {needle!r}')

# pending inserts per page: list of (page, callable).
# RULE: every lambda must bind its arguments as DEFAULTS (never free vars).
pending = []

def commit(page):
    page.apply_redactions(
        images=getattr(f, 'PDF_REDACT_IMAGE_NONE', 0),
        graphics=getattr(f, 'PDF_REDACT_LINE_ART_REMOVE', 1),
        text=getattr(f, 'PDF_REDACT_TEXT_REMOVE', 1),
    )
    for fn in list(pending):
        if fn[0] is page:
            fn[1]()
            pending.remove(fn)

def put(page, x, y, text, key, size):
    page.insert_text((x, y), text, fontname=key, fontfile=FONT_FILES[key], fontsize=size)

# ------------------------------------------------- mini typesetting (Q15)
def draw_rad(page, x, baseline, size, w_in, h=0.82):
    s = size
    a = (x + 0.05 * s, baseline - 0.22 * s)
    b = (x + 0.42 * s, baseline)
    c = (x + 0.72 * s, baseline - h * s)
    page.draw_polyline([a, b, c], width=0.28, closePath=False)
    page.draw_line(c, (x + 0.72 * s + w_in + 0.2, c[1]), width=0.32)
    return x + 0.72 * s + w_in + 0.2

def item_w(it, size):
    k = it[0]
    if k == 'T':   return txtw(it[2], it[1], it[3] if len(it) > 3 else size)
    if k == 'SP':  return it[1]
    if k == 'SUP': return item_w_seq(it[1], size * 0.7)
    if k == 'RAD': return 0.72 * size + item_w_seq(it[1], size) + 0.2
    if k == 'FRAD':  # fraction num / (a sqrt b)
        num, a, b = it[1], it[2], it[3]
        return max(txtw('KT', num, size), txtw('KT', a, size) + 0.72 * size + txtw('KT', b, size) + 0.2) + 1.0
    raise ValueError(k)

def item_w_seq(items, size):
    return sum(item_w(i, size) for i in items)

def draw_item(page, x, baseline, it, size):
    k = it[0]
    if k == 'T':
        s = it[3] if len(it) > 3 else size
        put(page, x, baseline, it[1], it[2], s)
        return x + txtw(it[2], it[1], s)
    if k == 'SP':
        return x + it[1]
    if k == 'SUP':
        return draw_item_seq(page, x, baseline - 2.4, it[1], size * 0.7)
    if k == 'RAD':
        h = it[2] if len(it) > 2 else 0.82
        w_in = item_w_seq(it[1], size)
        x2 = draw_rad(page, x, baseline, size, w_in, h)
        draw_item_seq(page, x2 - 0.2, baseline, it[1], size)
        return x2
    if k == 'FRAD':
        num, a, b = it[1], it[2], it[3]
        axis = baseline - 1.9
        w_den = txtw('KT', a, size) + 0.72 * size + txtw('KT', b, size) + 0.2
        w = max(txtw('KT', num, size), w_den) + 1.0
        x0f = x
        put(page, x0f + (w - txtw('KT', num, size)) / 2, axis - 4.4, num, 'KT', size)
        dx = x0f + (w - w_den) / 2
        put(page, dx, axis + 6.6, a, 'KT', size)
        dx += txtw('KT', a, size)
        dx = draw_rad(page, dx, axis + 6.6, size, txtw('KT', b, size), 0.82)
        put(page, dx - 0.2, axis + 6.6, b, 'KT', size)
        page.draw_line((x0f, axis), (x0f + w, axis), width=0.35)
        return x + w
    raise ValueError(k)

def draw_item_seq(page, x, baseline, items, size):
    for it in items:
        x = draw_item(page, x, baseline, it, size)
    return x

# ================================================================ PART A
def part_A():
    print('== Part A: corrections ==')
    for n, path in BOOKS.items():
        doc = f.open(path)
        apply_corrections(n, doc)
        for pg in list({id(t[0]): t[0] for t in pending}.values()):
            commit(pg)
        assert not pending, 'pending inserts remain'
        doc.save(OUT[n], garbage=3, deflate=True)
        doc.close()
        print(f'  MYP{n} saved -> {OUT[n]}')

def apply_corrections(n, doc):
    if n == 1:   m1(doc)
    elif n == 5: m5(doc)
    else:        print(f'  MYP{n}: no corrections (verified clean)')

# ---- MYP1
def m1(doc):
    print('  MYP1 corrections (2)')
    p = doc[216]  # C1: (67 words) -> (44 words)
    r = word_rect(p, '67 words', xmin=110, xmax=170, ymin=690, ymax=704)
    r67 = word_rect(p, '67', xmin=r.x0, xmax=r.x0 + 14, ymin=r.y0, ymax=r.y1)
    # redact only '67' (the '(' bbox ends at r67.x0 - 0.3); re-draw '(44' in bold
    p.add_redact_annot(f.Rect(r67.x0 - 0.2, r67.y0 - 0.3, r67.x1 + 0.3, r67.y1 + 0.3))
    size, key = 7.2, 'DSB'
    b = r67.y1 - 0.22 * size
    w44 = txtw(key, '44', size)
    x44 = r67.x0 + (r67.width - w44) / 2   # keep '44' centred on the old '67'
    pending.append((p, lambda pg=p, b=b, key=key, size=size, x44=x44: (put(pg, 121.8, b, '(', key, size), put(pg, x44, b, '44', key, size))))

    p = doc[218]  # C2: 57,665 -> 59,049 (KaTeX run "57, 665" then " / 1, 024")
    size, key = 7.34, 'KT1'
    r = word_rect(p, '665', xmin=340, xmax=390, ymin=208, ymax=225)
    x0 = 353.5
    w_old = txtw(key, '57, 665', size)
    p.add_redact_annot(f.Rect(x0 - 0.4, r.y0 - 0.4, x0 + w_old + 0.4, r.y1 + 0.4))
    x, b = x0, r.y1 - 0.22 * size
    pending.append((p, lambda x=x, b=b, key=key, size=size, pg=p: put(pg, x, b, '59, 049', key, size)))

# ---- MYP5
def m5(doc):
    print('  MYP5 corrections (5 key + 3 body)')
    p = doc[273]  # C1: 3 tokens in 3B Q7
    for old, new, box in [
        ('1.48661', '1.48780', (420, 460, 610, 630)),
        ('2973.22', '2975.61', (310, 350, 630, 650)),
        ('about 10', 'about 8', (375, 420, 630, 650)),
    ]:
        r = word_rect(p, old, xmin=box[0], xmax=box[1], ymin=box[2], ymax=box[3])
        p.add_redact_annot(f.Rect(r.x0 - 0.4, r.y0 - 0.4, r.x1 + 0.4, r.y1 + 0.4))
        key, size = span_font_at(p, (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        key = key or 'SS4'; size = size or 7.2
        x, b = r.x0, r.y1 - 0.22 * size
        pending.append((p, lambda x=x, b=b, new=new, key=key, size=size, pg=p: put(pg, x, b, new, key, size)))

    p = doc[299]  # C2 + C3
    r = word_rect(p, '64.49', xmin=440, xmax=480, ymin=95, ymax=112)
    p.add_redact_annot(f.Rect(r.x0 - 0.4, r.y0 - 0.4, r.x1 + 0.4, r.y1 + 0.4))
    key, size = span_font_at(p, (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2); key = key or 'SS4'; size = size or 7.2
    x, b = r.x0, r.y1 - 0.22 * size
    pending.append((p, lambda x=x, b=b, key=key, size=size, pg=p: put(pg, x, b, '79.98,', key, size)))

    r16 = word_rect(p, '16', xmin=485, xmax=500, ymin=106, ymax=120)
    p.add_redact_annot(f.Rect(r16.x0 - 0.4, r16.y0 - 0.4, r16.x1 + 0.4, r16.y1 + 0.4))
    key, size = span_font_at(p, (r16.x0 + r16.x1) / 2, (r16.y0 + r16.y1) / 2); key = key or 'KT'; size = size or 7.2
    cx = (r16.x0 + r16.x1) / 2; b = r16.y1 - 0.22 * size
    pending.append((p, lambda cx=cx, b=b, key=key, size=size, pg=p: put(pg, cx - txtw(key, '4', size) / 2, b, '4', key, size)))

    r = word_rect(p, '0.1905', xmin=310, xmax=345, ymin=124, ymax=140)
    p.add_redact_annot(f.Rect(r.x0 - 0.4, r.y0 - 0.4, r.x1 + 0.4, r.y1 + 0.4))
    key, size = span_font_at(p, (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2); key = key or 'SS4'; size = size or 7.2
    x, b = r.x0, r.y1 - 0.22 * size
    pending.append((p, lambda x=x, b=b, key=key, size=size, pg=p: put(pg, x, b, '0.0476,', key, size)))

    q15(doc)   # C4
    c5(doc)    # C5
    body_defects(doc)

# ---- MYP5 Q15
def q15(doc):
    p = doc[299]
    p.add_redact_annot(f.Rect(315.5, 536.5, 523.5, 561.5))
    S = 7.2
    x0, b1, b2 = 316.6, 545.8, 559.0
    def T(t, key='SS4', s=None):
        return ('T', t, key) if s is None else ('T', t, key, s)
    L1 = [
        T('Half-diagonal'), ('SP', 2.2), T('=', 'KT'), ('SP', 2.2),
        T('8', 'KT'), ('RAD', [T('2', 'KT')]),
        ('SP', 2.2), T('=', 'KT'), ('SP', 2.2),
        T('11.31\xa0m'), T(', so '), T('l', 'KTMI'),
        ('SP', 2.2), T('=', 'KT'), ('SP', 2.2),
        ('RAD', [T('(10', 'KT'), ('SUP', [T('2', 'KT')]), T(' + (8', 'KT'),
                 ('RAD', [T('2', 'KT')]), T(')', 'KT'), ('SUP', [T('2', 'KT')])], 1.02),
        ('SP', 2.2), T('=', 'KT'),
    ]
    L2 = [
        ('RAD', [T('228', 'KT')]),
        ('SP', 1.9), T('=', 'KT'), ('SP', 1.9),
        T('2', 'KT'), ('RAD', [T('57', 'KT')]),
        ('SP', 1.9), T('=', 'KT'), ('SP', 1.9),
        T('15.1', 'KT'), T('\xa0m and tan '), T('α', 'KTMI'),
        ('SP', 1.9), T('=', 'KT'), ('SP', 1.9),
        ('FRAD', '10', '8', '2'),
        ('SP', 1.9), T('=', 'KT'), ('SP', 1.9),
        T('0.8839', 'KT'), T(', α = ', 'SS4'),
        T('41.5', 'KT'), T('\u2218', 'KT', 5.04), T('. The'),
    ]
    w1, w2 = item_w_seq(L1, S), item_w_seq(L2, S)
    print(f'    Q15 widths {w1:.1f} / {w2:.1f} (max 206.2)')
    assert w1 <= 206.6, f'L1 too wide: {w1}'
    assert w2 <= 206.6, f'L2 too wide: {w2}'
    pending.append((p, lambda pg=p: (draw_item_seq(pg, x0, b1, L1, S), draw_item_seq(pg, x0, b2, L2, S))))

# ---- MYP5 C5
def c5(doc):
    p = doc[301]
    p.add_redact_annot(f.Rect(116.4, 591.2, 281.5, 602.5))
    p.add_redact_annot(f.Rect(82.0, 602.5, 281.5, 620.2))
    # the redact swallowed the KaTeX ')' of "(2.85, 1.42)" — restore it
    pending.append((p, lambda pg=p: put(pg, 114.2, 600.2, ')', 'KT', 7.2)))
    text = ('— a shift of 0.09 km, about 90 m; opposite-signed errors shift it '
            'up to about 0.11 km, so the position is reliable to ±0.12 km. '
            'Then LC = 3.92 km and the journey is 7.10 km in')
    spans = [(116.9, 280.3), (82.5, 280.3), (82.5, 280.3)]
    baselines = [600.7, 609.7, 618.6]
    def lw(s, S):  # SS4 width, ± taken from KaTeX (SS4 lacks ±)
        if '±' in s:
            pre, post = s.split('±', 1)
            return txtw('SS4', pre, S) + txtw('KT', '±', S) + txtw('SS4', post, S)
        return txtw('SS4', s, S)
    def wrap(S):
        words = text.split(' ')
        lines, cur = [], [words[0]]
        for wd in words[1:]:
            if len(lines) < 3:
                cap = spans[len(lines)][1] - spans[len(lines)][0]
                if lw(' '.join(cur + [wd]), S) <= cap:
                    cur.append(wd); continue
            lines.append(' '.join(cur)); cur = [wd]
        lines.append(' '.join(cur))
        return lines
    for S in (7.2, 7.0, 6.8):
        lines = wrap(S)
        if len(lines) <= 3 and all(
                lw(l, S) <= spans[i][1] - spans[i][0] for i, l in enumerate(lines)):
            break
    assert len(lines) <= 3, f'C5 needs {len(lines)} lines even at 6.8pt'
    print(f'    C5 at {S}pt:', [f'{l[:30]}…({lw(l, S):.0f}pt)' for l in lines])
    def render_line_pg(pg, x, b, l, S):
        if '±' in l:
            pre, post = l.split('±', 1)
            put(pg, x, b, pre, 'SS4', S)
            x += txtw('SS4', pre, S)
            put(pg, x, b, '±', 'KT', S)
            x += txtw('KT', '±', S)
            if post:
                put(pg, x, b, post, 'SS4', S)
        else:
            put(pg, x, b, l, 'SS4', S)
    for i, l in enumerate(lines):
        x, b = spans[i][0], baselines[i]
        pending.append((p, lambda x=x, b=b, l=l, S=S, pg=p: render_line_pg(pg, x, b, l, S)))

# ---- MYP5 body defects
def body_defects(doc):
    # defect 1: doc 231 — "3 × 3" label over a 2×2 matrix
    p = doc[231]
    r = word_rect(p, '3 × 3', xmin=330, xmax=370, ymin=184, ymax=205)
    p.add_redact_annot(f.Rect(r.x0 - 0.5, r.y0 - 0.5, r.x1 + 0.5, r.y1 + 0.5))
    size, key = 10.52, 'KT'
    x = (r.x0 + r.x1) / 2 - txtw(key, '2 × 2', size) / 2
    b = r.y1 - 0.24 * size
    pending.append((p, lambda x=x, b=b, key=key, size=size, pg=p: put(pg, x, b, '2 × 2', key, size)))

    # defect 2: doc 239 — GP hint "900 −4a" -> "900 +4a" (swap the minus)
    p = doc[239]
    r = word_rect(p, '−4a', xmin=450, xmax=480, ymin=660, ymax=678)
    minus = None
    for tr in p.get_texttrace():
        for ch in tr['chars']:
            q = f.Rect(ch[3])
            if r.x0 - 1.0 <= q.x0 <= r.x0 + 2.0 and r.y0 - 2 <= q.y0 <= r.y1:
                minus = q
    if minus is None:
        minus = f.Rect(r.x0 - 0.2, r.y0 - 0.5, r.x0 + 6.4, r.y1 + 0.5)
    p.add_redact_annot(minus + (-0.3, -0.4, 0.3, 0.4))
    size, key = 9.91, 'KT'
    cx = (minus.x0 + minus.x1) / 2; b = minus.y1 - 0.24 * size
    pending.append((p, lambda cx=cx, b=b, key=key, size=size, pg=p: put(pg, cx - txtw(key, '+', size) / 2, b, '+', key, size)))

    # defect 3: doc 328 — marking note quotes a preamble the book does not print
    p = doc[328]
    p.add_redact_annot(f.Rect(402.0, 496.8, 526.0, 507.6))
    p.add_redact_annot(f.Rect(316.0, 505.8, 526.0, 534.8))
    for x, b, t in [
        (402.6, 505.4, 'Note: the tank is modelled as'),
        (316.6, 514.4, 'draining at a constant rate; answering treats'),
        (316.6, 522.7, '1800 L/day as the net consumption while the tank drains.'),
    ]:
        pending.append((p, lambda x=x, b=b, t=t, pg=p: put(pg, x, b, t, 'SS4I', 7.0)))




# ================================================================ PART B
import re as _re

INK = '#1c2b3a'; ACC = '#1f4e79'
PAGEX, PAGEY, MARG = 594.96, 841.92, 58
FULLRECT = f.Rect(0, 0, PAGEX, PAGEY)
CONTENT = f.Rect(MARG, 54, PAGEX - MARG, PAGEY - 64)

CSS = """
body { font-family: serif; font-size: 10pt; line-height: 1.45; color: #1c2b3a; }
h2 { font-size: 14.5pt; font-weight: bold; color: #1f4e79; margin: 15pt 0 6pt 0;
     padding-bottom: 3pt; border-bottom-width: 1.5pt; border-bottom-style: solid;
     border-bottom-color: #1f4e79; }
h3 { font-size: 10.5pt; font-weight: bold; color: #1c2b3a; margin: 9pt 0 3pt 0; }
p { margin: 4pt 0; }
li { margin: 2.5pt 0 2.5pt 16pt; }
ul { margin: 3pt 0; }
.meta { color: #6b7684; font-size: 8.7pt; font-style: italic; margin: 2pt 0 8pt 0; }
.box { border-width: 1pt; border-style: solid; padding: 8pt 10pt; margin: 5pt 0 9pt 0;
       border-radius: 3pt; }
.tryit { border-color: #2f6b3a; background: #f0f7f1; }
.saa { border-color: #a05a17; background: #fbf4ea; }
.tryit h3 { color: #2f6b3a; margin-top: 0; }
.saa h3 { color: #a05a17; margin-top: 0; }
.answer { font-size: 8.9pt; color: #3d4a57; font-style: italic; margin-top: 5pt; }
.callout { border-width: 0 0 0 3pt; border-style: solid; border-color: #1f4e79;
          padding: 6pt 10pt; background: #f0f4f8; font-size: 9.3pt; margin: 8pt 0; }
.small { font-size: 9.2pt; color: #2a3948; }
.note { font-size: 9pt; color: #4a5866; }
"""

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def inline(t):
    t = esc(t)
    t = _re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = _re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', t)
    return t.replace('`', '')

def split_chapters(text):
    pre, chs, answers = [], {}, None
    mode, cur = 'pre', None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = _re.match(r'^## (?:Chapter|Section)\s+([\d.]+)\b\s*(?:·|:)?\s*(.*)$', line)
        if line.startswith('## Answers-section'):
            mode, cur, answers = 'answers', None, [line]; continue
        if m:
            mode, cur = 'ch', m.group(1)
            chs.setdefault(cur, [line]); continue
        if line.startswith('# ') or line == '---':
            continue
        if line.startswith('## '):
            continue
        if mode == 'pre':
            pre.append(line)
        elif mode == 'ch' and cur is not None:
            chs[cur].append(line)
        elif mode == 'answers':
            answers.append(line)
    return '\n'.join(pre), chs, '\n'.join(answers) if answers else ''

def split_strands(text):
    sections = []
    key, heading, body = None, None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        m = _re.match(r'^## (?:Chapter|Section)\s+([\d.]+)\b\s*(?:·|:)?\s*(.*)$', line)
        if line.startswith('## '):
            if key is not None:
                sections.append((key, heading, body))
            if m:
                key, heading, body = m.group(1), line, []
            else:
                key, heading, body = 'cap', line, []
            continue
        if line.startswith('# ') or line == '---':
            continue
        if key is not None:
            body.append(line)
    if key is not None:
        sections.append((key, heading, body))
    return sections

def block_html(lines, in_chapter=True):
    out = []
    li_buf, q_buf = [], []
    q_kind, ital, plain_i, last_heading = None, None, None, None
    boxes_open = 0

    def flush_li():
        if li_buf:
            for x in li_buf:
                out.append(f'<p style="margin-left:16pt">{x}</p>')
            li_buf.clear()
    def flush_q():
        nonlocal q_kind
        if q_buf:
            txt = ' '.join(x for x in q_buf if x)
            out.append(f'<p class="small">{txt}</p>' if q_kind == 'strand'
                       else f'<div class="callout">{txt}</div>')
            q_buf.clear(); q_kind = None
    def flush_ital():
        nonlocal ital
        if ital is not None:
            body = ' '.join(ital)
            cls = 'answer' if _re.match(r'^(Answers?:)', body, _re.I) else 'meta'
            out.append(f'<p class="{cls}">{body}</p>')
            ital = None
    def close_plain():
        nonlocal plain_i
        plain_i = None
    def close_boxes():
        nonlocal boxes_open
        if boxes_open:
            out.append('</div>'); boxes_open = 0

    for line in lines:
        line = line.rstrip()
        if ital is not None:
            if line.endswith('*'):
                ital.append(line[:-1]); flush_ital()
            else:
                ital.append(line)
            continue
        if not line.strip():
            flush_li(); flush_q(); close_plain(); last_heading = None
            continue
        if line.strip() == '---':
            flush_li(); flush_q(); flush_ital(); close_plain(); close_boxes()
            last_heading = None
            continue
        if line.startswith('**TRY-IT**'):
            flush_li(); flush_q(); close_plain(); close_boxes()
            out.append('<div class="box tryit"><h3>Try-it check</h3>'); boxes_open += 1
            continue
        if line.startswith('**STRETCH & APPLY**'):
            flush_li(); flush_q(); close_plain(); close_boxes()
            out.append('<div class="box saa"><h3>Stretch &amp; Apply</h3>'); boxes_open += 1
            continue
        if _re.match(r'^\*\*[A-D] · "', line):
            flush_li(); flush_q(); close_plain(); close_boxes()
            h = _re.sub(r'\s*— add:\s*$', '', line)
            out.append(f'<h3>{inline(h)}</h3>')
            last_heading = 'strand'
            continue
        if line.startswith('**') and line.endswith('**') and len(line) > 5:
            flush_li(); flush_q(); close_plain(); close_boxes()
            out.append(f'<p><b>{inline(line.strip("*"))}</b></p>')
            continue
        if _re.match(r'^\d+\.\s', line) or line.startswith('- '):
            flush_q(); flush_ital(); close_plain(); close_boxes()
            num = _re.match(r'^(\d+)\.\s', line)
            prefix = f'{num.group(1)}.&nbsp;&nbsp;' if num else '•&nbsp;&nbsp;'
            li_buf.append(prefix + inline(_re.sub(r'^\d+\.\s|^-\s', '', line)))
            continue
        if line.startswith('>'):
            flush_li(); flush_ital(); close_plain(); close_boxes()
            q_buf.append(inline(line[2:]) if line != '>' else '')
            if q_kind is None:
                q_kind = 'strand' if (in_chapter and last_heading == 'strand') else 'callout'
            continue
        if line.startswith('*') and not line.startswith('**') and len(line) > 2:
            flush_li(); flush_q(); close_plain(); close_boxes()
            if line.endswith('*') and len(line) > 4:
                body = line.strip('*')
                cls = 'answer' if _re.match(r'^(Answers?:)', body, _re.I) else 'meta'
                out.append(f'<p class="{cls}">{body}</p>')
            else:
                ital = [line[1:]]
            continue
        flush_li(); flush_q(); close_boxes()
        if plain_i is not None:
            out[plain_i] = out[plain_i][:-4] + ' ' + inline(line) + '</p>'
        else:
            out.append(f'<p>{inline(line)}</p>')
            plain_i = len(out) - 1
    flush_li(); flush_q(); flush_ital(); close_boxes()
    return out

LABEL_DEF = ('Try-it checks ask one or two rapid questions the moment a method is first '
             'shown. They test whether the new move is safe before you carry on; answers '
             'are given, so you can correct yourself in seconds. &nbsp;&nbsp; '
             'Stretch &amp; Apply boxes move the method one step into a new context. They '
             'are deliberately short, sit at the end of a concept sequence, and reward '
             'connecting the idea to something you have already seen.')

def corrections_html(n):
    if n == 1:
        return """
<h3>Answer-key corrections applied in this edition (2)</h3>
<ul>
<li>Chapter 1 · Criterion task “Museum label” (answers section, p217): “(67 words)” → “(44 words)”. The sample label contains 44 words; the task’s “no more than 70 words” requirement is met.</li>
<li>Chapter 2 · Investigation 2, Q8 (p219): “57,665 ÷ 1,024” → “59,049 ÷ 1,024”. 3¹⁰ = 59,049; the printed final value ≈ 57.7 was already correct (the numerator was a digit transposition).</li>
</ul>
<h3>Cleared on audit — no change</h3>
<ul><li>Chapter 5 · Application “The community market stall”, Q7: the key is correct — the 15% discount applies to the marked prices (revenue £381.65).</li></ul>
"""
    if n in (2, 3):
        return """<p>Every answer-key entry and worked example in this book was independently
recomputed during the verification pass. <b>No corrections were required.</b> The Try-it and
Stretch &amp; Apply boxes in this section were likewise recomputed before inclusion.</p>"""
    if n == 4:
        return """<p>Every answer-key entry and worked example in this book was independently
recomputed during the verification pass. <b>No corrections were required.</b> The gap recorded
for this book is structural: the assessment task headings carry the criterion label and rubric
but no strand-mapping line. The strand lines are provided in the chapter sections above —
ready to sit directly under each task heading.</p>"""
    return """
<h3>Answer-key corrections applied in this edition (5)</h3>
<ul>
<li>Chapter 3 · Exercise 3B, Q7 (p261): 2.7⁰·⁴ = 1.48661 → <b>1.48780</b>; the substitution 2973.22 → <b>2975.61</b>; “an error of about 10” → “about 8” (e⁰·⁴ = 1.49182 and 2000e⁰·⁴ = 2983.65 were already correct; the true difference is 8.04).</li>
<li>Chapter 7 · Mixed Practice 7, Q3 (p287): a² = 64.49 → <b>79.98</b> (9.5² + 7.2² − 2·9.5·7.2·cos 63° = 142.09 − 62.11); a = 8.94 cm was already correct.</li>
<li>Chapter 7 · Mixed Practice 7, Q4 (p287): numerator 16 → <b>4</b> (36 + 49 − 81); 0.1905 → <b>0.0476</b>; A = 87.3° was already correct.</li>
<li>Chapter 7 · Mixed Practice 7, Q15 (p287): the key used the half-diagonal of an 8 m base (4√2); the base is 16 m, so the corrected working reads Half-diagonal = 8√2 = 11.31 m, l = √228 = 2√57 ≈ <b>15.1 m</b>, tan α = 10/(8√2) = 0.8839, <b>α = 41.5°</b>; the dihedral angle β = 51.3° was already correct.</li>
<li>Criterion D task, Q5 (p289): the reliability sentence is corrected — (2.85, 1.42) is a shift of 0.09 km (≈ 90 m); opposite-signed errors shift the position up to about 0.11 km, so it is reliable to ±0.12 km; then L_C = 3.92 km and the journey is 7.10 km in 17.0 minutes — neither distance nor plan changes.</li>
</ul>
<h3>Body corrections applied in this edition (3)</h3>
<ul>
<li>Prerequisites for Chapter 11 (p218): a “3 × 3” label over a 2 × 2 array → “2 × 2”.</li>
<li>Section 11.4, GP Q2 hint (p226): “900 − 4a” → “900 + 4a”.</li>
<li>Criterion D, Q5 marking note (p315): the italic note no longer quotes a preamble sentence that is not printed in the book; it now states that the tank is modelled as draining at a constant rate and that answering treats 1800 L/day as the net consumption while the tank drains.</li>
</ul>
<h3>Flagged for a future edition — text left unchanged (1)</h3>
<ul><li>Chapter 11 · Milestone Q4: the key’s “10-year payback ≈ £3.67/m³” divides by 10 terms; the true 10-year payback is ≈ £0.92–1.22/m³.</li></ul>
<h3>Cleared on audit — no change</h3>
<ul><li>Mixed Practice 7, Q18 and Chapter 9 Criterion A, Q3: both keys verified correct on re-derivation.</li></ul>
"""

BOOK_NAMES = {1: 'MYP Mathematics 1', 2: 'MYP Mathematics 2', 3: 'MYP Mathematics 3',
              4: 'MYP Mathematics 4', 5: 'MYP Mathematics 5'}

def cover_page(doc, n):
    page = doc.new_page(width=PAGEX, height=PAGEY)
    cx = PAGEX / 2
    page.insert_text((cx - 118, 205), 'SUPPLEMENTARY  SECTION', fontname='DSB',
                     fontfile=FONT_FILES['DSB'], fontsize=25, color=(0.12, 0.31, 0.47))
    page.draw_line((cx - 200, 225), (cx + 200, 225), width=1.6, color=(0.12, 0.31, 0.47))
    page.insert_text((cx - 105, 258), f'{BOOK_NAMES[n]} — Student Coursebook',
                     fontname='DS', fontfile=FONT_FILES['DS'], fontsize=13, color=(0.11, 0.17, 0.23))
    page.insert_text((cx - 128, 282), 'Spec-gap additions and verified corrections · 2026 verification pass',
                     fontname='DS', fontfile=FONT_FILES['DS'], fontsize=9.5, color=(0.42, 0.46, 0.52))
    txt = open(f'{REPO}/rewrite/MYP{n}/chapter_additions.md', encoding='utf-8').read()
    chs = sorted({int(c) for c in _re.findall(r'^## Chapter\s+([\d.]+)\b', txt, _re.M)})
    span = f'Chapters {chs[0]}–{chs[-1]}' if chs else 'Chapters'
    items = ['How to use this section',
             f'{span} — Try-it checks and Stretch & Apply boxes, with answers']
    if n in (4, 5):
        items.append('Criterion strand lines for the assessment tasks')
    items += ['Answers-section entries to add', 'Corrections applied in this edition']
    y = 360
    for it in items:
        page.insert_text((cx - 160, y), '·   ' + it, fontname='DS', fontfile=FONT_FILES['DS'],
                         fontsize=11, color=(0.11, 0.17, 0.23))
        y += 22
    page.insert_text((cx - 130, 755), 'Appended to the coursebook — the original pagination is unchanged.',
                     fontname='DS', fontfile=FONT_FILES['DS'], fontsize=9, color=(0.42, 0.46, 0.52))

def story_to_doc(html):
    story = f.Story(html=html)
    writer = f.DocumentWriter('/tmp/story_tmp.pdf')
    more, _ = story.place(CONTENT)
    while True:
        dev = writer.begin_page(FULLRECT)
        story.draw(dev)
        writer.end_page()
        if not more:
            break
        more, _ = story.place(CONTENT)
    writer.close()
    return f.open('/tmp/story_tmp.pdf')

def part_B():
    print('== Part B: supplementary sections ==')
    for n in BOOKS:
        path = OUT[n]
        if not os.path.exists(path):
            print(f'  MYP{n}: missing {path}, run A first'); continue
        additions = open(f'{REPO}/rewrite/MYP{n}/chapter_additions.md', encoding='utf-8').read()
        pre, chs, ans = split_chapters(additions)
        sp = f'{REPO}/rewrite/MYP{n}/criterion_strands.md'
        strands_by_key = {k: (h, b) for k, h, b in split_strands(open(sp, encoding='utf-8').read())} \
                         if os.path.exists(sp) else {}

        H = []
        H.append('<h2>How to use this section</h2>')
        H += block_html(pre.splitlines(), in_chapter=False)
        if 'Try-it checks ask' not in pre:
            H.append(f'<div class="callout">{LABEL_DEF}</div>')
        for num in sorted(chs, key=float):
            head = chs[num][0]
            mm = _re.match(r'^## (Chapter|Section)\s+([\d.]+)\b\s*(?:·|:)?\s*(.*)$', head)
            H.append(f'<h2>{mm.group(1)} {mm.group(2)} — {esc(mm.group(3))}</h2>')
            H += block_html(chs[num][1:], in_chapter=True)
            if num in strands_by_key:
                h, b = strands_by_key[num]
                if any(x.strip() for x in b):
                    H.append('<h3>Criterion strand lines — insert directly under each task heading</h3>')
                    H += block_html(b, in_chapter=True)
        for k, (h, b) in strands_by_key.items():
            if k not in chs and any(x.strip() for x in b):
                mm = _re.match(r'^## (Chapter|Section)\s+([\d.]+)\b\s*(?:·|:)?\s*(.*)$', h)
                if mm:
                    H.append(f'<h2>{mm.group(1)} {mm.group(2)} — {esc(mm.group(3))}</h2>')
                else:
                    H.append(f'<h2>{esc(h[3:])}</h2>')
                H += block_html(b, in_chapter=True)
        if ans:
            H.append('<h2>Answers-section entries to add</h2>')
            H += block_html(ans.splitlines()[1:], in_chapter=False)
        H.append('<h2>Corrections applied in this edition</h2>')
        H.append(corrections_html(n))

        html = ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>' + CSS +
                '</style></head><body>' + ''.join(H) + '</body></html>')
        story_doc = story_to_doc(html)
        doc = f.open(path)
        cover_page(doc, n)
        base = doc.page_count
        doc.insert_pdf(story_doc)
        story_doc.close()
        for i in range(base, doc.page_count):
            pg = doc[i]
            pg.insert_text((MARG, PAGEY - 34), f'Supplementary section — {BOOK_NAMES[n]}',
                           fontname='DS', fontfile=FONT_FILES['DS'], fontsize=8,
                           color=(0.55, 0.58, 0.62))
            pg.insert_text((PAGEX - MARG - 14, PAGEY - 34), str(i + 1),
                           fontname='DS', fontfile=FONT_FILES['DS'], fontsize=8,
                           color=(0.55, 0.58, 0.62))
        total = doc.page_count
        tmp = path + '.new'
        doc.save(tmp, garbage=3, deflate=True)
        doc.close()
        os.replace(tmp, path)
        print(f'  MYP{n}: +1 cover +{total - base} content pages -> {total} pages total')



# ================================================================ PART C — BACK COVERS
BACK_STYLE = {
    1: dict(bg=(0.051, 0.165, 0.157), gold=(0.839, 0.647, 0.361),
            hdr_l=['MIDDLE YEARS PROGRAMME', 'YEAR 1 · MATHEMATICS'],
            hdr_r=['FIRST EDITION', '2026'],
            blurb=('The first volume of an original, inquiry-led series. A concept-driven course '
                   'in number, proportion, algebra, shape and data — every idea built from worked '
                   'examples, investigations and criterion-mapped tasks.'),
            inside=('INSIDE THIS VOLUME', [
                'Number systems · Place value and powers · Factors and primes',
                'Fractions and decimals · Percentages · Patterns and equations',
                'Lines, angles and constructions · Sets · Perimeter, area and volume · Data and graphs']),
            right_lbl=['MIDDLE YEARS', 'PROGRAMME']),
    2: dict(bg=(0.059, 0.122, 0.176), gold=(0.667, 0.514, 0.392),
            hdr_l=['MYP YEAR 2 · STUDENT COURSEBOOK'],
            hdr_r=[],
            blurb=('A concept-driven inquiry course in ratio and proportion, algebra and pattern, '
                   'geometry and space, probability and data — the second volume of a coherent '
                   'five-year series.'),
            inside=('INSIDE THIS VOLUME', [
                'Ratio and proportion · Algebra and pattern · Geometry and space',
                'Probability and data']),
            right_lbl=['MIDDLE YEARS', 'PROGRAMME']),
    3: dict(bg=(0.051, 0.106, 0.165), gold=(0.827, 0.631, 0.42),
            hdr_l=['MIDDLE YEARS PROGRAMME', 'YEAR 3 · MATHEMATICS'],
            hdr_r=['FIRST EDITION', '2026'],
            blurb=('An inquiry-led course in number, algebra, proof, space and evidence — built '
                   'around concepts, contexts and criteria, and designed as the third volume of a '
                   'coherent five-year series.'),
            inside=('INSIDE THIS VOLUME', [
                'Real numbers · Powers and scientific notation · Functions and algebra',
                'Linear relationships · Equations and systems · Transformations and congruence',
                'Similarity and trigonometry · Solids and measurement · Bivariate data · Probability and evidence']),
            right_lbl=['STUDENT EDITION', 'MYP YEAR 3']),
    4: dict(bg=(0.059, 0.106, 0.106), gold=(0.78, 0.635, 0.392),
            hdr_l=['A CONCEPT-BASED MATHEMATICS COURSE'],
            hdr_r=['YEARS 3 · 4 · 5', 'MIDDLE YEARS PROGRAMME'],
            blurb=('An original, inquiry-led course that builds algebraic fluency, geometric '
                   'reasoning, statistical literacy and mathematical modelling — the fourth volume '
                   'of a coherent five-year series.'),
            inside=('INSIDE THIS VOLUME', [
                'Number foundations · Algebraic expressions and factorisation · Linear equations and systems',
                'Functions and linear models · Quadratic expressions and functions · Sequences and generalisation',
                'Growth and financial mathematics · Congruence and transformations · Trigonometry · Statistics · Probability']),
            right_lbl=['STUDENT EDITION', 'MYP YEAR 4']),
    5: dict(bg=(0.059, 0.106, 0.106), gold=(0.78, 0.635, 0.392),
            hdr_l=['A CONCEPT-BASED MATHEMATICS COURSE'],
            hdr_r=['YEARS 3 · 4 · 5', 'MIDDLE YEARS PROGRAMME'],
            blurb=('The final volume of an original, inquiry-led course: exponential and logarithmic '
                   'functions, sequences and series, circle geometry, vectors and matrices, correlation '
                   'and conditional probability — closing with a sustained modelling capstone.'),
            inside=('INSIDE THIS VOLUME', [
                'Polynomials and the factor theorem · Functions: transformations, composites and inverses',
                'Exponential and logarithmic functions · Sequences and series · Quadratic inequalities',
                'Circle geometry · Sine and cosine rules · Vectors and matrices · Statistics · Probability']),
            right_lbl=['STUDENT EDITION', 'MYP YEAR 5']),
}
CREAM = (0.925, 0.905, 0.845)

def put_spaced(page, x, y, text, key, size, color, tracking=0.0):
    """Insert with manual letter-spacing; returns final x."""
    for ch in text:
        page.insert_text((x, y), ch, fontname=key, fontfile=FONT_FILES[key], fontsize=size, color=color)
        x += txtw(key, ch, size) + tracking
    return x

def wrap_text(text, key, size, maxw):
    words = text.split(' ')
    lines, cur = [], [words[0]]
    for wd in words[1:]:
        if txtw(key, ' '.join(cur + [wd]), size) <= maxw:
            cur.append(wd)
        else:
            lines.append(' '.join(cur)); cur = [wd]
    lines.append(' '.join(cur))
    return lines

def back_cover(n, doc):
    st = BACK_STYLE[n]
    bg, gold = st['bg'], st['gold']
    muted = tuple(min(1.0, c + 0.52) for c in bg)
    page = doc.new_page(width=PAGEX, height=PAGEY)
    page.draw_rect(f.Rect(0, 0, PAGEX, PAGEY), color=None, fill=bg, overlay=True)
    M = 58.0
    # header
    y = 64.0
    for i, t in enumerate(st['hdr_l']):
        put_spaced(page, M, y + i * 14, t.upper(), 'DSB', 7, muted, tracking=1.1)
    if st['hdr_r']:
        for i, t in enumerate(st['hdr_r']):
            w = txtw('DSB', t.upper(), 7) + 1.1 * (len(t.upper()) - 1)
            put_spaced(page, PAGEX - M - w, y + i * 14, t.upper(), 'DSB', 7,
                       gold if t == 'FIRST EDITION' else muted, tracking=1.1)
    page.draw_line((M, 92), (PAGEX - M, 92), width=0.7, color=muted)
    # about
    put_spaced(page, M, 250, 'ABOUT THIS COURSEBOOK', 'DSB', 8.5, gold, tracking=1.6)
    y = 278
    for ln in wrap_text(st['blurb'], 'SS4I', 11.5, 425):
        page.insert_text((M, y), ln, fontname='SS4I', fontfile=FONT_FILES['SS4I'], fontsize=11.5, color=CREAM)
        y += 17.5
    # gold rule + inside this volume
    y += 26
    page.draw_line((M, y - 8), (M + 60, y - 8), width=1.2, color=gold)
    label, toc = st['inside']
    put_spaced(page, M, y + 8, label, 'DSB', 8, muted, tracking=1.5)
    y += 26
    for ln in toc:
        page.insert_text((M, y), ln, fontname='DS', fontfile=FONT_FILES['DS'], fontsize=8.8, color=muted)
        y += 15
    # feature lines
    y = max(y + 30, 560)
    page.insert_text((M, y), 'COMPLETE WORKED SOLUTIONS · INVESTIGATIONS · CRITERION-MAPPED ASSESSMENT TASKS',
                     fontname='DS', fontfile=FONT_FILES['DS'], fontsize=8.3, color=muted)
    page.insert_text((M, y + 15), '2026 EDITION — ALL ANSWERS INDEPENDENTLY VERIFIED · SUPPLEMENTARY SECTION INCLUDED',
                     fontname='DSB', fontfile=FONT_FILES['DSB'], fontsize=8.3, color=gold)
    # author block
    page.draw_line((M, 742), (PAGEX - M, 742), width=0.7, color=muted)
    page.insert_text((M, 766), 'Sadikou Moukoddin', fontname='DSB', fontfile=FONT_FILES['DSB'],
                     fontsize=11.5, color=CREAM)
    put_spaced(page, M, 782, 'HEAD OF MATHEMATICS DEPARTMENT · MATHEMATICS TEACHER · CATEGORY 1',
               'DS', 6.8, muted, tracking=0.8)
    rx = PAGEX - M
    for i, t in enumerate(st['right_lbl']):
        w = txtw('DS', t.upper(), 6.8) + 0.8 * (len(t.upper()) - 1)
        put_spaced(page, rx - w, 762 + i * 11, t.upper(), 'DS', 6.8, muted, tracking=0.8)
    # geometric accent (bottom right)
    page.draw_circle((560, 806), 118, color=gold, width=0.8, fill=None)
    for i in range(4):
        page.draw_circle((418 + i * 26, 690), 5, color=gold, width=0.7, fill=None)
    for i in range(3):
        page.draw_circle((440 + i * 26, 712), 1.3, color=gold, width=1, fill=gold)
    return page

def part_C():
    print('== Part C: back covers ==')
    for n in BOOKS:
        path = OUT[n]
        if not os.path.exists(path):
            print(f'  MYP{n}: missing {path}, run A first'); continue
        doc = f.open(path)
        back_cover(n, doc)
        total = doc.page_count
        tmp = path + '.new'
        doc.save(tmp, garbage=3, deflate=True)
        doc.close()
        os.replace(tmp, path)
        print(f'  MYP{n}: back cover appended -> {total} pages total')

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('A', 'all'):
        part_A()
    if which in ('B', 'all'):
        part_B()
    if which in ('C', 'all'):
        part_C()
