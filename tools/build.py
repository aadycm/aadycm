# builds the profile readme
# renders every svg into assets/ and writes README.md from tools/README.template.md
# usage  python tools/build.py <asset version>  then bump the version on every change so github refetches the images
import cmath, json, math, os, random, re, sys, textwrap, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CONTRIB = json.load(open(os.path.join(HERE, 'contrib.json')))

PALETTES = {
    'chlorophyll': dict(bg='#090D0A', panel='#0D130F', panel2='#0A0F0C', line='#1E2A21', ink='#EAF2E6',
                        muted='#8C9C8F', faint='#627368', accent='#B8F35A', accent_dark='#3D7314', onaccent='#0B1205', warn='#F0705A'),
    'sodium':      dict(bg='#100C09', panel='#16120C', panel2='#110E09', line='#2D251C', ink='#F7ECDE',
                        muted='#A7937C', faint='#7B6851', accent='#FFB547', accent_dark='#A65F00', onaccent='#1A1003', warn='#FF6B5A'),
    'cobalt':      dict(bg='#070A12', panel='#0C111E', panel2='#090D18', line='#1B2440', ink='#E8ECF8',
                        muted='#8A93AD', faint='#606B8D', accent='#6E9BFF', accent_dark='#2A5BD7', onaccent='#050A1A', warn='#FF7A6B'),
}

SERIF = "Georgia,'Times New Roman',serif"
MONO = "ui-monospace,'SF Mono','Cascadia Mono',Consolas,Menlo,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
W = 880
# manim's smooth rate function near enough
SMOOTH = 'cubic-bezier(.65,0,.35,1)'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def base_css(p):
    # every animated element keeps its finished state as the base style
    # so with motion turned off the picture is complete rather than empty
    return f"""
.serif{{font-family:{SERIF};fill:{p['ink']}}}
.mono{{font-family:{MONO}}} .mono:not([letter-spacing]){{letter-spacing:.14em}}
.sans{{font-family:{SANS}}}
.ink{{fill:{p['ink']}}} .muted{{fill:{p['muted']}}} .faint{{fill:{p['faint']}}} .acc{{fill:{p['accent']}}} .warn{{fill:{p['warn']}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def svg(w, h, body, css, p, label, defs=''):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<defs>
<radialGradient id="glow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate({w*0.86:.0f} 0) scale({w*0.55:.0f} {h*1.1:.0f})">
<stop offset="0" stop-color="{p['accent']}" stop-opacity=".16"/><stop offset="1" stop-color="{p['accent']}" stop-opacity="0"/></radialGradient>
<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="{p['ink']}" fill-opacity=".06"/></pattern>
{defs}
</defs>
<style>{base_css(p)}{css}</style>
{body}
</svg>
"""


