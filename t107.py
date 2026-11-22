# -*- coding: utf-8 -*-
"""t107 后处理：窄屏把嵌套卡片垫平，正文贴到近屏边。"""
import re

def apply(h, page, site):
    if "assets/t106.css" not in h:
        print("t107 MISS t106.css", site, page)
        return h
    if "assets/t107.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t106\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            old = m.group(0)
            h = h.replace(old, old + f'<link rel="stylesheet" href="assets/t107.css?v={ver}.t107r2">', 1)
        else:
            print("t107 MISS exact t106 link", site, page)
    if 'data-chain="' in h and ",t107" not in h:
        if "t102,t106\"" in h:
            h = h.replace("t102,t106\"", "t102,t106,t107\"", 1)
        else:
            print("t107 MISS chain", site, page)
    return h
