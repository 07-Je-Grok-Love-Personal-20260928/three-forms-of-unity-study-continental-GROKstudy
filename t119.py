# -*- coding: utf-8 -*-
"""t119 / t118u: Q/A badges in flow, full grid titles, reflow, no page cites,
Traditional→Simplified, leading notices moved to an end details block."""
import re
from html import unescape

try:
    from opencc import OpenCC
    _CC = OpenCC("t2s")
except Exception:
    _CC = None


def _cut_tag(h, start, tag):
    open_t, close_t = f"<{tag}", f"</{tag}>"
    if not h.startswith(open_t, start):
        return start, start
    k = h.find(">", start) + 1
    if k == 0:
        return start, start
    depth = 1
    while k < len(h) and depth:
        nxt_o = h.find(open_t, k)
        nxt_c = h.find(close_t, k)
        if nxt_c < 0:
            return start, start
        if nxt_o >= 0 and nxt_o < nxt_c:
            depth += 1
            k = h.find(">", nxt_o) + 1
            if k == 0:
                return start, start
        else:
            depth -= 1
            k = nxt_c + len(close_t)
    return start, k


def _skip_ws(h, i):
    while i < len(h) and h[i] in " \t\r\n":
        i += 1
    return i


def _tag_name(h, i):
    if i >= len(h) or h[i] != "<":
        return None
    m = re.match(r"<(/?)([A-Za-z][A-Za-z0-9:-]*)", h[i:])
    if not m:
        return None
    return m.group(1), m.group(2).lower()


def _attr_class(h, i):
    end = h.find(">", i)
    if end < 0:
        return "", end
    head = h[i:end + 1]
    m = re.search(r'\bclass="([^"]*)"', head)
    return (m.group(1) if m else ""), end


def _has_class(cls, name):
    return f" {cls} ".find(f" {name} ") >= 0


# ---------------- assets / chain ----------------
def _assets(h, page, site):
    if "assets/t118.css" not in h:
        print("t119 MISS t118.css", site, page)
        return h
    if "assets/t119.css" not in h:
        m = re.search(r'<link rel="stylesheet" href="assets/t118\.css\?v=([^"]+)">', h)
        if m:
            ver = m.group(1)
            h = h.replace(
                m.group(0),
                m.group(0) + f'<link rel="stylesheet" href="assets/t119.css?v={ver}.t119">',
                1,
            )
        else:
            print("t119 MISS exact t118 link", site, page)
    if 'data-chain="' in h and ",t119" not in h:
        if 't102,t106,t107,t112,t114,t117,t118"' in h:
            h = h.replace(
                't102,t106,t107,t112,t114,t117,t118"',
                't102,t106,t107,t112,t114,t117,t118,t119"',
                1,
            )
        else:
            print("t119 MISS chain", site, page)
    return h


# ---------------- Q / A ----------------
def _qa(h):
    def qrepl(m):
        num, lab, rest = m.group(1), m.group(2), m.group(3)
        return (
            f'<h4 class="qh qq">'
            f'<span class="qa-badge" aria-hidden="true">Q</span>'
            f'<span class="qnum">{num}</span>'
            f'<span class="sr-qa">{lab}</span>'
            f'<span class="qa-text">{rest}</span></h4>'
        )

    h = re.sub(
        r'<h4 class="qh qq">\s*(\d+[.．、]?\s*)(问[：:])(.*?)</h4>',
        qrepl,
        h,
        flags=re.S,
    )

    def arepl(m):
        lab, rest = m.group(1), m.group(2)
        return (
            f'<p class="ex qa">'
            f'<span class="qa-badge a" aria-hidden="true">A</span>'
            f'<span class="sr-qa">{lab}</span>'
            f'<span class="qa-text">{rest}</span></p>'
        )

    h = re.sub(
        r'<p class="ex qa">\s*(答[：:])(.*?)</p>',
        arepl,
        h,
        flags=re.S,
    )

    # children's labs: 问/答 → Q/A (keep a visually hidden original if present)
    def lab_repl(m):
        which, inner = m.group(1), m.group(2).strip()
        if inner in ("问", "Q"):
            letter, hidden = "Q", "问"
        elif inner in ("答", "A"):
            letter, hidden = "A", "答"
        else:
            return m.group(0)
        # do not add sr-qa here — the source line never contained "问：" / "答："
        return f'<span class="cq-lab"{which}>{letter}</span>'

    h = re.sub(r'<span class="cq-lab"([^>]*)>([^<]*)</span>', lab_repl, h)
    return h


