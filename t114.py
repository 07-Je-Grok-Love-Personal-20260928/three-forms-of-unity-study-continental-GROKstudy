# -*- coding: utf-8 -*-
"""t114：六套克制主题 + 可隐藏顶栏目录。"""
import re

THEMES = [
    ("night", "#0b1110", "墨", "墨玉"),
    ("navy", "#0a1020", "夜", "午夜藏蓝金"),
    ("paper", "#f3ead8", "纸", "宫廷纸本"),
    ("celadon", "#e8f0ea", "瓷", "青瓷"),
    ("wisteria", "#efeaf4", "藤", "紫藤晨雾"),
    ("charcoal", "#161314", "灰", "炭灰玫瑰金"),
]
META = "{" + ",".join(f'{k}:"{c}"' for k, c, *_ in THEMES) + "}"
INIT = (
    '<script>try{var M=' + META + ';'
    'var A={night:"night",navy:"navy",paper:"paper",celadon:"celadon",wisteria:"wisteria",charcoal:"charcoal",'
    'dawn:"paper",jade:"navy",grape:"wisteria",sakura:"wisteria",ocean:"navy",amber:"charcoal",eye:"celadon"};'
    'var T=localStorage.getItem("ui.theme");T=A[T]||(M[T]?T:"night");'
    'if(T!==localStorage.getItem("ui.theme"))try{localStorage.setItem("ui.theme",T)}catch(e){}'
    'if(T&&T!=="night")document.documentElement.setAttribute("data-theme",T);'
    'else document.documentElement.removeAttribute("data-theme");'
    'var m=document.querySelector(\'meta[name="theme-color"]\');'
    'if(m)m.setAttribute("content",M[T]||M.night)}catch(e){}</script>'
)
WRAP_OPEN = (
    '<div id="ptabwrap" class="ptabwrap">'
    '<button type="button" class="ptab-tog" aria-expanded="true" aria-controls="ptabs" title="隐藏顶栏目录" aria-label="隐藏顶栏目录">▾</button>'
)
# button is prepended… actually we want tabs first then toggle. Fix in apply.

PTABS_OPEN = '<div id="ptabwrap" class="ptabwrap">'
PTABS_CLOSE = (
    '<button type="button" class="ptab-tog" aria-expanded="true" aria-controls="ptabs" '
    'title="隐藏顶栏目录" aria-label="隐藏顶栏目录">▾</button></div>'
    '<div id="ptabline" class="ptabline" aria-hidden="true">'
    '<button type="button" class="ptab-hair" aria-label="显示顶栏目录"></button>'
    '<button type="button" class="ptab-handle" aria-label="显示顶栏目录"></button>'
    '</div>'
)


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


def apply(h, page, site):
    if "assets/t112.css" not in h:
        print("t114 MISS t112.css", site, page)
        return h
    if "assets/t114.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t112\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            h = h.replace(m.group(0), m.group(0) + f'<link rel="stylesheet" href="assets/t114.css?v={ver}.t114r1">', 1)
        else:
            print("t114 MISS exact t112 link", site, page)
    if 'data-chain="' in h and ",t114" not in h:
        if 't102,t106,t107,t112"' in h:
            h = h.replace('t102,t106,t107,t112"', 't102,t106,t107,t112,t114"', 1)
        else:
            print("t114 MISS chain", site, page)

    # Replace the first-paint theme script (t87, possibly expanded by t90).
    h2, n = re.subn(
        r'<script>try\{var T=localStorage\.getItem\("ui\.theme"\);if\(T&&/\^\([^)]+\)\$/\.test\(T\)\)\{document\.documentElement\.setAttribute\("data-theme",T\);var M=\{[^}]+\};document\.querySelector\(\'meta\[name="theme-color"\]\'\)\.setAttribute\("content",M\[T\]\)\}\}catch\(e\)\{\}</script>',
        INIT,
        h,
        count=1,
    )
    if n != 1:
        print("t114 MISS INIT", site, page, n)
    else:
        h = h2

    # Replace theme menus entirely.
    h2, n = re.subn(
        r'(<div id="thmm"[^>]*>).*?(</div>)',
        lambda m: m.group(1) + _btns("menu") + m.group(2),
        h,
        count=1,
        flags=re.S,
    )
    if n != 1:
        print("t114 MISS thmm", site, page, n)
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
            print("t114 MISS thbar", site, page, n)
        else:
            h = h2

    # Light-theme L3 badge rule left by t90 (TEC).
    h = h.replace(
        "<style>html:is([data-theme=sakura],[data-theme=paper],[data-theme=eye]) .l3 .lb{color:#fff}</style>",
        "<style>html:is([data-theme=paper],[data-theme=celadon],[data-theme=wisteria]) .l3 .lb{color:#fff}</style>",
        1,
    )

    if 'id="ptabwrap"' not in h:
        m = re.search(r'<nav class="ptabs"[^>]*>.*?</nav>', h, flags=re.S)
        if not m:
            print("t114 MISS ptabs", site, page)
        else:
            nav = m.group(0).replace('<nav class="ptabs"', '<nav class="ptabs" id="ptabs"', 1)
            h = h[: m.start()] + PTABS_OPEN + nav + PTABS_CLOSE + h[m.end() :]

    return h
