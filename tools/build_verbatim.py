#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean pdftotext -layout extracts into structured verbatim chapters.

Fixes only extraction artifacts (running headers/footers, page numbers,
broken line-wraps, spaced-out CJK). No rewording, no omissions.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path("/workspace/lec103")
REPO = Path("/workspace/three-forms-of-unity-study-continental-20261017")
OUT = REPO / "data" / "lec-verbatim"

BOOKS = {
    "hc": {
        "pages": ROOT / "e2d6dfbab3c239c6fc84b809b2d458c17cc7469109063010316250eb523f94c4-pages",
        "title": "中国改革宗圣经学院：海德堡要理问答讲座",
        "headers": [
            "中国改革宗圣经学院：海德堡要理问答讲座",
            "http://www.ccifellowship.org/BibleCollege/programs.php",
        ],
    },
    "dort": {
        "pages": ROOT / "6f8a178b0c5216e9092c548391f2bb4baa93a99676674241e6959f5daa13d851-pages",
        "title": "靠主夸口——《多特信经》学习",
        "headers": [
            "靠主夸口",
            "——《多特信经》学习",
            "亚瑟·范·德尔登",
        ],
    },
    "bc": {
        "pages": ROOT / "2435d0212ed299e3b0d1027e4a381faa88a9291950d8b2da6b5df01a8bf26471-pages",
        "title": "《比利时信条》释义",
        "headers": [
            "《比利时信条》释义",
            "克莱伦斯·鲍曼",
        ],
    },
}

FOOTER_RE = re.compile(r"(请在使用本课资料时，注明资料来源|版权所有[，。]?未经许可不得翻印、更改|版权所有。使用时请注明资料来源|未经许可不得传播、翻印或更改|使用时请注明资料来源)")
CROP_RE = re.compile(r"(20190730nw|重新裁剪统一上下|上下目录移动到首页)")
PAGE_NUM_RE = re.compile(r"^\s*(\d{1,3})\s*$")
CJK = r"\u4e00-\u9fff"
END_PUNCT = "。！？：；…」』）)”:\"」"
HEAD_HINT = re.compile(
    r"^(第[一二三四五六七八九十百零0-9]+讲|第[一二三四五六七八九十]+条|主日\s*\d+|阅读经文|问答题|总结|本讲小结|思考题|讨论问题|"
    r"第一部|第二部|第三部|第[一二三四五]项教义|错谬反驳|谬误反驳)"
)

def collapse_cjk_spaces(s: str) -> str:
    return re.sub(
        rf"(?:[{CJK}] ){{3,}}[{CJK}]",
        lambda m: m.group(0).replace(" ", ""),
        s,
    )

def looks_heading(ln: str, chapter_heads=None) -> bool:
    t = ln.strip()
    if not t or len(t) > 48:
        return False
    if t[0] in "，。、；！？）)]”'" or t.startswith(("了", "的会议", "任命他", "也没有", "局如何", "同？")):
        return False
    if HEAD_HINT.match(t):
        return True
    if chapter_heads:
        for h in chapter_heads:
            h = (h or "").strip()
            if len(h) < 5 or len(h) > 36:
                continue
            # outlines sometimes stored mid-wrap fragments as "headings"
            if "。" in h or h[0] in "，。、；！？）)]”'" or re.match(r"^[了的也同局列]", h):
                continue
            if t == h or (len(h) >= 6 and (t.startswith(h) or h.startswith(t))):
                return True
    return False


def clean_page(raw: str, book: str, freq_headers) -> tuple[int | None, list[str]]:
    text = raw.replace("\ufeff", "").replace("\u000c", "\n").replace("\uf0b7", "·")
    lines = text.splitlines()
    print_no = None
    body: list[str] = []
    # first pass: drop footers, crop notes, capture page number near top
    content_i = 0
    for i, ln in enumerate(lines):
        if CROP_RE.search(ln):
            continue
        if FOOTER_RE.search(ln):
            # drop rest of page (footer block)
            break
        if print_no is None and i < 8 and PAGE_NUM_RE.match(ln):
            print_no = int(ln.strip())
            continue
        body.append(ln)
        if ln.strip():
            content_i += 1

    # strip running headers from the top few non-empty lines
    stripped: list[str] = []
    seen_text = 0
    for ln in body:
        s = collapse_cjk_spaces(re.sub(r"[ \t]+", " ", ln)).strip()
        if not s:
            if stripped and stripped[-1] != "":
                stripped.append("")
            continue
        # drop exact / prefix header lines near the top of the page
        is_hdr = (
            s in freq_headers
            or any(s == h or s.startswith(h) for h in BOOKS[book]["headers"])
            or (seen_text < 3 and s.startswith("http://") or s.startswith("https://"))
        )
        if is_hdr and seen_text < 5:
            continue
        seen_text += 1
        stripped.append(s)
    # trim trailing empties
    while stripped and not stripped[-1]:
        stripped.pop()
    return print_no, stripped

