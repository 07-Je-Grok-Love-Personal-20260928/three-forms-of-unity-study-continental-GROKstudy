# -*- coding: utf-8 -*-
"""t91 后处理：接入样式/脚本；图例补充；逐句精简（只改本站说明，不动 CCI 原文）。"""
import re

# 填入经核验、恰好出现一次的本站说明。构建时若打印 t91edit MISS 则跳过。
EDITS = {}

def apply(h, page, site):
    for o, n in EDITS.get((site, page), []):
        c = h.count(o)
        if c != 1:
            print("t91edit MISS", site, page, c, o[:24])
            continue
        h = h.replace(o, n, 1)
    m = re.search(r'assets/t90\.css\?v=([^"]+)"', h)
    if not m:
        print("t91 MISS t90.css", site, page)
        return h
    ver = m.group(1)
    h = h.replace(f'<link rel="stylesheet" href="assets/t90.css?v={ver}">',
                  f'<link rel="stylesheet" href="assets/t90.css?v={ver}"><link rel="stylesheet" href="assets/t91.css?v={ver}">', 1)
    h = h.replace(f'<script src="assets/t90.js?v={ver}" defer></script>',
                  f'<script src="assets/t90.js?v={ver}" defer></script><script src="assets/t91.js?v={ver}" defer></script>', 1)
    if 'class="mklegend"' in h and 'lg-box' not in h:
        def addleg(mm):
            s = mm.group(0)
            if 'lg-box' in s:
                return s
            return s[:-6] + '<span class="lgc"><i class="lg-box">重点区块</i></span></div>'
        h = re.sub(r'<div class="mklegend"[^>]*>.*?</div>', addleg, h, count=1, flags=re.S)
    return h
