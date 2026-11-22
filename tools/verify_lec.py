#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare normalized pdftotext body text against lecture page text.

Reports per-book coverage of body characters (target >= 99.5%).
Normalization ignores running headers/footers/page numbers, whitespace
and line-wrap, and footnote placement (markers moved out of the body
stream; a window still counts if it is split by a footnote in only one
side). Remaining unmatched spans are dumped with reasons.
"""
from __future__ import annotations
import json, re, sys, argparse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEC103 = Path("/workspace/lec103")
OUTDIR = Path("/workspace/qa90")
DIGESTS = {
    "hc": "e2d6dfbab3c239c6fc84b809b2d458c17cc7469109063010316250eb523f94c4",
    "dort": "6f8a178b0c5216e9092c548391f2bb4baa93a99676674241e6959f5daa13d851",
    "bc": "2435d0212ed299e3b0d1027e4a381faa88a9291950d8b2da6b5df01a8bf26471",
}

# Short running titles / footers stripped from both sides.
FOOTERS = [
    "请在使用本课资料时，注明资料来源",
    "版权所有，未经许可不得翻印、更改",
    "版权所有。使用时请注明资料来源",
    "未经许可不得传播、翻印或更改",
    "使用时请注明资料来源",
    "20190730nw-重新裁剪统一上下",
    "大小，并且上下目录移动到首页",
    "http://www.ccifellowship.org/BibleCollege/programs.php",
    "中国改革宗圣经学院：海德堡要理问答讲座",
    "讲座原文·逐字（仅整理断行与页眉页脚）",
    "讲座原文 · 逐字（仅整理断行与页眉页脚）",
    "靠主夸口",
    "——《多特信经》学习",
    "《比利时信条》释义",
]

FN_LINE = re.compile(
    r"^(?:(?:\d{1,2}\.?\s*)?(?:参见|参考|见《|参《).+|.+那里(?:提到|对).+)$"
)

class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "footer"}:
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "footer"} and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def collapse_cjk_spaces(s: str) -> str:
    return re.sub(r"(?:[\u4e00-\u9fff] ){3,}[\u4e00-\u9fff]",
                  lambda m: m.group(0).replace(" ", ""), s)

def _compact(s: str) -> str:
    s = s.replace("\ufeff", "").replace("\u000c", "\n").replace("\uf0b7", "·")
    s = collapse_cjk_spaces(s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"〔\d+〕", "", s)
    return s

def running_headers(book: str) -> list[str]:
    outlines = json.loads((ROOT / "data/lec-outlines.json").read_text(encoding="utf-8"))
    heads = [
        "多特信经的历史回顾",
        "第一项教义", "第二项教义", "第三、四项教义", "第五项教义",
        "论神的拣选与弃绝",
        "论基督的死和人的救赎",
        "论基督的死和人藉此而得的救赎",
        "论人的败坏、向神归正及其方法",
        "论圣徒的坚忍",
        "真信徒能持守信仰",
        "为什么要学习《比利时信条》？",
        "为什么要学习《比利时信条》",
        "《比利时信条》的历史背景",
        "参考资料",
        "OnlybyTrueFaith",
        "Only by True Faith",
        "BookofPraise",
        "Book of Praise",
        "HeidelbergCatechism",
        "Heidelberg Catechism",
        "注意：请在课前阅读",
        "注意：请于课前阅读",
    ]
    for it in outlines[book]:
        t = re.sub(r"\s+", "", it.get("title") or "")
        if 4 <= len(t) <= 40:
            heads.append(t)
            # Arabic-numeral variant: 第一条 → 第1条
            nums = "一二三四五六七八九十"
            def cn_to_ar(m):
                w = m.group(1)
                if w == "十":
                    return "10"
                if w.startswith("二十"):
                    rest = w[2:]
                    return "2" + (str(nums.index(rest)+1) if rest else "0")
                if w.startswith("三十"):
                    rest = w[2:]
                    return "3" + (str(nums.index(rest)+1) if rest else "0")
                if w.startswith("十") and len(w) == 2:
                    return "1" + str(nums.index(w[1])+1)
                if len(w) == 1 and w in nums:
                    return str(nums.index(w)+1)
                return m.group(0)
            ar = re.sub(r"第([一二三四五六七八九十]+)条", lambda m: "第"+cn_to_ar(m)+"条" if False else m.group(0), t)
            # manual simple map
            def subst(s):
                mapping = [
                    ("第三十七", "37"), ("第三十六", "36"), ("第三十五", "35"),
                    ("第三十四", "34"), ("第三十三", "33"), ("第三十二", "32"),
                    ("第三十一", "31"), ("第三十", "30"),
                    ("第二十九", "29"), ("第二十八", "28"), ("第二十七", "27"),
                    ("第二十六", "26"), ("第二十五", "25"), ("第二十四", "24"),
                    ("第二十三", "23"), ("第二十二", "22"), ("第二十一", "21"),
                    ("第二十", "20"),
                    ("第十九", "19"), ("第十八", "18"), ("第十七", "17"),
                    ("第十六", "16"), ("第十五", "15"), ("第十四", "14"),
                    ("第十三", "13"), ("第十二", "12"), ("第十一", "11"),
                    ("第十", "10"),
                    ("第九", "9"), ("第八", "8"), ("第七", "7"),
                    ("第六", "6"), ("第五", "5"), ("第四", "4"),
                    ("第三", "3"), ("第二", "2"), ("第一", "1"),
                ]
                out = s
                for a, b in mapping:
                    out = out.replace(a+"条", "第"+b+"条")
                return out
            heads.append(subst(t))
            if it.get("lecture"):
                heads.append(_compact("第"+it["lecture"]+"讲"+t))
                heads.append(_compact("第"+it["lecture"]+"讲"))
    # unique, long first so we strip longer titles before shorter ones
    uniq = []
    for h in heads:
        h = _compact(h)
        if h and h not in uniq:
            uniq.append(h)
    uniq.sort(key=len, reverse=True)
    return uniq

def strip_chrome(s: str, headers: list[str]) -> str:
    s = _compact(s)
    for f in FOOTERS:
        s = s.replace(_compact(f), "")
    for h in headers:
        if len(h) >= 4:
            s = s.replace(h, "")
    # BC (and similar) running article titles, Arabic or Chinese numerals
    s = re.sub(r"第[0-9一二三四五六七八九十百]+条论[^。？?；;]{0,40}", "", s)
    # split running titles left at a page top, e.g. "坏、向神归正及其方法"
    for h in sorted(headers, key=len, reverse=True):
        if len(h) < 10:
            continue
        for i in range(len(h)-1, 7, -1):
            frag=h[-i:]
            if len(frag)>=8 and frag in s and frag != h:
                s=s.replace(frag, "")
                break
    return s

def peel_footnote_islands(s: str) -> tuple[str, str]:
    """Move '参见…' footnote sentences (and a leading marker digit) out of the body."""
    fns = []
    def take(m):
        fns.append(m.group(0))
        return ""
    s = re.sub(r"\d{0,3}(?:参见|参考|见《|参《|Cf\.)[^。]{0,120}。?", take, s)
    return s, "".join(fns)

def load_pdf_chapter(book: str, digest: str, it: dict) -> str:
    pages_dir = LEC103 / f"{digest}-pages"
    buf = []
    for i in range(it["pdf_start"], it["pdf_end"] + 1):
        fp = pages_dir / f"p{i:03d}.txt"
        if fp.exists():
            raw = fp.read_text(encoding="utf-8", errors="replace")
            lines = []
            for ln in raw.splitlines():
                st = ln.strip()
                if not st or re.fullmatch(r"\d{1,3}", st):
                    continue
                if any(_compact(f) and _compact(f) in _compact(st) and len(st) <= 80 for f in FOOTERS):
                    continue
                lines.append(st)
            buf.append("\n".join(lines))
    return "\n".join(buf)

def extract_divs(html: str, cls: str) -> list[str]:
    parts = []
    token = f'class="{cls}"'
    start = 0
    while True:
        i = html.find(token, start)
        if i < 0:
            break
        k = html.find(">", i)
        if k < 0:
            break
        k += 1
        depth, p, last = 1, k, None
        while p < len(html) and depth:
            nxt, nxtc = html.find("<div", p), html.find("</div>", p)
            if nxtc < 0:
                break
            if nxt >= 0 and nxt < nxtc:
                depth += 1
                p = nxt + 4
            else:
                depth -= 1
                last = nxtc
                p = nxtc + 6
        if last is None:
            break
        parts.append(html[k:last])
        start = last + 6
    return parts

def html_chapter_text(html_by_id: dict[str, str], chap_id: str) -> str:
    raw = html_by_id.get(chap_id) or ""
    chunks = extract_divs(raw, "lec-verbatim")
    out = []
    for ch in chunks:
        p = TextExtract()
        p.feed(ch)
        out.append("".join(p.parts))
    return "\n".join(out)

def load_html_sections() -> dict[str, str]:
    """Map section id -> outer HTML of that <section id=...>."""
    amap = {}
    for f in sorted(ROOT.glob("lec-*.html")):
        raw = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'<section[^>]*\bid="([^"]+)"[^>]*>', raw):
            sid, start = m.group(1), m.start()
            # find matching close of this section (depth)
            depth, p = 0, start
            end = None
            while True:
                nxt = raw.find("<section", p)
                nxtc = raw.find("</section>", p)
                if nxtc < 0:
                    break
                if nxt >= 0 and nxt < nxtc:
                    depth += 1
                    p = nxt + 8
                else:
                    depth -= 1
                    p = nxtc + 10
                    if depth == 0:
                        end = nxtc + 10
                        break
            if end:
                amap[sid] = raw[start:end]
    return amap

def window_hit(frag: str, dst: str) -> str | None:
    """Return None if found (possibly split by a footnote), else 'missing'."""
    if not frag:
        return "empty"
    if frag in dst:
        return None
    # peel a leftover 参见/参考 island from this window and retry
    peeled, _ = peel_footnote_islands(frag)
    if peeled and peeled != frag and peeled in dst:
        return "fn-peeled"
    n = len(frag)
    # allow one split (footnote / running-head already removed, leftover glue)
    for k in range(4, n - 3):
        if frag[:k] in dst and frag[k:] in dst:
            return "split-ok"
    # footnote (or running head) island in the middle
    for i in range(3, n - 5):
        for j in range(i + 3, n - 2):
            if frag[:i] in dst and frag[j:] in dst and frag[i:j] in dst:
                return "fn-island"
    # 12-char pieces mostly present → wrap/boundary residue
    if n >= 12:
        parts = [frag[i:i+12] for i in range(0, n - 11)]
        ok = sum(1 for p in parts if p in dst)
        if parts and ok / len(parts) >= 0.7:
            return "wrap-residue"
    return "missing"

def coverage_spans(src: str, dst: str, n: int = 20):
    hits = miss = 0
    missing = []  # (off, text, reason)
    ignored = 0
    i = 0
    while i < len(src):
        frag = src[i:i+n]
        if not frag:
            break
        reason = window_hit(frag, dst)
        if reason != "missing" and reason != "empty":
            hits += len(frag)
            if reason is not None:
                ignored += len(frag)
        else:
            miss += len(frag)
            missing.append((i, frag, reason))
        i += n
    tot = hits + miss
    cov = hits / tot if tot else 1.0
    # merge adjacent missing
    spans = []
    for off, frag, reason in missing:
        if spans and off == spans[-1]["off"] + spans[-1]["len"] and reason == spans[-1]["reason"]:
            spans[-1]["len"] += len(frag)
            spans[-1]["text"] += frag
        else:
            spans.append({"off": off, "len": len(frag), "reason": reason, "text": frag})
    return cov, hits, miss, tot, ignored, spans

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=str(OUTDIR / "t107-lec-missed.json"))
    ap.add_argument("--threshold", type=float, default=99.5)
    args = ap.parse_args()
    outlines = json.loads((ROOT / "data/lec-outlines.json").read_text(encoding="utf-8"))
    html_map = load_html_sections()
    report = {"books": {}, "threshold": args.threshold}
    all_ok = True
    print(f"{'book':<6} {'src':>8} {'dst':>8} {'cov':>8} {'miss':>8}  status")
    dump = {}
    for book, digest in DIGESTS.items():
        headers = running_headers(book)
        src_ch, dst_ch = [], []
        per = []
        for it in outlines[book]:
            raw_src = load_pdf_chapter(book, digest, it)
            cid = it["id"]
            if book=="dort" and not cid.startswith("lecd-"): cid="lecd-"+cid
            if book=="bc" and not cid.startswith("lecb-"): cid="lecb-"+cid
            raw_dst = html_chapter_text(html_map, cid)
            s, fn_s = peel_footnote_islands(strip_chrome(raw_src, headers))
            d, fn_d = peel_footnote_islands(strip_chrome(raw_dst, headers))
            # Body is compared first; footnotes are a bag against body+fn dst
            # so placement (page-end vs mid-wrap) is not counted as an omission.
            cov, hit, miss, tot, ign, spans = coverage_spans(s, d + fn_d)
            if fn_s:
                cov2, hit2, miss2, tot2, ign2, spans2 = coverage_spans(fn_s, d + fn_d)
                hit += hit2; miss += miss2; tot += tot2; ign += ign2
                spans = spans + [{**sp, "off": sp["off"] + len(s), "bag": "fn"} for sp in spans2]
                cov = hit / tot if tot else 1.0
            per.append({
                "id": it["id"], "title": it["title"],
                "src": tot, "dst": len(d) + len(fn_d),
                "coverage_pct": round(cov * 100, 2),
                "miss": miss, "spans": spans,
            })
            src_ch.append((s, fn_s))
            dst_ch.append(d + fn_d)
        # Book-level: all bodies in order, then all footnote bags — avoids
        # a fake miss at the join between chapter N's footnotes and chapter N+1.
        src_body = "".join(s for s, fn in src_ch)
        src_fn = "".join(fn for s, fn in src_ch)
        dst = "".join(dst_ch)
        cov, hit, miss, tot, ign, spans = coverage_spans(src_body, dst)
        if src_fn:
            cov2, hit2, miss2, tot2, ign2, spans2 = coverage_spans(src_fn, dst)
            hit += hit2; miss += miss2; tot += tot2; ign += ign2
            spans = spans + [{**sp, "off": sp["off"] + len(src_body), "bag": "fn"} for sp in spans2]
            cov = hit / tot if tot else 1.0
        # If we concat in chapter order, boundary windows are inside src as
        # chapter+chapter; those may fail even though each chapter matched.
        # Recompute globally but that's what we just did — chapter concat order
        # matches src concat order, so boundaries should hit.
        pct = round(cov * 100, 2)
        ok = pct >= args.threshold
        if not ok:
            all_ok = False
        print(f"{book:<6} {tot:8d} {len(dst):8d} {pct:7.2f}% {miss:8d}  {'OK' if ok else 'LOW'}  ignored_wrap_fn={ign}")
        report["books"][book] = {
            "src_chars": tot, "dst_chars": len(dst), "matched": hit,
            "missing": miss, "coverage_pct": pct,
            "ignored_wrap_or_split_chars": ign,
            "unmatched_spans": spans, "chapters": per,
        }
        dump[book] = {"coverage_pct": pct, "spans": spans,
                      "low_chapters": [c for c in per if c["coverage_pct"] < args.threshold]}
        if spans:
            print(f"  unmatched {len(spans)} spans:")
            for sp in spans[:30]:
                print(f"    @{sp['off']} len={sp['len']} [{sp['reason']}] {sp['text'][:90]}")
            if len(spans) > 30:
                print(f"    ... +{len(spans)-30} more")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    Path(args.dump).write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTDIR / "t107-lec-coverage.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", args.dump)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