def panel(w, h, p, glow=True):
    g = f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="url(#glow)"/>' if glow else ''
    return (f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="{p["panel"]}" stroke="{p["line"]}"/>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="url(#dots)"/>{g}')


# ---------- scene timeline ----------
# every diagram is one looping scene on a single clock like a manim scene
# each element gets its own keyframes placed on that clock so beats happen in order

class TL:
    def __init__(s, T, pre):
        s.T, s.pre, s.n, s.css = T, pre, 0, []
        s.out0, s.out1 = T - 0.9, T - 0.3
        s.rest_at, s.static = T - 1.0, []

    def anim(s, frames, extra='', ease=SMOOTH):
        s.n += 1
        name = f'{s.pre}{s.n}'
        ks = ''.join(f'{max(0, min(100, t / s.T * 100)):.3f}%{{{pr};animation-timing-function:{ease}}}' for t, pr in frames)
        s.css.append(f'@keyframes {name}{{{ks}}}.{name}{{animation:{name} {s.T}s infinite;{extra}}}')
        # with motion off each element rests where the scene ends rather than at its base style
        rest = [pr for t, pr in frames if t <= s.rest_at]
        if rest:
            s.static.append(f'.{name}{{{rest[-1]}}}')
        return name

    def _span(s, t, d, a, b, off=None, offd=0.4, last=None):
        # a is the hidden state and b the shown one both as css text
        off = s.out0 if off is None else off
        end = s.out1 if off == s.out0 else off + offd
        z = last or a
        return [(0, a), (t, a), (t + d, b), (off, b), (end, z), (s.T, z)]

    def draw(s, t, d=.8, off=None):
        fr = s._span(t, d, 'stroke-dashoffset:1.02;opacity:1', 'stroke-dashoffset:0;opacity:1', off,
                     last='stroke-dashoffset:0;opacity:0')
        return s.anim(fr, 'stroke-dasharray:1.02 1.02')

    def undraw(s, t, d, t2, d2=.5, back=None):
        # draws on then retracts at t2 then optionally redraws at back
        fr = [(0, 'stroke-dashoffset:1.02'), (t, 'stroke-dashoffset:1.02'), (t + d, 'stroke-dashoffset:0'),
              (t2, 'stroke-dashoffset:0'), (t2 + d2, 'stroke-dashoffset:-1.02')]
        if back:
            fr += [(back, 'stroke-dashoffset:1.02'), (back + .6, 'stroke-dashoffset:0'), (s.out0, 'stroke-dashoffset:0;opacity:1'),
                   (s.out1, 'stroke-dashoffset:0;opacity:0')]
        fr += [(s.T, 'stroke-dashoffset:-1.02;opacity:0')]
        return s.anim(fr, 'stroke-dasharray:1.02 1.02')

    def fade(s, t, d=.5, op=1, off=None):
        return s.anim(s._span(t, d, 'opacity:0', f'opacity:{op}', off))

    def grow(s, t, d=.4, off=None, origin='center'):
        fr = s._span(t, d, 'opacity:0;transform:scale(0)', 'opacity:1;transform:scale(1)', off,
                     last='opacity:0;transform:scale(1)')
        return s.anim(fr, f'transform-box:fill-box;transform-origin:{origin}')

    def growy(s, t, d=.7):
        fr = s._span(t, d, 'transform:scaleY(0);opacity:1', 'transform:scaleY(1);opacity:1', None,
                     last='transform:scaleY(1);opacity:0')
        return s.anim(fr, 'transform-box:fill-box;transform-origin:center bottom')

    def indicate(s, t, k=1.25):
        fr = [(0, 'transform:scale(1)'), (t, 'transform:scale(1)'), (t + .3, f'transform:scale({k})'),
              (t + .7, 'transform:scale(1)'), (s.T, 'transform:scale(1)')]
        return s.anim(fr, 'transform-box:fill-box;transform-origin:center')

    def write(s, t, d, box, inner, off=None):
        # manim write approximated as a left to right wipe plus a fade
        x, y, w, h = box
        cid = f'{s.pre}k{s.n + 1}'
        rc = s.anim([(0, 'transform:scaleX(0)'), (t, 'transform:scaleX(0)'), (t + d, 'transform:scaleX(1)'), (s.T, 'transform:scaleX(1)')],
                    'transform-box:fill-box;transform-origin:left center')
        fc = s.fade(t, d * .6, off=off)
        return (f'<clipPath id="{cid}"><rect class="{rc}" x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
                f'<g clip-path="url(#{cid})"><g class="{fc}">{inner}</g></g>')

    def text(s, t, x, y, txt, cls, size, anchor='start', d=None, off=None, extra=''):
        cw = size * (0.62 if 'mono' in cls else 0.55)
        w = len(txt) * cw * (1.25 if 'mono' in cls else 1) + 12
        bx = x - 4 if anchor == 'start' else (x - w / 2 if anchor == 'middle' else x - w + 4)
        inner = f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" text-anchor="{anchor}" {extra}>{esc(txt)}</text>'
        return s.write(t, d or min(1.2, .25 + len(txt) * .03), (bx, y - size - 2, w, size * 1.7), inner, off)

    def style(s):
        return ''.join(s.css) + '@media (prefers-reduced-motion:reduce){' + ''.join(s.static) + '}'


def P(d, cls, p, stroke, extra=''):
    return f'<path class="{cls}" pathLength="1" d="{d}" fill="none" stroke="{stroke}" {extra}/>'


# ---------- hero ----------

TAGLINES = [
    'I build things, then measure whether they hold up.',
    'I break LLM agents on purpose to see where they fail.',
    'Bad information broke my agent more than broken tools.',
    'Do agents report honestly when a defense blocks them?',
]


def hero_text(p):
    css = """
.rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) both} .d2{animation-delay:.12s} .d3{animation-delay:.24s} .d4{animation-delay:.36s}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
"""
    # each tagline writes in holds then fades and the next one takes its place
    per = 4.4
    tl = TL(per * len(TAGLINES), 'g')
    tl.rest_at = 1.5
    lines = ''
    for i, line in enumerate(TAGLINES):
        t0 = i * per
        inner = f'<text x="40" y="270" class="serif muted" font-size="18" font-style="italic">{esc(line)}</text>'
        lines += tl.write(t0 + .05, 1.3, (36, 250, 480, 30), inner, off=t0 + per - .55)
    body = f"""
<text x="40" y="50" class="mono faint" font-size="10.5">AADYCM / README.MD</text>
<g class="rise"><text x="40" y="98" class="mono acc" font-size="11">FIRMWARE · RETRIEVAL · AGENT EVALUATION</text></g>
<g class="rise d2"><text x="38" y="164" class="serif" font-size="64">Aadithya</text>
<text x="38" y="230" class="serif" font-size="64">Chandramouli<tspan class="acc">.</tspan></text></g>
<g class="rise d3">{lines}</g>
<g class="rise d4"><text x="40" y="306" class="mono faint" font-size="10.5">4TH YEAR CS · PENN STATE · STATE COLLEGE, PA</text></g>
"""
    return body, css + tl.style()


def monogram_loop():
    # the letters a and c as one closed pen path
    # visible runs are ink and the hidden runs are where the pen lifts
    yb = 64
    xl, xr = 40 * (110 - yb) / 110, 40 + 40 * yb / 110
    cx, cy, rr = 162, 55, 52
    a0, a1 = math.radians(-42), math.radians(-318)
    arc = [(cx + rr * math.cos(a0 + (a1 - a0) * i / 200), cy + rr * math.sin(a0 + (a1 - a0) * i / 200)) for i in range(201)]
    runs = [([(0, 110), (40, 0)], 1), ([(40, 0), (80, 110)], 1), ([(80, 110), (xr, yb)], 1), ([(xr, yb), (xl, yb)], 1),
            ([(xl, yb), arc[0]], 0), (arc, 1), ([arc[-1], (0, 110)], 0)]
    seg = []
    for pts, vis in runs:
        for a, b in zip(pts, pts[1:]):
            seg.append((a, b, vis))
    lens = [math.dist(a, b) for a, b, _ in seg]
    total = sum(lens)
    M = 720
    out, si, acc = [], 0, 0.0
    for n in range(M):
        target = n / M * total
        while acc + lens[si] < target:
            acc += lens[si]
            si += 1
        a, b, vis = seg[si]
        f = (target - acc) / lens[si]
        out.append((complex(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), vis))
    return out


def hero_fourier(p):
    T = 14.0
    pts = monogram_loop()
    M = len(pts)
    S, ox, oy = 1.4, 540, 96
    z = [complex(ox, oy) + S * q for q, _ in pts]
    coef = {}
    for k in range(-90, 91):
        coef[k] = sum(z[n] * cmath.exp(-2j * math.pi * k * n / M) for n in range(M)) / M
    terms = sorted((k for k in coef if k != 0), key=lambda k: -abs(coef[k]))[:80]
    c0 = coef[0]
    recon = [c0 + sum(coef[k] * cmath.exp(2j * math.pi * k * n / M) for k in terms) for n in range(M)]

    css = ''
    spins = set()
    g = f'<g transform="translate({c0.real:.2f} {c0.imag:.2f})">'
    pk, pphi = 0, 0.0
    for i, k in enumerate(terms):
        c = coef[k]
        r = abs(c)
        phi = math.degrees(cmath.phase(c))
        dk = k - pk
        name = f'sp{"m" if dk < 0 else ""}{abs(dk)}'
        spins.add((name, dk))
        g += f'<g transform="rotate({phi - pphi:.3f})"><g class="{name}">'
        if i < 28:
            g += (f'<circle r="{r:.2f}" fill="none" stroke="{p["ink"]}" stroke-opacity="{.22 if i < 8 else .12}"/>'
                  f'<line x2="{r:.2f}" stroke="{p["accent"]}" stroke-opacity=".55"/>')
        g += f'<g transform="translate({r:.3f} 0)">'
        pk, pphi = k, phi
    g += f'<circle r="3.2" fill="{p["accent"]}"/>' + '</g></g></g>' * len(terms) + '</g>'
    for name, dk in spins:
        if dk:
            css += f'@keyframes {name}{{to{{transform:rotate({dk * 360}deg)}}}}.{name}{{animation:{name} {T}s linear infinite}}'

    # ink trail in sync with the pen with one path per visible run
    tl = TL(T, 'f')
    runs, cur = [], None
    for n, (_, vis) in enumerate(pts):
        if vis and cur is None:
            cur = n
        if not vis and cur is not None:
            runs.append((cur, n))
            cur = None
    if cur is not None:
        runs.append((cur, M))
    fade_at = runs[-1][1] / M * T
    tl.rest_at = fade_at + .01
    trail = ''
    for a, b in runs:
        q = recon[a:min(b + 1, M)]
        d = 'M' + ' L'.join(f'{v.real:.1f} {v.imag:.1f}' for v in q)
        t0, t1 = a / M * T, b / M * T
        cls = tl.anim([(0, 'stroke-dashoffset:1.02;opacity:1'), (t0, 'stroke-dashoffset:1.02;opacity:1'),
                       (t1, 'stroke-dashoffset:0;opacity:1'), (fade_at, 'stroke-dashoffset:0;opacity:1'),
                       (min(T, fade_at + .6), 'stroke-dashoffset:0;opacity:0'), (T, 'stroke-dashoffset:0;opacity:0')],
                      'stroke-dasharray:1.02 1.02', ease='linear')
        trail += f'<path class="{cls}" pathLength="1" d="{d}" fill="none" stroke="{p["accent"]}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>'
    hb, hcss = hero_text(p)
    body = panel(W, 340, p) + hb + f"""
<g clip-path="url(#hclip)">{trail}{g}</g>
<text x="{W-40}" y="306" class="mono faint" font-size="9.5" text-anchor="end">FIG. 01 · {len(terms)} ROTATING CIRCLES DRAW MY INITIALS</text>
"""
    defs = f'<clipPath id="hclip"><rect x="470" y="1" width="{W-471}" height="338" rx="12"/></clipPath>'
    return svg(W, 340, body, hcss + css + tl.style(), p, 'Aadithya Chandramouli', defs)


def hero_network(p):
    rnd = random.Random(7)
    P_, K = 30.0, 40
    nodes = []
    for i in range(34):
        nodes.append(dict(cx=rnd.uniform(470, 860), cy=rnd.uniform(20, 320), ax=rnd.uniform(10, 34), ay=rnd.uniform(8, 28),
                          k=rnd.choice([1, -1, 1, 2]), ph=rnd.uniform(0, 2 * math.pi), hot=rnd.random() < .18))
    def pos(nd, j):
        a = nd['ph'] + 2 * math.pi * nd['k'] * j / K
        return nd['cx'] + nd['ax'] * math.cos(a), nd['cy'] + nd['ay'] * math.sin(a)
    track = [[pos(nd, j) for j in range(K + 1)] for nd in nodes]
    def vals(seq):
        return ';'.join(f'{v:.1f}' for v in seq)
    lines = ''
    TH = 92
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            ds = [math.dist(track[i][t], track[j][t]) for t in range(K + 1)]
            if min(ds) > TH:
                continue
            op = [max(0, 1 - d / TH) * .5 for d in ds]
            lines += (f'<line stroke="{p["accent"] if nodes[i]["hot"] and nodes[j]["hot"] else p["ink"]}" stroke-width=".8">'
                      f'<animate attributeName="x1" dur="{P_}s" repeatCount="indefinite" values="{vals(q[0] for q in track[i])}"/>'
                      f'<animate attributeName="y1" dur="{P_}s" repeatCount="indefinite" values="{vals(q[1] for q in track[i])}"/>'
                      f'<animate attributeName="x2" dur="{P_}s" repeatCount="indefinite" values="{vals(q[0] for q in track[j])}"/>'
                      f'<animate attributeName="y2" dur="{P_}s" repeatCount="indefinite" values="{vals(q[1] for q in track[j])}"/>'
                      f'<animate attributeName="stroke-opacity" dur="{P_}s" repeatCount="indefinite" values="{";".join(f"{o:.2f}" for o in op)}"/></line>')
    dots = ''
    for i, nd in enumerate(nodes):
        dots += (f'<circle r="{2.6 if nd["hot"] else 1.8}" fill="{p["accent"] if nd["hot"] else p["ink"]}" fill-opacity="{1 if nd["hot"] else .7}">'
                 f'<animate attributeName="cx" dur="{P_}s" repeatCount="indefinite" values="{vals(q[0] for q in track[i])}"/>'
                 f'<animate attributeName="cy" dur="{P_}s" repeatCount="indefinite" values="{vals(q[1] for q in track[i])}"/></circle>')
    defs = (f'<linearGradient id="nf" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="nm"><rect x="420" y="0" width="{W-420}" height="340" fill="url(#nf)"/></mask>')
    hb, hcss = hero_text(p)
    body = panel(W, 340, p) + f'<g mask="url(#nm)">{lines}{dots}</g>' + hb
    return svg(W, 340, body, hcss, p, 'Aadithya Chandramouli', defs)


# ---------- section header ----------

def header(p, num, kicker, title, right, light=False):
    h = 118
    if light:
        p = dict(p, ink='#1F2328', faint='#59636E', line='#D1D9E0', accent=p['accent_dark'])
    css = f"""
.run{{animation:run 6s cubic-bezier(.45,0,.2,1) infinite}}
@keyframes run{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}80%{{opacity:1}}100%{{transform:translateX(800px);opacity:0}}}}
"""
    body = f"""
<rect x="4" y="22" width="7" height="7" fill="{p['accent']}"/>
<text x="20" y="30" class="mono acc" font-size="11">{num}  {esc(kicker)}</text>
<text x="{W-4}" y="30" class="mono faint" font-size="10" text-anchor="end">{esc(right)}</text>
<text x="2" y="82" class="serif" font-size="40">{esc(title)}</text>
<line x1="4" x2="{W-4}" y1="104" y2="104" stroke="{p['line']}"/>
<line x1="4" x2="180" y1="104" y2="104" stroke="{p['accent']}"/>
<circle class="run" cx="40" cy="104" r="2.5" fill="{p['accent']}"/>
"""
    return svg(W, h, body, css, p, f'{kicker}: {title}')


# ---------- project cards ----------

def card(p, kicker, title, desc, stats, tags, motif, motif_css, label, button='VIEW REPO →'):
    h = 330
    lines = textwrap.wrap(desc, 54)
    d = ''.join(f'<text x="40" y="{142+i*22}" class="sans muted" font-size="15">{esc(l)}</text>' for i, l in enumerate(lines))
    st = ''
    for i, (num, c1, c2) in enumerate(stats):
        x = 40 + i * 148
        st += (f'<text x="{x}" y="248" class="serif" font-size="34">{esc(num)}</text>'
               f'<text x="{x}" y="268" class="mono faint" font-size="9">{esc(c1)}</text>'
               f'<text x="{x}" y="281" class="mono faint" font-size="9">{esc(c2)}</text>')
    tg, tx = '', 40
    for t in tags:
        tw = len(t) * 6.6 + 18
        tg += (f'<rect x="{tx}" y="296" width="{tw:.0f}" height="20" rx="10" fill="none" stroke="{p["line"]}"/>'
               f'<text x="{tx+9}" y="309.5" class="mono muted" font-size="9.5" letter-spacing=".06em">{esc(t)}</text>')
        tx += tw + 6
    body = panel(W, h, p) + f"""
<text x="40" y="52" class="mono acc" font-size="10.5">{esc(kicker)}</text>
<text x="38" y="104" class="serif" font-size="42">{esc(title)}</text>
{d}{st}{tg}{button_svg(p, 470 - (len(button) * 6.9 + 30), 294, button, h=24)[0]}
<g transform="translate(500 30)"><rect x="0" y="0" width="350" height="270" rx="10" fill="{p['panel2']}" stroke="{p['line']}"/>{motif}</g>
"""
    return svg(W, h, body, motif_css, p, label)


def hydronode(p):
    tl = TL(12.0, 'h')
    A, L, F, Wn = p['accent'], p['line'], p['faint'], p['warn']
    xs = [52, 114, 176, 238, 300]
    beds = ['NFT', 'DRIP', 'ZONES', 'AERO', 'SAFFRON']
    m = ''
    # captions narrate the scene in the top left
    m += tl.text(.2, 16, 24, 'ONE BOARD · FIVE SYSTEMS', 'mono faint', 9, off=2.8)
    m += tl.text(3.0, 16, 24, 'DATA GOES UP · WATER GOES DOWN', 'mono muted', 9, off=6.0)
    m += tl.text(6.3, 16, 24, 'THEN THE WIFI DROPS', 'mono warn', 9, off=8.2)
    m += tl.text(8.5, 16, 24, 'THE BOARD KEEPS WATERING', 'mono acc', 9)
    # the board
    m += f'<rect class="{tl.fade(1.0, .6, .07)}" x="110" y="98" width="130" height="48" rx="7" fill="{A}"/>'
    m += f'<rect class="{tl.draw(.2, 1.0)}" pathLength="1" x="110" y="98" width="130" height="48" rx="7" fill="none" stroke="{A}"/>'
    m += f'<g class="{tl.indicate(8.7, 1.12)}">' + tl.text(1.0, 175, 120, 'ESP32', 'serif', 16, 'middle') + '</g>'
    m += tl.text(1.3, 175, 136, 'LOGIC ON THE BOARD', 'mono muted', 7.5, 'middle')
    m += f'<rect class="{tl.draw(8.5, .7, off=10.0)}" pathLength="1" x="100" y="88" width="150" height="68" rx="11" fill="none" stroke="{A}" stroke-width="1.5"/>'
    # the cloud and the link that breaks
    fb = tl.anim([(0, 'opacity:0'), (1.4, 'opacity:0'), (1.9, 'opacity:1'), (6.5, 'opacity:1'), (7.0, 'opacity:.35'),
                  (tl.out0, 'opacity:.35'), (tl.out1, 'opacity:0'), (12, 'opacity:0')])
    m += f'<g class="{fb}"><rect x="232" y="38" width="102" height="34" rx="6" fill="none" stroke="{L}"/>'
    m += f'<text x="283" y="59" class="mono muted" font-size="9.5" text-anchor="middle">FIREBASE</text></g>'
    m += P('M240 116 H283 V72', tl.undraw(2.2, .8, 6.3, .6), p, A, 'stroke-width="1.4"')
    flow = tl.fade(3.0, .4, off=6.3, op=1)
    m += f'<g class="{flow}"><path class="flow" d="M240 116 H283 V72" fill="none" stroke="{p["panel2"]}" stroke-dasharray="3 5" stroke-width="1.6"/></g>'
    m += f'<path class="{tl.fade(6.6, .5)}" d="M240 116 H283 V72" fill="none" stroke="{Wn}" stroke-opacity=".5" stroke-dasharray="2 4"/>'
    m += P('M277 88 l12 12', tl.draw(6.8, .25), p, Wn, 'stroke-width="1.8"')
    m += P('M289 88 l-12 12', tl.draw(7.0, .25), p, Wn, 'stroke-width="1.8"')
    # pipes beds and water
    m += P(f'M175 146 V172 M{xs[0]} 172 H{xs[-1]}', tl.draw(3.0, .9), p, A, 'stroke-opacity=".6"')
    drops = ''
    for i, (x, b) in enumerate(zip(xs, beds)):
        m += f'<line class="{tl.draw(3.5 + i * .1, .5)}" pathLength="1" x1="{x}" x2="{x}" y1="172" y2="222" stroke="{L}"/>'
        m += f'<rect class="{tl.fade(4.1 + i * .1, .5, .12)}" x="{x-24}" y="222" width="48" height="14" rx="3" fill="{A}"/>'
        m += f'<rect class="{tl.draw(3.7 + i * .1, .6)}" pathLength="1" x="{x-24}" y="222" width="48" height="14" rx="3" fill="none" stroke="{L}"/>'
        m += f'<text class="{tl.fade(4.3 + i * .08, .4)}" x="{x}" y="254" font-family="{MONO}" font-size="7.5" letter-spacing=".08em" text-anchor="middle" fill="{F}">{b}</text>'
        drops += f'<circle class="drop" style="animation-delay:{i*0.23:.2f}s" cx="{x}" cy="176" r="2.6" fill="{A}"/>'
    m += f'<g class="{tl.fade(4.4, .4)}">{drops}</g>'
    css = tl.style() + """
.flow{animation:flow .8s linear infinite} @keyframes flow{to{stroke-dashoffset:-8}}
.drop{animation:drop 1.15s cubic-bezier(.5,0,1,1) infinite}
@keyframes drop{0%{transform:translateY(0);opacity:0}15%{opacity:1}90%{opacity:1}100%{transform:translateY(44px);opacity:0}}
"""
    return card(p, '01 · FIRMWARE · PRIVATE REPO · LIVE AT HYDRONODE.IN', 'HydroNode',
                'Five growing systems whose watering and safety logic run on the board, not the cloud, so the plants still get water when the WiFi drops.',
                [('5', 'GROWING', 'SYSTEMS'), ('~4.5k', 'LINES OF', 'FIRMWARE'), ('~1.9k', 'LINES OF', 'FRONTEND')],
                ['C++', 'ESP32', 'RA4M1', 'FIREBASE', 'MODBUS'], m, css, 'HydroNode', button='HYDRONODE.IN →')


def semantic(p):
    tl = TL(13.0, 's')
    A, Mu = p['accent'], p['muted']
    m = tl.text(0, 16, 24, '35 QUESTIONS · WRITTEN BEFORE EITHER RAN', 'mono faint', 9)
    grids = [(22, 'V1 · STDLIB · NO DEPS', 30, '30/35', 'RECALL@1 85.7%', 2.0),
             (190, 'V2 · MINILM · 1.0 GB', 31, '31/35', 'RECALL@1 88.6%', 3.5)]
    for gi, (gx, title, hits, big, rec, t_hit) in enumerate(grids):
        m += tl.text(.3 + gi * .3, gx - 6, 52, title, 'mono muted', 8.5, extra='letter-spacing=".1em"')
        for i in range(35):
            cx, cy = gx + (i % 7) * 20, 72 + (i // 7) * 20
            m += f'<circle class="{tl.grow(.6 + gi * .25 + i * .018, .3)}" cx="{cx}" cy="{cy}" r="5.4" fill="none" stroke="{Mu}" stroke-width="1.2"/>'
            if i < hits:
                m += f'<circle class="{tl.grow(t_hit + i * .04, .3)}" cx="{cx}" cy="{cy}" r="6" fill="{A}"/>'
            else:
                m += f'<circle class="{tl.grow(8.7 + (i - hits) * .08, .35)}" cx="{cx}" cy="{cy}" r="5.4" fill="{A}" fill-opacity=".22" stroke="{A}" stroke-width="1.3"/>'
        m += tl.text(t_hit + 1.3, gx - 6, 196, big, 'serif', 28)
        m += tl.text(t_hit + 1.5, gx - 6, 214, rec, 'mono faint', 8.5, extra='letter-spacing=".1em"')
    # the one question that separates them
    for gx in (22, 190):
        m += f'<circle class="{tl.draw(6.1, .6, off=8.1)}" pathLength="1" cx="{gx + 40}" cy="152" r="10.5" fill="none" stroke="{A}" stroke-width="1.5"/>'
    m += f'<line x1="16" x2="334" y1="232" y2="232" stroke="{p["line"]}"/>'
    m += tl.text(6.5, 16, 252, 'ONE QUESTION APART', 'mono acc', 8.5, off=8.2, extra='letter-spacing=".1em"')
    m += tl.text(8.5, 16, 252, 'IN THE TOP THREE · BOTH 35 OF 35', 'mono acc', 8.5, extra='letter-spacing=".1em"')
    return card(p, '02 · RETRIEVAL · TWO VERSIONS · ONE BENCHMARK', 'Semantic Notes',
                'The same notes search built twice: once on the standard library alone, once with a real sentence encoder. The gigabyte buys one question in 35.',
                [('85.7%', 'RECALL@1', 'STDLIB ONLY'), ('88.6%', 'RECALL@1', 'WITH 1 GB OF DEPS'), ('100%', 'BOTH, IN', 'THE TOP THREE')],
                ['PYTHON', 'FASTAPI', 'MINILM', 'STDLIB'], m, tl.style(), 'Semantic Notes')


def papertrail(p):
    tl = TL(13.0, 'p')
    A, Mu, Wn = p['accent'], p['muted'], p['warn']
    top = [(48, 'd'), (110, 'e'), (175, 'f'), (240, 'g'), (302, 'h')]
    mid = [(90, 'a'), (175, 'b'), (260, 'c')]
    pos = {k: (x, 54) for x, k in top}
    pos.update({k: (x, 112) for x, k in mid})
    pos['B'], pos['R'] = (175, 168), (175, 226)
    edges = [('d', 'a', 0), ('e', 'a', 0), ('e', 'b', 0), ('f', 'b', 0), ('g', 'c', 0), ('h', 'c', 0), ('f', 'c', 0),
             ('a', 'B', 1), ('b', 'B', 1), ('c', 'B', 1), ('B', 'R', 2)]
    m = tl.text(0, 16, 24, 'WHAT EVERYTHING RESTS ON', 'mono faint', 9, off=7.6)
    m += tl.text(8.0, 16, 24, 'REMOVE IT AND THE GRAPH SPLITS', 'mono warn', 9, off=10.2)
    m += tl.text(10.5, 16, 24, 'THAT IS A CUT VERTEX', 'mono acc', 9)
    dim = tl.anim([(0, 'opacity:1'), (7.9, 'opacity:1'), (8.4, 'opacity:.12'), (9.9, 'opacity:.12'), (10.4, 'opacity:1'), (13, 'opacity:1')])
    keep, cut = '', ''
    for i, (s, t, layer) in enumerate(edges):
        (x1, y1), (x2, y2) = pos[s], pos[t]
        e = (f'<line class="{tl.draw(1.6 + layer * .7 + i * .05, .6)}" pathLength="1" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
             f'stroke="{A if t in "BR" else Mu}" stroke-opacity=".85"/>')
        if t in 'BR':
            cut += e
        else:
            keep += e
    m += keep
    for i, (k, (x, y)) in enumerate(pos.items()):
        if k in 'BR':
            continue
        m += f'<circle class="{tl.grow(.3 + i * .08, .35)}" cx="{x}" cy="{y}" r="5.5" fill="{p["panel2"]}" stroke="{Mu}"/>'
    bx, by = pos['B']
    rx, ry = pos['R']
    bnode = (f'<circle class="ring" cx="{bx}" cy="{by}" r="9" fill="none" stroke="{A}"/>'
             f'<g class="{tl.indicate(6.4, 1.4)}"><circle class="{tl.grow(1.2, .4)}" cx="{bx}" cy="{by}" r="8" fill="{A}"/></g>')
    m += f'<g class="{dim}">{cut}{bnode}</g>'
    m += f'<circle class="{tl.grow(1.4, .4)}" cx="{rx}" cy="{ry}" r="8" fill="{p["panel2"]}" stroke="{p["ink"]}" stroke-width="1.5"/>'
    m += f'<g class="{dim}">' + tl.text(3.3, bx + 18, by - 2, '1998', 'serif', 14)
    m += tl.text(6.6, bx + 18, by + 12, 'SOLE BRIDGE', 'mono acc', 8, extra='letter-spacing=".1em"') + '</g>'
    m += tl.text(3.5, rx + 18, ry - 2, '1986', 'serif', 14)
    m += tl.text(3.8, rx + 18, ry + 12, '9 PAPERS REST ON IT', 'mono muted', 8, extra='letter-spacing=".1em"')
    # every route down the graph has to pass through 1998
    routes = [('d', 'a'), ('e', 'b'), ('f', 'b'), ('g', 'c'), ('h', 'c')]
    for i, (s, mm) in enumerate(routes):
        st = 4.2 + i * .12
        way = [pos[s], pos[mm], pos['B'], pos['R']]
        def tr(q):
            return f'transform:translate({q[0]}px,{q[1]}px)'
        fr = [(0, f'opacity:0;{tr(way[0])}'), (st, f'opacity:0;{tr(way[0])}'), (st + .15, f'opacity:1;{tr(way[0])}'),
              (st + .7, f'opacity:1;{tr(way[1])}'), (st + 1.3, f'opacity:1;{tr(way[2])}'), (st + 1.9, f'opacity:1;{tr(way[3])}'),
              (st + 2.2, f'opacity:0;{tr(way[3])}'), (13, f'opacity:0;{tr(way[3])}')]
        m += f'<circle class="{tl.anim(fr)}" r="3" fill="{A}" opacity="0"/>'
    m += P('M40 140 H310', tl.draw(8.3, .5, off=9.9), p, Wn, 'stroke-width="1.4"')
    m += f'<text x="16" y="256" class="mono faint" font-size="8" letter-spacing=".1em">FROM THE SHIPPED EXAMPLE</text>'
    css = tl.style() + """
.ring{transform-box:fill-box;transform-origin:center;animation:ring 13s infinite;opacity:0}
@keyframes ring{0%,49%{opacity:0;transform:scale(1)}50%{opacity:.9;transform:scale(1)}58%{opacity:0;transform:scale(2.8)}100%{opacity:0}}
"""
    return card(p, '03 · GRAPHS · STANDARD LIBRARY ONLY', 'Paper Trail',
                'Turns a reading list of papers into a graph of which results rest on which, so the one everything leans on is visible.',
                [('3', 'MEASURES THAT', 'DISAGREE USEFULLY'), ('31', 'TESTS, INCL. A', '3,000-NODE CHAIN'), ('0', 'PACKAGES', 'NEEDED')],
                ['PYTHON', 'STDLIB', 'PAGERANK', 'CUT VERTICES'], m, css, 'Paper Trail')


def vbrace(x, y1, y2, w=6):
    mid = (y1 + y2) / 2
    return (f'M{x} {y1} q{w} 0 {w} {w} V{mid - w} q0 {w} {w} {w} q{-w} 0 {-w} {w} V{y2 - w} q0 {w} {-w} {w}')


def agent(p):
    tl = TL(13.0, 'a')
    A, Mu, F, L = p['accent'], p['muted'], p['faint'], p['line']
    base, sc, x0, x1 = 212, 148, 56, 300
    rows = [('BASE', '23/23', 1.0, '100%'), ('FLAKY', '21/23', .913, '91%'),
            ('BUDGET', '17/23', .739, '74%'), ('SEARCH', '8/21', .381, '38%')]
    cxs = [96, 156, 216, 276]
    m = tl.text(0, 16, 24, 'SAME MODEL · 23 TASKS · WORSE CONDITIONS', 'mono faint', 9, off=5.6)
    m += tl.text(6.0, 16, 24, 'DEGRADED SEARCH · −62 POINTS', 'mono acc', 9)
    # axes first like a manim scene
    m += P(f'M{x0} {base} V{base - sc - 12}', tl.draw(.2, .6), p, Mu)
    m += P(f'M{x0} {base} H{x1}', tl.draw(.4, .7), p, Mu)
    m += f'<line class="{tl.fade(.9, .6)}" x1="{x0}" x2="{x1}" y1="{base - sc}" y2="{base - sc}" stroke="{F}" stroke-dasharray="3 4"/>'
    for v, lab in [(0, '0'), (.5, '50'), (1, '100')]:
        y = base - v * sc
        m += f'<g class="{tl.fade(.8, .4)}"><line x1="{x0-4}" x2="{x0}" y1="{y}" y2="{y}" stroke="{Mu}"/>'
        m += f'<text x="{x0-8}" y="{y+3}" font-family="{MONO}" font-size="8" fill="{F}" text-anchor="end">{lab}</text></g>'
    for i, ((name, frac, v, pct), cx) in enumerate(zip(rows, cxs)):
        hot = i == 3
        h = v * sc
        bar = f'<rect class="{tl.growy(1.4 + i * .4)}" x="{cx-16}" y="{base-h:.1f}" width="32" height="{h:.1f}" rx="2" fill="{A if hot else Mu}" fill-opacity="{1 if hot else .5}"/>'
        m += f'<g class="{tl.indicate(4.3, 1.08)}">{bar}</g>' if hot else bar
        m += tl.text(2.0 + i * .4, cx, base - h - 8, pct, 'serif acc' if hot else 'serif', 14, 'middle', extra=f'paint-order="stroke" stroke="{p["panel2"]}" stroke-width="6" stroke-linejoin="round"')
        m += f'<text class="{tl.fade(1.2 + i * .1, .4)}" x="{cx}" y="228" font-family="{MONO}" font-size="8" letter-spacing=".1em" text-anchor="middle" fill="{A if hot else Mu}">{name}</text>'
        m += f'<text class="{tl.fade(1.3 + i * .1, .4)}" x="{cx}" y="240" font-family="{MONO}" font-size="7.5" text-anchor="middle" fill="{F}">{frac}</text>'
    top38 = base - .381 * sc
    m += P(vbrace(300, base - sc, top38), tl.draw(4.8, .7), p, A, 'stroke-width="1.3"')
    m += tl.text(5.4, 316, (base - sc + top38) / 2 + 4, '−62', 'serif acc', 13)
    m += f'<line x1="16" x2="334" y1="248" y2="248" stroke="{L}"/>'
    m += tl.text(6.6, 16, 263, 'BAD INFORMATION HURT MORE THAN BAD TOOLS', 'mono acc', 8.5, extra='letter-spacing=".08em"')
    return card(p, '04 · EVALUATION · TOOL-USING LLM AGENT', 'Agent Reliability',
                'The first study hit a ceiling and the write-up says so. The second degraded the environment instead, and found where the agent breaks.',
                [('23', 'TASKS WITH', 'KNOWN ANSWERS'), ('100%', 'AT', 'BASELINE'), ('38%', 'WITH SEARCH', 'RESULTS TRUNCATED')],
                ['PYTHON', 'GEMINI API', 'GEMMA', 'MCNEMAR'], m, tl.style(), 'Agent Reliability')


def button_svg(p, x, y, label, h=26):
    # a pill that reads as a button while the whole card is the actual link
    bw = len(label) * 6.9 + 30
    return (f'<rect x="{x:.0f}" y="{y}" width="{bw:.0f}" height="{h}" rx="{h/2:g}" fill="{p["accent"]}" fill-opacity=".1" stroke="{p["accent"]}" stroke-opacity=".7"/>'
            f'<text x="{x + 15:.0f}" y="{y + h/2 + 3.6:.1f}" font-family="{MONO}" font-size="10" letter-spacing=".1em" fill="{p["accent"]}">{esc(label)}</text>'), bw


# ---------- research cards ----------

def rcard(p, kicker, title, desc, meta, button, motif, motif_css, label):
    h = 240
    lines = textwrap.wrap(desc, 58)
    assert len(lines) <= 3, f'research blurb too long for the card: {desc}'
    d = ''.join(f'<text x="40" y="{122+i*20}" class="sans muted" font-size="14">{esc(l)}</text>' for i, l in enumerate(lines))
    b, bw = private_svg(p, 40, 186) if button is None else button_svg(p, 40, 186, button)
    body = panel(W, h, p) + f"""
<text x="40" y="46" class="mono acc" font-size="10.5">{esc(kicker)}</text>
<text x="38" y="90" class="serif" font-size="31">{esc(title)}</text>
{d}{b}
<text x="{40 + bw + 14:.0f}" y="203" class="mono faint" font-size="9" letter-spacing=".08em">{esc(meta)}</text>
<g transform="translate(500 24)"><rect x="0" y="0" width="350" height="192" rx="10" fill="{p['panel2']}" stroke="{p['line']}"/>{motif}</g>
"""
    return svg(W, h, body, motif_css, p, label)


def private_svg(p, x, y, h=26):
    # a quiet pill with a small lock that says the repo is not public yet
    label = 'PRIVATE REPO'
    bw = len(label) * 6.9 + 44
    cy = y + h / 2
    return (f'<rect x="{x}" y="{y}" width="{bw:.0f}" height="{h}" rx="{h/2:g}" fill="none" stroke="{p["line"]}"/>'
            f'<rect x="{x + 13}" y="{cy - 1.5:.1f}" width="9" height="7" rx="1.5" fill="{p["muted"]}"/>'
            f'<path d="M{x + 15} {cy - 1.5:.1f} v-2.2 a2.5 2.5 0 0 1 5 0 v2.2" fill="none" stroke="{p["muted"]}" stroke-width="1.3"/>'
            f'<text x="{x + 29}" y="{cy + 3.6:.1f}" font-family="{MONO}" font-size="10" letter-spacing=".1em" fill="{p["muted"]}">{label}</text>'), bw


def box(tl, t, x, y, w, h, stroke, rx=6, d=.6):
    return f'<rect class="{tl.draw(t, d)}" pathLength="1" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{stroke}"/>'


def r_injection(p):
    tl = TL(12.0, 'ra')
    A, Mu, Wn, I, L = p['accent'], p['muted'], p['warn'], p['ink'], p['line']
    m = tl.text(0, 16, 22, 'WHEN A DEFENSE BLOCKS AN ATTACK', 'mono faint', 9, off=6.4)
    m += tl.text(6.7, 16, 22, 'DOES THE AGENT SAY SO HONESTLY?', 'mono acc', 9)
    # agent calls the tool on the top lane and the reply comes back on the bottom lane
    m += box(tl, .3, 16, 70, 74, 44, A)
    m += tl.text(.8, 53, 97, 'AGENT', 'serif', 14, 'middle')
    m += box(tl, .6, 142, 70, 74, 44, Mu)
    m += tl.text(1.1, 179, 97, 'TOOL', 'serif', 14, 'middle')
    m += P('M90 82 H141', tl.draw(1.3, .5), p, A)
    m += P('M135 78 l6 4 l-6 4', tl.draw(1.75, .2), p, A)
    m += tl.text(2.2, 179, 52, 'INJECTED TEXT', 'mono warn', 7.5, 'middle', extra='letter-spacing=".06em"')
    m += P('M179 57 V69', tl.draw(2.5, .3), p, Wn, 'stroke-width="1.4"')
    # the poisoned reply travels back and stops dead at the defense
    m += P('M142 102 H118', tl.draw(2.9, .5), p, Wn, 'stroke-width="1.4"')
    m += P('M115 90 V114', tl.draw(3.3, .3), p, I, 'stroke-width="2.6" stroke-linecap="round"')
    m += tl.text(3.7, 115, 132, 'BLOCKED', 'mono ink', 7.5, 'middle', extra='letter-spacing=".08em"')
    # what the agent then says about it
    m += box(tl, 4.6, 228, 44, 108, 116, L, rx=7)
    m += tl.text(5.0, 240, 62, 'AGENT REPORT', 'mono muted', 7.5, extra='letter-spacing=".08em"')
    for i, row in enumerate(['FALSE COMPLETION', 'FABRICATION', 'MISSING LIMITS']):
        y = 88 + i * 22
        cy = y - 2.6
        m += (f'<g class="{tl.indicate(7.4 + i * .25, 1.3)}">'
              f'<circle class="{tl.grow(5.5 + i * .5, .3)}" cx="245" cy="{cy}" r="5.2" fill="none" stroke="{Wn}" stroke-width="1.1"/>'
              f'<text class="{tl.fade(5.6 + i * .5, .3)}" x="245" y="{cy}" dominant-baseline="central" text-anchor="middle" '
              f'font-family="{SANS}" font-size="7" font-weight="700" fill="{Wn}">?</text></g>')
        m += tl.text(5.7 + i * .5, 257, y, row, 'mono ink', 7, extra='letter-spacing=".03em"')
    m += tl.text(8.4, 16, 180, 'FOUR-CONDITION AGENTDOJO EXPERIMENT', 'mono faint', 8, extra='letter-spacing=".1em"')
    return rcard(p, 'R1 · LLM AGENTS · SECURITY', 'Prompt-injection defenses',
                 'Do LLM agents misreport their results once a prompt-injection defense blocks an attack, compared with an ordinary tool failure? Studied in AgentDojo.',
                 'ADVISOR DR. SUMAN SAHA · FALL 2026 – NOW', None, m, tl.style(), 'Prompt-injection defenses research')


def r_framing(p):
    tl = TL(12.0, 'rc')
    A, Mu, L = p['accent'], p['muted'], p['line']
    m = tl.text(0, 16, 22, 'SAME RISK · TWO FRAMINGS', 'mono faint', 9, off=6.3)
    m += tl.text(6.6, 16, 22, 'WHAT DOES EACH SIDE PRIORITIZE?', 'mono acc', 9)
    m += box(tl, .3, 16, 76, 82, 40, Mu)
    m += tl.text(.7, 57, 100, 'SCENARIO', 'mono ink', 8, 'middle')
    m += P('M98 96 C120 96 120 62 142 62', tl.draw(1.0, .5), p, Mu)
    m += P('M98 96 C120 96 120 130 142 130', tl.draw(1.15, .5), p, Mu)
    m += box(tl, 1.4, 142, 46, 70, 32, L)
    m += tl.text(1.7, 177, 66, 'FRAME A', 'mono ink', 8, 'middle')
    m += box(tl, 1.55, 142, 114, 70, 32, L)
    m += tl.text(1.85, 177, 134, 'FRAME B', 'mono ink', 8, 'middle')
    m += box(tl, 2.2, 258, 40, 78, 30, A)
    m += tl.text(2.5, 297, 60, 'Humans', 'serif', 13, 'middle')
    m += box(tl, 2.35, 258, 122, 78, 30, A)
    m += tl.text(2.65, 297, 142, 'LLMs', 'serif', 13, 'middle')
    links = [((212, 62), (258, 55)), ((212, 62), (258, 137)), ((212, 130), (258, 55)), ((212, 130), (258, 137))]
    for i, ((x1, y1), (x2, y2)) in enumerate(links):
        m += f'<line class="{tl.draw(2.9 + i * .15, .4)}" pathLength="1" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{Mu}" stroke-opacity=".6"/>'
        st = 3.8 + i * .2
        def tr(x, y, op):
            return f'opacity:{op};transform:translate({x}px,{y}px)'
        fr = [(0, tr(x1, y1, 0)), (st, tr(x1, y1, 0)), (st + .1, tr(x1, y1, 1)), (st + .8, tr(x2, y2, 1)),
              (st + 1.0, tr(x2, y2, 0)), (12, tr(x2, y2, 0))]
        m += f'<circle class="{tl.anim(fr)}" r="3" fill="{A}" opacity="0"/>'
    for y in (82, 164):
        m += tl.text(6.9, 297, y, 'PRIORITIES ?', 'mono acc', 7.5, 'middle', extra='letter-spacing=".08em"')
    m += tl.text(7.6, 16, 180, 'STUDENT-LED · EXPERIMENT IN DESIGN', 'mono faint', 8, extra='letter-spacing=".1em"')
    return rcard(p, 'R2 · DECISIONS · HUMANS AND LLMS', 'Humans vs LLMs on risk',
                 'A student-led study of how the initial framing of a scenario shapes what humans and LLMs prioritize when safety and environmental risk is ambiguous.',
                 'ADVISOR DR. JEREMY GERNAND · FALL 2026 – NOW', None, m, tl.style(), 'Risk decision research')


# ---------- heatmap with a snake ----------

def heatmap(p):
    h = 270
    days = CONTRIB
    first = datetime.date.fromisoformat(days[0]['date'])
    lead = (first.weekday() + 1) % 7  # github columns start on sunday
    cell, gap = 11, 3
    pitch = cell + gap
    x0, y0 = 66, 116
    total = sum(d['count'] for d in days)
    active_n = sum(1 for d in days if d['count'])
    best = cur = 0
    for d in days:
        cur = cur + 1 if d['count'] else 0
        best = max(best, cur)
    alpha = {1: .28, 2: .5, 3: .75, 4: 1}
    ncols = (len(days) + lead + 6) // 7
    grid, months, last_m, active = '', '', None, []
    for i, d in enumerate(days):
        k = i + lead
        col, row = k // 7, k % 7
        x, y = x0 + col * pitch, y0 + row * pitch
        dt = datetime.date.fromisoformat(d['date'])
        if row == 0 and dt.month != last_m and col < ncols - 2:
            months += f'<text x="{x}" y="{y0-10}" class="mono faint" font-size="8.5" letter-spacing=".08em">{dt.strftime("%b").upper()}</text>'
            last_m = dt.month
        grid += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{p["line"]}" fill-opacity=".7"/>'
        if d['level']:
            active.append((col, row, d['level']))

    # the snake walks grid lines greedily to the nearest square it has not eaten yet
    def c(col, row):
        return x0 + col * pitch + cell / 2, y0 + row * pitch + cell / 2
    here = (-2, 0)
    todo = list(active)
    path = [c(*here)]
    dist, arrive = 0.0, {}
    while todo:
        nxt = min(todo, key=lambda q: (abs(q[0] - here[0]) + abs(q[1] - here[1]), q[0]))
        todo.remove(nxt)
        if nxt[1] != here[1]:
            path.append(c(here[0], nxt[1]))
        path.append(c(nxt[0], nxt[1]))
        dist += (abs(nxt[0] - here[0]) + abs(nxt[1] - here[1])) * pitch
        arrive[(nxt[0], nxt[1])] = dist
        here = (nxt[0], nxt[1])
    path.append(c(ncols + 1, here[1]))
    dist += (ncols + 1 - here[0]) * pitch
    speed, hold, nseg = 150.0, 2.5, 7
    move = dist / speed
    D = move + hold
    f = move / D
    lag = pitch / speed / D
    d_attr = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in path)
    food = ''
    for col, row, lv in active:
        x, y = x0 + col * pitch, y0 + row * pitch
        a = arrive[(col, row)] / dist * f
        food += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{p["accent"]}" fill-opacity="{alpha[lv]}">'
                 f'<animate attributeName="opacity" dur="{D:.2f}s" repeatCount="indefinite" values="1;1;0;0;1" '
                 f'keyTimes="0;{a:.4f};{min(a + .002, .97):.4f};.985;1"/></rect>')
    snake = ''
    for i in range(nseg - 1, -1, -1):
        s0 = i * lag
        sz = 10 if i == 0 else 9 - i * .6
        snake += (f'<rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" rx="3" fill="{p["accent"] if i == 0 else p["ink"]}" '
                  f'fill-opacity="{1 if i == 0 else .9 - i * .11:.2f}">'
                  f'<animateMotion dur="{D:.2f}s" repeatCount="indefinite" calcMode="linear" path="{d_attr}" '
                  f'keyPoints="0;0;1;1" keyTimes="0;{s0:.4f};{min(f + s0, .995):.4f};1"/></rect>')
    for r, lab in [(1, 'MON'), (3, 'WED'), (5, 'FRI')]:
        grid += f'<text x="{x0-12}" y="{y0 + r*pitch + 9}" class="mono faint" font-size="8" letter-spacing=".06em" text-anchor="end">{lab}</text>'
    stats = ''
    for i, (n, cpt) in enumerate([(f'{total:,}', 'CONTRIBUTIONS'), (str(active_n), 'ACTIVE DAYS'), (str(best), 'DAY BEST STREAK')]):
        x = W - 40 - (2 - i) * 120
        stats += (f'<text x="{x}" y="72" class="serif" font-size="30" text-anchor="end">{n}</text>'
                  f'<text x="{x}" y="88" class="mono faint" font-size="8.5" letter-spacing=".1em" text-anchor="end">{cpt}</text>')
    snap = datetime.date.fromisoformat(days[-1]['date']).strftime('%d %b %Y').upper()
    body = panel(W, h, p) + f"""
<text x="40" y="52" class="mono acc" font-size="10.5">COMMIT LOG · PUBLIC ACTIVITY</text>
<text x="38" y="84" class="serif" font-size="24">One square per day, <tspan font-style="italic" class="muted">for a year.</tspan></text>
{stats}{months}{grid}{food}<g clip-path="url(#gclip)">{snake}</g>
<text x="40" y="{h-24}" class="mono faint" font-size="8.5" letter-spacing=".1em">SNAPSHOT {snap} · REAL DATA FROM GITHUB</text>
"""
    defs = f'<clipPath id="gclip"><rect x="{x0-4}" y="{y0-4}" width="{ncols*pitch+4}" height="{7*pitch+8}"/></clipPath>'
    return svg(W, h, body, '', p, f'{total} contributions in the last year', defs)


