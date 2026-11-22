# -*- coding: utf-8 -*-
"""讲座／释义页：本站整理要点 + PDF 逐字全文，标明来源与印刷页码，与 CCI 原文分开。"""
import json, re, html as H
from pathlib import Path
from core import *
from c_common import *

DATA = json.load(open("data/lec-outlines.json", encoding="utf-8"))
_VDIR = Path("data/lec-verbatim")
VER = {k: json.loads((_VDIR / f"{k}.json").read_text(encoding="utf-8"))
       for k in ("hc", "dort", "bc") if (_VDIR / f"{k}.json").exists()}

EXTRA = []   # (key, filename, label, icon, html)
CHAIN = {}   # key -> (prev_key|None, next_key|None, hub_key)

def _cid(kind, it):
    """Stable unique section id (Dort/BC both used p{page} and collided)."""
    i = it["id"]
    if kind == "hc":
        return i
    prefix = {"dort": "lecd-", "bc": "lecb-"}[kind]
    return i if i.startswith(prefix) else prefix + i


def _ok(s):
    s = (s or "").strip()
    if not s or len(s) < 8:
        return ""
    if s[-1] not in "。！？；…」』）)":
        if len(s) < 40:
            return ""
        return ""
    return s

def _cite(page):
    return f'<cite class="lec-cite">第 {page} 页</cite>'

def _pts(items, cls="lec-pts"):
    lis, seen = [], set()
    for it in items:
        t = _ok(it.get("text", ""))
        if not t:
            continue
        k = re.sub(r"\s+", "", t)[:36]
        if k in seen:
            continue
        seen.add(k)
        if t.startswith(("因此", "所以", "可见", "总之", "这就是说", "换句话说")):
            t = f'<span class="mk-hl">{t}</span>'
        lis.append(f'<li>{t} {_cite(it["page"])}</li>')
    return f'<ul class="{cls}">' + "".join(lis) + "</ul>" if lis else ""

def _qs(items):
    lis = []
    for it in items:
        t = (it.get("text") or "").strip()
        if len(t) < 4:
            continue
        lis.append(f'<li>{H.escape(t)} {_cite(it["page"])}</li>')
    return ('<div class="call app"><b>🧠 记忆提问</b><ol class="lec-q">' + "".join(lis) + "</ol></div>") if lis else ""

def _banner(kind, full=True):
    src = DATA["sources"][kind]
    kind_zh = "全文逐字" if full else "精华整理"
    return (
        f'<div class="lec-banner call note"><b>📚 {src["label"]}</b>'
        f'本页收录用户授权发布的讲座／释义 PDF 的<b>{kind_zh}</b>，并在每章之前附上本站整理的要点。'
        f'这不是信条原文，也不可代替 CCI《赞美手册》中文版。'
        f'原文仅整理了断行、页眉页脚与页码，没有改写或删节。来源：{H.escape(src["full"])}。</div>'
    )

def _summary(it):
    """Refined site key-points, clearly labelled as not verbatim."""
    body = '<div class="lec-sum"><div class="lec-flag sum">本站整理要点 · 非逐字</div>'
    hs = [h for h in it.get("headings") or [] if h.get("text") and len(h["text"]) < 36 and "。" not in h["text"]]
    if hs:
        body += '<p class="lec-struct">结构：' + " · ".join(
            f'{H.escape(h["text"])}<cite class="lec-cite">{h["page"]}</cite>' for h in hs[:8]
        ) + "</p>"
    if it.get("overview"):
        body += "<p class='lec-k'>📌 本段主线</p>" + _pts(it["overview"], "lec-ov")
    if it.get("points"):
        body += "<p class='lec-k'>✨ 要点</p>" + _pts(it["points"])
    body += _qs(it.get("questions") or [])
    body += "</div>"
    return body

