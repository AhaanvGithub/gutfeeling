"""Write the README pipeline diagram as light and dark SVGs (GitHub picks one per theme with <picture>)."""
import sys
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

THEMES = {
    "light": dict(bg="#ffffff", fill="#f6f8fa", edge="#d0d7de", text="#1f2328", sub="#59636e", line="#8c959f",
                  accent="#0969da", accent_fill="#ddf4ff", llm="#8250df", llm_fill="#fbefff", group="#fbfcfd"),
    "dark": dict(bg="#0d1117", fill="#161b22", edge="#30363d", text="#e6edf3", sub="#9198a1", line="#6e7681",
                 accent="#4493f8", accent_fill="#0d2347", llm="#ab7df8", llm_fill="#24123f", group="#10151c"),
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
W, H, MID = 1260, 450, 232


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(theme):
    t = THEMES[theme]
    el = []

    def rect(x, y, w, h, fill, edge, r=12, dash=None, sw=1.4):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{edge}" stroke-width="{sw}"{d}/>')

    def text(x, y, s, size, color, weight=400, spacing=0):
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        el.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="middle" dominant-baseline="middle"{ls}>{esc(s)}</text>')

    def box(cx, cy, w, h, title, subs, kind="plain", ts=22, ss=16.5):
        fill, edge = t["fill"], t["edge"]
        if kind == "accent":
            fill, edge = t["accent_fill"], t["accent"]
        elif kind == "llm":
            fill, edge = t["llm_fill"], t["llm"]
        rect(cx - w / 2, cy - h / 2, w, h, fill, edge)
        lines = 1 + len(subs)
        gap = ss * 1.45
        top = cy - (ts * 0.6 + gap * (lines - 1)) / 2 + ts * 0.3
        text(cx, top, title, ts, t["text"], 600)
        for i, s in enumerate(subs):
            text(cx, top + ts * 0.95 + gap * i + 4, s, ss, t["sub"])

    def arrow(x0, y0, x1, y1):
        el.append(f'<line x1="{x0}" y1="{y0}" x2="{x1 - 9}" y2="{y1}" stroke="{t["line"]}" stroke-width="1.8"/>')
        el.append(f'<path d="M{x1},{y1} l-10,-5.5 v11 z" fill="{t["line"]}"/>')

    def stage(cx, n, label):
        text(cx, 30, f"{n}  {label}", 15, t["sub"], 600, 1.6)

    bw, bh = 192, 132
    xs = [104, 318, 532]
    for cx, n, lab in zip(xs, (1, 2, 3), ("SNIP", "FIELD", "CALL")):
        stage(cx, n, lab)
    box(xs[0], MID, bw, bh, "Hotkey", ["over any slide viewer", "true-colour capture"])
    box(xs[1], MID, bw, bh, "Field", ["scale bar read by OCR", "sized to 448 µm"])
    box(xs[2], MID, bw, bh, "Ensemble", ["ConvNeXt-B + MUSK", "calibrated call, ~2 s"], kind="accent")
    arrow(xs[0] + bw / 2, MID, xs[1] - bw / 2, MID)
    arrow(xs[1] + bw / 2, MID, xs[2] - bw / 2, MID)

    gx, gw, gh = 770, 214, 76
    ys = [104, 189, 274, 359]
    gtop, gbot = ys[0] - gh / 2 - 16, ys[-1] + gh / 2 + 16
    rect(gx - gw / 2 - 16, gtop, gw + 32, gbot - gtop, t["group"], t["edge"], r=16, dash="5 5", sw=1.2)
    stage(gx, 4, "EVIDENCE")
    items = [("Evidence map", "occlusion, 16 → 128 grid"), ("Crypts", "U-Net, measured in µm"),
             ("Similar cases", "454 fields, other labs"), ("Unfamiliar check", "distance to training set")]
    for (title, sub), y in zip(items, ys):
        box(gx, y, gw, gh, title, [sub], ts=18.5, ss=15)
    arrow(xs[2] + bw / 2, MID, gx - gw / 2 - 16, MID)

    lx, rx, rw = 1010, 1190, 124
    stage(lx, 5, "EXPLAIN"); stage(rx, 6, "SHOW")
    box(lx, MID, bw, bh, "Literature", ["Gemma-4 31B + RAG", "cited, never overrules"], kind="llm")
    arrow(gx + gw / 2 + 16, MID, lx - bw / 2, MID)
    # the results panel spans the evidence column, so the second arrow runs straight under the literature box
    rect(rx - rw / 2, gtop, rw, gbot - gtop, t["fill"], t["edge"], r=14)
    text(rx, gtop + 46, "Results", 22, t["text"], 600)
    text(rx, gtop + 74, "panel", 22, t["text"], 600)
    for i, s in enumerate(["call", "evidence map", "crypts", "similar cases", "reading"]):
        text(rx, MID - 30 + i * 33, s, 15.5, t["sub"])
    arrow(lx + bw / 2, MID, rx - rw / 2, MID)
    arrow(gx + gw / 2 + 16, ys[-1], rx - rw / 2, ys[-1])

    body = "\n  ".join(el)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n  <rect width="{W}" height="{H}" fill="{t["bg"]}"/>\n  {body}\n</svg>\n')


for th in THEMES:
    (out / f"pipeline_{th}.svg").write_text(svg(th), encoding="utf-8")
print("ok")