# ---------- skills ----------

def skills(p):
    rows = [('LANGUAGES', ['Python', 'C++', 'Java', 'Swift', 'JavaScript', 'SQL']),
            ('ML / AI', ['PyTorch', 'TensorFlow', 'OpenCV', 'YOLOv8', 'XGBoost', 'Pandas']),
            ('LLMS & AGENTS', ['Prompt engineering', 'LLM APIs', 'Function calling', 'AgentDojo', 'RAG', 'LangChain', 'Vector embeddings']),
            ('EMBEDDED', ['ESP32', 'Renesas RA4M1', 'RS485 Modbus']),
            ('BACKEND & TOOLS', ['Node.js', 'Firebase', 'FastAPI', 'Apps Script', 'Git'])]
    body, y, n = '', 40, 0
    for ri, (lab, items) in enumerate(rows):
        if ri:
            body += f'<line x1="40" x2="{W-40}" y1="{y-14}" y2="{y-14}" stroke="{p["line"]}"/>'
        body += f'<text x="40" y="{y+16}" class="mono acc" font-size="9.5">0{ri+1}  {esc(lab)}</text>'
        x = 230
        for it in items:
            w = len(it) * 6.9 + 24
            if x + w > W - 40:
                x, y = 230, y + 32
            body += (f'<g class="k" style="animation-delay:{n*.035:.3f}s"><rect x="{x}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{p["panel2"]}" stroke="{p["line"]}"/>'
                     f'<text x="{x+12}" y="{y+16}" font-family="{MONO}" font-size="11.5" fill="{p["ink"]}">{esc(it)}</text></g>')
            x += w + 8
            n += 1
        y += 50
    h = y - 4
    css = """.k{animation:k .6s cubic-bezier(.2,.7,.2,1) both} @keyframes k{from{opacity:0;transform:translateY(6px)}}"""
    return svg(W, h, panel(W, h, p, glow=False) + body, css, p, 'Skills')


