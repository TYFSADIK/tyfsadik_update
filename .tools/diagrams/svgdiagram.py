#!/usr/bin/env python3
"""svgdiagram - dependency-free generator for the site's inline SVG diagrams.

Every diagram is drawn on a fixed 860-unit-wide canvas, the width of the
project page content column, so text renders at its true size on desktop
(labels 14px, detail lines 12.5px) instead of being shrunk to fit the way
auto-laid-out mermaid charts were. Layout is explicit: the author places
each box on a grid, so nothing can sprawl.

Diagram kinds:
  Flow      boxes on a grid, optional titled groups, orthogonal arrows
  Sequence  actors with lifelines and numbered messages
  Timeline  phases left to right with a status for each
  Stack     layered architecture, top to bottom
  Bars      horizontal bar chart for real, measured or cited numbers only

Colors and fonts match the hand-drawn figures already on the site (VLAN
diagram etc.): dark panels, Georgia, and one accent color per element.
All text is escaped; output is deterministic so rebuilds are byte-stable.
"""
import re
from html import escape

W = 860
FONT = "Georgia, 'Times New Roman', serif"
MONO = "'DepartureMono', ui-monospace, monospace"

COLORS = {
    "blue": "#5B93EF", "cyan": "#00d4ff", "green": "#00ff88", "orange": "#ff8800",
    "yellow": "#E6C947", "purple": "#b18cff", "red": "#ff5f5f", "grey": "#9FA2A4",
}
BG, PANEL, GROUP = "#161616", "#1f1f1f", "#1a1a1a"
TEXT, SUB, DIM = "#ECEBEB", "#B5B4B4", "#9FA2A4"

TITLE_PX, SUB_PX, SMALL_PX = 14, 12.5, 11.5


def text_width(s, px):
    """Approximate rendered width of Georgia text (average glyph ~0.53em,
    wide glyphs and capitals weighted more). Errs on the wide side."""
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!()[] ":
            w += 0.30
        elif ch in "mwMW@%":
            w += 0.90
        elif ch.isdigit():
            w += 0.56
        elif ch.isupper():
            w += 0.67
        else:
            w += 0.505
    return w * px


def wrap(s, px, maxw):
    """Greedy word wrap to maxw pixels. Explicit \\n forces a break. A single
    token wider than the box (kube-controller-manager) breaks after - or /."""
    lines = []
    for para in s.split("\n"):
        pieces = []  # (text, joiner) joiner is " " between words, "" inside a split token
        for wi, word in enumerate(para.split(" ")):
            parts = re.split(r"(?<=[-/])", word) if text_width(word, px) > maxw else [word]
            for pi, part in enumerate(parts):
                if part:
                    pieces.append((part, "" if pi else (" " if wi else "")))
        cur = ""
        for part, joiner in pieces:
            trial = cur + joiner + part if cur else part
            if cur and text_width(trial, px) > maxw:
                lines.append(cur)
                cur = part
            else:
                cur = trial
        lines.append(cur)
    return lines


def _t(x, y, s, px=TITLE_PX, fill=TEXT, anchor="middle", weight=None, family=FONT, italic=False):
    extra = f' font-weight="{weight}"' if weight else ""
    extra += ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'font-family="{family}" font-size="{px}"{extra}>{escape(s)}</text>')


def _svg(h, title, desc, body, uid):
    return (
        f'<svg class="dg" viewBox="0 0 {W} {h:.0f}" role="img" aria-labelledby="{uid}-t {uid}-d" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<title id="{uid}-t">{escape(title)}</title><desc id="{uid}-d">{escape(desc)}</desc>'
        f'<defs><marker id="{uid}-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker></defs>'
        f'<rect x="0" y="0" width="{W}" height="{h:.0f}" fill="{BG}"/>'
        + "".join(body) + "</svg>"
    )


