# -*- coding: utf-8 -*-
"""t91 后处理：接入样式/脚本；图例补充；示意图；逐句精简（只改本站说明，不动 CCI 原文）。"""
import re

EDITS = {
    ("tfu", "bible"): [
        ('<span class="mk-u">下面三个名称是神学归纳</span>，<span class="mk-x">不是三项联合信条里的条目名</span>；先看各指什么，再看三份文件哪里真用到约字。',
         '<span class="mk-u">三个名称是神学归纳</span>，<span class="mk-x">不是三项联合信条的条目名</span>；先看各指什么，再看三份文件哪里真用到约字。'),
    ],
}

FLOW_TFU = (
    '<div class="t91flow t90-in" aria-label="三份文件如何分工">'
    '<h3>🧭 一图记住：三份文件各管什么</h3>'
    '<p class="sub">本站概述：体裁不同，要解决的问题也不同，所以是三份而不是一份。</p>'
    '<ol class="t91steps">'
    '<li style="--i:0"><b>比利时信条</b>受逼迫的教会向官府申辩：我们是谁、信什么。</li>'
    '<li style="--i:1"><b>海德堡要理问答</b>领地教会的教导与讲道：用问答把信仰教给会众。</li>'
    '<li style="--i:2"><b>多特信经</b>全国总会的裁决：争论来时给出边界与牧养。</li>'
    '</ol>'
    '<p class="sub">缺了教导，信仰停在知道；缺了裁决，争论一来就失去边界；缺了告白，教会只剩法庭。三份合起来才是教导—宣告—守卫（本站概述）。</p>'
    '</div>'
)
FLOW_TEC = (
    '<div class="t91flow t90-in" aria-label="三份信经如何分工">'
    '<h3>🧭 一图记住：为何需要三份信经</h3>'
    '<p class="sub">本站概述：不是把同一段话写三遍，而是精度不同、要回答的问题不同。</p>'
    '<ol class="t91steps">'
    '<li style="--i:0"><b>使徒信经</b>洗礼认信：用一段叙事，按父—子—灵把救恩历史背下来。</li>'
    '<li style="--i:1"><b>尼西亚信经</b>会议定义：用同质一词守住子是真神，并认信圣灵。</li>'
    '<li style="--i:2"><b>亚他那修信经</b>可背的展开：把三一与基督一位二性写成短句和界限。</li>'
    '</ol>'
    '<p class="sub">只有叙事，遇到亚流之争就不够精确；只有会议定义，还需要能背、能划界的句子。三份合在一起，认信、定义与展开才齐全（本站概述）。</p>'
    '</div>'
)
FLOW_COV = (
    '<div class="t91flow t90-in" aria-label="圣约故事线">'
    '<h3>📜 一图记住：圣约怎样串起救赎历史</h3>'
    '<p class="sub">本站概述：事件据圣经记载；吾珥、西奈与部分年代为传统说法，标约。</p>'
    '<ol class="t91steps">'
    '<li style="--i:0"><b>吾珥蒙召</b>应许之约（年代约）</li>'
    '<li style="--i:1"><b>西奈</b>律法之约（地点与年代约）</li>'
    '<li style="--i:2"><b>耶路撒冷</b>大卫之约与圣殿</li>'
    '<li style="--i:3"><b>巴比伦</b>被掳（前 586）</li>'
    '<li style="--i:4"><b>基督里成全</b>死与复活（约）</li>'
    '<li style="--i:5"><b>安提阿／罗马</b>福音传到万国</li>'
    '</ol>'
    '</div>'
)

def _insert_in_section(h, sid, block):
    if block[:48] in h:
        return h
    i = h.find('id="%s"' % sid)
    if i < 0:
        print('t91flow MISS sid', sid)
        return h
    j = h.find('</h3>', i)
    k = h.find('</h4>', i)
    cuts = [x for x in (j, k) if x >= 0]
    if not cuts:
        print('t91flow MISS heading', sid)
        return h
    at = min(cuts) + 5
    return h[:at] + block + h[at:]

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
    if site == 'tfu' and page in ('compare', 'compare.html'):
        h = _insert_in_section(h, 'cp-why', FLOW_TFU)
    if site == 'tec' and page in ('compare', 'compare.html'):
        h = _insert_in_section(h, 'cmp-why', FLOW_TEC)
    if site == 'tfu' and page in ('bible', 'bible.html'):
        h = _insert_in_section(h, 'bi-cov', FLOW_COV)
    if site == 'tec' and page in ('bible', 'bible.html'):
        h = _insert_in_section(h, 'bible-cov', FLOW_COV)
    import t93; h = t93.apply(h, page, site)
    import t94; h = t94.apply(h, page, site)
    import t97; h = t97.apply(h, page, site)
    import t99; h = t99.apply(h, page, site)
    import t100; h = t100.apply(h, page, site)
    import t101; h = t101.apply(h, page, site)
    import t102; h = t102.apply(h, page, site)
    import t106; h = t106.apply(h, page, site)
    import t107; h = t107.apply(h, page, site)
    import t112; h = t112.apply(h, page, site)
    import t114; h = t114.apply(h, page, site)
    import t117; h = t117.apply(h, page, site)
    return h