# ---------------- page-number citations ----------------
_PAGE_TEXT = re.compile(
    r"(?:"
    r"印刷第\s*\d+\s*[–\-至到]\s*\d+\s*页。"
    r"|印刷第\s*\d+\s*页。"
    r"|〔第\s*\d+\s*页〕"
    r"|〔\s*\d+\s*〕"
    r"|幻灯片第\s*\d+\s*页"
    r"|第\s*\d+\s*[–\-至到]\s*\d+\s*页"
    r"|第\s*\d+\s*页"
    r"|\(p\.\s*\d+\)"
    r")",
)


def _protect_pages(s):
    """Avoid eating 本页 / 首页 / 网页 / 原页面."""
    # 第N页 after 本/首/网/原页 would not match our pattern (we require 第).
    return s


def _strip_page_cites(h):
    # keep id anchors without visible marks
    def pg(m):
        attrs = m.group(1)
        mid = re.search(r'\bid="([^"]+)"', attrs)
        if mid:
            return f'<span id="{mid.group(1)}" hidden></span>'
        return ""

    h = re.sub(r'<a class="lec-pg"([^>]*)>.*?</a>', pg, h, flags=re.S)
    h = re.sub(r'<cite class="lec-cite">.*?</cite>', "", h, flags=re.S)
    h = re.sub(r'<span class="ln"[^>]*>.*?</span>', "", h, flags=re.S)
    # short chip-like pdfsrc (「出自…第 N 页」「幻灯片第 N 页」); intro paragraphs handled in notices
    h = re.sub(
        r'<span class="pdfsrc">.*?</span>',
        "",
        h,
        flags=re.S,
    )
    h = re.sub(r'<span class="l3t">\s*第\s*\d[^<]*页\s*</span>', "", h)
    # bare text citations left in prose / headings / table cells
    def txt(m):
        s = m.group(0)
        # don't touch 本页 already-read, etc.
        return ""

    # operate only outside tags
    parts = re.split(r"(<[^>]+>)", h)
    for i, p in enumerate(parts):
        if not p or p.startswith("<"):
            continue
        parts[i] = _PAGE_TEXT.sub("", p)
    h = "".join(parts)
    # tidy leftover empty parens in visible text only (never inside script/style)
    def tidy_text(s):
        s = re.sub(r"（\s*）", "", s)
        s = re.sub(r"\(\s*\)", "", s)
        s = re.sub(r"[ \t]{2,}", " ", s)
        return s
    chunks = re.split(r"(<script[\s\S]*?</script>|<style[\s\S]*?</style>)", h, flags=re.I)
    out=[]
    for ch in chunks:
        if re.match(r"<script", ch, re.I) or re.match(r"<style", ch, re.I):
            out.append(ch)
        else:
            parts2 = re.split(r"(<[^>]+>)", ch)
            out.append("".join(tidy_text(x) if not x.startswith("<") else x for x in parts2))
    return "".join(out)


# ---------------- reflow hard line breaks ----------------
_END_PUNCT = set("。！？；…」』）】》")


def _plain(s):
    s = re.sub(r"<[^>]+>", "", s)
    return unescape(s).strip()


def _ends_open(text):
    t = _plain(text)
    if not t:
        return False
    ch = t[-1]
    if ch in _END_PUNCT:
        return False
    if ch in ".!?":
        return False
    return True


