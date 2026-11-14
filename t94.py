# -*- coding: utf-8 -*-
"""t94 后处理：接入目录样式/脚本，并在首屏前恢复已保存的目录宽度。"""
import re

KEYS = {
    "tfu": ("tfu1.tw", "tfu1.twm"),
    "tec": ("tec4.tw", "tec4.twm"),
}

def _boot(kd, km):
    return (
        '<script data-t94-tw-boot>(function(){try{'
        "var w=innerWidth>=1100,k=w?'" + kd + "':'" + km + "',"
        "v=JSON.parse(localStorage.getItem(k));"
        "if(typeof v==='number'){var r=document.documentElement;"
        "r.style.setProperty(w?'--tw':'--twm',v+'px');"
        "if(w)r.style.setProperty('--tw-hold',v+'px')}"
        "}catch(e){}})();</script>"
    )

def apply(h, page, site):
    m = re.search(r'assets/t93\.css\?v=([^"]+)"', h)
    if not m:
        print("t94 MISS t93.css", site, page)
        return h
    ver = m.group(1)
    h = h.replace(
        f'<link rel="stylesheet" href="assets/t93.css?v={ver}">',
        f'<link rel="stylesheet" href="assets/t93.css?v={ver}"><link rel="stylesheet" href="assets/t94.css?v={ver}">',
        1,
    )
    h = h.replace(
        f'<script src="assets/t93.js?v={ver}" defer></script>',
        f'<script src="assets/t93.js?v={ver}" defer></script><script src="assets/t94.js?v={ver}" defer></script>',
        1,
    )
    kd, km = KEYS.get(site, KEYS["tfu"])
    boot = _boot(kd, km)
    if "data-t94-tw-boot" not in h:
        if "</title>" in h:
            h = h.replace("</title>", "</title>" + boot, 1)
        else:
            h = h.replace("<head>", "<head>" + boot, 1)
    return h
