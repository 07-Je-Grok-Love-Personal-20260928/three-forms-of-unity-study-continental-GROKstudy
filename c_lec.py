# -*- coding: utf-8 -*-
"""讲座／释义精读页：从 data/lec-outlines.json 生成，标明来源与页码，与 CCI 原文分开。"""
import json, re, html as H
from core import *
from c_common import *

DATA = json.load(open("data/lec-outlines.json", encoding="utf-8"))

def _ok(s):
    s = (s or "").strip()
    if not s or len(s) < 8:
        return ""
    # drop mid-wrap fragments
    if s[-1] not in "。！？；…」』）)":
        if len(s) < 40:
            return ""
        # keep if it looks like a complete clause ending with comma? no
        return ""
    return s

def _cite(page):
    return f'<cite class="lec-cite">第 {page} 页</cite>'

def _pts(items, cls="lec-pts"):
    lis = []
    seen = set()
    for it in items:
        t = _ok(it.get("text", ""))
        if not t:
            continue
        k = re.sub(r"\s+", "", t)[:36]
        if k in seen:
            continue
        seen.add(k)
        # light marks on essence openers
        if t.startswith(("因此", "所以", "可见", "总之", "这就是说", "换句话说")):
            t = f'<span class="mk-hl">{t}</span>'
        lis.append(f'<li>{t} {_cite(it["page"])}</li>')
    return f'<ul class="{cls}">' + "".join(lis) + "</ul>" if lis else ""

def _ov(items):
    return _pts(items, "lec-ov")

def _qs(items):
    lis = []
    for it in items:
        t = (it.get("text") or "").strip()
        if len(t) < 4:
            continue
        lis.append(f'<li>{H.escape(t)} {_cite(it["page"])}</li>')
    return ('<div class="call app"><b>🧠 记忆提问</b><ol class="lec-q">' + "".join(lis) + "</ol></div>") if lis else ""

def _banner(kind):
    src = DATA["sources"][kind]
    return (
        f'<div class="lec-banner call note"><b>📚 {src["label"]}</b>'
        f'本页是对用户提供的讲座／释义 PDF 的<b>精华整理</b>，不是信条原文，也不可代替 CCI《赞美手册》中文版。'
        f'要点均注明印刷页码；对照阅读请打开对应原文库。来源：{H.escape(src["full"])}。</div>'
    )

def _sec(it, icon="book", tag=""):
    rng = (f'第 {it["page_start"]}–{it["page_end"]} 页'
           if it["page_start"] != it["page_end"] else f'第 {it["page_start"]} 页')
    title = it["title"]
    if it.get("lecture"):
        title = f'第{it["lecture"]}讲　{title}'
    body = ""
    hs = [h for h in it.get("headings") or [] if h.get("text") and len(h["text"]) < 36]
    if hs:
        body += '<p class="lec-struct">结构：' + " · ".join(
            f'{H.escape(h["text"])}<cite class="lec-cite">{h["page"]}</cite>' for h in hs[:8]
        ) + "</p>"
    if it.get("overview"):
        body += "<p class='lec-k'>本段主线</p>" + _ov(it["overview"])
    if it.get("points"):
        body += "<p class='lec-k'>要点</p>" + _pts(it["points"])
    body += _qs(it.get("questions") or [])
    body += f'<p class="lec-src">出处：{H.escape(it.get("source") or "")} {rng}。</p>'
    return L3(it["id"], title, body, icon=icon, tag=tag or rng)