def frequent_headers(pages: dict[int, str], book: str) -> set[str]:
    from collections import Counter
    c = Counter()
    n = 0
    for raw in pages.values():
        n += 1
        nonempty = [collapse_cjk_spaces(re.sub(r"[ \t]+", " ", ln)).strip()
                    for ln in raw.splitlines() if ln.strip()]
        for ln in nonempty[:6]:
            if 4 <= len(ln) <= 40 and not PAGE_NUM_RE.match(ln):
                c[ln] += 1
    # appear on >= 15% of pages and at least 8 times
    return {k for k, v in c.items() if v >= max(8, int(n * 0.15))}

def load_pages(book: str) -> dict[int, str]:
    d = BOOKS[book]["pages"]
    out = {}
    for p in sorted(d.glob("p*.txt")):
        out[int(p.stem[1:])] = p.read_text(encoding="utf-8", errors="replace")
    return out

def join_paragraphs(lines: list[str], heads: list[str]) -> list[tuple[str, str]]:
    """Return list of (kind, text) where kind in p/h/q/li/fn."""
    chunks: list[str] = []
    for ln in lines:
        if ln == "":
            chunks.append("")  # paragraph break
            continue
        if not chunks:
            chunks.append(ln)
            continue
        prev = chunks[-1]
        if prev == "" or looks_heading(ln, heads) or looks_heading(prev, heads):
            chunks.append(ln)
            continue
        # never glue a new question or answer onto the previous line / footnote
        if re.match(r"^(答：|答:|\d+\s*[\.．、]?\s*问：)", ln):
            chunks.append(ln)
            continue
        # hyphenated latin wrap
        if re.search(r"[A-Za-z]-$", prev) and re.match(r"[A-Za-z]", ln):
            chunks[-1] = prev[:-1] + ln
            continue
        ended = bool(re.search(r"[。！？…][」』”\")]*$", prev)) or prev.endswith(("：", ":"))
        if not ended:
            if re.search(rf"[{CJK}]$", prev) and re.match(rf"[{CJK}“「]", ln):
                chunks[-1] = prev + ln
            else:
                chunks[-1] = prev.rstrip() + " " + ln
            continue
        chunks.append(ln)

    blocks: list[tuple[str, str]] = []
    for ch in chunks:
        t = ch.strip()
        if not t:
            continue
        if looks_heading(t, heads):
            blocks.append(("h", t))
        elif t.startswith(("“", "「")) and len(t) > 8:
            blocks.append(("q", t))
        elif re.match(r"^(·|•|\d+[\.、]|（\d+）|\(\d+\))", t):
            blocks.append(("li", t))
        elif re.match(r"^\d+\s+\S", t) and len(t) < 200 and not re.match(r"^\d{4}", t):
            # possible footnote "1 text"
            blocks.append(("fn", t))
        else:
            blocks.append(("p", t))
    # attach a short leading scripture parenthesis to the previous block
    merged=[]
    for kind, text in blocks:
        if merged and (m:=re.match(r"^[（(][\u4e00-\u9fffA-Za-z0-9:：,，\-–—\s]{2,40}[）)]", text)):
            pk, pt = merged[-1]
            merged[-1]=(pk, pt + m.group(0))
            rest=text[m.end():].strip()
            if rest:
                merged.append((kind, rest))
            continue
                # lone footnote number-as-heading already handled; merge "1. 参见..." already
        if kind=="h" and text.isdigit():
            continue
        merged.append((kind, text))
    return merged

