# -*- coding: utf-8 -*-
"""t93 后处理：接入样式/脚本。逐句精简在各页源文件中完成（只改本站说明）。"""
import re

def apply(h, page, site):
    m = re.search(r'assets/t91\.css\?v=([^"]+)"', h)
    if not m:
        print("t93 MISS t91.css", site, page)
        return h
    ver = m.group(1)
    h = h.replace(f'<link rel="stylesheet" href="assets/t91.css?v={ver}">',
                  f'<link rel="stylesheet" href="assets/t91.css?v={ver}"><link rel="stylesheet" href="assets/t93.css?v={ver}">', 1)
    h = h.replace(f'<script src="assets/t91.js?v={ver}" defer></script>',
                  f'<script src="assets/t91.js?v={ver}" defer></script><script src="assets/t93.js?v={ver}" defer></script>', 1)
    return h
