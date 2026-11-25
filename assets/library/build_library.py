#!/usr/bin/env python3
"""Builds the flat-style SVG asset library from the brand palette (original work, MIT with the repo code).
Flat-vector rules (borrowed from claude-drawing-skill's FlatVector principles, re-implemented in SVG):
  no outlines; one light from the upper left -> every solid splits into a LIT face and a SHADE face;
  each lifted object drops a short soft night-blue shadow (offset +6,+8); only palette colours and their tones.
Output: svg/<group>/<name>.svg (+ remotion/public/library/<name>.svg). Thumbnails/catalog: make_catalog.py"""
from pathlib import Path
import json, random
R = Path(__file__).resolve().parent; PUB = R.parents[1] / "remotion" / "public" / "library"
P = json.loads((R / "palette.json").read_text())
c = lambda k: P[k]
SH = '<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="6" dy="8" stdDeviation="5" flood-color="#05060A" flood-opacity="0.45"/></filter>'
def svg(w, h, body, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><defs>{SH}{defs}</defs>{body}</svg>'
A = {}

# ---------------- machines
A["machines/elevator_car"] = svg(320, 360, f'''<g filter="url(#sh)">
<rect x="20" y="30" width="260" height="310" rx="18" fill="{c('steel')}"/><rect x="150" y="30" width="130" height="310" rx="18" fill="{c('steelD')}"/>
<rect x="40" y="60" width="220" height="260" rx="10" fill="{c('ink3')}"/><rect x="40" y="60" width="110" height="260" fill="#2C3242"/>
<rect x="148" y="60" width="4" height="260" fill="{c('line')}"/>
<rect x="120" y="8" width="60" height="30" rx="6" fill="{c('steelD')}"/><rect x="146" y="0" width="8" height="14" fill="{c('paper')}"/>
<circle cx="250" cy="45" r="7" fill="{c('amber')}"/></g>''')
A["machines/counterweight"] = svg(160, 300, f'''<g filter="url(#sh)">
<rect x="20" y="20" width="120" height="270" rx="12" fill="{c('eng')}"/><rect x="80" y="20" width="60" height="270" rx="12" fill="{c('engD')}"/>
''' + "".join(f'<rect x="20" y="{40+i*36}" width="120" height="6" fill="#1E3B26" opacity="0.35"/>' for i in range(7)) + f'''
<rect x="70" y="0" width="20" height="28" rx="4" fill="{c('steelD')}"/></g>''')
spokes = "".join(f'<rect x="-6" y="-100" width="12" height="100" rx="6" fill="{c("steelD")}" transform="rotate({a})"/>' for a in range(0, 360, 60))
A["machines/traction_sheave"] = svg(260, 260, f'''<g transform="translate(130 130)" filter="url(#sh)">
<circle r="118" fill="{c('steel')}"/><path d="M0,-118 A118,118 0 0,1 0,118 Z" fill="{c('steelD')}"/>
''' + "".join(f'<circle r="{r}" fill="none" stroke="{c("ink3")}" stroke-width="5" opacity="0.6"/>' for r in (108, 96)) + f'''
<circle r="82" fill="{c('ink3')}"/>{spokes}<circle r="28" fill="{c('steel')}"/><circle r="10" fill="{c('ink')}"/></g>''')
A["machines/traction_motor"] = svg(360, 240, f'''<g filter="url(#sh)">
<rect x="20" y="60" width="200" height="150" rx="24" fill="{c('tech')}"/><rect x="20" y="135" width="200" height="75" rx="24" fill="{c('techD')}"/>
''' + "".join(f'<rect x="{40+i*30}" y="70" width="10" height="130" rx="5" fill="#1B6F8E" opacity="0.45"/>' for i in range(6)) + f'''
<rect x="220" y="110" width="40" height="40" fill="{c('steelD')}"/>
<g transform="translate(290 130)"><circle r="62" fill="{c('steel')}"/><path d="M0,-62 A62,62 0 0,1 0,62 Z" fill="{c('steelD')}"/><circle r="40" fill="{c('ink3')}"/><circle r="12" fill="{c('steel')}"/></g>
<rect x="10" y="205" width="300" height="20" rx="6" fill="{c('line')}"/><rect x="60" y="30" width="80" height="34" rx="8" fill="{c('amber')}"/></g>''')
A["machines/tower_crane"] = svg(360, 420, f'''<g filter="url(#sh)">
<rect x="150" y="60" width="34" height="350" fill="{c('amber')}"/><rect x="167" y="60" width="17" height="350" fill="{c('amberD')}"/>
''' + "".join(f'<path d="M150,{80+i*40} L184,{100+i*40}" stroke="{c("amberD")}" stroke-width="5"/>' for i in range(8)) + f'''
<rect x="20" y="40" width="330" height="26" fill="{c('amber')}"/><rect x="20" y="53" width="330" height="13" fill="{c('amberD')}"/>
<rect x="20" y="66" width="60" height="44" rx="4" fill="{c('steelD')}"/><rect x="150" y="10" width="34" height="34" fill="{c('steel')}"/>
<rect x="300" y="66" width="4" height="170" fill="{c('paperD')}"/><rect x="278" y="236" width="48" height="40" rx="6" fill="{c('steel')}"/>
<rect x="110" y="400" width="114" height="16" fill="{c('line')}"/></g>''')
A["machines/balance_scale"] = svg(400, 320, f'''<g filter="url(#sh)">
<path d="M200,90 L150,290 L250,290 Z" fill="{c('eng')}"/><path d="M200,90 L200,290 L250,290 Z" fill="{c('engD')}"/>
<rect x="30" y="80" width="340" height="18" rx="9" fill="{c('paper')}"/><rect x="200" y="80" width="170" height="18" rx="9" fill="{c('paperD')}"/>
<circle cx="200" cy="89" r="14" fill="{c('amber')}"/><rect x="120" y="290" width="160" height="18" rx="8" fill="{c('line')}"/></g>''')
teeth = "".join(f'<rect x="-14" y="-104" width="28" height="30" rx="5" fill="{c("amber")}" transform="rotate({a})"/>' for a in range(0, 360, 30))
A["machines/gear"] = svg(240, 240, f'<g transform="translate(120 120)" filter="url(#sh)">{teeth}<circle r="80" fill="{c("amber")}"/><path d="M0,-80 A80,80 0 0,1 0,80 Z" fill="{c("amberD")}"/><circle r="30" fill="{c("ink2")}"/></g>')
A["machines/brake_shoe"] = svg(200, 160, f'''<g filter="url(#sh)"><path d="M30,20 Q100,-10 170,20 L160,60 Q100,36 40,60 Z" fill="{c('red')}"/><path d="M100,6 Q140,8 170,20 L160,60 Q130,46 100,44 Z" fill="{c('redD')}"/>
<rect x="88" y="60" width="24" height="90" rx="6" fill="{c('steelD')}"/></g>''')

# ---------------- objects
rnd = random.Random(7); mods = ""
N = 21
for y in range(N):
    for x in range(N):
        finder = (x < 7 and y < 7) or (x > 13 and y < 7) or (x < 7 and y > 13)
        if not finder and rnd.random() < 0.48: mods += f'<rect x="{20+x*10}" y="{20+y*10}" width="10" height="10" fill="{c("ink")}"/>'
def finder(x, y):
    return f'<rect x="{x}" y="{y}" width="70" height="70" fill="{c("ink")}"/><rect x="{x+10}" y="{y+10}" width="50" height="50" fill="{c("paper")}"/><rect x="{x+20}" y="{y+20}" width="30" height="30" fill="{c("ink")}"/>'
A["objects/qr_generic"] = svg(250, 250, f'<g filter="url(#sh)"><rect width="250" height="250" rx="16" fill="{c("paper")}"/>{mods}{finder(20,20)}{finder(160,20)}{finder(20,160)}</g>'
                              '<!-- random modules: NOT a scannable code (finder squares only), safe to show -->')
A["objects/smartphone"] = svg(220, 400, f'''<g filter="url(#sh)"><rect x="10" y="10" width="200" height="380" rx="34" fill="{c('ink3')}"/><rect x="110" y="10" width="100" height="380" rx="34" fill="#1A1E28"/>
<rect x="24" y="40" width="172" height="320" rx="18" fill="{c('tech')}"/><rect x="24" y="200" width="172" height="160" rx="18" fill="{c('techD')}"/>
<rect x="80" y="22" width="60" height="10" rx="5" fill="{c('ink')}"/>
<path d="M60,120 L60,90 L90,90 M160,90 L130,90 M160,90 L160,120 M60,250 L60,280 L90,280 M160,250 L160,280 L130,280" stroke="{c('paper')}" stroke-width="8" fill="none" stroke-linecap="round"/>
<rect x="56" y="183" width="108" height="6" rx="3" fill="{c('amber')}"/></g>''')
A["objects/compact_disc"] = svg(260, 260, f'''<g transform="translate(130 130)" filter="url(#sh)"><circle r="120" fill="{c('steel')}"/>
<path d="M0,-120 A120,120 0 0,1 120,0 L0,0 Z" fill="{c('tech')}" opacity="0.55"/><path d="M0,120 A120,120 0 0,1 -120,0 L0,0 Z" fill="{c('philo')}" opacity="0.35"/>
<circle r="40" fill="{c('paperD')}"/><circle r="16" fill="{c('ink')}"/><path d="M-80,-40 L40,70" stroke="{c('ink')}" stroke-width="4" opacity="0.6"/><path d="M-30,-95 L90,-20" stroke="{c('ink')}" stroke-width="3" opacity="0.5"/></g>''')
A["objects/byte_block"] = svg(140, 140, f'<g filter="url(#sh)"><rect x="10" y="10" width="120" height="120" rx="16" fill="{c("tech")}"/><path d="M130,26 L130,114 Q130,130 114,130 L26,130 Z" fill="{c("techD")}"/><text x="70" y="86" font-family="monospace" font-size="40" font-weight="700" fill="{c("ink")}" text-anchor="middle">01</text></g>')
A["objects/magnifier"] = svg(240, 240, f'<g filter="url(#sh)"><rect x="140" y="140" width="30" height="100" rx="12" fill="{c("amberD")}" transform="rotate(-45 155 190)"/><circle cx="100" cy="100" r="80" fill="{c("amber")}"/><circle cx="100" cy="100" r="58" fill="{c("tech")}" opacity="0.5"/><path d="M60,80 A45,45 0 0,1 90,52" stroke="{c("paper")}" stroke-width="10" fill="none" stroke-linecap="round"/></g>')

# ---------------- characters (faceless, rounded, brand style)
def person(x, y, body, s=1.0, extra=""):
    return f'''<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="-118" r="30" fill="{body}"/>
<rect x="-36" y="-82" width="72" height="110" rx="30" fill="{body}"/><rect x="0" y="-82" width="36" height="110" rx="18" fill="#000" opacity="0.18"/>
<rect x="-30" y="20" width="24" height="70" rx="12" fill="{c('ink3')}"/><rect x="6" y="20" width="24" height="70" rx="12" fill="#1A1E28"/>{extra}</g>'''
A["characters/person"] = svg(160, 300, f'<g filter="url(#sh)">{person(80, 200, c("paper"))}</g>')
A["characters/person_phone"] = svg(180, 300, f'<g filter="url(#sh)">{person(80, 200, c("amber"), extra=f"<rect x=\"30\" y=\"-70\" width=\"34\" height=\"58\" rx=\"8\" fill=\"{c("ink3")}\"/><rect x=\"35\" y=\"-64\" width=\"24\" height=\"40\" rx=\"4\" fill=\"{c("tech")}\"/>")}</g>')
A["characters/office_crowd"] = svg(420, 300, '<g filter="url(#sh)">' + "".join(person(60 + i * 75, 210 + (i % 2) * 12, [c("paper"), c("amber"), c("paperD"), c("tech"), c("eng")][i], 0.85) for i in range(5)) + '</g>')

# ---------------- science / nature
A["nature/sun"] = svg(300, 300, f'<g transform="translate(150 150)">' + "".join(f'<circle r="{r}" fill="{c("amber")}" opacity="{o}"/>' for r, o in ((140, 0.10), (115, 0.16), (92, 0.25))) + f'<circle r="72" fill="{c("sunCore")}"/><path d="M0,-72 A72,72 0 0,1 0,72 Z" fill="{c("amber")}" opacity="0.35"/></g>')
A["nature/earth_flat"] = svg(320, 320, f'''<g transform="translate(160 160)" filter="url(#sh)"><circle r="140" fill="{c('ocean')}"/>
<path d="M-90,-80 Q-40,-120 10,-90 Q30,-50 -20,-30 Q-60,-10 -70,30 Q-110,0 -90,-80Z" fill="{c('eng')}"/><path d="M30,20 Q90,0 110,50 Q80,110 30,90 Q10,60 30,20Z" fill="{c('eng')}"/>
<path d="M0,-140 A140,140 0 0,1 0,140 A90,140 0 0,0 0,-140Z" fill="{c('ink')}" opacity="0.55"/><circle r="152" fill="none" stroke="{c('tech')}" stroke-width="10" opacity="0.35"/></g>''')
A["nature/air_molecule"] = svg(200, 160, f'<g filter="url(#sh)"><circle cx="70" cy="80" r="44" fill="{c("sci")}"/><circle cx="130" cy="80" r="44" fill="{c("sciD")}"/><circle cx="58" cy="66" r="12" fill="{c("paper")}" opacity="0.6"/></g>')
def wave(col, period, amp, n):
    pts = " ".join(f"{x},{80 + amp * __import__('math').sin(x / period * 6.283)}" for x in range(0, n, 4))
    return f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round"/>'
A["nature/wave_blue_short"] = svg(400, 160, wave(c("blueLight"), 50, 40, 400))
A["nature/wave_red_long"] = svg(400, 160, wave(c("red"), 160, 40, 400))
A["nature/eye"] = svg(240, 160, f'<g filter="url(#sh)"><path d="M10,80 Q120,-10 230,80 Q120,170 10,80Z" fill="{c("paper")}"/><circle cx="120" cy="80" r="44" fill="{c("tech")}"/><circle cx="120" cy="80" r="20" fill="{c("ink")}"/><circle cx="108" cy="68" r="8" fill="{c("paper")}"/></g>')
A["nature/cloud"] = svg(300, 160, f'<g filter="url(#sh)"><circle cx="90" cy="100" r="50" fill="{c("paper")}"/><circle cx="150" cy="75" r="62" fill="{c("paper")}"/><circle cx="215" cy="102" r="46" fill="{c("paper")}"/><rect x="60" y="100" width="190" height="48" rx="24" fill="{c("paper")}"/><rect x="60" y="122" width="190" height="26" rx="13" fill="{c("paperD")}"/></g>')
bld = ""
rb = random.Random(3)
for i, (x, w, h) in enumerate([(0, 120, 300), (110, 90, 420), (190, 140, 260), (320, 100, 520), (410, 130, 340), (530, 110, 460), (630, 150, 300)]):
    bld += f'<rect x="{x}" y="{600-h}" width="{w}" height="{h}" fill="{c("ink3")}"/><rect x="{x+w*0.6}" y="{600-h}" width="{w*0.4}" height="{h}" fill="#1A1E28"/>'
    for yy in range(600 - h + 24, 580, 40):
        for xx in range(int(x + 14), int(x + w - 20), 28):
            if rb.random() < 0.35: bld += f'<rect x="{xx}" y="{yy}" width="14" height="18" fill="{c("amber")}" opacity="{0.5 + rb.random() * 0.5:.2f}"/>'
A["nature/city_skyline"] = svg(780, 600, bld)

for k, v in A.items():
    p = R / "svg" / f"{k}.svg"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(v)
    PUB.mkdir(parents=True, exist_ok=True); (PUB / f"{k.split('/')[1]}.svg").write_text(v)
print(len(A), "svgs")