def drop_mid_sentence_fn_markers(lines):
    """A lone footnote number that lands between two halves of one sentence
    (common in pdftotext footnote blocks) must not be glued into the sentence."""
    out=[]
    i=0
    while i < len(lines):
        s=lines[i].strip()
        if s.isdigit() and 1 <= int(s) <= 200:
            prev = next((x.strip() for x in reversed(out) if x.strip()), "")
            ended = prev.endswith(("。","！","？","…","：",":"))
            if prev and not ended:
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                continue
        out.append(lines[i])
        i += 1
    return out

def expected_print(page_start, pdf_start, fp, detected):
    mapped = page_start + (fp - pdf_start)
    return detected if detected == mapped else mapped

def drop_trailing_page_no(lines, pno):
    if not lines or pno is None:
        return lines
    # last nonempty line is a lone page number
    i = len(lines) - 1
    while i >= 0 and not lines[i].strip():
        i -= 1
    if i >= 0 and lines[i].strip().isdigit() and int(lines[i].strip()) == pno:
        return lines[:i]
    return lines

def merge_footnote_markers(lines):
    """Turn a lone integer line + following text into a single footnote line."""
    out=[]
    i=0
    while i < len(lines):
        s=lines[i].strip()
        if s.isdigit() and 1 <= int(s) <= 200:
            prev = next((x.strip() for x in reversed(out) if x.strip()), "")
            ended = (not prev) or prev.endswith(("。","！","？","…","：",":"))
            if prev and not ended:
                # mid-sentence marker: skip the number, keep the sentence joining
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                continue
            nxt=""
            j=i+1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                nxt=lines[j].strip()
            # if next is not a new section heading, treat as footnote
            if nxt and not looks_heading(nxt) and not nxt.startswith(("第", "主日")):
                out.append(f"{s}. {nxt}")
                i=j+1
                continue
        out.append(lines[i])
        i += 1
    return out


def peel_running_title_leaks(blocks, title_heads):
    """Remove a running title that pdftotext glued into a longer paragraph."""
    heads=[]
    seen=set()
    for h in title_heads or []:
        hs=re.sub(r"\s+", "", (h or "").strip())
        if 6 <= len(hs) <= 48 and hs not in seen:
            seen.add(hs); heads.append(hs)
    # longest first so we strip the full title before a short fragment
    heads.sort(key=len, reverse=True)
    if not heads:
        return blocks
    out=[]
    for kind, text in blocks:
        if kind in {"h","pg"} or not text:
            out.append((kind, text)); continue
        compact=re.sub(r"\s+", "", text)
        new=text
        for h in heads:
            if h and h in compact and compact != h:
                # only drop a mid-paragraph occurrence, not a heading-only block
                new=new.replace(h, "")
                # also drop if original had spaces inside the title
                new=re.sub(re.escape(h), "", new)
        new=re.sub(r"[ \t]{2,}", " ", new).strip()
        if new:
            out.append((kind, new))
    return out