def part_lec_hc():
    src = DATA["sources"]["hc"]
    items = DATA["hc"]
    groups = [
        ("lech-intro", "介绍与圣约", lambda it: it.get("lecture") in {"一","二","二十","二十一"}, "book", "#d4af37"),
        ("lech-m1", "第一部　愁苦（主日 1–4）", lambda it: it.get("lecture") in {"三","四","五","六"}, "alert", "#e07a5f"),
        ("lech-m2", "第二部　得救（主日 5–31）", lambda it: it.get("lecture") in {
            "七","八","九","十","十一","十二","十三","十四","十五","十六","十七","十八","十九","二十二","二十三","二十四","二十五","二十六"}, "heart", "#5aa9e6"),
        ("lech-m3", "第三部　感恩（主日 32–52）", lambda it: True, "flame", "#81b29a"),
    ]
    used = set()
    b = _banner("hc")
    b += flow([
        ("介绍", "为何需要要理问答", "#d4af37"),
        ("愁苦", "主日 1–4　知罪", "#e07a5f"),
        ("得救", "主日 5–31　中保·信心·圣礼", "#5aa9e6"),
        ("圣约", "约与洗礼的连接", "#a78bfa"),
        ("感恩", "主日 32–52　律法与主祷文", "#81b29a"),
    ])
    b += key("抓住一条线：<b>用神所规定的方法敬拜神</b>，而不是按自己的方法；要理问答是教会用圣经教义牧养人的工具，不能代替圣经，却帮助人记住圣经的核心。对照 CCI 原文见" + '<a href="hct.html">第七部分</a>。')
    b += note("本页 53 讲覆盖全书 52 主日，并另有「圣约」上下两讲。每讲只留主线、要点与页码，不作全文转录。")
    for gid, gtitle, pred, ico, col in groups:
        chunk = []
        for it in items:
            if it["id"] in used:
                continue
            if pred(it):
                used.add(it["id"])
                chunk.append(_sec(it, ico))
        b += L2(gid, "", gtitle, "".join(chunk))
    b += app('回到深读页：<a href="hc.html">二、海德堡要理问答深读</a> · 原文：<a href="hct.html">七、HC 原文</a>。')
    return L1("lec-hc", "十三", "海德堡要理问答讲座精读", "heart",
              "中国改革宗圣经学院 53 讲的精华整理（讲座材料，非 CCI 原文）；按愁苦—得救—感恩排列，并注明页码。", b)

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
        ("lecd-hist", "历史回顾：从伯拉纠到多特大会", "hist", "clock", "#e07a5f"),
        ("lecd-h1", "第一项　论神的拣选与弃绝", "h1", "scale", "#d4af37"),
        ("lecd-h2", "第二项　论基督的死和人藉此而得的救赎", "h2", "heart", "#5aa9e6"),
        ("lecd-h34", "第三、四项　论人的败坏、向神归正及其方法", "h34", "alert", "#e07a5f"),
        ("lecd-h5", "第五项　真信徒能持守信仰", "h5", "shield", "#81b29a"),
        ("lecd-sum", "总结", "sum", "flame", "#a78bfa"),
    ]
    b = _banner("dort")
    b += flow([
        ("历史", "阿米念与抗辩书", "#e07a5f"),
        ("拣选", "第一项", "#d4af37"),
        ("救赎", "第二项", "#5aa9e6"),
        ("归正", "第三、四项", "#e07a5f"),
        ("保守", "第五项", "#81b29a"),
    ])
    b += key("记忆口诀仍是后来的 TULIP，但本讲座按信经本身的顺序讲解：<b>父的拣选、子的救赎、灵的归正、三一神的保守</b>。对照 CCI 原文见" + '<a href="dtt.html">第九部分</a>。')
    b += note("作者亚瑟·范·德尔登。每条只留讲解要点与页码；信经正文仍以 CCI 逐字文本为准。")
    for gid, gtitle, keyg, ico, col in groups:
        chunk = "".join(_sec(it, ico) for it in items if _dort_group(it) == keyg)
        b += L2(gid, "", gtitle, chunk)
    b += app('回到深读页：<a href="dort.html">四、多特信经深读</a> · 原文：<a href="dtt.html">九、Dort 原文</a>。')
    return L1("lec-dort", "十四", "靠主夸口：多特信经学习精读", "scale",
              "亚瑟·范·德尔登《靠主夸口》的精华整理（讲解材料，非 CCI 原文）；按五项教义排列，并注明页码。", b)

def _bc_group(it):
    p = it["page_start"]
    title = it["title"]
    if p < 11:
        return "intro"
    # article numbers from title when present
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
        ("lecb-intro", "为何学习，以及历史背景", "intro", "clock", "#e07a5f"),
        ("lecb-god", "论神与启示（第 1–11 条）", "god", "book", "#5aa9e6"),
        ("lecb-creat", "创造、护理、人的堕落（第 12–15 条）", "creat", "map", "#81b29a"),
        ("lecb-christ", "基督与救恩（第 16–26 条）", "christ", "heart", "#d4af37"),
        ("lecb-church", "教会与治理（第 27–32 条）", "church", "church", "#e07a5f"),
        ("lecb-end", "圣礼、政府与末日（第 33–37 条）", "end", "flame", "#6bb8d6"),
    ]
    b = _banner("bc")
    b += flow([
        ("神与启示", "1–11", "#5aa9e6"),
        ("创造与堕落", "12–15", "#81b29a"),
        ("基督与救恩", "16–26", "#d4af37"),
        ("教会", "27–32", "#e07a5f"),
        ("圣礼与末事", "33–37", "#6bb8d6"),
    ])
    b += key("德布利写信条，是要在逼迫中向国王与世人表明：改革宗信徒是<b>按圣经告白信仰的守法子民</b>，不是叛乱者。本页是鲍曼释义的精华，对照 CCI 原文见" + '<a href="bct.html">第八部分</a>。')
    b += note("作者克莱伦斯·鲍曼。37 条及两篇导论均已覆盖；只留主线与页码，不作全书转录。")
    for gid, gtitle, keyg, ico, col in groups:
        chunk = "".join(_sec(it, ico) for it in items if _bc_group(it) == keyg)
        b += L2(gid, "", gtitle, chunk)
    b += app('回到深读页：<a href="bc.html">三、比利时信条深读</a> · 原文：<a href="bct.html">八、BC 原文</a>。')
    return L1("lec-bc", "十五", "比利时信条释义精读", "scroll",
              "克莱伦斯·鲍曼《比利时信条》释义的精华整理（释义材料，非 CCI 原文）；按 37 条排列，并注明页码。", b)
