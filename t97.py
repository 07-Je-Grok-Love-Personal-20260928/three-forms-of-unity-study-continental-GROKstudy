# -*- coding: utf-8 -*-
"""t97 后处理：接入本轮样式/脚本，并把 app.js 与增强脚本错开到独立短任务。"""
import re

# Fresh HTML still has the full defer chain from t94.py.
_CHAIN_RE = re.compile(
    r'<script src="assets/app\.js\?v=([^"]+)" defer></script>'
    r'(?:<script src="assets/t\d+\.js\?v=[^"]+" defer></script>)+'
)

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
    if 'data-t97-chain' not in h:
        h2, n = _CHAIN_RE.subn(
            r'<script src="assets/t97.js?v=\1" defer data-t97-chain data-chain="app,t87,t89,t90,t91,t93,t94"></script>',
            h,
            count=1,
        )
        if n:
            h = h2
        elif "assets/t97.js" not in h:
            h = h.replace(
                f'<script src="assets/t94.js?v={ver}" defer></script>',
                f'<script src="assets/t94.js?v={ver}" defer></script><script src="assets/t97.js?v={ver}" defer></script>',
                1,
            )
    return h