def _join_cn(a, b):
    # no extra space between CJK; keep one space if latin/digit boundary
    a = a.rstrip()
    b = b.lstrip()
    if not a or not b:
        return a + b
    if a[-1] in " \n\t" or b[0] in " \n\t":
        return a + b
    la, lb = a[-1], b[0]
    def is_cjk(c):
        o = ord(c)
        return 0x4E00 <= o <= 0x9FFF or c in "，、：；「」『』（）【】《》"
    if is_cjk(la) or is_cjk(lb):
        return a + b
    return a + " " + b


def _merge_siblings(inner, tag="p"):
    """Merge adjacent <tag>…</tag> when the first does not end a sentence."""
    pat = re.compile(rf"(<{tag}(?:\s[^>]*)?>)(.*?)(</{tag}>)", re.S)
    items = []
    last = 0
    for m in pat.finditer(inner):
        items.append(("text", inner[last:m.start()]))
        items.append(("p", m))
        last = m.end()
    items.append(("text", inner[last:]))
    out = []
    buf = None  # (open, body, close)
    for kind, val in items:
        if kind == "text":
            if buf is not None and val.strip():
                out.append(buf[0] + buf[1] + buf[2])
                buf = None
                out.append(val)
            elif buf is not None and not val.strip():
                # whitespace only between two p's — keep merging chance
                pass
            else:
                out.append(val)
            continue
        m = val
        open_, body, close = m.group(1), m.group(2), m.group(3)
        if buf is not None and buf[0]==open_ and _ends_open(buf[1]):
            buf = (buf[0], _join_cn(buf[1], body), close)
        else:
            if buf is not None:
                out.append(buf[0] + buf[1] + buf[2])
            buf = (open_, body, close)
    if buf is not None:
        out.append(buf[0] + buf[1] + buf[2])
    return "".join(out)


def _reflow_region(h, start_pat, end_pat=None):
    """Apply paragraph merge and newline collapse inside matching regions."""
    def work(inner):
        inner = re.sub(r"<br\s*/?>", "", inner, flags=re.I)
        # collapse source newlines inside text
        parts = re.split(r"(<[^>]+>)", inner)
        for i, p in enumerate(parts):
            if p and not p.startswith("<"):
                parts[i] = re.sub(r"\s*\n\s*", "", p)
        inner = "".join(parts)
        inner = _merge_siblings(inner, "p")
        # consecutive one-item lists that continue a sentence → rare; skip
        return inner

    if start_pat.startswith("class="):
        cls = start_pat.split("=", 1)[1]
        out, last = [], 0
        for m in re.finditer(r'<([a-zA-Z0-9]+)([^>]*\bclass="([^"]*)"[^>]*)>', h):
            classes = m.group(3).split()
            if cls not in classes:
                continue
            tag = m.group(1)
            s, e = _cut_tag(h, m.start(), tag)
            if e <= s or s < last:
                continue
            # find inner
            gt = h.find(">", s) + 1
            close_len = len(f"</{tag}>")
            inner = h[gt:e - close_len]
            out.append(h[last:gt])
            out.append(work(inner))
            out.append(h[e - close_len:e])
            last = e
        out.append(h[last:])
        return "".join(out)
    return h


def _reflow(h):
    h = re.sub(r"<br\s*/?>", "", h, flags=re.I)
    for cls in ("lec-verbatim", "deck", "sot-poster", "sot-solablock", "pdfh"):
        h = _reflow_region(h, f"class={cls}")
    # also merge early-break <p> siblings directly under l3 / article bodies
    h = _reflow_region(h, "class=l3")
    return h


