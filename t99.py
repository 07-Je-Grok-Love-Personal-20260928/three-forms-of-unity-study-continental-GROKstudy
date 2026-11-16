# -*- coding: utf-8 -*-
"""t99 后处理：接入本轮样式，并把 t99.js 接进既有错开加载链。"""
def apply(h, page, site):
    if "assets/t97.css" not in h:
        print("t99 MISS t97.css", site, page)
        return h
    if "assets/t99.css" not in h:
        h = h.replace(
            'href="assets/t97.css?v=',
            'href="assets/t97.css?v=',
            1,
        )
        # insert after the t97.css link tag
        needle = 'assets/t97.css?v='
        i = h.find(needle)
        j = h.find('">', i)
        if i < 0 or j < 0:
            print("t99 MISS t97.css tag", site, page)
            return h
        ver = h[i+len(needle):j]
        old = f'<link rel="stylesheet" href="assets/t97.css?v={ver}">'
        new = old + f'<link rel="stylesheet" href="assets/t99.css?v={ver}">'
        if old not in h:
            print("t99 MISS exact t97 link", site, page)
        else:
            h = h.replace(old, new, 1)
    old = 'data-chain="app,t87,t89,t90,t91,t93,t94"'
    new = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99"'
    if old in h:
        h = h.replace(old, new, 1)
    elif 't94,t99' not in h:
        print("t99 MISS chain", site, page)
    return h
