"""Profile banner: a new haplotype built from pieces of a reference panel (the copying model behind
phasing and imputation). SMIL animation, which GitHub plays in a README.
usage: make_banner.py OUT_DIR"""
import random
import sys

W, H = 1280, 320
T = 14.0                                  # seconds per loop
NCOL, NROW = 24, 8                        # sites, panel haplotypes
CW, STEP = 19, 23                         # cell width, column step
X0 = 654                                  # first column
TY = 58                                   # target row
PY, PSTEP, CH = 120, 21, 15               # panel: first row, row step, cell height
TYPED = set(range(1, NCOL, 3))            # sites the "array" read
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

THEMES = {
    "dark": dict(bg0="#0d1117", bg1="#161b22", fg="#e6edf3", sub="#8b949e", accent="#58a6ff",
                 ref="#21262d", alt="#6e7681", empty="#30363d",
                 seg=["#58a6ff", "#3fb950", "#d29922", "#f778ba", "#a371f7"]),
    "light": dict(bg0="#ffffff", bg1="#f6f8fa", fg="#1f2328", sub="#59636e", accent="#0969da",
                  ref="#e6eaef", alt="#8c959f", empty="#d0d7de",
                  seg=["#0969da", "#1a7f37", "#9a6700", "#bf3989", "#8250df"]),
}

# Toy data, the same in both themes: panel alleles, a copying path, the target it makes.
rng = random.Random(22)
PANEL = [[int(rng.random() < 0.38) for _ in range(NCOL)] for _ in range(NROW)]
BREAKS = [0, 5, 10, 15, 20, NCOL]
ROWS = [2, 6, 0, 4, 7]
SEGS = list(zip(BREAKS, BREAKS[1:], ROWS))
TARGET = [PANEL[r][c] for a, b, r in SEGS for c in range(a, b)]
SEG_T0 = [1.6 + 2.1 * k for k in range(len(SEGS))]      # when each piece is picked
END = 13.0                                               # everything fades out


def kt(*ts):
    return ";".join(f"{min(max(t / T, 0), 1):.4f}" for t in ts)


def show(on, off, fade=0.3):
    """Opacity 0 -> 1 at `on`, back to 0 at `off`, every loop."""
    return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
            f'keyTimes="0;{kt(on, on + fade, off, off + fade)};1" dur="{T}s" repeatCount="indefinite"/>')


def cx(c):
    return X0 + c * STEP


def py(r):
    return PY + r * PSTEP


def cell(x, y, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{CW}" height="{h}" rx="3" fill="{fill}"{extra}/>'


def mosaic(t):
    out = []
    out.append(f'<text x="{X0 - 14}" y="{TY + 14}" text-anchor="end" font-family="{FONT}" font-size="13" '
               f'font-weight="600" fill="{t["fg"]}">new haplotype</text>')
    out.append(f'<text x="{X0 - 14}" y="{PY + 11}" text-anchor="end" font-family="{FONT}" font-size="13" '
               f'font-weight="600" fill="{t["fg"]}">reference</text>')
    out.append(f'<text x="{X0 - 14}" y="{PY + 27}" text-anchor="end" font-family="{FONT}" font-size="13" '
               f'font-weight="600" fill="{t["fg"]}">panel</text>')
    for r in range(NROW):
        for c in range(NCOL):
            out.append(cell(cx(c), py(r), CH, t["alt"] if PANEL[r][c] else t["ref"]))
    for c in range(NCOL):
        out.append(f'<rect x="{cx(c) + 0.5}" y="{TY + 0.5}" width="{CW - 1}" height="19" rx="3" fill="none" '
                   f'stroke="{t["empty"]}" stroke-dasharray="3 2"/>')
        if c in TYPED:
            out.append(cell(cx(c), TY, 20, t["alt"] if TARGET[c] else t["ref"]))
            out.append(f'<circle cx="{cx(c) + CW / 2}" cy="{TY - 8}" r="2" fill="{t["sub"]}"/>')
    for k, (a, b, r) in enumerate(SEGS):
        col = t["seg"][k]
        t0 = SEG_T0[k]
        x, w = cx(a) - 3, cx(b - 1) + CW - cx(a) + 6
        out.append(f'<rect x="{x}" y="{py(r) - 3}" width="{w}" height="{CH + 6}" rx="5" fill="none" '
                   f'stroke="{col}" stroke-width="2" opacity="0">{show(t0, END)}</rect>')
        tint = "".join(cell(cx(c), py(r), CH, col, ' opacity="0.95"' if PANEL[r][c] else ' opacity="0.35"')
                       for c in range(a, b))
        out.append(f'<g opacity="0">{show(t0 + 0.2, END)}{tint}</g>')
        dy = py(r) - TY
        fly = "".join(cell(cx(c), TY, 20, col, ' opacity="1"' if TARGET[c] else ' opacity="0.4"')
                      for c in range(a, b))
        move = (f'<animateTransform attributeName="transform" type="translate" '
                f'values="0,{dy};0,{dy};0,0;0,0" keyTimes="0;{kt(t0 + 0.5, t0 + 1.4)};1" calcMode="spline" '
                f'keySplines="0 0 1 1;.4 0 .2 1;0 0 1 1" dur="{T}s" repeatCount="indefinite"/>')
        out.append(f'<g opacity="0">{move}{show(t0 + 0.5, END, 0.15)}{fly}</g>')
        out.append(f'<rect x="{cx(a)}" y="{TY + 25}" width="{cx(b - 1) + CW - cx(a)}" height="3" rx="1.5" '
                   f'fill="{col}" opacity="0">{show(t0 + 1.3, END)}</rect>')
    return "".join(out)


def caption(t, text, on, off):
    return (f'<text x="{cx(NCOL - 1) + CW}" y="{H - 18}" text-anchor="end" font-family="{MONO}" font-size="12" '
            f'fill="{t["sub"]}" opacity="0">{text}{show(on, off, 0.25)}</text>')


def banner(name):
    t = THEMES[name]
    last = SEG_T0[-1] + 1.5
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Adriano De Marino, bioinformatics scientist. Animation: a new haplotype is built from pieces of a reference panel.">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<text x="56" y="124" font-family="{FONT}" font-size="50" font-weight="700" fill="{t["fg"]}">Adriano De Marino</text>
<text x="58" y="164" font-family="{FONT}" font-size="22" fill="{t["sub"]}">Bioinformatics scientist · PhD · Los Angeles</text>
<text x="58" y="218" font-family="{MONO}" font-size="17" fill="{t["accent"]}">phasing · imputation · population genetics</text>
<text x="58" y="246" font-family="{MONO}" font-size="17" fill="{t["accent"]}">Rust · Python · AWS</text>
<rect x="258" y="232" width="9" height="18" fill="{t["accent"]}"><animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" repeatCount="indefinite"/></rect>
{mosaic(t)}
{caption(t, "a chip reads a few sites", 0.0, SEG_T0[0])}
{caption(t, "the rest is copied, piece by piece, from people in the panel", SEG_T0[0] + 0.3, last)}
{caption(t, "one new haplotype, five pieces, five people", last + 0.3, END)}
</svg>
'''


if __name__ == "__main__":
    for name in THEMES:
        with open(f"{sys.argv[1]}/banner_{name}.svg", "w") as f:
            f.write(banner(name))
