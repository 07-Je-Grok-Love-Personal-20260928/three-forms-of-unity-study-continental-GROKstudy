# -*- coding: utf-8 -*-
"""t100 后处理：去掉页首主题文字条，把主题按钮并入右下导航簇，并接入样式与加载链。"""
import re

def _cut_div(h, start_idx):
    k = start_idx
    depth = 0
    while k < len(h):
        if h.startswith("<div", k):
            depth += 1
            k = h.find(">", k) + 1
            if k == 0:
                break
        elif h.startswith("</div>", k):
            depth -= 1
            k += 6
            if depth == 0:
                return start_idx, k
        else:
            k += 1
    return start_idx, start_idx

def apply(h, page, site):
    if "assets/t99.css" not in h:
        print("t100 MISS t99.css", site, page)
        return h
    if "assets/t100.css" not in h:
        needle = "assets/t99.css?v="
        i = h.find(needle)
        j = h.find('">', i)
        if i < 0 or j < 0:
            print("t100 MISS t99.css tag", site, page)
            return h
        ver = h[i + len(needle):j]
        old = f'<link rel="stylesheet" href="assets/t99.css?v={ver}">'
        new = old + f'<link rel="stylesheet" href="assets/t100.css?v={ver}">'
        if old in h:
            h = h.replace(old, new, 1)
        else:
            print("t100 MISS exact t99 link", site, page)
    oldc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99"'
    newc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99,t100"'
    if oldc in h:
        h = h.replace(oldc, newc, 1)
    elif "t99,t100" not in h:
        print("t100 MISS chain", site, page)

    h = re.sub(r'<div class="thbar"[^>]*>.*?</div>', "", h, count=1, flags=re.S)

    if 'id="top"' not in h:
        h = re.sub(r"<body([^>]*)>", r'<body id="top"\1>', h, count=1)
    if 'id="bot"' not in h:
        h = h.replace('<footer class="foot">', '<footer class="foot" id="bot">', 1)

    h = h.replace(
        '<button type="button" data-nv="top" aria-label="回到页面顶部" title="顶部">⤒</button>',
        '<a href="#top" data-nv="top" aria-label="回到页面顶部" title="顶部">⤒</a>',
    )
    h = h.replace(
        '<button type="button" data-nv="bot" aria-label="到页面底部" title="底部">⤓</button>',
        '<a href="#bot" data-nv="bot" aria-label="到页面底部" title="底部">⤓</a>',
    )

    if 'id="thmb"' in h and "aria-label=\"切换主题配色\"" not in h.split('id="thmb"', 1)[1][:200]:
        h = h.replace(
            'title="切换主题配色">🎨<span>主题</span></button>',
            'title="切换主题配色" aria-label="切换主题配色">🎨</button>',
            1,
        )

    if 'id="tocbtn"' in h and ">☰ 目录</button>" in h:
        h = h.replace(
            '<button id="tocbtn" class="fab" aria-label="显示目录" aria-controls="toc" type="button">☰ 目录</button>',
            '<button id="tocbtn" class="fab" aria-label="显示目录" aria-controls="toc" type="button" title="目录">☰</button>',
            1,
        )

    ti = h.find('<div id="thm">')
    ni = h.find('id="navc"')
    if ti >= 0 and ni >= 0 and ti < h.find("</div>", h.find('class="nv-t"')):
        a, b = _cut_div(h, ti)
        thm = h[a:b]
        h = h[:a] + h[b:]
        nv = h.find('<div id="navc">')
        if nv < 0:
            print("t100 MISS navc after move", site, page)
            return h
        # re-find end of opening structure: insert dock before closing </div> of #navc
        # after cutting thm, navc is intact
        mark = '<button type="button" class="nv-t"'
        m = h.find(mark, nv)
        if m < 0:
            print("t100 MISS nv-t", site, page)
            return h
        end_btn = h.find("</button>", m)
        if end_btn < 0:
            print("t100 MISS nv-t end", site, page)
            return h
        end_btn += len("</button>")
        dock = '<div class="nv-dock">' + thm + h[m:end_btn] + "</div>"
        h = h[:m] + dock + h[end_btn:]
    elif ti >= 0 and ni >= 0:
        # thm already after navc start? leave
        pass

    return h