def slice_chapter(cleaned, pdf_start, pdf_end, page_start, heads, title_heads=None):
    """Concatenate chapter pages, join wraps across page breaks, mark print pages."""
    pages_used=[]
    stream=[]  # ('pg', pno, fp) or ('ln', text, pno)
    prev_tail=None
    pending_fn=[]
    all_fns=[]
    title_heads = [h for h in (title_heads or []) if h]
    seen_tops=set()
    for h in title_heads:
        hs=h.strip()
        if hs:
            seen_tops.add(hs)
            seen_tops.add(re.sub(r"\s+", "", hs))
    for fp in range(pdf_start, pdf_end + 1):
        if fp not in cleaned:
            continue
        detected, lines = cleaned[fp]
        pno = expected_print(page_start, pdf_start, fp, detected)
        lines = drop_trailing_page_no(lines, pno)
        # peel trailing footnotes (marker + 参见/参考) so a mid-wrap body line can join the next page
        foot_lines=[]
        while lines:
            s=lines[-1].strip()
            if not s:
                lines.pop(); continue
            if s.isdigit() and 1<=int(s)<=200:
                foot_lines.append(lines.pop()); continue
            if s.startswith(("参见","参考","见《")) or re.match(r"^\d+\.?\s*(参见|参考|见《)", s) or (s.startswith("1.") and "参见" in s):
                foot_lines.append(lines.pop()); continue
            break
        foot_lines=list(reversed(foot_lines))
        # Drop a top-of-page running title only when it is the chapter title
        # or a short line already seen in this chapter. Never drop a first-occurrence
        # Q&A / section heading (those were being swallowed as "running titles").
        if stream and lines:
            top=next((ln for ln in lines if ln.strip()), "")
            ts=top.strip()
            compact=lambda s: re.sub(r"\s+", "", s or "")
            is_run = False
            if ts and len(ts) <= 48:
                if ts in seen_tops or compact(ts) in seen_tops:
                    is_run = True
                else:
                    for h in title_heads:
                        hc, sc = compact(h), compact(ts)
                        if not hc or len(hc) < 4 or len(hc) > 48:
                            continue
                        if sc == hc:
                            is_run = True
                            break
                        # split running titles: "论人的败" / "坏、向神归正及其方法"
                        if len(sc) >= 8 and (hc.endswith(sc) or sc.endswith(hc) or (len(hc) >= 8 and sc.startswith(hc))):
                            is_run = True
                            break
            if is_run:
                dropped=False
                new=[]
                for ln in lines:
                    if not dropped and ln.strip() and ln.strip()==ts:
                        dropped=True
                        continue
                    new.append(ln)
                lines=new
        for ln in lines:
            s=ln.strip()
            if s and len(s) <= 48:
                seen_tops.add(s)
                seen_tops.add(re.sub(r"\s+", "", s))
        lines = merge_footnote_markers(lines)
        lines = drop_mid_sentence_fn_markers(lines)
        # peel again after merging "1" + "参见..." into one line
        while lines:
            s=lines[-1].strip()
            if not s:
                lines.pop(); continue
            if s.startswith(("参见","参考","见《")) or re.match(r"^\d+\.?\s*(参见|参考|见《)", s):
                foot_lines.append(lines.pop()); continue
            break
        foot_lines=list(dict.fromkeys(foot_lines))  # keep order, no dups if peeled twice
        # restore order: earlier peel was reversed already; re-run unique only
        pages_used.append({"file_page": fp, "print_page": pno})
        stream.append(("pg", pno, fp))
        # If previous page ended mid-wrap, glue first nonempty line back
        if prev_tail is not None:
            k=0
            while k < len(lines) and not lines[k].strip():
                k += 1
            if k < len(lines):
                stream.append(("ln", lines[k], pno))
                lines=lines[k+1:]
            prev_tail=None
        all_fns.extend((pno, fl) for fl in pending_fn)
        pending_fn=[]
        for ln in lines:
            stream.append(("ln", ln, pno))
        nonempty=[ln for ln in lines if ln.strip()]
        if nonempty and not re.search(r"[。！？…][」』”\")]*$", nonempty[-1]) and not nonempty[-1].endswith(("：", ":")):
            prev_tail=True
        else:
            prev_tail=None
        pending_fn = foot_lines


    all_fns.extend((page_start, fl) for fl in pending_fn)
    # flatten to lines with page side-channel via sentinel
    lines=[]
    page_of=[]
    pg_at=[]
    for item in stream:
        if item[0]=="pg":
            pg_at.append((len(lines), item[1], item[2]))
        else:
            lines.append(item[1])
            page_of.append(item[2])
    joined = join_paragraphs(lines, heads)
    joined = peel_running_title_leaks(joined, title_heads)
    # assign pages: walk original lines? simpler: use first page marker then current
    # join_paragraphs lost line index; estimate by text search
    blocks=[]
    # re-emit page markers in order, interleave by finding first occurrence
    # Collect joined texts and later attach the page of the first source line they contain.
    # Simpler approach: rebuild with page-aware join below if needed.
    # For now, stamp each joined block with the page of the earliest matching line.
    used=set()
    cur_page = page_start
    pg_iter = iter(pg_at)
    next_pg = next(pg_iter, None)
    # We'll just insert all pg markers first then blocks? No — insert pg when content from that page starts.
    # Approximate: after join, scan
    text_to_page=[]
    idx=0
    # map each original non-empty line to page
    src=[(ln, pg) for ln, pg in zip(lines, page_of) if ln.strip()]
    for kind, text in joined:
        p = cur_page
        for ln, pg in src:
            if ln and ln[:8] in text:
                p=pg
                break
        blocks.append((kind, text, p))
    # now interleave pg markers in print-page order at first block of that page
    out=[]
    seen=set()
    for kind, text, p in blocks:
        if p not in seen:
            out.append(("pg", p, p))
            seen.add(p)
        out.append((kind, text, p))
    # attach footnotes after the last content block of the same print page
    if all_fns:
        attached=[]
        used=set()
        for i,b in enumerate(out):
            attached.append(b)
            page=b[1] if b[0]=='pg' else b[2]
            # if next block jumps to a later page, flush fns for this page
            nxt=out[i+1] if i+1<len(out) else None
            nxtp=None
            if nxt:
                nxtp=nxt[1] if nxt[0]=='pg' else nxt[2]
            if nxt is None or (nxtp and nxtp!=page):
                for pno, fl in all_fns:
                    if pno==page and (pno, fl) not in used:
                        attached.append(("fn", fl if fl.startswith(tuple("123456789")) else fl, pno))
                        used.add((pno, fl))
        out=attached
    return out, pages_used

