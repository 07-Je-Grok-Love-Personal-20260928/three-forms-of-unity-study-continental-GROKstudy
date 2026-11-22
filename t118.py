# -*- coding: utf-8 -*-
"""t118: header ☰ in layout flow; hide while the drawer is open; wrap level buttons."""
import re


def _cut_tag(h, start, tag):
    open_t, close_t = f"<{tag}", f"</{tag}>"
    if not h.startswith(open_t, start):
        return start, start
    k = h.find(">", start) + 1
    if k == 0:
        return start, start
    depth = 1
    while k < len(h) and depth:
        nxt_o = h.find(open_t, k)
        nxt_c = h.find(close_t, k)
        if nxt_c < 0:
            return start, start
        if nxt_o >= 0 and nxt_o < nxt_c:
            depth += 1
            k = h.find(">", nxt_o) + 1
            if k == 0:
                return start, start
        else:
            depth -= 1
            k = nxt_c + len(close_t)
    return start, k


def _div_start(h, id_):
    needle = f'id="{id_}"'
    i = h.find(needle)
    if i < 0:
        return -1
    return h.rfind("<div", 0, i)


def apply(h, page, site):
    if "assets/t117.css" not in h:
        print("t118 MISS t117.css", site, page)
        return h
    if "assets/t118.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t117\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            h = h.replace(m.group(0), m.group(0) + f'<link rel="stylesheet" href="assets/t118.css?v={ver}.t118">', 1)
        else:
            print("t118 MISS exact t117 link", site, page)
    if 'data-chain="' in h and ",t118" not in h:
        if 't102,t106,t107,t112,t114,t117"' in h:
            h = h.replace('t102,t106,t107,t112,t114,t117"', 't102,t106,t107,t112,t114,t117,t118"', 1)
        else:
            print("t118 MISS chain", site, page)

    if 'id="ptabrow"' in h:
        return h

    m = re.search(r'<button[^>]*\sid="tochd"[^>]*>.*?</button>', h)
    if not m:
        print("t118 MISS tochd", site, page)
        return h
    tochd = m.group(0)
    h = h[: m.start()] + h[m.end() :]

    ws = _div_start(h, "ptabwrap")
    ls = _div_start(h, "ptabline")
    if ws < 0 or ls < 0:
        print("t118 MISS ptabwrap/line", site, page)
        # put the button back so later pages are not silently missing it
        if "<main id=\"main\">" in h:
            h = h.replace("<main id=\"main\">", tochd + "<main id=\"main\">", 1)
        return h
    _, we = _cut_tag(h, ws, "div")
    _, le = _cut_tag(h, ls, "div")
    if we <= ws or le <= ls:
        print("t118 MISS cut ptab", site, page)
        return h
    first, last = min(ws, ls), max(we, le)
    inner = h[first:last]
    wrapped = '<div id="ptabrow" class="ptabrow">' + tochd + inner + "</div>"
    h = h[:first] + wrapped + h[last:]
    return h
