# -*- coding: utf-8 -*-
"""t102 后处理：接入本轮样式，并把 t102.js 接进既有错开加载链。"""
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
        new = old + f'<link rel="stylesheet" href="assets/t102.css?v={ver}">'
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
    return h