def _fn_refs(text):
    """Mark in-text footnote callouts like '败坏。1他' without changing the characters."""
    def repl(m):
        return f'{m.group(1)}<sup class="lec-fnr">{m.group(2)}</sup>{m.group(3)}'
    return re.sub(r'([。，、；：”」）])(\d{1,2})([\u4e00-\u9fffA-Za-z“「（])', repl, text)

def _verbatim(ch):
    out = ['<div class="lec-verbatim">',
           '<div class="lec-flag src">讲座原文 · 逐字（仅整理断行与页眉页脚）</div>']
    for b in ch.get("blocks") or []:
        typ, text, page = b.get("type"), b.get("text") or "", b.get("page")
        if typ == "pg":
            aid=H.escape(str(ch.get("aid") or ch["id"]))
            out.append(f'<a class="lec-pg" id="{aid}-p{page}" href="#{aid}-p{page}">〔{page}〕</a>')
            continue
        esc = _fn_refs(H.escape(text))
        if typ == "h":
            out.append(f'<h5>{esc}</h5>')
        elif typ == "q":
            out.append(f'<blockquote class="lec-q">{esc}</blockquote>')
        elif typ == "li":
            # bare item; wrap each in its own list to avoid broken ol state
            out.append(f'<ul><li>{esc}</li></ul>')
        elif typ == "fn":
            out.append(f'<p class="lec-fn">📝 {esc}</p>')
        else:
            out.append(f'<p>{esc}</p>')
    rng = (f'第 {ch["page_start"]}–{ch["page_end"]} 页'
           if ch["page_start"] != ch["page_end"] else f'第 {ch["page_start"]} 页')
    out.append(f'<p class="lec-src">出处：{H.escape(ch.get("source") or "")} {rng}。</p>')
    out.append("</div>")
    return "".join(out)

def _chapter_title(it):
    title = it["title"]
    if it.get("lecture"):
        title = f'第{it["lecture"]}讲　{title}'
    return title

def _sec_full(it, ch, icon="book", kind="hc"):
    rng = (f'第 {it["page_start"]}–{it["page_end"]} 页'
           if it["page_start"] != it["page_end"] else f'第 {it["page_start"]} 页')
    body = _summary(it) + _verbatim(ch)
    return L3(_cid(kind, it), _chapter_title(it), body, icon=icon, tag=rng)

def _book_toc(kind, groups, items, vmap, files):
    """In-page multi-level expandable TOC."""
    out = ['<nav class="lec-toc" aria-label="本书目录">']
    for gid, gtitle, pred, ico, filename in groups:
        kids = [it for it in items if pred(it)]
        out.append(f'<details open><summary>{H.escape(gtitle)}</summary><ol>')
        for it in kids:
            href = f'{filename}#{_cid(kind, it)}'
            out.append(f'<li><a href="{href}">{H.escape(_chapter_title(it))}</a> '
                       f'<cite class="lec-cite">第 {it["page_start"]}–{it["page_end"]} 页</cite>')
            heads = [h for h in it.get("headings") or [] if h.get("text") and len(h["text"]) < 28 and "。" not in h["text"]]
            if heads:
                out.append("<ol>")
                for h in heads[:8]:
                    out.append(f'<li>{H.escape(h["text"])} <cite class="lec-cite">{h["page"]}</cite></li>')
                out.append("</ol>")
            out.append("</li>")
        out.append("</ol></details>")
    out.append("</nav>")
    return "".join(out)