# ---------------- Traditional → Simplified ----------------
def _t2s(h, page):
    if _CC is None:
        print("t119 MISS opencc", page)
        return h
    h = h.replace('lang="zh-Hant"', 'lang="zh-Hans"')
    parts = re.split(r"(<script[\s\S]*?</script>|<style[\s\S]*?</style>)", h, flags=re.I)
    out = []
    for p in parts:
        if re.match(r"<script", p, re.I) or re.match(r"<style", p, re.I):
            out.append(p)
        else:
            out.append(_CC.convert(p))
    return "".join(out)


# ---------------- hero lead cleanup ----------------
_META_LEAD = re.compile(
    r"(?:"
    r"逐字收录[，。]?"
    r"|不改正文中的笔误[；。]?"
    r"|校记另列[。]?"
    r"|本站未改动一字[^。]*。"
    r"|先读本站要点，再读逐字原文。"
    r"|先读彩色标记；“辅助”区块默认折叠。"
    r"|并注明页码。"
    r"|讲座材料，不是 CCI《赞美手册》原文。"
    r"|这不是信条原文，也不可代替 CCI《赞美手册》中文版。"
    r"|偏旁字形已按规则还原，断行已并成段落，其余字符不改。不是信条原文。"
    r"|以下按无歧义配对重排各条，逐字保留繁体，行号为提取行。"
    r"|据用户提供的 PDF 转录，逐字照录。"
    r")"
)


def _clean_leads(h):
    def repl(m):
        pre, text, post = m.group(1), m.group(2), m.group(3)
        # strip known meta even when highlight spans wrap the words
        t = re.sub(
            r'(?:<span[^>]*>)?讲座材料(?:</span>)?，(?:<span[^>]*>)?不是 CCI《赞美手册》原文(?:</span>)?。',
            '',
            text,
        )
        t = re.sub(
            r'(?:<span[^>]*>)?讲解材料(?:</span>)?，(?:<span[^>]*>)?不是 CCI《赞美手册》原文(?:</span>)?。',
            '',
            t,
        )
        t = re.sub(
            r'(?:<span[^>]*>)?释义材料(?:</span>)?，(?:<span[^>]*>)?不是 CCI《赞美手册》原文(?:</span>)?。',
            '',
            t,
        )
        t = re.sub(r'本页是第十六部分的子页。[^<。]*。(?:信条摘引逐字取自 CCI；经文为和合本；讲座与海报原文另行标明。)?', '', t)
        t = _META_LEAD.sub("", t)
        t = re.sub(r"[；;]\s*[；;]", "；", t)
        t = re.sub(r"。+", "。", t)
        t = re.sub(r"\s{2,}", "", t).strip(" ；;、")
        if not t:
            t = ""
            return pre + t + post
        # keep at most one short sentence
        # if more than ~80 chars, cut at first period
        if len(re.sub(r"<[^>]+>", "", t)) > 90:
            plain_end = t.find("。")
            if 8 <= plain_end <= 90:
                t = t[: plain_end + 1]
        return pre + t + post

    return re.sub(r'(<p class="lead">)(.*?)(</p>)', repl, h, flags=re.S)


# ---------------- move leading notices ----------------
_NOTICE_CLASSES = {
    "readchip",
    "secbar",
    "mklegend",
    "mkdefs",
    "exn",
    "rxbar",
    "cq-corr",
    "cq-toolbar",
    "src",
    "pdfsrc",
    "lec-banner",
    "pdfnote",
}
_NOTICE_CALL_HINTS = (
    "📌 说明",
    "以下为本站归纳",
    "原文说明",
    "阅读建议",
    "本页已读",
    "标记图例",
    "干净背诵版",
    "逐字取自",
    "逐字收录",
    "不是信条原文",
    "不是 CCI",
    "本站未改动",
    "校记",
    "来源：",
    "海报原文",
    "讲座幻灯片原文",
    "本页收录用户授权",
)


def _is_notice(tag, cls, inner):
    classes = cls.split()
    if any(c in _NOTICE_CLASSES for c in classes):
        return True
    if "call" in classes and "note" in classes:
        plain = _plain(inner)
        if any(k in plain or k in inner for k in _NOTICE_CALL_HINTS):
            return True
    if tag == "p" and "lead" not in classes:
        plain = _plain(inner)
        if any(k in plain for k in ("来源：", "原文说明", "逐字照录", "逐字取自")):
            return True
    return False


