# -*- coding: utf-8 -*-
"""t117：六套产品风主题 + 两点启动器 + 顶左目录 + 呼吸发丝线。"""
import re

THEMES = [
    ("night", "#0f1011", "墨", "墨灰"),
    ("lights", "#000000", "夜", "夜幕"),
    ("dim", "#15202b", "蓝", "暗蓝灰"),
    ("paper", "#f0f2f5", "雅", "雅白"),
    ("warm", "#fbfbfa", "纸", "素纸"),
    ("mono", "#ffffff", "净", "素净"),
]
META = "{" + ",".join(f'{k}:"{c}"' for k, c, *_ in THEMES) + "}"
INIT = (
    '<script>try{var M=' + META + ';'
    'var A={night:"night",lights:"lights",dim:"dim",paper:"paper",warm:"warm",mono:"mono",'
    'navy:"dim",celadon:"warm",wisteria:"mono",charcoal:"lights",'
    'dawn:"paper",jade:"dim",grape:"mono",sakura:"mono",ocean:"dim",amber:"lights",eye:"warm"};'
    'var T=localStorage.getItem("ui.theme");T=A[T]||(M[T]?T:"night");'
    'if(T!==localStorage.getItem("ui.theme"))try{localStorage.setItem("ui.theme",T)}catch(e){}'
    'if(T&&T!=="night")document.documentElement.setAttribute("data-theme",T);'
    'else document.documentElement.removeAttribute("data-theme");'
    'var m=document.querySelector(\'meta[name="theme-color"]\');'
    'if(m)m.setAttribute("content",M[T]||M.night)}catch(e){}</script>'
)

TOCHD = (
    '<button type="button" id="tochd" class="tochd" aria-label="显示目录" title="目录" '
    'aria-controls="toc" aria-expanded="false">☰</button>'
)

SUM_OLD = (
    '<summary id="nvsum" class="nvlaunch-btn" aria-label="快捷操作" title="快捷操作" aria-expanded="false">⋯</summary>'
)
SUM_NEW = (
    '<summary id="nvsum" class="nvlaunch-btn" aria-label="快捷操作" title="快捷操作" aria-expanded="false">'
    '<span class="nv-dots" aria-hidden="true"><i></i><i></i></span></summary>'
)

FALL_OLD = '<a class="nv-toc-fallback" href="#toc">目录</a>'
FALL_NEW = '<a class="nv-toc-fallback" href="#toc" aria-label="目录" title="目录">☰</a>'


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


def _btns(kind):
    if kind == "menu":
        return "".join(
            f'<button type="button" role="menuitemradio" data-theme-set="{k}" style="--sw:{c}"><i>{e}</i>{n}</button>'
            for k, c, e, n in THEMES
        )
    return "".join(
        f'<button type="button" role="menuitemradio" data-theme-set="{k}" style="--sw:{c}" title="{n}"><i></i>{e}<b>{n}</b></button>'
        for k, c, e, n in THEMES
    )


def _dock(h, page, site):
    if 'id="nvdock"' in h:
        return h
    ls = h.find('<details id="nvlaunch"')
    if ls < 0:
        print("t117 MISS nvlaunch", site, page)
        return h
    la, lb = _cut_tag(h, ls, "details")
    block = h[la:lb]
    ts = block.find('<button id="tocbtn"')
    tocbtn = ""
    if ts >= 0:
        te = block.find("</button>", ts)
        if te >= 0:
            te += len("</button>")
            tocbtn = block[ts:te]
            block = block[:ts] + block[te:]
    if not tocbtn:
        print("t117 MISS tocbtn-in-launch", site, page)
        return h
    if FALL_OLD in block:
        block = block.replace(FALL_OLD, "", 1)
    elif 'class="nv-toc-fallback"' in block:
        block = re.sub(r'<a class="nv-toc-fallback"[^>]*>.*?</a>', "", block, count=1, flags=re.S)
    if SUM_OLD in block:
        block = block.replace(SUM_OLD, SUM_NEW, 1)
    elif ">⋯</summary>" in block:
        block = block.replace(">⋯</summary>", ">" + '<span class="nv-dots" aria-hidden="true"><i></i><i></i></span></summary>', 1)
    wrapped = '<div id="nvdock" class="nvdock">' + tocbtn + FALL_NEW + block + "</div>"
    return h[:la] + wrapped + h[lb:]


def apply(h, page, site):
    if "assets/t114.css" not in h:
        print("t117 MISS t114.css", site, page)
        return h
    if "assets/t117.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t114\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            h = h.replace(m.group(0), m.group(0) + f'<link rel="stylesheet" href="assets/t117.css?v={ver}.t117r1">', 1)
        else:
            print("t117 MISS exact t114 link", site, page)
    if 'data-chain="' in h and ",t117" not in h:
        if 't102,t106,t107,t112,t114"' in h:
            h = h.replace('t102,t106,t107,t112,t114"', 't102,t106,t107,t112,t114,t117"', 1)
        else:
            print("t117 MISS chain", site, page)

    h2, n = re.subn(
        r'<script>try\{var M=\{[^}]+\};var A=\{[^}]+\}.*?catch\(e\)\{\}</script>',
        INIT,
        h,
        count=1,
        flags=re.S,
    )
    if n != 1:
        h2, n = re.subn(
            r'<script>try\{var T=localStorage\.getItem\("ui\.theme"\);if\(T&&/\^\([^)]+\)\$/\.test\(T\)\)\{document\.documentElement\.setAttribute\("data-theme",T\);var M=\{[^}]+\};document\.querySelector\(\'meta\[name="theme-color"\]\'\)\.setAttribute\("content",M\[T\]\)\}\}catch\(e\)\{\}</script>',
            INIT,
            h,
            count=1,
        )
    if n != 1:
        print("t117 MISS INIT", site, page, n)
    else:
        h = h2

    h2, n = re.subn(
        r'(<div id="thmm"[^>]*>).*?(</div>)',
        lambda m: m.group(1) + _btns("menu") + m.group(2),
        h,
        count=1,
        flags=re.S,
    )
    if n != 1:
        print("t117 MISS thmm", site, page, n)
    else:
        h = h2
    if 'class="thbar"' in h:
        h2, n = re.subn(
            r'(<div class="thbar"[^>]*>)<span>🎨 主题</span>.*?(</div>)',
            lambda m: m.group(1) + "<span>🎨 主题</span>" + _btns("bar") + m.group(2),
            h,
            count=1,
            flags=re.S,
        )
        if n != 1:
            print("t117 MISS thbar", site, page, n)
        else:
            h = h2

    h = _dock(h, page, site)

    if 'id="tochd"' not in h:
        if "<main id=\"main\">" in h:
            h = h.replace("<main id=\"main\">", TOCHD + "<main id=\"main\">", 1)
        else:
            print("t117 MISS main", site, page)

    return h