def _register_groups(kind, hub, hub_num, groups, items, icon_default, vmap):
    """Build one file per group, register EXTRA/CHAIN, return (group_cards_html)."""
    # map id -> chapter verbatim
    vchap = {c["id"]: c for c in vmap.get("chapters", [])}
    file_keys = []
    cards = []
    saved_f, saved_c2 = CUR["f"], CUR["c2"]
    for gid, gtitle, pred, ico, filename in groups:
        kids = [it for it in items if pred(it)]
        if not kids:
            continue
        key = filename.replace(".html", "")
        CUR["f"] = filename
        def _ch(it):
            ch = dict(vchap.get(it["id"], {"id": it["id"], "blocks": [],
                       "page_start": it["page_start"], "page_end": it["page_end"],
                       "source": it.get("source") or ""}))
            ch["aid"] = _cid(kind, it)
            return ch
        chunk = "".join(_sec_full(it, _ch(it), ico, kind=kind)
                        for it in kids)
        body = L2(gid, "", gtitle, chunk)
        # slim header for the chapter file (no second L1 — stays under the hub TOC)
        first, last = kids[0], kids[-1]
        lead = (f'{DATA["sources"][kind]["label"]}本册分组：{gtitle}。'
                f'印刷第 {first["page_start"]}–{last["page_end"]} 页。先读本站要点，再读逐字原文。')
        html = (f'<p class="lec-crumb"><a href="{hub}.html">返回{hub_num}、目录</a> · {H.escape(gtitle)}</p>'
                f'<p class="lead">{lead}</p>' + body)
        EXTRA.append((key, filename, f'{hub_num} {gtitle}', ico, html))
        file_keys.append(key)
        nch = len(kids)
        cards.append((ico, gtitle,
                      f'{nch} 章 · 第 {first["page_start"]}–{last["page_end"]} 页',
                      filename))
    CUR["f"], CUR["c2"] = saved_f, saved_c2
    for i, key in enumerate(file_keys):
        prev = file_keys[i-1] if i else None
        nxt = file_keys[i+1] if i+1 < len(file_keys) else None
        CHAIN[key] = (prev, nxt, hub)
    # group cards on the hub
    grid = '<div class="grid g3">' + "".join(
        f'<a class="card vcard" href="{href}" style="--c:#d4af37"><div class="ct"><span>{ic(ico,"ic")}</span>{H.escape(title)}</div><p>{H.escape(desc)}</p></a>'
        for ico, title, desc, href in cards
    ) + "</div>"
    return grid

def _hub(kind, l1_id, num, title, ico, lead, groups, items, extra_intro=""):
    vmap = VER[kind]
    files = [g[4] for g in groups]
    b = _banner(kind, full=True)
    b += extra_intro
    b += '<p class="lec-k">本书目录</p>'
    b += _book_toc(kind, groups, items, vmap, files)
    b += '<p class="lec-k">分组阅读</p>'
    b += _register_groups(kind, l1_id, num, groups, items, ico, vmap)
    return L1(l1_id, num, title, ico, lead, b)

# ---------- grouping ----------
def _hc_lecture_in(it, names):
    return it.get("lecture") in names