def _extract_buttons(html):
    """Pull useful control widgets out of notice blocks."""
    btns = []
    for m in re.finditer(
        r'<button\b[^>]*>.*?</button>|<label class="cq-recite">.*?</label>',
        html,
        flags=re.S,
    ):
        btns.append(m.group(0))
    return btns


def _move_notices(h):
    # find insertion window: after #ptabrow (or <main>) until first real content
    main = h.find('<main id="main">')
    if main < 0:
        main = h.find("<main")
    if main < 0:
        return h
    # start after ptabrow if present
    pr = h.find('id="ptabrow"', main)
    if pr >= 0:
        ps = h.rfind("<div", main, pr)
        _, pe = _cut_tag(h, ps, "div")
        cursor = pe
    else:
        gt = h.find(">", main) + 1
        cursor = gt

    collected = []
    buttons = []
    kept_prefix = []  # pieces to leave in place (crumb, etc.)
    # Walk siblings until first l2 / article content, extracting notices
    # Also walk through l1 header (leave it) and notices after the header.

    def take_from(start, stop_at_l2=True):
        nonlocal buttons
        out_keep = []
        bits = []
        i = _skip_ws(h, start)
        while i < len(h):
            i = _skip_ws(h, i)
            if i >= len(h) or h.startswith("</main>", i) or h.startswith('<nav class="pager"', i) or h.startswith("<footer", i):
                break
            info = _tag_name(h, i)
            if not info:
                break
            slash, tag = info
            if slash:
                break
            cls, _ = _attr_class(h, i)
            # comments?
            if h.startswith("<!--", i):
                k = h.find("-->", i)
                if k < 0:
                    break
                i = k + 3
                continue
            s, e = _cut_tag(h, i, tag)
            if e <= s:
                break
            block = h[s:e]
            inner_gt = h.find(">", s) + 1
            inner = h[inner_gt:e - len(f"</{tag}>")]
            # always keep the part hero / l1 itself, but recurse into its body after header
            if tag == "section" and _has_class(cls, "l1"):
                # split header vs rest
                hd = re.search(r"<header\b", block)
                if hd:
                    hs, he = _cut_tag(block, hd.start(), "header")
                    # hs is relative to block
                    head = block[hs:he]
                    # opening section tag
                    open_end = block.find(">") + 1
                    close = f"</{tag}>"
                    mid = block[he:len(block) - len(close)]
                    # extract notices from mid
                    sub_keep, sub_bits, mid_end_unused = _extract_sequence(mid)
                    out_keep.append(block[:open_end] + head + sub_keep + close)
                    bits.extend(sub_bits)
                    i = e
                    # after the (first) l1, continue looking? usually more content is inside l1.
                    # if we already consumed the l1, we're done with the prefix.
                    break
                else:
                    out_keep.append(block)
                    i = e
                    break
            if tag == "section" and (_has_class(cls, "l2") or _has_class(cls, "l3")):
                # start of main content — stop
                break
            if tag == "p" and _has_class(cls, "lec-crumb"):
                out_keep.append(block)
                i = e
                continue
            if tag == "p" and _has_class(cls, "cq-fulltitle"):
                out_keep.append(block)
                i = e
                continue
            if tag == "p" and _has_class(cls, "lec-k"):
                # keep section kicker that introduces a grid (content nav)
                out_keep.append(block)
                i = e
                continue
            if tag == "nav" and _has_class(cls, "cq-grid"):
                out_keep.append(block)
                i = e
                continue
            if _is_notice(tag, cls, inner):
                buttons.extend(_extract_buttons(block))
                # for toolbar, still move the whole block (hint prose) to the end;
                # buttons are copied into pgtools
                bits.append(block)
                i = e
                continue
            # unknown block before l1/l2: if it looks like a notice, move; else keep and stop if it's content
            plain = _plain(inner)
            if any(k in plain for k in _NOTICE_CALL_HINTS) and not _has_class(cls, "lead"):
                buttons.extend(_extract_buttons(block))
                bits.append(block)
                i = e
                continue
            # lead sits inside header already; a loose lead before l2 (lecture chapters) — clean and keep
            if tag == "p" and _has_class(cls, "lead"):
                out_keep.append(block)
                i = e
                continue
            # otherwise this is content — stop
            break
        return "".join(out_keep), bits, i

    def _extract_sequence(mid):
        """Extract notices from a fragment (l1 body). Returns (kept, bits, unused)."""
        # operate on a standalone fragment by temporarily walking it
        dummy = mid
        i = _skip_ws(dummy, 0)
        keep, bits = [], []
        while i < len(dummy):
            i = _skip_ws(dummy, i)
            if i >= len(dummy):
                break
            info = _tag_name(dummy, i)
            if not info:
                keep.append(dummy[i:])
                break
            slash, tag = info
            if slash:
                keep.append(dummy[i:])
                break
            cls, _ = _attr_class(dummy, i)
            s, e = _cut_tag(dummy, i, tag)
            if e <= s:
                keep.append(dummy[i:])
                break
            block = dummy[s:e]
            inner_gt = dummy.find(">", s) + 1
            inner = dummy[inner_gt:e - len(f"</{tag}>")]
            if tag == "section" and (_has_class(cls, "l2") or _has_class(cls, "l3")):
                keep.append(dummy[i:])
                break
            if tag == "p" and _has_class(cls, "lec-crumb"):
                keep.append(block); i = e; continue
            if tag == "p" and _has_class(cls, "cq-fulltitle"):
                keep.append(block); i = e; continue
            if tag == "p" and _has_class(cls, "lec-k"):
                keep.append(block); i = e; continue
            if tag == "nav" and _has_class(cls, "cq-grid"):
                keep.append(block); i = e; continue
            if tag == "p" and _has_class(cls, "lead"):
                keep.append(block); i = e; continue
            if _is_notice(tag, cls, inner):
                buttons.extend(_extract_buttons(block))
                bits.append(block)
                i = e
                continue
            plain = _plain(inner)
            if any(k in plain for k in _NOTICE_CALL_HINTS) and not _has_class(cls, "lead"):
                buttons.extend(_extract_buttons(block))
                bits.append(block)
                i = e
                continue
            # content starts
            keep.append(dummy[i:])
            break
        return "".join(keep), bits, i

    keep, bits, new_cursor = take_from(cursor)
    collected.extend(bits)

    if not collected and not buttons:
        # still clean leads; maybe no notices on index
        return h

    # de-dupe buttons (same markup)
    seen_b, uniq_b = set(), []
    for b in buttons:
        if b not in seen_b:
            seen_b.add(b)
            uniq_b.append(b)
    tools = ""
    if uniq_b:
        tools = '<div class="pgtools" role="toolbar" aria-label="本页工具">' + "".join(uniq_b) + "</div>"

    # ids already used in the compact toolbar must not be repeated in the end block
    used_ids = set(re.findall(r'\bid="([^"]+)"', tools))
    def _strip_used_ids(block):
        for i in used_ids:
            block = re.sub(r'\s+id="%s"' % re.escape(i), "", block)
        return block

    # about block (collapse; drop empty after page-cite strip)
    body_bits = []
    seen_c = set()
    for b in collected:
        key = re.sub(r"\s+", "", b)
        if key in seen_c:
            continue
        seen_c.add(key)
        body_bits.append(_strip_used_ids(b))
    # one-line catechism note if this is childq and we dropped 校记
    if 'id="childq"' in h or 'id="cq-1"' in h:
        if not any("个别笔误" in x for x in body_bits):
            body_bits.append('<p class="src">个别笔误已据上下文改正。</p>')
    about = ""
    if body_bits:
        about = (
            '<details class="about-page">'
            "<summary>关于本页 / 来源与说明</summary>"
            '<div class="about-body">' + "".join(body_bits) + "</div>"
            "</details>"
        )

    # rebuild: h[:cursor] + keep (with tools injected after header/lead) + rest from new_cursor
    rest = h[new_cursor:]
    # inject tools at the start of keep if keep begins with section.l1 — actually tools should be
    # after the hero, i.e. after </header> inside the first l1, or before l2 / at start of keep
    if tools:
        if "</header>" in keep:
            keep = keep.replace("</header>", "</header>" + tools, 1)
        else:
            keep = tools + keep

    # place about before pager / footer
    def inject_about(tail):
        if not about:
            return tail
        if 'class="about-page"' in tail or 'class="about-page"' in keep:
            return tail
        for mark in ('<nav class="pager"', '<footer class="foot"', "</main>"):
            k = tail.find(mark)
            if k >= 0:
                return tail[:k] + about + tail[k:]
        return tail + about

    return h[:cursor] + keep + inject_about(rest)