def to_json_blocks(blocks):
    out = []
    for b in blocks:
        if b[0] == "pg":
            out.append({"type": "pg", "page": b[1], "file_page": b[2]})
        else:
            out.append({"type": b[0], "text": b[1], "page": b[2]})
    return out

def body_char_count(blocks) -> int:
    n = 0
    for b in blocks:
        if b.get("type") in {"p", "h", "q", "li", "fn"}:
            n += len(re.sub(r"\s+", "", b["text"]))
    return n

def main():
    outlines = json.loads((REPO / "data" / "lec-outlines.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for book in ("hc", "dort", "bc"):
        raw_pages = load_pages(book)
        freq = frequent_headers(raw_pages, book)
        cleaned = {fp: clean_page(raw, book, freq) for fp, raw in raw_pages.items()}
        chapters = []
        for it in outlines[book]:
            heads = [h["text"].strip() for h in (it.get("headings") or []) if h.get("text")]
            heads.append(it["title"])
            if it.get("lecture"):
                heads.append(f'第{it["lecture"]}讲')
            title_heads = [it["title"]]
            if it.get("lecture"):
                title_heads += [f'第{it["lecture"]}讲', f'第{it["lecture"]}讲{it["title"]}']
            # recurring section labels that are true running heads, not body titles
            title_heads += [
                "第一项教义","第二项教义","第三、四项教义","第三、 四项教义",
                "第五项教义","多特信经的历史回顾",
                "论神的拣选与弃绝","论基督的死和人的救赎",
                "论人的败坏、向神归正及其方法","论圣徒的坚忍",
            ]
            blocks, used = slice_chapter(cleaned, it["pdf_start"], it["pdf_end"], it["page_start"], heads, title_heads)
            jb = to_json_blocks(blocks)
            chapters.append({
                "id": it["id"],
                "lecture": it.get("lecture"),
                "title": it["title"],
                "source": it.get("source") or "",
                "page_start": it["page_start"],
                "page_end": it["page_end"],
                "pdf_start": it["pdf_start"],
                "pdf_end": it["pdf_end"],
                "headings": it.get("headings") or [],
                "blocks": jb,
                "chars": body_char_count(jb),
            })
        payload = {
            "book": book,
            "title": BOOKS[book]["title"],
            "source": outlines["sources"][book],
            "freq_headers_stripped": sorted(freq),
            "chapters": chapters,
            "chapter_count": len(chapters),
            "chars": sum(c["chars"] for c in chapters),
        }
        dest = OUT / f"{book}.json"
        dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        summary[book] = {
            "chapters": len(chapters),
            "chars": payload["chars"],
            "headers": sorted(freq)[:12],
            "file": str(dest),
            "kb": round(dest.stat().st_size / 1024, 1),
        }
        print(f"{book}: {summary[book]['chapters']} chapters, {summary[book]['chars']} chars, {summary[book]['kb']} KB")
        # sample first chapter first 8 blocks
        ch0 = chapters[0]
        print(f"  first: {ch0['id']} {ch0['title']} p{ch0['page_start']}-{ch0['page_end']} chars={ch0['chars']}")
        for b in ch0["blocks"][:10]:
            if b["type"] == "pg":
                print(f"    [pg {b['page']}]")
            else:
                print(f"    [{b['type']}] {b['text'][:80]}")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)

if __name__ == "__main__":
    main()
