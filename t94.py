# -*- coding: utf-8 -*-
"""t94 后处理：接入目录样式/脚本；首屏恢复目录宽度；
把非当前一级目录的子列表放入 <template>（惰性水合，缩短首屏样式/布局）；
把 #tocx 移出 #toc，避免桌面收起时因祖先 transform 而不可点。"""
import re

KEYS = {
    "tfu": ("tfu1.tw", "tfu1.twm"),
    "tec": ("tec4.tw", "tec4.twm"),
}

def _boot(kd, km):
    return (
        '<script data-t94-tw-boot>(function(){try{'
        "var w=innerWidth>=1100,k=w?'" + kd + "':'" + km + "',"
        "v=JSON.parse(localStorage.getItem(k));"
        "if(typeof v==='number'){var r=document.documentElement;"
        "r.style.setProperty(w?'--tw':'--twm',v+'px');"
        "if(w)r.style.setProperty('--tw-hold',v+'px')}"
        "}catch(e){}})();</script>"
    )

def _end_of_open(h, i):
    j = h.find(">", i)
    return -1 if j < 0 else j + 1

def _match_tag(h, i, name):
    """i points at '<' of <name ...>. Return (open_end, close_start, close_end)."""
    if not h.startswith("<" + name, i):
        return None
    open_end = _end_of_open(h, i)
    if open_end < 0:
        return None
    depth = 1
    k = open_end
    open_tok = "<" + name
    close_tok = "</" + name + ">"
    ln = len(name)
    while k < len(h) and depth:
        a = h.find(open_tok, k)
        b = h.find(close_tok, k)
        if b < 0:
            return None
        if a >= 0 and a < b:
            nxt = a + len(open_tok)
            if nxt < len(h) and h[nxt] not in " \t\n\r/>":
                k = nxt
                continue
            depth += 1
            k = _end_of_open(h, a)
            if k < 0:
                return None
        else:
            depth -= 1
            if depth == 0:
                return open_end, b, b + len(close_tok)
            k = b + len(close_tok)
    return None

def _skip_div(h, i, cls_prefix="t1r"):
    m = re.match(r'\s*<div class="' + re.escape(cls_prefix) + r'"', h[i:])
    if not m:
        return None
    start = i + m.start() + m.group(0).find("<div")
    # m.start is relative; easier:
    abs_lt = i + h[i:].find("<div")
    return _match_tag(h, abs_lt, "div")

def wrap_closed_t1(h):
    """Wrap the child <ol> of every li.t1.closed in <template class="t1pack">."""
    if 'class="t1pack"' in h:
        return h
    out = []
    i = 0
    for m in re.finditer(r'<li class="t1 closed"[^>]*>', h):
        li_open_end = m.end()
        out.append(h[i:li_open_end])
        div_start = h.find("<div", li_open_end)
        div = _match_tag(h, div_start, "div") if div_start >= 0 else None
        if not div:
            i = li_open_end
            continue
        out.append(h[li_open_end:div[2]])
        # next non-space should be <ol>
        k = div[2]
        while k < len(h) and h[k] in " \t\n\r":
            out.append(h[k])
            k += 1
        if not h.startswith("<ol", k):
            i = k
            continue
        ol = _match_tag(h, k, "ol")
        if not ol:
            i = k
            continue
        out.append('<template class="t1pack">')
        out.append(h[k:ol[2]])
        out.append("</template>")
        i = ol[2]
    out.append(h[i:])
    return "".join(out)

def hoist_tocx(h):
    m = re.search(r'<button id="tocx"[^>]*>.*?</button>', h)
    if not m:
        return h
    btn = m.group(0)
    # already hoisted?
    after = h[m.end():m.end() + 200]
    # if button is already outside nav, skip
    nav_close = h.find("</nav>")
    if nav_close >= 0 and m.start() > nav_close:
        return h
    h = h[:m.start()] + h[m.end():]
    nav_close = h.find("</nav>")
    if nav_close < 0:
        return h
    return h[:nav_close + 6] + btn + h[nav_close + 6:]

def apply(h, page, site):
    m = re.search(r'assets/t93\.css\?v=([^"]+)"', h)
    if not m:
        print("t94 MISS t93.css", site, page)
        return h
    ver = m.group(1)
    h = h.replace(
        f'<link rel="stylesheet" href="assets/t93.css?v={ver}">',
        f'<link rel="stylesheet" href="assets/t93.css?v={ver}"><link rel="stylesheet" href="assets/t94.css?v={ver}">',
        1,
    )
    h = h.replace(
        f'<script src="assets/t93.js?v={ver}" defer></script>',
        f'<script src="assets/t93.js?v={ver}" defer></script><script src="assets/t94.js?v={ver}" defer></script>',
        1,
    )
    kd, km = KEYS.get(site, KEYS["tfu"])
    boot = _boot(kd, km)
    if "data-t94-tw-boot" not in h:
        if "</title>" in h:
            h = h.replace("</title>", "</title>" + boot, 1)
        else:
            h = h.replace("<head>", "<head>" + boot, 1)
    h = wrap_closed_t1(h)
    h = hoist_tocx(h)
    return h
