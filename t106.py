# -*- coding: utf-8 -*-
"""t106 后处理：窄屏通栏与紧凑卡片栅格。"""
import re

def apply(h, page, site):
    if "assets/t102.css" not in h:
        print("t106 MISS t102.css", site, page)
        return h
    if "assets/t106.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t102\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            old = m.group(0)
            h = h.replace(old, old + f'<link rel="stylesheet" href="assets/t106.css?v={ver}.t106r1">', 1)
        else:
            print("t106 MISS exact t102 link", site, page)
    oldc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99,t100,t101,t102"'
    newc = 'data-chain="app,t87,t89,t90,t91,t93,t94,t99,t100,t101,t102,t106"'
    if oldc in h:
        h = h.replace(oldc, newc, 1)
    elif "t102,t106" not in h:
        print("t106 MISS chain", site, page)
    return h