_SCOOP_HINTS = ("📌 说明", "以下为本站归纳", "原文说明", "本页目录覆盖", "来源与版权", "本站未改动一字")


def _inside_about(h, pos):
    a = h.rfind('class="about-page"', 0, pos)
    if a < 0:
        return False
    ds = h.rfind("<details", 0, a)
    if ds < 0:
        return False
    _, de = _cut_tag(h, ds, "details")
    return ds <= pos < de


def _scoop_meta(h):
    """Move leftover 原文说明 / 📌 说明 blocks that still open a section into the end details."""
    moved = []
    guard = 0
    while guard < 80:
        guard += 1
        hit = None
        for m in re.finditer(
            r'<(p|div)(?=[^>]*\bclass="[^"]*\b(?:exn|lec-banner|pdfsrc|call\s+note)\b)[^>]*>',
            h,
        ):
            if _inside_about(h, m.start()):
                continue
            tag = m.group(1)
            s, e = _cut_tag(h, m.start(), tag)
            if e <= s:
                continue
            block = h[s:e]
            cls = re.search(r'\bclass="([^"]*)"', m.group(0))
            classes = (cls.group(1) if cls else "").split()
            if "exn" in classes or "lec-banner" in classes or "pdfsrc" in classes:
                hit = (s, e, block)
                break
            if "call" in classes and "note" in classes:
                if any(k in block for k in _SCOOP_HINTS):
                    hit = (s, e, block)
                    break
        if not hit:
            break
        s, e, block = hit
        moved.append(block)
        h = h[:s] + h[e:]

    if not moved:
        return h

    insertion = "".join(moved)
    mark = '<div class="about-body">'
    i = h.find(mark)
    if i >= 0:
        j = i + len(mark)
        return h[:j] + insertion + h[j:]
    about = (
        '<details class="about-page">'
        "<summary>关于本页 / 来源与说明</summary>"
        f'<div class="about-body">{insertion}</div>'
        "</details>"
    )
    for mk in ('<nav class="pager"', '<footer class="foot"', "</main>"):
        k = h.find(mk)
        if k >= 0:
            return h[:k] + about + h[k:]
    return h + about


def apply(h, page, site):
    h = _assets(h, page, site)
    h = _qa(h)
    h = _strip_page_cites(h)
    h = _reflow(h)
    h = _clean_leads(h)
    h = _move_notices(h)
    h = _scoop_meta(h)
    # Do not run OpenCC t2s over the whole page: it maps 藉→借 and would
    # alter already-simplified CCI / catechism wording. Poster text is
    # converted at render time in c_sot.poster_html.
    # close mkdefs in the end block if it was open
    h = h.replace('<details class="mkdefs" open>', '<details class="mkdefs">')
    return h
