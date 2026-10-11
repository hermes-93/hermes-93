#!/usr/bin/env python3
"""Generates every SVG in ../assets.

Edit the text in the CONTENT section and run:  python3 tools/gen.py
Fonts are embedded as base64 so GitHub renders them (an <img> SVG
can't load anything external).
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "assets"

# ── palette ───────────────────────────────────────────────────────────
BG_CENTER = "#3a3576"
BG_MID = "#27244f"
BG_EDGE = "#141327"
PANEL = "#111117"
LINE = "#3b3870"      # card borders, orbit
TITLE_A = "#e4dcfa"   # title gradient: lavender → violet → sky
TITLE_B = "#b2a2ef"
TITLE_C = "#8ec8f5"
TEXT = "#cdc7ea"
SUB = "#8f8ab8"
DIM = "#646092"
GREEN = "#7fd6a0"
ACCENT = "#a99cf0"


def font_face():
    def b64(w):
        return base64.b64encode((FONTS / f"plex-{w}.woff2").read_bytes()).decode()
    return (
        f"@font-face{{font-family:'Plex';font-weight:400;src:url(data:font/woff2;base64,{b64(400)}) format('woff2')}}"
        f"@font-face{{font-family:'Plex';font-weight:600;src:url(data:font/woff2;base64,{b64(600)}) format('woff2')}}"
    )


BASE_CSS = f"""
{{FONT}}
text {{ font-family:'Plex','IBM Plex Mono','DejaVu Sans Mono',monospace; fill:{TEXT}; }}
.sub  {{ fill:{SUB}; }}
.dim  {{ fill:{DIM}; }}
.grn  {{ fill:{GREEN}; }}
.acc  {{ fill:{ACCENT}; }}
.b    {{ font-weight:600; }}
.pulse {{ animation:pulse 2.4s ease-in-out infinite; }}
@keyframes pulse {{ 50% {{ opacity:.35 }} }}
.cur  {{ animation:blink 1.05s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity:0 }} }}
.roll {{ animation:roll 9s linear infinite; }}
@keyframes roll {{ from {{ transform:translateY(-80px) }} to {{ transform:translateY(900px) }} }}
.flick {{ animation:flick 7s steps(1) infinite; }}
@keyframes flick {{ 0%,94%,100% {{ opacity:1 }} 95% {{ opacity:.6 }} 96% {{ opacity:1 }} 97% {{ opacity:.75 }} }}
.in   {{ opacity:0; animation:in .35s ease-out forwards; }}
@keyframes in {{ to {{ opacity:1 }} }}
.drift {{ animation:drift 60s linear infinite; transform-origin:center; transform-box:fill-box; }}
@keyframes drift {{ to {{ transform:rotate(360deg) }} }}
"""


def defs(w, h, extra_css=""):
    return f"""<defs>
  <radialGradient id="bg" cx="50%" cy="42%" r="75%">
    <stop offset="0" stop-color="{BG_CENTER}"/><stop offset=".55" stop-color="{BG_MID}"/><stop offset="1" stop-color="{BG_EDGE}"/>
  </radialGradient>
  <linearGradient id="title" x1="0" x2="1">
    <stop offset="0" stop-color="{TITLE_A}"/><stop offset=".55" stop-color="{TITLE_B}"/><stop offset="1" stop-color="{TITLE_C}"/>
  </linearGradient>
  <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>
  <pattern id="dith" width="2" height="2" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill="{SUB}"/><rect x="1" y="1" width="1" height="1" fill="{SUB}"/></pattern>
  <pattern id="dith2" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="1" height="1" fill="{SUB}"/><rect x="2" y="2" width="1" height="1" fill="{SUB}"/></pattern>
  <filter id="noise" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .07 0"/>
  </filter>
  <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-20%" y="-60%" width="140%" height="220%">
    <feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity=".55"/>
  </filter>
  <style>{(BASE_CSS + extra_css).replace("{FONT}", font_face())}</style>
</defs>"""


def backdrop(w, h, seed=0):
    """Indigo field + orbit ring + faint constellation, like the reference site."""
    cx, cy, r = w / 2, h / 2 + 20, min(w, h) * 0.62
    pts = [(cx - r * .25, cy - r * .62), (cx + r * .05, cy - r * .40), (cx + r * .60, cy - r * .08),
           (cx + r * .30, cy + r * .55), (cx - r * .45, cy + r * .35), (cx - r * .70, cy - r * .05)]
    pts = pts[seed % 6:] + pts[:seed % 6]
    lines = "".join(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>'
                    for a, b in zip(pts, pts[1:]))
    nodes = "".join(f'<rect x="{p[0]-4:.0f}" y="{p[1]-4:.0f}" width="8" height="8" fill="none"/>' for p in pts)
    return f"""<rect width="{w}" height="{h}" fill="url(#bg)"/>
