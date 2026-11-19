# -*- coding: utf-8 -*-
"""t102 后处理：接入本轮样式，并把 t102.js 提前加载（独立查询串，避免旧缓存）。"""
import re

_T97 = re.compile(
    r'(<script src="assets/t97\.js\?v=([^"]+)" defer data-t97-chain[^>]*>\s*</script>)'
)

def apply(h, page, site):
    if "assets/t101.css" not in h:
        print("t102 MISS t101.css", site, page)
        return h
    if "assets/t102.css" not in h:
        needle = "assets/t101.css?v="
        i = h.find(needle)
        j = h.find('">', i)
        if i < 0 or j < 0:
            print("t102 MISS t101.css tag", site, page)
            return h
        ver = h[i + len(needle):j]
        old = f'<link rel="stylesheet" href="assets/t101.css?v={ver}">'
        new = old + f'<link rel="stylesheet" href="assets/t102.css?v={ver}.r3">'
        if old in h:
            h = h.replace(old, new, 1)
        else:
            print("t102 MISS exact t101 link", site, page)
    oldc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99,t100,t101"'
    newc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99,t100,t101,t102"'
    if oldc in h:
        h = h.replace(oldc, newc, 1)
    elif "t101,t102" not in h:
        print("t102 MISS chain", site, page)
    if "assets/t102.js?v=" not in h:
        m = _T97.search(h)
        if m:
            ver = m.group(2)
            h = h[:m.end()] + f'<script src="assets/t102.js?v={ver}.r3" defer></script>' + h[m.end():]
        else:
            print("t102 MISS early script", site, page)
    return h
