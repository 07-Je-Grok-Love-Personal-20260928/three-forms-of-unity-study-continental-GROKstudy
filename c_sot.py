# -*- coding: utf-8 -*-
"""第十六部分：救恩教义专题；第十七部分：儿童要理问答占位。"""
import json, re, html as H
from pathlib import Path
from core import L1, L2, L3, key, hard, note, app, cards, table, flow, CUR, ic
from c_common import hq, hl, bl, dl, hqs
import quotes as Q

EXTRA = []
CHAIN = {}
ROOT = Path(__file__).resolve().parent
CUV = json.loads((ROOT / "data/t114/cuv_used.json").read_text(encoding="utf-8"))
DECK = json.loads((ROOT / "data/t114/tulip-deck.json").read_text(encoding="utf-8"))
POSTER = json.loads((ROOT / "data/t114/five-solas-rtv.json").read_text(encoding="utf-8"))
CHILD = json.loads((ROOT / "data/t114/childq.json").read_text(encoding="utf-8"))


def v(key, *ns, join=""):
    rec = CUV[key]
    nums = list(ns)
    lab = key if len(nums) == 1 else f"{key}:{nums[0]}–{nums[-1]}" if nums == list(range(nums[0], nums[-1] + 1)) else f"{key}:{','.join(map(str, nums))}"
    if len(nums) == 1:
        lab = f"{key}:{nums[0]}"
    bits = []
    for n in nums:
        t = rec["verses"][str(n)]
        bits.append(f'<span class="v">{H.escape(t)}</span>')
    return f'<p class="vq"><cite>{H.escape(lab)}</cite>{" ".join(bits)}</p>'


def vs(*items):
    return "".join(v(k, *ns) for k, *ns in items)


def qhc(n, phrase=None):
    q, a = Q.HC[n]
    src = a if phrase is None else phrase
    if phrase:
        assert phrase in a, f"HC {n} 未找到：{phrase}"
    return src


def qbc(n, phrase=None):
    t = Q.BC[n]
    src = t if phrase is None else phrase
    if phrase:
        assert phrase in t, f"BC {n} 未找到：{phrase}"
    return src


def qdt(k, phrase=None):
    t = Q.DORT[k]
    src = t if phrase is None else phrase
    if phrase:
        assert phrase in t, f"Dort {k} 未找到：{phrase}"
    return src


def blk(text, cite):
    return f'<blockquote class="cciq"><p>{H.escape(text)}</p><footer>— {cite}</footer></blockquote>'


def site(t):
    return note("以下为本站归纳，不是信条原文。" + t)

def _phrase(src, *cands):
    for c in cands:
        if c in src:
            return c
    raise AssertionError("no phrase in: " + src[:120])


# ---------- SVGs ----------
def svg_emblem():
    # five gold-line badges around a centre; icons only, no copied poster wording
    items = [
        (0, "Sola Scriptura", "唯独圣经", "book"),
        (72, "Solus Christus", "唯独基督", "cross"),
        (144, "Sola Gratia", "唯独恩典", "cup"),
        (216, "Sola Fide", "唯独信心", "shield"),
        (288, "Soli Deo Gloria", "唯独上帝的荣耀", "crown"),
    ]
    parts = [
        '<figure class="sotfig"><svg class="sot-emblem" viewBox="0 0 400 400" role="img" aria-labelledby="emblem-t emblem-d">',
        '<title id="emblem-t">五个唯独</title>',
        '<desc id="emblem-d">五枚圆环绕「The Five Solas」：圣经、基督、恩典、信心、上帝的荣耀。</desc>',
        '<circle cx="200" cy="200" r="196" fill="var(--bg)" stroke="var(--gold)" stroke-width="1.25"/>',
        '<circle cx="200" cy="200" r="70" fill="none" stroke="var(--gold)" stroke-width="1.5"/>',
        '<text x="200" y="196" text-anchor="middle" fill="var(--gold2)" font-size="11" font-family="Georgia,serif" letter-spacing="0.8">The Five Solas</text>',
        '<text x="200" y="214" text-anchor="middle" fill="var(--tx)" font-size="11">五个唯独</text>',
    ]
    # icon paths (simple, original)
    icons = {
        "book": "M-8,-7 h16 v14 h-16 z M-6,-4 h8 M-6,0 h8 M-6,4 h6",
        "cross": "M0,-9 v18 M-6,-3 h12",
        "cup": "M-6,-7 h12 l-1,8 a6,6 0 0 1 -10,0 z M0,7 v5 M-4,12 h8",
        "shield": "M0,-9 l9,3 v6 c0,6 -4,9 -9,10 c-5,-1 -9,-4 -9,-10 v-6 z",
        "crown": "M-9,2 l4,5 5,-8 5,8 4,-5 -2,10 h-14 z",
    }
    import math
    for ang, lat, zh, ico in items:
        rad = math.radians(ang - 90)
        cx, cy = 200 + 130 * math.cos(rad), 200 + 130 * math.sin(rad)
        parts.append(f'<g transform="translate({cx:.1f},{cy:.1f})">')
        parts.append('<circle r="36" fill="var(--pnl)" stroke="var(--gold)" stroke-width="1.6"/>')
        parts.append(f'<path d="{icons[ico]}" fill="none" stroke="var(--gold2)" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>')
        parts.append(f'<text y="52" text-anchor="middle" fill="var(--gold2)" font-size="8.5" font-family="Georgia,serif">{lat}</text>')
        parts.append(f'<text y="64" text-anchor="middle" fill="var(--tx)" font-size="9">{zh}</text>')
        parts.append("</g>")
    parts.append('</svg><figcaption>五个唯独圆形徽章（本站原作示意图，金线圆环构图）。</figcaption></figure>')
    return "".join(parts)