<g class="drift" stroke="{LINE}" stroke-width="1.2" fill="none" opacity=".55">
  <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}"/>
  <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r*.97:.0f}" stroke-dasharray="2 9" opacity=".6"/>
</g>
<g stroke="{SUB}" stroke-width="1" opacity=".22">{lines}{nodes}</g>"""


def overlay(w, h):
    return f"""<rect width="{w}" height="{h}" filter="url(#noise)"/>
<rect width="{w}" height="{h}" fill="url(#scan)"/>
<rect class="roll" width="{w}" height="46" fill="#ffffff" opacity=".035"/>"""


def panel(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}" opacity=".93" filter="url(#shadow)"/>'


def brackets(x, y, w, h, s=8):
    c = f'stroke="{DIM}" stroke-width="1" fill="none"'
    return (f'<path d="M{x+s} {y} H{x} V{y+s*2}" {c}/><path d="M{x+w-s} {y} H{x+w} V{y+s*2}" {c}/>'
            f'<path d="M{x+s} {y+h} H{x} V{y+h-s*2}" {c}/><path d="M{x+w-s} {y+h} H{x+w} V{y+h-s*2}" {c}/>')


def title(cx, y, size=56):
    return (f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="{size}" class="b flick" '
            f'fill="url(#title)" style="fill:url(#title)" filter="url(#glow)" letter-spacing="1">hermes-93</text>')


def subtitle(cx, y):
    return (f'<text x="{cx}" y="{y}" text-anchor="middle" font-size="13" class="sub" letter-spacing="6">'
            f'DevOps  |  Software Engineer</text>')


def dither_glyph(x, y):
    """▒║▒   ▒║▒ drawn with real dither tiles (the font has no block glyphs)."""
    def one(ox):
        return (f'<rect x="{ox}" y="{y}" width="16" height="22" fill="url(#dith)"/>'
                f'<rect x="{ox+19}" y="{y}" width="2" height="22" fill="{SUB}"/><rect x="{ox+23}" y="{y}" width="2" height="22" fill="{SUB}"/>'
                f'<rect x="{ox+28}" y="{y}" width="16" height="22" fill="url(#dith2)"/>')
    return f'<g opacity=".8">{one(x)}{one(x+112)}</g>'


def svg(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{defs(w, h, css)}{body}</svg>')


# ── CONTENT ───────────────────────────────────────────────────────────
CARDS = [
    ("01", "Stack",      "kubectl get skills"),
    ("02", "Projects",   "ls ~/src"),
    ("03", "Experience", "git log --graph"),
    ("04", "Pipeline",   "how I ship"),
    ("05", "Signal",     "github stats"),
    ("06", "Contact",    "whoami &amp; links"),
]

SKILLS = [  # name, ready, kind, age
    ("go",            "1/1", "lang",    "core"),
    ("python",        "1/1", "lang",    "5y"),
    ("bash",          "1/1", "lang",    "7y"),
    ("linux",         "1/1", "os",      "7y"),
    ("kubernetes",    "1/1", "orchestr","5y"),
    ("docker",        "1/1", "runtime", "5y"),
    ("terraform",     "1/1", "iac",     "4y"),
    ("ansible",       "1/1", "iac",     "4y"),
    ("prometheus",    "2/2", "observe", "5y"),
    ("grafana",       "1/1", "observe", "5y"),
    ("gitlab-ci",     "1/1", "ci/cd",   "4y"),
    ("argocd",        "1/1", "gitops",  "2y"),
]

CAREER = [  # hash, refs, message  (newest first) — edit order/dates to taste
    ("9f3a1c4", "HEAD -> main", "CTO @ TestudoScan — Go LLM security gateway"),
    ("7b21e0d", "",             "A2kod / Mind Software (Mobiti) — platform &amp; hypervisor tooling in Go"),
    ("5c90a8f", "",             "Avito — SRE / platform engineering"),
    ("41d7e22", "",             "MTS — infrastructure &amp; support engineering"),
    ("2e8b6f1", "",             "Sberbank — infrastructure &amp; support engineering"),
    ("0a1c3b9", "tag: v0.1",    "2GIS — Linux System Administrator (2019)"),
]


# ── builders ──────────────────────────────────────────────────────────
def hero():
    W, H = 900, 690
    px, py, pw, ph = 70, 40, 760, 610
    cx = W // 2
    cards = []
    cw, chh, gap = 220, 96, 16
    gx = cx - (cw * 3 + gap * 2) // 2
    for i, (n, name, hint) in enumerate(CARDS):
        x = gx + (i % 3) * (cw + gap)
        y = py + 250 + (i // 3) * (chh + gap)
        d = f"{0.6 + i*0.12:.2f}s"
        cards.append(
            f'<g class="in" style="animation-delay:{d}">'
            f'<rect x="{x}" y="{y}" width="{cw}" height="{chh}" fill="none" stroke="{LINE}"/>'
            f'<text x="{x+cw/2}" y="{y+26}" text-anchor="middle" font-size="11" class="acc" letter-spacing="2">{n}</text>'
            f'<text x="{x+cw/2}" y="{y+54}" text-anchor="middle" font-size="19" class="b" letter-spacing="4" filter="url(#soft)">{name}</text>'
            f'<text x="{x+cw/2}" y="{y+76}" text-anchor="middle" font-size="10.5" class="sub" letter-spacing="1">{hint}</text>'
            f'</g>')
    body = f"""{backdrop(W, H)}
{panel(px, py, pw, ph)}
{brackets(px+200, py+40, pw-400, 476)}
<text x="{cx}" y="{py+70}" text-anchor="middle" font-size="12" class="sub">hermes-93@github:~$ ls<tspan class="cur acc">█</tspan></text>
{title(cx, py+132)}
{subtitle(cx, py+164)}
<text x="{cx}" y="{py+192}" text-anchor="middle" font-size="12" class="sub" letter-spacing="1">linux · kubernetes · terraform · ci/cd · go · python</text>
<text x="{cx}" y="{py+218}" text-anchor="middle" font-size="12" class="sub"><tspan class="acc pulse">●</tspan> all systems operational</text>
{''.join(cards)}
<line x1="{px}" y1="{py+ph-80}" x2="{px+pw}" y2="{py+ph-80}" stroke="{LINE}"/>
<text x="{cx}" y="{py+ph-44}" text-anchor="middle" font-size="13" class="sub" letter-spacing="6">You are connected.</text>
<text x="{cx}" y="{py+ph-20}" text-anchor="middle" font-size="12" class="dim" letter-spacing="4">tbilisi, ge  ·  utc+4  ·  en / ru</text>
{overlay(W, H)}"""
    return svg(W, H, body)


def motto():
    W, H = 900, 600
    cx = W // 2
    steps = [
        ('$ git push origin main', TEXT, 1.6),
        ('  ci › lint ✓   test ✓   build ✓   scan ✓', GREEN, 2.3),
        ('  image signed   sha256:9f3a…c41e', SUB, 3.0),
        ('$ kubectl rollout status deploy/api', TEXT, 3.7),
        ('  deployment "api" successfully rolled out', GREEN, 4.6),
    ]
    term = "".join(
        f'<text x="100" y="{432 + i*22}" font-size="13" fill="{c}" style="fill:{c};animation-delay:{d}s" class="in" xml:space="preserve">{t}</text>'
        for i, (t, c, d) in enumerate(steps))
    body = f"""{backdrop(W, H, seed=2)}
{panel(70, 40, 760, 330)}
{title(cx, 128, 64)}
{subtitle(cx, 162)}
<g font-size="20" letter-spacing="5" filter="url(#soft)">
  <text x="{cx-185}" y="218" class="in" style="animation-delay:.2s">Make it reproducible.</text>
  <text x="{cx-135}" y="250" class="in" style="animation-delay:.8s">Make it observable.</text>
  <text x="{cx-60}"  y="282" class="in" style="animation-delay:1.4s">Make it boring.</text>