def part_lec_hc():
    items = DATA["hc"]
    groups = [
        ("lech-intro", "介绍", lambda it: it.get("lecture") in {"一", "二"}, "book", "lec-hc-intro.html"),
        ("lech-m1", "第一部　愁苦（主日 1–4）", lambda it: it.get("lecture") in {"三", "四", "五", "六"}, "alert", "lec-hc-m1.html"),
        ("lech-m2a", "第二部　得救（上）（主日 5–25）", lambda it: it.get("lecture") in {
            "七", "八", "九", "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九"}, "heart", "lec-hc-m2a.html"),
        ("lech-cov", "圣约（上／下）", lambda it: it.get("lecture") in {"二十", "二十一"}, "link", "lec-hc-cov.html"),
        ("lech-m2b", "第二部　得救（下）（主日 26–31）", lambda it: it.get("lecture") in {
            "二十二", "二十三", "二十四", "二十五", "二十六"}, "heart", "lec-hc-m2b.html"),
        ("lech-m3a", "第三部　感恩（上）（主日 32–38）", lambda it: it.get("lecture") in {
            "二十七", "二十八", "二十九", "三十", "三十一", "三十二", "三十三", "三十四", "三十五", "三十六"}, "flame", "lec-hc-m3a.html"),
        ("lech-m3b", "第三部　感恩（下）（主日 39–52）", lambda it: it.get("lecture") in {
            "三十七", "三十八", "三十九", "四十", "四十一", "四十二", "四十三", "四十四", "四十五", "四十六",
            "四十七", "四十八", "四十九", "五十", "五十一", "五十二", "五十三"}, "flame", "lec-hc-m3b.html"),
    ]
    intro = flow([
        ("介绍", "为何需要要理问答", "#d4af37"),
        ("愁苦", "主日 1–4　知罪", "#e07a5f"),
        ("得救", "主日 5–31　中保·信心·圣礼", "#5aa9e6"),
        ("圣约", "约与洗礼的连接", "#a78bfa"),
        ("感恩", "主日 32–52　律法与主祷文", "#81b29a"),
    ])
    intro += key("抓住一条线：<b>用神所规定的方法敬拜神</b>，而不是按自己的方法；要理问答是教会用圣经教义牧养人的工具，不能代替圣经，却帮助人记住圣经的核心。对照 CCI 原文见" + '<a href="hct.html">第七部分</a>。')
    intro += note("本页目录覆盖全部 53 讲（52 主日，另加「圣约」上下两讲）。每讲先给出本站整理要点，再给出讲座逐字原文，并标明印刷页码。")
    intro += app('回到深读页：<a href="hc.html">二、海德堡要理问答深读</a> · 原文：<a href="hct.html">七、HC 原文</a>。')
    return _hub("hc", "lec-hc", "十三", "海德堡要理问答讲座", "heart",
                "中国改革宗圣经学院 53 讲的逐字全文与本站要点（讲座材料，非 CCI 原文）；按愁苦—得救—感恩排列，并注明页码。",
                groups, items, intro)

def _dort_group(it):
    p = it["page_start"]
    if it["id"] == "hist" or p < 13:
        return "hist"
    if p < 85:
        return "h1"
    if p < 123:
        return "h2"
    if p < 211:
        return "h34"
    if it["id"] == "sum" or p >= 291:
        return "sum"
    return "h5"

def part_lec_dort():
    items = DATA["dort"]
    groups = [
        ("lecd-hist", "历史回顾：从伯拉纠到多特大会", lambda it: _dort_group(it) == "hist", "clock", "lec-dort-hist.html"),
        ("lecd-h1", "第一项　论神的拣选与弃绝", lambda it: _dort_group(it) == "h1", "scale", "lec-dort-h1.html"),
        ("lecd-h2", "第二项　论基督的死和人藉此而得的救赎", lambda it: _dort_group(it) == "h2", "heart", "lec-dort-h2.html"),
        ("lecd-h34", "第三、四项　论人的败坏、向神归正及其方法", lambda it: _dort_group(it) == "h34", "alert", "lec-dort-h34.html"),
        ("lecd-h5", "第五项　真信徒能持守信仰", lambda it: _dort_group(it) == "h5", "shield", "lec-dort-h5.html"),
        ("lecd-sum", "总结", lambda it: _dort_group(it) == "sum", "flame", "lec-dort-sum.html"),
    ]
    intro = flow([
        ("历史", "阿米念与抗辩书", "#e07a5f"),
        ("拣选", "第一项", "#d4af37"),
        ("救赎", "第二项", "#5aa9e6"),
        ("归正", "第三、四项", "#e07a5f"),
        ("保守", "第五项", "#81b29a"),
    ])
    intro += key("记忆口诀仍是后来的 TULIP，但本讲座按信经本身的顺序讲解：<b>父的拣选、子的救赎、灵的归正、三一神的保守</b>。对照 CCI 原文见" + '<a href="dtt.html">第九部分</a>。')
    intro += note("作者亚瑟·范·德尔登。每条先给出本站整理要点，再给出讲座逐字原文；信经正文仍以 CCI 逐字文本为准。")
    intro += app('回到深读页：<a href="dort.html">四、多特信经深读</a> · 原文：<a href="dtt.html">九、Dort 原文</a>。')
    return _hub("dort", "lec-dort", "十四", "靠主夸口：多特信经学习", "scale",
                "亚瑟·范·德尔登《靠主夸口》的逐字全文与本站要点（讲解材料，非 CCI 原文）；按五项教义排列，并注明页码。",
                groups, items, intro)

