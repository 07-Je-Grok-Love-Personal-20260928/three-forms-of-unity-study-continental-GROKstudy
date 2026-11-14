# -*- coding: utf-8 -*-
"""t97 后处理：接入本轮样式/脚本。"""
import re

def apply(h, page, site):
    m = re.search(r'assets/t94\.css\?v=([^"]+)"', h)
    if not m:
        print("t97 MISS t94.css", site, page)
        return h
    ver = m.group(1)
    if "assets/t97.css" not in h:
        h = h.replace(
            f'<link rel="stylesheet" href="assets/t94.css?v={ver}">',
            f'<link rel="stylesheet" href="assets/t94.css?v={ver}"><link rel="stylesheet" href="assets/t97.css?v={ver}">',
            1,
        )
    if "assets/t97.js" not in h:
        h = h.replace(
            f'<script src="assets/t94.js?v={ver}" defer></script>',
            f'<script src="assets/t94.js?v={ver}" defer></script><script src="assets/t97.js?v={ver}" defer></script>',
            1,
        )
    return h