# ---------- closer ----------

def closer(p):
    h = 200
    css = """
.ul{stroke-dasharray:1.02 1.02;animation:ul 5s cubic-bezier(.65,0,.35,1) infinite}
@keyframes ul{0%{stroke-dashoffset:1.02}30%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-1.02}}
"""
    body = panel(W, h, p) + f"""
<rect x="40" y="40" width="7" height="7" fill="{p['accent']}"/>
<text x="56" y="48" class="mono acc" font-size="11">05  CONTACT</text>
<text x="38" y="106" class="serif" font-size="40">Let&#8217;s build something that holds up<tspan class="acc">.</tspan></text>
<text x="40" y="152" class="serif acc" font-size="24" textLength="244" lengthAdjust="spacing">aadycm05@gmail.com</text>
<path class="ul" pathLength="1" d="M40 164 H284" stroke="{p['accent']}" stroke-width="1.4"/>
"""
    return svg(W, h, body, css, p, 'Contact: aadycm05@gmail.com')


def build(name, out):
    p = PALETTES[name]
    os.makedirs(out, exist_ok=True)
    files = {
        'hero.svg': hero_fourier(p),
        'h-work.svg': header(p, '01', 'SELECTED WORK', 'Measured, not claimed.', 'FULL WRITE-UPS LIVE IN EACH REPO'),
        'h-work-light.svg': header(p, '01', 'SELECTED WORK', 'Measured, not claimed.', 'FULL WRITE-UPS LIVE IN EACH REPO', light=True),
        'card-hydronode.svg': hydronode(p),
        'card-semantic.svg': semantic(p),
        'card-papertrail.svg': papertrail(p),
        'card-agent.svg': agent(p),
        'h-research.svg': header(p, '02', 'RESEARCH', 'Questions I am working on.', 'PENN STATE · FALL 2026 – NOW'),
        'h-research-light.svg': header(p, '02', 'RESEARCH', 'Questions I am working on.', 'PENN STATE · FALL 2026 – NOW', light=True),
        'r-injection.svg': r_injection(p),
        'r-framing.svg': r_framing(p),
        'h-log.svg': header(p, '03', 'COMMIT LOG', 'Shipping, in public.', 'LAST 12 MONTHS'),
        'h-log-light.svg': header(p, '03', 'COMMIT LOG', 'Shipping, in public.', 'LAST 12 MONTHS', light=True),
        'heatmap.svg': heatmap(p),
        'h-skills.svg': header(p, '04', 'SKILLS', 'What I work with.', 'FROM MY RESUME AND REPOS'),
        'h-skills-light.svg': header(p, '04', 'SKILLS', 'What I work with.', 'FROM MY RESUME AND REPOS', light=True),
        'skills.svg': skills(p),
        'closer.svg': closer(p),
    }
    for f, s in files.items():
        open(os.path.join(out, f), 'w', encoding='utf8').write(s)
    return out, {f: len(s) for f, s in files.items()}


if __name__ == '__main__':
    ver = sys.argv[1] if len(sys.argv) > 1 else '1'
    root = os.path.dirname(HERE)
    out = os.path.join(root, 'assets')
    for f in os.listdir(out) if os.path.isdir(out) else []:
        if f.endswith('.svg'):
            os.remove(os.path.join(out, f))
    _, sizes = build('sodium', out)
    tpl = open(os.path.join(HERE, 'README.template.md'), encoding='utf8').read()
    md = re.sub(r'A/([a-z-]+\.svg)', lambda m: f'assets/{m.group(1)}?v={ver}', tpl.replace('A/HERO', 'A/hero.svg'))
    open(os.path.join(root, 'README.md'), 'w', encoding='utf8', newline='\n').write(md)
    print('assets', len(sizes), 'version', ver)