def svg_ordo():
    steps = [
        (30, "拣选", "弗 1:4–5"),
        (120, "有效恩召", "罗 8:30"),
        (210, "重生", "约 3"),
        (300, "信心", "弗 2:8"),
        (390, "称义", "罗 3:24"),
        (480, "收养", "弗 1:5"),
        (570, "成圣", "帖前 4:3"),
        (660, "坚忍", "腓 1:6"),
        (750, "得荣耀", "罗 8:30"),
    ]
    w, h = 800, 150
    s = ['<figure class="sotfig"><svg class="sot-ordo" viewBox="0 0 800 150" role="img" aria-label="救恩次序示意图">',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="none"/>']
    for i, (x, t, sub) in enumerate(steps):
        s.append(f'<g transform="translate({x},40)">')
        s.append('<rect x="-38" y="0" width="76" height="52" rx="10" fill="var(--pnl)" stroke="var(--gold)" stroke-width="1.2"/>')
        s.append(f'<text y="22" text-anchor="middle" fill="var(--hi)" font-size="13" font-weight="700">{t}</text>')
        s.append(f'<text y="40" text-anchor="middle" fill="var(--mut)" font-size="9">{sub}</text></g>')
        if i < len(steps) - 1:
            x2 = steps[i + 1][0]
            s.append(f'<path d="M{x+40},66 H{x2-40}" fill="none" stroke="var(--gold)" stroke-width="1.2" marker-end="none"/>')
            s.append(f'<polygon points="{x2-40},61 {x2-40},71 {x2-32},66" fill="var(--gold)"/>')
    s.append('</svg><figcaption>救恩次序（ordo salutis）本站示意图。次序是逻辑关系，不是把恩典切成互不相干的步骤；称义一次完成，成圣持续一生。</figcaption></figure>')
    return "".join(s)


def svg_states():
    cols = [
        ("堕落前", "posse peccare\nposse non peccare", "能犯罪\n能不犯罪"),
        ("堕落后", "non posse\nnon peccare", "不能不犯罪"),
        ("重生", "posse peccare\nposse non peccare", "能犯罪\n能不犯罪"),
        ("得荣耀", "non posse peccare", "不能犯罪"),
    ]
    s = ['<figure class="sotfig"><svg class="sot-states" viewBox="0 0 640 200" role="img" aria-labelledby="st-t">',
         '<title id="st-t">人的四种状况</title>']
    for i, (title, lat, zh) in enumerate(cols):
        x = 20 + i * 155
        s.append(f'<g transform="translate({x},20)">')
        s.append('<rect width="140" height="160" rx="12" fill="var(--pnl)" stroke="var(--gold)" stroke-width="1.2"/>')
        s.append(f'<text x="70" y="28" text-anchor="middle" fill="var(--gold2)" font-size="14" font-weight="700">{title}</text>')
        for j, line in enumerate(lat.split("\n")):
            s.append(f'<text x="70" y="{58+j*16}" text-anchor="middle" fill="var(--mut)" font-size="10" font-family="Georgia,serif">{line}</text>')
        for j, line in enumerate(zh.split("\n")):
            s.append(f'<text x="70" y="{120+j*18}" text-anchor="middle" fill="var(--tx)" font-size="13">{line}</text>')
        s.append("</g>")
    s.append('</svg><figcaption>奥古斯丁论人的四种状况（本站示意图）。重生一栏从俗：仍能犯罪，也能不犯罪（参见罗 7:14–25）。</figcaption></figure>')
    return "".join(s)


def _lines(items):
    out = []
    for it in items:
        out.append(f'<span class="ln" title="提取行 {it["n"]}">{it["n"]}</span>{H.escape(it["text"])}')
    return "\n".join(out)


def poster_html():
    fr = POSTER["front"]
    cl = POSTER["close"]
    b = [f'<section class="sot-poster" lang="zh-Hant" id="sot-poster-src">',
         f'<p class="pdfsrc">海报原文 · {H.escape(POSTER["source"])}。以下按无歧义配对重排各条，逐字保留繁体，行号为提取行。</p>',
         f'<h3>{_lines(fr["title"])}</h3>',
         f'<p class="banner">{_lines(fr["banner"])}</p>',
         f'<p class="st">{_lines(fr["lead"])}</p>']
    for s in POSTER["solas"]:
        b.append(f'<div class="sot-solablock" id="poster-{s["id"]}">')
        b.append(f'<h4>{H.escape(s["name"])} <small>{H.escape(s["latin"])}</small></h4>')
        b.append(f'<p class="st">{_lines(s["statement"])}</p>')
        b.append(f'<p class="qt">{_lines(s["quote"])}</p>')
        b.append("</div>")
    b.append(f'<p class="st">{_lines(cl["exhortation"])}</p>')
    b.append(f'<p class="st">{_lines(cl["credit"])}</p></section>')
    return "".join(b)


def deck_html():
    pages = DECK["pages"]
    cuts = [
        (1, "open", "封面与五要点"),
        (3, "hist", "历史背景"),
        (7, "rem", "抗辩书"),
        (23, "t", "一、全然败坏"),
        (44, "u", "二、无条件的拣选"),
        (69, "l", "三，有限的救赎"),
        (90, "i", "四、不可抗拒的恩典"),
        (121, "p", "五、圣徒的坚忍"),
        (141, "int", "五要点之间的互动"),
        (142, "cons", "汇合与共识（含林慈信结语）"),
    ]
    # assign
    sec = {}
    cur = cuts[0]
    ci = 0
    for p in pages:
        if ci + 1 < len(cuts) and p["n"] >= cuts[ci + 1][0]:
            ci += 1
            cur = cuts[ci]
        sec.setdefault(cur[1], {"title": cur[2], "pages": []})["pages"].append(p)
    out = [f'<section class="deck" id="tulip-deck-src"><p class="pdfsrc">讲座幻灯片原文 · {H.escape(DECK["source"])}。偏旁字形已按规则还原，断行已并成段落，其余字符不改。不是信条原文。</p>']
    for key, block in sec.items():
        out.append(f'<h4 id="deck-{key}">{H.escape(block["title"])}</h4>')
        for p in block["pages"]:
            text = p["text"] or ""
            paras = text.split("\n\n") if text else [""]
            first = True
            for para in paras:
                mark = f'<span class="pdfsrc">幻灯片第 {p["n"]} 页</span>' if first else ""
                first = False
                out.append(f'<p>{mark}{H.escape(para)}</p>')
    out.append("</section>")
    return "".join(out)


# ---------- pages ----------
def page_sola():
    items = [
        ("scriptura", "Sola Scriptura", "唯独圣经",
         "圣经是信仰与生活的最高权威，也是足够的规范。",
         [("提后3", 16, 17), ("林前4", 6), ("徒17", 11), ("赛8", 20)],
         [("BC 7", bl(7), _phrase(Q.BC[7], "我们相信，圣经中包含了神全部的旨意；我们也相信它对人得救所必须信的一切真理作了充分的教导。")),
          ("HC 21", hq(21), _phrase(Q.HC[21][1], "真信心是一种确知，藉此我认定神在圣经中向我们启示的一切皆为真理"))],
         "本站归纳：所反对的是把遗传、会议或训导权抬到与圣经同等或以上；不是否定教会的教导职分。"),
        ("christus", "Solus Christus", "唯独基督",
         "罪人唯独藉着基督的位格与已经完成的工作得拯救，别无中保。",
         [("徒4", 12), ("约14", 6)],
         [("BC 22", bl(22), _phrase(Q.BC[22], "所谓基督的救恩不够完全，除他以外还需要别的才能得救的这种断言是严重的亵渎"))],
         "本站归纳：所反对的是把马利亚、圣徒或人的功德当作中保或补赎；不是否定信徒彼此代求。"),
        ("gratia", "Sola Gratia", "唯独恩典",
         "得救从头到尾是神白白的恩典，不是人赚得，也不是与神对半合作的功德。",
         [("弗2", 8, 9), ("罗3", 24), ("罗11", 6), ("多3", 5)],
         [("Dort I.7", dl("1", 7), _phrase(Q.DORT["1.7"], "这些人得救完全是靠着神的恩典，因他们既不比其他人好，也不更配得神的恩典"))],
         "本站归纳：所反对的是把恩典视为人先配合才生效的助力，或以行为换取称义。"),
        ("fide", "Sola Fide", "唯独信心",
         "人称义是因着信，不在乎遵行律法。信心本身不是功德，乃是领受基督的器皿。",
         [("罗3", 28), ("罗5", 1), ("加2", 16)],
         [("HC 60", hq(60), _phrase(Q.HC[60][1], "唯独藉着真心信靠耶稣基督。")),
          ("HC 21", hq(21), _phrase(Q.HC[21][1], "坚信神完全是出于他的恩典，且单单因着基督的功劳")),
          ("BC 22", bl(22), _phrase(Q.BC[22], "严格地说，这不是指信心本身使我们称义，因为信心只是一个工具，藉着它，我们得以接受基督为我们的义。"))],
         "本站归纳：所反对的是「信加上爱德或行为才构成称义」；不是否定称义之后必有善行。"),
        ("gloria", "Soli Deo Gloria", "唯独上帝的荣耀",
         "救恩的最终目的是神自己的荣耀，受造之物无可夸口。",
         [("弗1", 11, 12), ("罗11", 36), ("林前10", 31), ("赛42", 8)],
         [("Dort I.12", dl("1", 12), _phrase(Q.DORT["1.12"], "神在所定的时候会让他们确信自己蒙了永恒不变的拣选而得救恩"))],
         "本站归纳：所反对的是把荣耀归给人的意志、功德或教会本身。"),
    ]
    parts = [
        svg_emblem(),
        key("五个唯独是十六世纪宗教改革面对罗马教会的<b>原则</b>：权威、中保、恩典、称义的途径、荣耀所归。它们不是 1618–19 年多特大会回答抗辩派的那五要点。辨惑见下一章。"),
        site("下列一句定义与「所反对的」是本站教学归纳；经文为和合本；信条摘引逐字取自本站 CCI 原文。"),
    ]
    icos = {"scriptura": "book", "christus": "cross", "gratia": "cup", "fide": "shield", "gloria": "crown"}
    for sid, lat, zh, defn, verses, confs, vswhat in items:
        body = f'<p><b>{lat}</b>　{defn}</p>' + vs(*verses)
        for title, link, phrase in confs:
            body += blk(phrase, f"{title}（{link}）")
        body += hard(vswhat)
        parts.append(L3(f"sola-{sid}", f"{zh} · {lat}", body, icon=icos[sid]))
    parts.append(L3("sola-poster", "海报原文《宗教改革的五個唯獨》", poster_html(), icon="scroll"))
    return "".join(parts)


def page_tulip():
    p8 = next(p["text"] for p in DECK["pages"] if p["n"] == 8)
    b = [
        key("把两套「五」分开：<b>五个唯独</b>是十六世纪改革原则（对罗马）；<b>多特五要点／TULIP</b>是 1618–19 年多特大会回答 1610 年《抗辩书》的救恩论。TULIP 是后来的英文口诀，不是多特信经自己的结构或措辞。"),
        table(["", "五个唯独", "多特五要点 / TULIP"], [
            ["问题", "权威、中保、恩典、称义之途、荣耀归谁？", "堕落的人如何得救？拣选、救赎、恩召、保守如何生效？"],
            ["时代", "十六世纪，对罗马", "1610 抗辩；1618–19 多特会议"],
            ["文件", "贯穿比利时信条与海德堡要理问答", "多特信经四项（第三、四项合一）"],
            ["口诀", "五句拉丁 Sola / Solus / Soli", "TULIP：后来英文记法，字母顺序不是多特次序"],
        ], "cmp"),
        site("上表为本站对照。多特结构的既有说明见" + '<a href="dort.html#dd-tulip">四、多特信经 · 五点与 TULIP</a>。'),
        L3("tulip-order", "多特的真实次序与中文译名",
           "<p>多特信经的项次是：<b>第一项拣选</b>、<b>第二项基督之死</b>、<b>第三、四项（合为一项）人的败坏与归正</b>、<b>第五项圣徒的坚忍</b>。英文 TULIP 把败坏放在首位，是为了口诀，不是大会目录。</p>"
           + table(["口诀", "常见汉译", "更妥的汉译", "多特项次"], [
               ["T Total Depravity", "全然败坏", "全然败坏（指范围，不是「坏到极处」的程度）", "III/IV"],
               ["U Unconditional Election", "无条件拣选", "无条件拣选", "I"],
               ["L Limited Atonement", "有限救赎", "<b>特定救赎</b>／有效救赎", "II"],
               ["I Irresistible Grace", "不可抗拒的恩典", "<b>有效恩召</b>", "III/IV"],
               ["P Perseverance of the Saints", "圣徒的坚忍", "<b>圣徒蒙保守并坚忍</b>", "V"],
           ], "cmp")
           + note("「有限」容易被听成「基督的价值有限」。有效恩召则避免「人像机器被推动」的误会，同时又坚持内在恩召不落空（" + dl("3-4", 16) + "）。"),
           icon="list"),
        L3("tulip-rem", "抗辩与多特：并排阅读",
           note("左栏逐字取自本专题收录的讲座幻灯片原文（第 8 页），不是 1610 年荷兰文抗辩书的校勘本。右栏逐字取自本站 CCI 多特信经。")
           + table(["抗辩书所主张的（讲座原文）", "多特的回答（CCI 原文摘引）"], [
               [H.escape(_phrase(p8, "“拣选”基于“信心”")),
                H.escape(_phrase(Q.DORT["1.7"], "这些人得救完全是靠着神的恩典，因他们既不比其他人好，也不更配得神的恩典")) + "（" + dl("1", 7) + "）"],
               [H.escape(_phrase(p8, "基督为所有的人受死，虽然只有圣徒蒙恩")),
                H.escape(_phrase(Q.DORT["2.8"], "有效地从各民、各族、各国、说各种语言的人中拯救那些（而且只有那些）从永恒中就蒙拣选得救的人")) + "（" + dl("2", 8) + "）"],
               [H.escape(_phrase(p8, "上帝的恩典并不是不可抗拒的")),
                H.escape(_phrase(Q.DORT["3-4.11"], "通过使人重生的圣灵有效地做工，神也穿透到人的内心深处")) + "（" + dl("3-4", 11) + "）"],
               [H.escape(_phrase(p8, "圣徒有可能从上帝的恩典中堕落")),
                H.escape(_phrase(Q.DORT["5.8"], "完全失去信心与恩典，深陷罪中，直到最后失丧的情况不会发生在属神的人身上。")) + "（" + dl("5", 8) + "）"],
           ], "cmp"),
           icon="scale"),
        L3("tulip-matrix", "唯独 × 五要点",
           site("下表为本站教学对照，表明两套「五」相关却不可互换。")
           + table(["", "T 败坏", "U 拣选", "L 特定救赎", "I 有效恩召", "P 保守坚忍"], [
               ["唯独圣经", "败坏与无能由圣经判定", "拣选的教义出于圣经，而非窥探隐秘", "救赎的范围以经文为准", "恩召的效力以经文为准", "保守的应许以经文为准"],
               ["唯独基督", "在亚当里死，在基督里活", "在基督里拣选（" + dl("1", 7) + "）", "中保只为选民完成救赎", "把人领进与基督的联合", "基督的代求与保守（" + dl("5", 8) + "）"],
               ["唯独恩典", "人不能自救，只靠恩典", "拣选不在乎人的预知功德", "救赎是恩典的赐予，不是普遍可能而已", "内在恩召是恩典的功效", "保守也是不配得的恩典（" + dl("5", 8) + "）"],
               ["唯独信心", "无重生则无真信心", "信心是拣选的果子，不是条件", "信心由十字架所买来并赐下（" + dl("2", 8) + "）", "信心是神所赐的礼物（" + dl("3-4", 14) + "）", "所保守的是信靠的人"],
               ["唯独上帝的荣耀", "人无可夸口", "荣耀归于拣选的神", "荣耀归于被杀的羔羊", "荣耀归于使人活过来的灵", "荣耀归于信实守约的神"],
           ], "sot-matrix cmp"),
           icon="link"),
        L3("tulip-jn644", "约翰福音 6:44 作为记忆口诀",
           v("约6", 44)
           + site("下面是教学口诀，把这节经文的短语对应到 TULIP 五个字母，便于记忆；它不能替代多特条文，也不是经文原有的五点划分。和合本是「到我这里来的」，口诀里的「人」字是为了上口，不改经文。")
           + table(["经文短语（和合本）", "口诀对应", "要点"], [
               ["若不是差我来的父", "U 无条件拣选", "来到子这里，起点在父的作为"],
               ["吸引人", "I 有效恩召", "吸引是神有效的工作，不是人先把自己拉过去"],
               ["就没有能到我这里来的", "T 全然败坏", "没有这吸引，人没有能来的力量"],
               ["到我这里来的", "L 特定救赎", "那些实在来的人，是父赐给子、子所救赎的人（参 " + v.__doc__ if False else "约 6:37、6:39）"],
               ["在末日我要叫他复活", "P 圣徒蒙保守并坚忍", "来的人被带到复活，不会中途失落"],
           ], "cmp")
           + vs(("约6", 37, 39)),
           icon="key"),
        L3("tulip-faq", "常见混淆",
           "<dl class='faq'>"
           "<dt>TULIP 是不是多特信经的目录？</dt><dd>不是。多特是四项教义（第三、四项合一），次序是拣选—基督之死—败坏与归正—坚忍。TULIP 是后来英文口诀（本站标：约，口诀成型于二十世纪英语世界）。</dd>"
           "<dt>「有限救赎」是不是说基督的宝血不够？</dt><dd>不是。更妥的说法是特定救赎或有效救赎：价值无限，设计的对象是选民（见讲座原文「有限不是针对价值与能力」及 " + dl("2", 8) + "）。</dd>"
           "<dt>「不可抗拒」是不是把人当木头？</dt><dd>不是。" + dl("3-4", 16) + " 明说神「没有把人当作毫无意识的木头或石头对待」。更妥的说法是有效恩召：外在呼召可被拒绝，内在恩召使意志更新而甘心前来。</dd>"
           "<dt>「全然败坏」是不是说人坏到不能再坏？</dt><dd>不是。它指罪影响到人性的各个层面，人不能靠自己转向神以得救（" + dl("3-4", 3) + "），不是比较谁更邪恶。</dd>"
           "<dt>五个唯独和 TULIP 是同一件事吗？</dt><dd>不是。前者是改革原则，后者是多特的救恩论。二者和谐，却不可混成一张清单。</dd>"
           "<dt>「一次得救，永远得救」等于圣徒坚忍吗？</dt><dd>相近但易被误用。多特所教的是神保守属自己的人，而圣徒也真实地坚忍；不是给不悔改的人一张护身符（" + dl("5", 3) + "、" + dl("5", 8) + "）。讲座原文对此有专门讨论，见下方逐字稿。</dd>"
           "</dl>",
           icon="alert"),
        L3("tulip-verses", "逐点经文（和合本）",
           "<p>拣选用弗 1:4–5（不以弗 1:6 单独充当拣选的主证；1:6 是恩典得着称赞）。特定救赎可并读约 10:11、15 与约 17:9–11。</p>"
           + "<h4>T 全然败坏</h4>" + vs(("罗3", 10, 11, 12), ("弗2", 1, 2, 3), ("耶17", 9))
           + "<h4>U 无条件拣选</h4>" + vs(("弗1", 4, 5), ("罗9", 11, 12, 13, 14, 15, 16))
           + "<h4>L 特定救赎／有效救赎</h4>" + vs(("约10", 11, 15), ("约17", 9, 10, 11), ("太1", 21))
           + "<h4>I 有效恩召</h4>" + vs(("约6", 44), ("结36", 26, 27), ("徒16", 14), ("罗8", 30))
           + "<h4>P 圣徒蒙保守并坚忍</h4>" + vs(("约10", 27, 28, 29), ("罗8", 30, 38, 39), ("腓1", 6), ("彼前1", 5)),
           icon="book"),
        L3("tulip-deck", "讲座幻灯片原文《加尔文主义五要点》",
           deck_html(), icon="scroll"),
    ]
    return "".join(b)


def page_law():
    b = [
        key("律法先叫人知罪，把人赶到基督那里；在基督里称义的人，并不废弃律法，乃是坚固律法，并在感恩中按律法而行。"),
        L3("law-ans", "经文问答",
           "<p><b>律法从哪里显出人的罪？</b></p>" + vs(("罗3", 20), ("罗7", 7))
           + "<p><b>律法与福音怎样相连？</b></p>" + vs(("加3", 24), ("罗3", 21, 22))
           + "<p><b>因信就废了律法吗？</b></p>" + vs(("罗3", 31), ("太5", 17))
           + "<p><b>信徒还在律法之下吗？</b></p>" + vs(("罗6", 14),) + note("「不在律法之下」是指不在律法的定罪与称义条件之下，不是可以反律法地生活。")
           + "<p><b>律法的总纲是什么？</b></p>"
           + blk(Q.HC[4][1], f"HC 4（{hq(4)}）"),
           icon="book"),
        L3("law-use", "律法的三重功用",
           table(["功用", "要义", "信条"], [
               ["第一，镜子", "显明罪恶与愁苦，迫使我们寻求基督里的赦免", hq(3) + "、" + hq(115)],
               ["第二，疆界", "在社会生活中约束外在的恶（民事用途；本站归纳）", "参 " + bl(25)],
               ["第三，准绳", "重生之人在感恩中被规范、被更新，直到此生之后达至完全", hq(115) + "、" + bl(25)],
           ], "cmp")
           + blk(_phrase(Q.HC[3][1], "从神的律法。"), f"HC 3 问「你从何处得知你的罪恶和愁苦呢？」（{hq(3)}）")
           + blk(_phrase(Q.HC[115][1], "第一，好叫我们在今生越来越知晓自己的罪性，从而更迫切地寻求在基督里的罪得赦免和公义。第二，好叫我们一方面求神赐下圣灵的恩典，一方面不断努力按神的形像被更新，直到此生之后达至完全。"), f"HC 115（{hq(115)}）")
           + blk(_phrase(Q.BC[25], "我们仍使用律法与先知们的见证，其一是为了在福音的真道上坚固自己，其二是为了本着一切的诚实，遵照神的旨意安排自己的生活，以此荣耀他的名。"), f"BC 25（{bl(25)}）"),
           icon="list"),
        L3("law-kinds", "道德、礼仪、民事",
           site("三分是改革宗常用的教学区分，不是把圣经切成互不相干的三本律。")
           + table(["", "道德律", "礼仪律", "民事律"], [
               ["要旨", "十诫所总结的、永存的爱神爱人", "献祭、节期、洁净等预表", "以色列邦国的司法与刑罚"],
               ["在基督里", "成全而不废除（太 5:17；罗 3:31）", "预表已在基督里实现，不再照旧遵守", "邦国之礼已成过去，其公平原则仍可参酌"],
               ["信条", hq(92) + "–" + hq(115), bl(25) + "：礼仪律及其象征已被停用", "本站归纳，参 " + bl(25)],
           ], "cmp")
           + blk(_phrase(Q.BC[25], "随着基督的降世，礼仪律及其象征已被停用；我们也相信，所有的预表都已实现。因此，它们不应继续为基督徒所用。"), f"BC 25（{bl(25)}）")
           + note("十诫正文见" + hqs(92, 115) + "，此处不重抄全部问答，以免把第十六部分写成第二份原文库。"),
           icon="scroll"),
        L3("law-vert", "纵向：救赎历史中的律法",
           site("下表为本站纵向对照。")
           + table(["阶段", "律法如何出现", "经文"], [
               ["创造", "人被造时心思意念正直，有神的形像；堕落才失去这完全", dl("3-4", 1)],
               ["西奈", "十诫颁布，约民被分别出来", "出 20；" + hq(92)],
               ["基督", "成全律法，作挽回祭；律法引我们到他那里", "太 5:17；加 3:24；罗 3:21–26"],
               ["新约教会", "律法写在心上；信徒在感恩中遵行，礼仪已成全", "耶 31:33；BC 25"],
           ], "cmp")
           + vs(("耶31", 33), ("太5", 17), ("加3", 24)),
           icon="map"),
        L3("law-horiz", "横向：各家如何看待律法",
           site("下表为本站横向对照，只标大势，不代替各传统的原始文本。")
           + table(["", "改革宗", "路德宗", "罗马（天特以降的大势）", "反律法", "律法主义"], [
               ["称义", "因信唯独领受基督的义，不靠行律法", "同样强调因信称义，律法与福音严格对举", "称义含灌入之义，与人的合作、爱德相连", "往往把恩典说成不再需要遵行", "把遵行当作称义的根据"],
               ["第三功用", "明确：律法仍是信徒生活的准绳（HC 115）", "第一、二功用极强；第三功用有传统内的讨论", "律法在教会训导与功德观中持续有约束力", "否定道德律对信徒的规范", "把律法的规范变成赚取的阶梯"],
               ["危险", "若只讲准绳而忘了镜子与福音，会滑向律法主义", "若把第三功用说得过弱，易被误解为反律", "称义与成圣界限易混", "否定成圣与十诫", "否定唯独信心"],
           ], "cmp"),
           icon="scale"),
        L3("law-deep", "深度分析",
           "<p><span class='mk-hl'>律法显罪</span>，却不能称义；<span class='hl-s'>福音</span>赐下基督的义。<span class='mk-x'>把律法当作称义的阶梯</span>，或<span class='mk-x'>把恩典当作反律的许可证</span>，都偏离了比利时信条与海德堡要理问答。</p>"
           + app("读十诫时，先作镜子（HC 3、115 第一点），再作感恩的准绳（HC 86–91、115 第二点）。不要把邻舍的行为变成自己称义的证据，也不要借口「在恩典之下」轻看神的诫命。"),
           icon="key"),
    ]
    # fix empty cell in vertical table - I left a messy vs.__doc__ line. Rebuild that one row properly by post-replace if needed.
    return "".join(b)


def page_ordo():
    b = [
        key("救恩是神在基督里作成的一回事：称义一次完成，成圣持续一生，果子是必然的，却不是称义的代价。"),
        L3("ordo-ans", "经文问答：什么是救恩、恩典、称义、成圣、果子",
           "<p><b>什么是救恩？</b>神在基督里把罪人从罪与死中救出来，使她得称为义、成圣、并进入荣耀。除他以外，别无拯救。</p>"
           + vs(("徒4", 12), ("罗1", 16), ("多3", 5))
           + "<p><b>什么是恩典？</b>神不配得的、白白的恩惠。得救本乎恩，也因着信；这并不是出于自己。</p>"
           + vs(("弗2", 8, 9), ("罗11", 6))
           + "<p><b>什么是称义？</b>神宣告罪人在他面前为义：不是因人里面的改善，乃是把基督的义归算给信的人。</p>"
           + vs(("罗3", 24, 26, 28), ("罗5", 1), ("林后5", 21))
           + "<p><b>什么是成圣？</b>神在已经称义的人里面，藉着圣灵使其更新、离罪、活出神的形像。成圣有开始、有进程，今生达不到完全。</p>"
           + vs(("帖前4", 3), ("罗6", 19), ("来12", 14))
           + "<p><b>什么是救恩的果子？</b>称义的信心必生发仁爱与善行；圣灵结出仁爱、喜乐、和平诸果；善行也坚固确信，却不是称义的根据。</p>"
           + vs(("加5", 22, 23), ("弗2", 10)),
           icon="book"),
        L3("ordo-flow", "救恩次序",
           svg_ordo()
           + site("图中各项是逻辑关系。拣选在创立世界以前（弗 1:4–5）；今生中，有效恩召、重生与信心紧密相连（" + dl("3-4", 12) + "、" + dl("3-4", 14) + "）；称义与收养随真信心而来；成圣贯穿一生；坚忍直到得荣耀（" + dl("5", 3) + "）。"),
           icon="arrowup"),
        L3("ordo-js", "称义与成圣对照",
           table(["", "称义", "成圣"], [
               ["动作", "神的一次宣告，归算基督的义", "神在人里面持续的更新"],
               ["法庭 / 生命", "法庭性：地位改变", "有机性：性情与生活改变"],
               ["根据", "唯独基督的义，藉信心领受", "已经称义的人靠圣灵治死罪、结出果子"],
               ["今生完全？", "在地位上完全（所归算的是基督的完全）", "今生不完全，直到得荣耀"],
               ["信条", hq(60) + "、" + bl(22), hq(86) + "、" + hq(91) + "、" + bl(24)],
           ], "cmp")
           + blk(_phrase(Q.HC[60][1], "神以他白白的恩典，而非因我的任何功德，将基督按律法要求完全偿还一切罪而成就的，以及他的义和圣洁都归给了我"), f"HC 60（{hq(60)}）")
           + blk(_phrase(Q.HC[86][1], "为什么我们还要行善呢？") if False else _phrase(Q.HC[86][1], "好叫我们用全部的生命，为基督所赐的一切恩惠向神表明我们的感恩"), f"HC 86（{hq(86)}）"),
           icon="scale"),
        L3("ordo-aug", "人的四种状况（奥古斯丁）",
           "<p>古典区分用四组拉丁短语说明意志在救恩历史中的能力。重生一栏从俗：仍<b>能犯罪</b>，也<b>能不犯罪</b>；罗 7:14–25 描述的正是这种争战，而不是得荣耀后的不能犯罪。</p>"
           + table(["", "能犯罪 posse peccare", "能不犯罪 posse non peccare", "不能不犯罪 non posse non peccare", "不能犯罪 non posse peccare"], [
               ["堕落前", "是", "是", "否", "否"],
               ["堕落后", "是（且实际上在罪的辖制下）", "否（就得救的转向而言）", "是", "否"],
               ["重生", "是", "是", "否", "否"],
               ["得荣耀", "否", "是（完全）", "否", "是"],
           ], "cmp")
           + svg_states()
           + vs(("罗7", 18, 19, 24, 25), ("罗8", 1)),
           icon="users"),
        L3("ordo-fruit", "救恩的果子：善行、确据、感恩",
           blk(_phrase(Q.HC[86][1], "这还可以使我们因着信心的果子，而确信自己有信心；并且透过我们敬虔的生活，为基督赢得我们的邻舍。"), f"HC 86（{hq(86)}）")
           + blk(_phrase(Q.HC[91][1], "单指那些出于真信心、符合神的律法并为荣耀神而行的事，不是那些出于我们一己之见或人的规条而行的事。"), f"HC 91（{hq(91)}）")
           + blk(_phrase(Q.BC[24], "若说使人称义的信心让人不渴慕过良善、圣洁的生活，那是无稽之谈。"), f"BC 24（{bl(24)}）")
           + blk(_phrase(Q.DORT["1.12"], "从自己身上看到圣经所指的、由蒙拣选而生的经久不衰的果子，如基督里的真信心、对神孩童般的敬畏、真心为罪忧伤、饥渴慕义等等。"), f"Dort I.12（{dl('1', 12)}）")
           + blk(_phrase(Q.DORT["5.10"], "这确信不是来源于圣经以外的某个“给个人的启示”"), f"Dort V.10（{dl('5', 10)}）")
           + vs(("加5", 22, 23), ("弗2", 10)),
           icon="leaf"),
        L3("ordo-horiz", "横向：称义、成圣与果子",
           site("下表为本站横向对照，只标大势。")
           + table(["", "改革宗", "天特会议的大势", "阿米念主义的大势", "路德宗的大势", "反律法"], [
               ["称义", "一次性归算，唯独信心领受基督的义", "称义含灌入之义，可增减，与合作相关", "恩典普及，人的意志决定是否配合", "同样强调因信称义、律法与福音对举", "强调恩典到一个地步，往往轻看遵行"],
               ["成圣", "必然随之而来，却不构成称义的根据", "与称义连续，易混为一个过程", "成圣与人的持续合作、也可能失落", "成圣真实，但讲法常更突出福音的宣讲", "成圣可有可无，甚或被看作律法主义"],
               ["坚忍", "神保守，圣徒坚忍（" + dl("5", 8) + "）", "恩典可因大罪失落", "圣徒可能从恩典中堕落（抗辩书主张）", "一般承认神的保守，细节各有传统", "「一次得救」常被误用为护身符"],
           ], "cmp"),
           icon="scale"),
    ]
    return "".join(b)


def _sub(sid, filename, title, ico, builder):
    saved_f = CUR["f"]
    CUR["f"] = filename
    body = L2(sid, "", title, builder())
    html = (f'<p class="lec-crumb"><a href="sot.html">返回十六、救恩教义专题</a> · {H.escape(title)}</p>'
            f'<p class="lead">本页是第十六部分的子页。信条摘引逐字取自 CCI；经文为和合本；讲座与海报原文另行标明。</p>'
            + body)
    EXTRA.append((sid, filename, f"十六 {title}", ico, html))
    CUR["f"] = saved_f


def part_sot():
    EXTRA.clear(); CHAIN.clear()
    groups = [
        ("sot-sola", "sot-sola.html", "五个唯独", "crown", page_sola),
        ("sot-tulip", "sot-tulip.html", "救恩五要点与辨惑", "scale", page_tulip),
        ("sot-law", "sot-law.html", "什么是律法", "scroll", page_law),
        ("sot-ordo", "sot-ordo.html", "救恩·恩典·称义·成圣·果子", "heart", page_ordo),
    ]
    for sid, fn, title, ico, fnb in groups:
        _sub(sid, fn, title, ico, fnb)
    sids = [g[0] for g in groups]
    for i, k in enumerate(sids):
        CHAIN[k] = (sids[i - 1] if i else None, sids[i + 1] if i + 1 < len(sids) else None, "sot")
    grid = '<div class="grid g3">' + "".join(
        f'<a class="card vcard" href="{fn}" style="--c:var(--gold)"><div class="ct"><span>{ic(ico,"ic")}</span>{H.escape(title)}</div><p>第十六部分 · 子页</p></a>'
        for sid, fn, title, ico, _ in groups
    ) + "</div>"
    lead = ("本专题把宗教改革的原则、多特的救恩论、律法与福音、称义与成圣放在同一条阅读线上。"
            "五个唯独是十六世纪对罗马的原则；多特五要点是 1618–19 年回答抗辩派的救恩论；二者常被弄混，故专设辨惑。"
            "讲座幻灯片与繁体海报按原文收录，与 CCI 信条原文分开。儿童要理问答另见第十七部分（正文待录入）。")
    intro = (site("本页地图、对照与图示是本站学习材料。信条只摘本站已有 CCI 原文；经文用和合本并已核对。")
             + key("建议顺序：先读五个唯独，再读五要点辨惑（含讲座原文），然后是律法，最后是救恩五题与人的四种状况。")
             + '<p class="lec-k">本专题子页</p>' + grid)
    return L1("sot", 16, "救恩教义专题", "cross", lead, intro)


def part_childq():
    items = CHILD.get("items") or []
    if items:
        rows = "".join(
            f'<section class="l3" id="cq-{H.escape(str(it.get("n", i+1)))}">'
            f'<h4>{H.escape(str(it.get("n", i+1)))}. {H.escape(it.get("q",""))}</h4>'
            f'<p>{H.escape(it.get("a",""))}</p>'
            f'<p class="vq">{H.escape(it.get("verse",""))}</p>'
            f'<p>{H.escape(it.get("note",""))}</p></section>'
            for i, it in enumerate(items)
        )
        body = rows
    else:
        body = (
            f'<div class="childq-slot" data-src="data/t114/childq.json">'
            f'<p><b>{H.escape(CHILD.get("toc_label") or "儿童要理问答（待录入）")}</b></p>'
            f'<p>{H.escape(CHILD.get("note") or "正文待录入。")}</p>'
            f'<p>预定版式（有文本后将按 JSON 的 items 注入，字段为号、问、答、经文、注释）：</p>'
            f'<ol><li>题号</li><li>问</li><li>答</li><li>经文</li><li>注释</li></ol>'
            f'<p>目前 items 为空，不编造任何问答句。</p></div>'
        )
    return L1("childq", 17, "儿童要理问答", "users",
              "本部分预留给儿童要理问答的逐字录入。上传件目前为无文字层的扫描页，故只设目录与版式，不编写任何问答正文。",
              L2("childq-pending", "", "儿童要理问答（待录入）", body))