def _bc_group(it):
    p = it["page_start"]
    title = it["title"]
    if p < 11:
        return "intro"
    order = [
        ("第一条", "god"), ("第二条", "god"), ("第三条", "god"), ("第四条", "god"),
        ("第五条", "god"), ("第六条", "god"), ("第七条", "god"), ("第八", "god"),
        ("第十条", "god"), ("第十一条", "god"),
        ("第十二条", "creat"), ("第十三条", "creat"), ("第十四条", "creat"),
        ("第十五条", "creat"),
        ("第十六条", "christ"), ("第十七条", "christ"), ("第十八条", "christ"),
        ("第十九条", "christ"), ("第二十条", "christ"), ("第二十一条", "christ"),
        ("第二十二条", "christ"), ("第二十三条", "christ"), ("第二十四条", "christ"),
        ("第二十五条", "christ"), ("第二十六条", "christ"),
        ("第二十七条", "church"), ("第二十八条", "church"), ("第二十九条", "church"),
        ("第三十条", "church"), ("第三十一条", "church"), ("第三十二条", "church"),
        ("第三十三条", "end"), ("第三十四条", "end"), ("第三十五条", "end"),
        ("第三十六条", "end"), ("第三十七条", "end"),
    ]
    for pref, g in order:
        if title.startswith(pref):
            return g
    return "end"

def part_lec_bc():
    items = DATA["bc"]
    groups = [
        ("lecb-intro", "为何学习，以及历史背景", lambda it: _bc_group(it) == "intro", "clock", "lec-bc-intro.html"),
        ("lecb-god", "论神与启示（第 1–11 条）", lambda it: _bc_group(it) == "god", "book", "lec-bc-god.html"),
        ("lecb-creat", "创造、护理、人的堕落（第 12–15 条）", lambda it: _bc_group(it) == "creat", "map", "lec-bc-creat.html"),
        ("lecb-christ", "基督与救恩（第 16–26 条）", lambda it: _bc_group(it) == "christ", "heart", "lec-bc-christ.html"),
        ("lecb-church", "教会与治理（第 27–32 条）", lambda it: _bc_group(it) == "church", "church", "lec-bc-church.html"),
        ("lecb-end", "圣礼、政府与末日（第 33–37 条）", lambda it: _bc_group(it) == "end", "flame", "lec-bc-end.html"),
    ]
    intro = flow([
        ("神与启示", "1–11", "#5aa9e6"),
        ("创造与堕落", "12–15", "#81b29a"),
        ("基督与救恩", "16–26", "#d4af37"),
        ("教会", "27–32", "#e07a5f"),
        ("圣礼与末事", "33–37", "#6bb8d6"),
    ])
    intro += key("德布利写信条，是要在逼迫中向国王与世人表明：改革宗信徒是<b>按圣经告白信仰的守法子民</b>，不是叛乱者。对照 CCI 原文见" + '<a href="bct.html">第八部分</a>。')
    intro += note("作者克莱伦斯·鲍曼。37 条及两篇导论均收录逐字全文；每章先给出本站整理要点，再给出释义原文。")
    intro += app('回到深读页：<a href="bc.html">三、比利时信条深读</a> · 原文：<a href="bct.html">八、BC 原文</a>。')
    return _hub("bc", "lec-bc", "十五", "比利时信条释义", "scroll",
                "克莱伦斯·鲍曼《比利时信条》释义的逐字全文与本站要点（释义材料，非 CCI 原文）；按 37 条排列，并注明页码。",
                groups, items, intro)
