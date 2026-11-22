# -*- coding: utf-8 -*-
"""t112：右下角三枚按钮收成一颗低调的 ⋯ 启动器，正文横向铺满、不再为簇让位。"""
import re

def _cut_div(h, start_idx):
    k = start_idx
    depth = 0
    while k < len(h):
        if h.startswith("<div", k):
            depth += 1
            k = h.find(">", k) + 1
            if k == 0:
                break
        elif h.startswith("</div>", k):
            depth -= 1
            k += 6
            if depth == 0:
                return start_idx, k
        else:
            k += 1
    return start_idx, start_idx


def apply(h, page, site):
    if "assets/t107.css" not in h:
        print("t112 MISS t107.css", site, page)
        return h
    if "assets/t112.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t107\.css\?v=([^"]+)">', h)
        if m:
            old = m.group(0)
            ver = m.group(1)
            h = h.replace(old, old + f'<link rel="stylesheet" href="assets/t112.css?v={ver}.t112r1">', 1)
        else:
            print("t112 MISS exact t107 link", site, page)
    if 'data-chain="' in h and ",t112" not in h:
        if "t102,t106,t107\"" in h:
            h = h.replace("t102,t106,t107\"", "t102,t106,t107,t112\"", 1)
        else:
            print("t112 MISS chain", site, page)

    if 'id="nvlaunch"' in h:
        return h

    ns = h.find('<div id="navc">')
    if ns < 0:
        print("t112 MISS navc", site, page)
        return h
    na, nb = _cut_div(h, ns)
    navc = h[na:nb]

    ts = h.find('<button id="tocbtn"')
    if ts < 0:
        print("t112 MISS tocbtn", site, page)
        return h
    te = h.find("</button>", ts)
    if te < 0:
        print("t112 MISS tocbtn end", site, page)
        return h
    te += len("</button>")
    tocbtn = h[ts:te]

    # Drop the old compass toggle from the dock; ⋯ is the only launcher.
    inner = navc[len('<div id="navc">'):-len("</div>")]
    inner = re.sub(
        r'<button type="button" class="nv-t"[^>]*>.*?</button>',
        "",
        inner,
        count=1,
        flags=re.S,
    )
    # nv-dock may now only wrap #thm
    launch = (
        '<details id="nvlaunch" class="nvlaunch">'
        '<summary id="nvsum" class="nvlaunch-btn" aria-label="快捷操作" title="快捷操作" aria-expanded="false">⋯</summary>'
        '<div class="nvlaunch-pop" id="nvpop" role="group" aria-label="快捷操作">'
        '<div id="navc">'
        + inner +
        tocbtn +
        '<a class="nv-toc-fallback" href="#toc">目录</a>'
        "</div></div></details>"
    )

    # Remove tocbtn and navc; insert launcher at the earlier of the two positions.
    if ts > na:
        # tocbtn after navc: remove tocbtn first (higher index), then replace navc
        h = h[:ts] + h[te:]
        h = h[:na] + launch + h[nb:]
    else:
        h = h[:na] + h[nb:]
        # tocbtn index may have shifted if navc was after it (not the case), re-find
        ts = h.find('<button id="tocbtn"')
        te = h.find("</button>", ts) + len("</button>")
        h = h[:ts] + launch + h[te:]

    return h