</g>
{dither_glyph(cx-78, 300)}
<text x="{cx}" y="350" text-anchor="middle" font-size="11" class="sub" letter-spacing="5">[uptime: 99.98%]</text>
{panel(70, 392, 760, 168)}
{term}
<text x="100" y="{432 + 5*22}" font-size="13" class="in" style="animation-delay:5.2s">$ <tspan class="cur acc">█</tspan></text>
{overlay(W, H)}"""
    return svg(W, H, body)


def terminal(name, cmd, header, rows, height=None):
    """Generic panel: prompt + table rows. rows = list of (text, css_class)."""
    W = 900
    H = height or 196 + len(rows) * 22
    lines = []
    for i, (t, cls) in enumerate(rows):
        lines.append(f'<text x="100" y="{150 + i*22}" font-size="13" class="{cls} in" '
                     f'style="animation-delay:{0.5 + i*0.12:.2f}s" xml:space="preserve">{t}</text>')
    body = f"""{backdrop(W, H, seed=len(rows))}
{panel(70, 30, 760, H - 60)}
<text x="100" y="68" font-size="11" class="acc" letter-spacing="3">{name}</text>
<text x="100" y="98" font-size="13" xml:space="preserve"><tspan class="sub">hermes-93@github:~$</tspan> {cmd}</text>
<text x="100" y="126" font-size="13" class="dim" xml:space="preserve">{header}</text>
{''.join(lines)}
<text x="100" y="{150 + len(rows)*22 + 10}" font-size="13" class="sub">hermes-93@github:~$ <tspan class="cur acc">█</tspan></text>
{overlay(W, H)}"""
    return svg(W, H, body)


def skills():
    # colour only the STATUS column
    rows = [(f'{n:<16}{r:<8}<tspan class="grn">Running</tspan>    {k:<11}{a}', "") for n, r, k, a in SKILLS]
    return terminal("01 // STACK", "kubectl get skills -n hermes-93",
                    f"{'NAME':<16}{'READY':<8}{'STATUS':<11}{'KIND':<11}AGE", rows)


def experience():
    rows = []
    for i, (h, ref, msg) in enumerate(CAREER):
        refs = f' <tspan class="acc">({ref})</tspan>' if ref else ""
        rows.append((f'<tspan class="acc">*</tspan> <tspan class="dim">{h}</tspan>{refs} {msg}', ""))
        if i < len(CAREER) - 1:
            rows.append(('<tspan class="acc">|</tspan>', ""))
    return terminal("03 // EXPERIENCE", "git log --graph --oneline career", "", rows)


def pipeline():
    W, H = 900, 250
    stages = ["commit", "lint", "test", "build", "scan", "sign", "deploy", "observe"]
    n = len(stages)
    x0, x1, y = 120, 780, 140
    step = (x1 - x0) / (n - 1)
    dots, labels = [], []
    for i, s in enumerate(stages):
        x = x0 + i * step
        d = f"{0.4 + i*0.35:.2f}s"
        dots.append(f'<rect x="{x-6:.0f}" y="{y-6}" width="12" height="12" fill="{PANEL}" stroke="{ACCENT}"/>'
                    f'<rect x="{x-3:.0f}" y="{y-3}" width="6" height="6" fill="{GREEN}" class="in" style="animation-delay:{d}"/>')
        labels.append(f'<text x="{x:.0f}" y="{y+32}" text-anchor="middle" font-size="11" class="sub" letter-spacing="1">{s}</text>')
    body = f"""{backdrop(W, H, seed=4)}
{panel(70, 30, 760, 190)}
<text x="100" y="68" font-size="11" class="acc" letter-spacing="3">04 // PIPELINE</text>
<text x="{x1}" y="68" text-anchor="end" font-size="11" class="dim" letter-spacing="2">gitops · signed images · zero-touch</text>
<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{LINE}" stroke-width="2"/>
<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 10" opacity=".7">
  <animate attributeName="stroke-dashoffset" from="160" to="0" dur="2.4s" repeatCount="indefinite"/>
