"""Profile banner: a haplotype mosaic (the Li-Stephens picture behind phasing and imputation)."""
import random
import sys

W, H = 1280, 300
THEMES = {
    "dark": dict(bg0="#0d1117", bg1="#161b22", fg="#e6edf3", sub="#8b949e", accent="#58a6ff",
                 pal=["#58a6ff", "#3fb950", "#d29922", "#f778ba", "#a371f7"], track="#21262d"),
    "light": dict(bg0="#ffffff", bg1="#f6f8fa", fg="#1f2328", sub="#59636e", accent="#0969da",
                  pal=["#0969da", "#1a7f37", "#9a6700", "#bf3989", "#8250df"], track="#eaeef2"),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


T = 9  # seconds per loop: typed sites only -> haplotypes fill in left to right -> hold -> fade


def k(*v):
    return ";".join(f"{x:.4f}" if isinstance(x, float) else str(x) for x in v)


def mosaic(t, rng):
    x0, x1, y0, rows, h, gap = 640, 1230, 52, 14, 9, 5
    tracks, fills, heads, ticks, clips = [], [], [], [], []
    for r in range(rows):
        y = y0 + r * (h + gap)
        tracks.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="4.5" fill="{t["track"]}"/>')
        x, c = x0, rng.randrange(5)
        segs = []
        while x < x1:
            w = min(rng.randint(40, 190), x1 - x)
            segs.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t["pal"][c]}" opacity="0.85"/>')
            x += w
            c = (c + rng.randint(1, 4)) % 5
        a = 0.10 + 0.014 * r      # this row starts filling
        b = a + 0.30              # and is full
        kt = k(0, a, b, 0.97, 1)
        spl = "0 0 1 1;.45 .05 .25 1;0 0 1 1;0 0 1 1"
        clips.append(f'<clipPath id="r{r}"><rect x="{x0}" y="{y - 3}" width="0" height="{h + 6}">'
                     f'<animate attributeName="width" values="{k(0, 0, x1 - x0, x1 - x0, 0)}" keyTimes="{kt}" '
                     f'calcMode="spline" keySplines="{spl}" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>')
        fills.append(f'<g clip-path="url(#r{r})">{"".join(segs)}</g>')
        heads.append(f'<rect x="{x0}" y="{y - 2}" width="3" height="{h + 4}" rx="1.5" fill="{t["fg"]}" opacity="0">'
                     f'<animate attributeName="x" values="{k(x0, x0, x1 - 3, x1 - 3, x0)}" keyTimes="{kt}" '
                     f'calcMode="spline" keySplines="{spl}" dur="{T}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{k(0, a, a + 0.01, b - 0.01, b, 1)}" '
                     f'dur="{T}s" repeatCount="indefinite"/></rect>')
        for _ in range(rng.randint(2, 4)):
            tx = rng.randint(x0 + 10, x1 - 10)
            ticks.append(f'<rect x="{tx}" y="{y - 2}" width="2" height="{h + 4}" fill="{t["fg"]}" opacity="0.55"/>')
    fade = (f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="{k(0, 0.86, 0.94, 0.995, 1)}" '
            f'dur="{T}s" repeatCount="indefinite"/>')
    body = (f'{"".join(tracks)}<g>{fade}{"".join(fills)}</g>{"".join(heads)}{"".join(ticks)}')
    return "".join(clips), body


def caption(t, text, show):
    """Bottom-right caption visible during the keyTimes window `show` = (start, end)."""
    s, e = show
    return (f'<text x="1230" y="276" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["sub"]}" opacity="0">{text}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{k(0, s, s + 0.03, e - 0.03, e, 1)}" '
            f'dur="{T}s" repeatCount="indefinite"/></text>')


def banner(name):
    t = THEMES[name]
    rng = random.Random(22)  # chr22, same mosaic in both themes
    clip, bars = mosaic(t, rng)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Adriano De Marino, bioinformatics scientist">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>
{clip}
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<text x="56" y="112" font-family="{FONT}" font-size="50" font-weight="700" fill="{t["fg"]}">Adriano De Marino</text>
<text x="58" y="152" font-family="{FONT}" font-size="22" fill="{t["sub"]}">Bioinformatics scientist · PhD · Los Angeles</text>
<text x="58" y="206" font-family="{MONO}" font-size="17" fill="{t["accent"]}">phasing · imputation · population genetics</text>
<text x="58" y="234" font-family="{MONO}" font-size="17" fill="{t["accent"]}">Rust · Python · AWS</text>
<rect x="258" y="220" width="9" height="18" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect>
{bars}
{caption(t, "typed sites only", (0.0, 0.12))}
{caption(t, "phasing + imputing against the reference panel…", (0.12, 0.40))}
{caption(t, "each row a haplotype, copied in pieces from a reference panel", (0.40, 0.92))}
</svg>
'''


if __name__ == "__main__":
    out = sys.argv[1]
    for name in THEMES:
        with open(f"{out}/banner_{name}.svg", "w") as f:
            f.write(banner(name))