class Flow:
    """Grid flow diagram.

    node(id, title, sub="", at=(row, col), span=1, color="blue")
    group(title, rows=(r0, r1), cols=(c0, c1), color="grey")
    edge(a, b, label="", dashed=False, exit=None, enter=None, bend=0)
      exit/enter: 'l','r','t','b' to force sides; bend shifts the elbow.
    """

    MARGIN, GAPX, GAPY, GROUP_PAD = 18, 26, 46, 12

    def __init__(self, uid, title, desc, cols=4):
        self.uid, self.title, self.desc, self.cols = uid, title, desc, cols
        self.nodes, self.groups, self.edges = {}, [], []

    def node(self, nid, title, sub="", at=(0, 0), span=1, color="blue"):
        self.nodes[nid] = dict(title=title, sub=sub, row=at[0], col=at[1], span=span, color=color)
        return self

    def group(self, title, rows, cols, color="grey"):
        self.groups.append(dict(title=title, rows=rows, cols=cols, color=color))
        return self

    def edge(self, a, b, label="", dashed=False, exit=None, enter=None, bend=0):
        self.edges.append(dict(a=a, b=b, label=label, dashed=dashed, exit=exit, enter=enter, bend=bend))
        return self

    def _layout(self):
        colw = (W - 2 * self.MARGIN - (self.cols - 1) * self.GAPX) / self.cols
        rows = max(n["row"] for n in self.nodes.values()) + 1
        # groups need room for their title above the first row they cover
        group_top = {g["rows"][0] for g in self.groups}
        heights = [0.0] * rows
        for n in self.nodes.values():
            w = colw * n["span"] + self.GAPX * (n["span"] - 1)
            n["w"] = w
            n["tl"] = wrap(n["title"], TITLE_PX * 1.15, w - 18)  # bold Georgia runs ~15% wider
            n["sl"] = wrap(n["sub"], SUB_PX, w - 16) if n["sub"] else []
            n["h"] = 16 + len(n["tl"]) * 18 + len(n["sl"]) * 16 + 4
            heights[n["row"]] = max(heights[n["row"]], n["h"])
        ys, y = [], self.MARGIN
        for r in range(rows):
            if r in group_top:
                y += 26
            ys.append(y)
            y += heights[r] + self.GAPY
        for n in self.nodes.values():
            n["h"] = heights[n["row"]]  # every box in a row shares one height
            n["x"] = self.MARGIN + n["col"] * (colw + self.GAPX)
            n["y"] = ys[n["row"]]
            n["cx"], n["cy"] = n["x"] + n["w"] / 2, n["y"] + n["h"] / 2
        self.colw, self.ys, self.heights = colw, ys, heights
        return y - self.GAPY + self.MARGIN + 4

    def _port(self, n, side):
        return {"l": (n["x"], n["cy"]), "r": (n["x"] + n["w"], n["cy"]),
                "t": (n["cx"], n["y"]), "b": (n["cx"], n["y"] + n["h"])}[side]

    def render(self):
        h = self._layout()
        out, titles = [], []
        for g in self.groups:
            r0, r1 = g["rows"]
            c0, c1 = g["cols"]
            x0 = self.MARGIN + c0 * (self.colw + self.GAPX) - self.GROUP_PAD
            x1 = self.MARGIN + c1 * (self.colw + self.GAPX) + self.colw + self.GROUP_PAD
            y0 = self.ys[r0] - 26
            y1 = self.ys[r1] + self.heights[r1] + self.GROUP_PAD
            x0, x1 = max(x0, 4), min(x1, W - 4)
            col = COLORS[g["color"]]
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="5" '
                       f'fill="{GROUP}" stroke="{col}" stroke-opacity="0.55" stroke-dasharray="4,3"/>')
            tw = text_width(g["title"].upper(), SMALL_PX * 1.1) + 12
            titles.append(f'<rect x="{x0 + 4:.1f}" y="{y0 + 4:.1f}" width="{tw:.1f}" height="18" fill="{GROUP}"/>')
            titles.append(_t(x0 + 10, y0 + 17, g["title"].upper(), SMALL_PX, col, "start", "bold"))
        edge_svg, label_svg = [], []
        for e in self.edges:
            a, b = self.nodes[e["a"]], self.nodes[e["b"]]
            if a["row"] == b["row"]:
                ex, en = ("r", "l") if a["cx"] < b["cx"] else ("l", "r")
            elif b["row"] > a["row"]:
                ex, en = "b", "t"
            else:
                ex, en = "t", "b"
            ex, en = e["exit"] or ex, e["enter"] or en
            (x1, y1), (x2, y2) = self._port(a, ex), self._port(b, en)
            if ex in "lr" and en in "lr":
                mx = (x1 + x2) / 2 + e["bend"]
                pts = [(x1, y1), (mx, y1), (mx, y2), (x2, y2)]
            elif ex in "tb" and en in "tb":
                my = (y1 + y2) / 2 + e["bend"]
                pts = [(x1, y1), (x1, my), (x2, my), (x2, y2)]
            elif ex in "lr":
                pts = [(x1, y1), (x2, y1), (x2, y2)]
            else:
                pts = [(x1, y1), (x1, y2), (x2, y2)]
            pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            dash = ' stroke-dasharray="5,4"' if e["dashed"] else ""
            edge_svg.append(f'<path d="{d}" fill="none" stroke="{DIM}" stroke-width="1.4"{dash} '
                            f'marker-end="url(#{self.uid}-a)"/>')
            if e["label"]:
                segs = list(zip(pts, pts[1:]))
                (sx, sy), (tx, ty) = max(segs, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
                lx, ly = (sx + tx) / 2, (sy + ty) / 2
                tw = text_width(e["label"], SMALL_PX) + 10
                if a["row"] == b["row"] and sy == ty and abs(tx - sx) < tw + 6:
                    # short hop between neighbours: label sits in the gap above the boxes
                    ly = min(a["y"], b["y"]) - 13
                label_svg.append(f'<rect x="{lx - tw / 2:.1f}" y="{ly - 9:.1f}" width="{tw:.1f}" height="17" rx="3" fill="{BG}"/>')
                label_svg.append(_t(lx, ly + 4, e["label"], SMALL_PX, SUB, italic=True))
        out += edge_svg
        for n in self.nodes.values():
            col = COLORS[n["color"]]
            out.append(f'<rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="4" '
                       f'fill="{PANEL}" stroke="{col}" stroke-width="1.5"/>')
            ty = n["y"] + (n["h"] - len(n["tl"]) * 18 - len(n["sl"]) * 16) / 2 + 14
            for ln in n["tl"]:
                out.append(_t(n["cx"], ty, ln, TITLE_PX, TEXT, weight="bold"))
                ty += 18
            for ln in n["sl"]:
                out.append(_t(n["cx"], ty, ln, SUB_PX, SUB))
                ty += 16
        out += titles + label_svg
        return _svg(h, self.title, self.desc, out, self.uid)


class Sequence:
    """Actors across the top, messages top to bottom.
    msg(a, b, text, dashed=False)   a == b draws a self-step
    note(text, over=(a, b))"""

    def __init__(self, uid, title, desc, actors):
        self.uid, self.title, self.desc = uid, title, desc
        self.actors = actors  # list of (id, label, color)
        self.items = []

    def msg(self, a, b, text, dashed=False):
        self.items.append(("m", a, b, text, dashed))
        return self

    def note(self, text, over):
        self.items.append(("n", over[0], over[1], text, False))
        return self

    def render(self):
        n = len(self.actors)
        m = 18
        step = (W - 2 * m) / n
        xs = {aid: m + step * i + step / 2 for i, (aid, _, _) in enumerate(self.actors)}
        boxw = min(step - 16, 170)
        out = []
        head = 0
        for aid, label, color in self.actors:
            head = max(head, len(wrap(label, TITLE_PX - 1, boxw - 12)))
        headh = 14 + head * 17
        y = m + headh + 26
        rows = []
        for kind, a, b, text, dashed in self.items:
            if kind == "m":
                width = abs(xs[a] - xs[b]) - 14 if a != b else step - 30
                lines = wrap(text, SUB_PX, max(width, 120))
                rows.append((kind, a, b, lines, dashed, y))
                y += 16 * len(lines) + (34 if a == b else 22)
            else:
                lines = wrap(text, SUB_PX, abs(xs[a] - xs[b]) + boxw - 24)
                rows.append((kind, a, b, lines, dashed, y))
                y += 16 * len(lines) + 24
        h = y + 8
        for aid, label, color in self.actors:
            x = xs[aid]
            col = COLORS[color]
            out.append(f'<line x1="{x:.1f}" y1="{m + headh:.1f}" x2="{x:.1f}" y2="{h - 6:.1f}" stroke="{col}" '
                       f'stroke-opacity="0.45" stroke-dasharray="3,4"/>')
            out.append(f'<rect x="{x - boxw / 2:.1f}" y="{m:.1f}" width="{boxw:.1f}" height="{headh:.1f}" rx="4" '
                       f'fill="{PANEL}" stroke="{col}" stroke-width="1.5"/>')
            for i, ln in enumerate(wrap(label, TITLE_PX - 1, boxw - 12)):
                out.append(_t(x, m + 22 + i * 17, ln, TITLE_PX - 1, TEXT, weight="bold"))
        num = 0
        for kind, a, b, lines, dashed, y0 in rows:
            if kind == "n":
                x0 = min(xs[a], xs[b]) - boxw / 2 + 6
                x1 = max(xs[a], xs[b]) + boxw / 2 - 6
                hh = 16 * len(lines) + 10
                out.append(f'<rect x="{x0:.1f}" y="{y0 - 4:.1f}" width="{x1 - x0:.1f}" height="{hh:.1f}" rx="3" '
                           f'fill="#2a2614" stroke="{COLORS["yellow"]}" stroke-opacity="0.6"/>')
                for i, ln in enumerate(lines):
                    out.append(_t((x0 + x1) / 2, y0 + 12 + i * 16, ln, SUB_PX, TEXT))
                continue
            num += 1
            dash = ' stroke-dasharray="5,4"' if dashed else ""
            x1, x2 = xs[a], xs[b]
            ty = y0 + 8
            mid = (x1 + x2) / 2 if a != b else x1 + 60
            for i, ln in enumerate(lines):
                txt = (f"{num}. " if i == 0 else "") + ln
                out.append(_t(mid if a != b else x1 + 10, ty + i * 16, txt, SUB_PX, SUB, "middle" if a != b else "start"))
            ay = ty + 16 * (len(lines) - 1) + 8
            if a == b:
                out.append(f'<path d="M{x1:.1f},{ay:.1f} h40 v14 h-38" fill="none" stroke="{DIM}" stroke-width="1.4"{dash} '
                           f'marker-end="url(#{self.uid}-a)"/>')
            else:
                out.append(f'<line x1="{x1:.1f}" y1="{ay:.1f}" x2="{x2 + (-3 if x2 > x1 else 3):.1f}" y2="{ay:.1f}" '
                           f'stroke="{DIM}" stroke-width="1.4"{dash} marker-end="url(#{self.uid}-a)"/>')
        return _svg(h, self.title, self.desc, out, self.uid)


class Timeline:
    """phase(title, detail, status) where status is done | doing | next."""

    STATUS = {"done": ("green", "Done"), "doing": ("yellow", "In progress"), "next": ("grey", "Next")}

    def __init__(self, uid, title, desc):
        self.uid, self.title, self.desc, self.phases = uid, title, desc, []

    def phase(self, title, detail="", status="next"):
        self.phases.append((title, detail, status))
        return self

    def render(self):
        n = len(self.phases)
        m, gap = 18, 14
        w = (W - 2 * m - gap * (n - 1)) / n
        body = []
        maxl = 0
        prepared = []
        for t, d, s in self.phases:
            tl, dl = wrap(t, TITLE_PX - 0.5, w - 14), wrap(d, SUB_PX - 0.5, w - 14) if d else []
            prepared.append((tl, dl, s))
            maxl = max(maxl, len(tl) * 18 + len(dl) * 15)
        boxh = 56 + maxl
        y0 = m + 34
        body.append(f'<line x1="{m:.1f}" y1="{m + 12:.1f}" x2="{W - m:.1f}" y2="{m + 12:.1f}" stroke="{DIM}" stroke-width="1.4"/>')
        for i, (tl, dl, s) in enumerate(prepared):
            x = m + i * (w + gap)
            color, label = self.STATUS[s]
            col = COLORS[color]
            body.append(f'<circle cx="{x + w / 2:.1f}" cy="{m + 12:.1f}" r="7" fill="{col if s != "next" else BG}" stroke="{col}" stroke-width="2"/>')
            body.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{boxh:.1f}" rx="4" fill="{PANEL}" stroke="{col}" stroke-width="1.5"/>')
            body.append(_t(x + w / 2, y0 + 18, f"PHASE {i + 1} · {label.upper()}", SMALL_PX - 0.5, col, weight="bold"))
            ty = y0 + 40
            for ln in tl:
                body.append(_t(x + w / 2, ty, ln, TITLE_PX - 0.5, TEXT, weight="bold"))
                ty += 18
            for ln in dl:
                body.append(_t(x + w / 2, ty, ln, SUB_PX - 0.5, SUB))
                ty += 15
        return _svg(y0 + boxh + m, self.title, self.desc, body, self.uid)


class Stack:
    """Layered architecture: layer(name, items, color), drawn top to bottom."""

    def __init__(self, uid, title, desc):
        self.uid, self.title, self.desc, self.layers = uid, title, desc, []

    def layer(self, name, items, color="blue"):
        self.layers.append((name, items, color))
        return self

    def render(self):
        m, namew, gap = 18, 190, 8
        body, y = [], m
        for name, items, color in self.layers:
            col = COLORS[color]
            n = len(items)
            iw = (W - 2 * m - namew - 12 - gap * (n - 1)) / n
            wrapped = [wrap(it, SUB_PX, iw - 12) for it in items]
            nl = wrap(name, TITLE_PX, namew - 20)
            h = max(max(len(wl) for wl in wrapped) * 16 + 22, len(nl) * 18 + 18)
            body.append(f'<rect x="{m}" y="{y:.1f}" width="{W - 2 * m}" height="{h:.1f}" rx="4" fill="{GROUP}" stroke="{col}" stroke-width="1.5"/>')
            for i, ln in enumerate(nl):
                body.append(_t(m + 12, y + h / 2 - (len(nl) - 1) * 9 + 5 + i * 18, ln, TITLE_PX, col, "start", "bold"))
            for i, wl in enumerate(wrapped):
                x = m + namew + i * (iw + gap)
                body.append(f'<rect x="{x:.1f}" y="{y + 6:.1f}" width="{iw:.1f}" height="{h - 12:.1f}" rx="3" fill="{PANEL}" stroke="#3a3a3a"/>')
                for j, ln in enumerate(wl):
                    body.append(_t(x + iw / 2, y + h / 2 - (len(wl) - 1) * 8 + 4 + j * 16, ln, SUB_PX, TEXT))
            y += h + 10
        return _svg(y - 10 + m, self.title, self.desc, body, self.uid)


class Bars:
    """Horizontal bars. Only for real numbers: measured, cited, or a
    published spec. bar(label, value, note="", color="blue")."""

    def __init__(self, uid, title, desc, unit="", max_value=None):
        self.uid, self.title, self.desc, self.unit, self.max_value = uid, title, desc, unit, max_value
        self.rows = []

    def bar(self, label, value, note="", color="blue"):
        self.rows.append((label, value, note, color))
        return self

    def render(self):
        m, lw, rh = 18, 230, 34
        top = max(self.max_value or 0, max(v for _, v, _, _ in self.rows))
        span = W - 2 * m - lw - 150
        body, y = [], m
        for label, value, note, color in self.rows:
            col = COLORS[color]
            bw = max(2, span * value / top)
            body.append(_t(m + lw - 10, y + 17, label, SUB_PX + 0.5, TEXT, "end"))
            body.append(f'<rect x="{m + lw:.1f}" y="{y + 5:.1f}" width="{bw:.1f}" height="18" rx="2" fill="{col}" fill-opacity="0.85"/>')
            vt = f"{value:g} {self.unit}".strip() + (f"  {note}" if note else "")
            body.append(_t(m + lw + bw + 8, y + 18, vt, SUB_PX, SUB, "start"))
            y += rh
        return _svg(y + m - 6, self.title, self.desc, body, self.uid)