</line>
{''.join(dots)}{''.join(labels)}
<text x="{W//2}" y="200" text-anchor="middle" font-size="12" class="sub" letter-spacing="4">if it isn't in git, it doesn't exist.</text>
{overlay(W, H)}"""
    return svg(W, H, body)


def footer():
    W, H = 900, 200
    cx = W // 2
    body = f"""{backdrop(W, H, seed=1)}
{panel(70, 24, 760, 100)}
<text x="{cx}" y="64" text-anchor="middle" font-size="13" class="sub" letter-spacing="6">You are connected.</text>
<text x="{cx}" y="94" text-anchor="middle" font-size="12" class="dim" letter-spacing="4">no pager went off while rendering this page</text>
<rect x="{cx-250}" y="146" width="500" height="24" fill="{PANEL}" opacity=".9"/>
<text x="{cx}" y="162" text-anchor="middle" font-size="11" class="sub" letter-spacing="3">© 2026 hermes-93  |  up since 2019  |  <tspan class="acc pulse">●</tspan> online</text>
{overlay(W, H)}"""
    return svg(W, H, body)


def section(n, name):
    """Thin section header strip: ⌈ 02 // PROJECTS ⌋."""
    W, H = 900, 64
    body = f"""<rect width="{W}" height="{H}" fill="url(#bg)"/>
{panel(70, 12, 760, 40)}
<text x="100" y="37" font-size="12" class="acc" letter-spacing="3">{n} //</text>
<text x="160" y="37" font-size="14" class="b" letter-spacing="5" filter="url(#soft)">{name}</text>
<text x="800" y="37" text-anchor="end" font-size="11" class="dim" letter-spacing="2">hermes-93</text>
<rect width="{W}" height="{H}" fill="url(#scan)"/>"""
    return svg(W, H, body)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "hero.svg": hero(),
        "motto.svg": motto(),
        "skills.svg": skills(),
        "experience.svg": experience(),
        "pipeline.svg": pipeline(),
        "footer.svg": footer(),
        "sec-projects.svg": section("02", "PROJECTS"),
        "sec-signal.svg": section("05", "SIGNAL"),
        "sec-contact.svg": section("06", "CONTACT"),
    }
    for name, data in files.items():
        (OUT / name).write_text(data, encoding="utf-8")
        print(f"{name:<18}{len(data)//1024:>4} KB")


if __name__ == "__main__":
    main()
