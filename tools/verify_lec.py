#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare normalized pdftotext body text against lecture page text.

Reports per-book coverage of body characters (target ~100%).
Strips running headers/footers/page numbers and whitespace; does not
require punctuation-identical wrapping.
"""
from __future__ import annotations
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEC103 = Path("/workspace/lec103")
PDFS = {
    "hc": ("e2d6dfbab3c239c6fc84b809b2d458c17cc7469109063010316250eb523f94c4",
           list(ROOT.glob("lec-hc*.html"))),
    "dort": ("6f8a178b0c5216e9092c548391f2bb4baa93a99676674241e6959f5daa13d851",
             list(ROOT.glob("lec-dort*.html"))),
    "bc": ("2435d0212ed299e3b0d1027e4a381faa88a9291950d8b2da6b5df01a8bf26471",
           list(ROOT.glob("lec-bc*.html"))),
}

HDR = re.compile(
    r"(中国改革宗圣经学院：海德堡要理问答讲座|"
    r"http://www\.ccifellowship\.org/BibleCollege/programs\.php|"
    r"请在使用本课资料时，注明资料来源|"
    r"版权所有，未经许可不得翻印、更改|"
    r"20190730nw|重新裁剪统一上下|上下目录移动到首页|"
    r"靠主夸口|——《多特信经》学习|"
    r"《比利时信条》释义)"
)
# front-matter / TOC file pages excluded from the body corpus (by file page)
# Use outline pdf ranges: everything not in any chapter is front matter.

class TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts=[]
        self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in {"script","style","nav","footer"}:
            self.skip += 1
        # only count verbatim blocks when class contains lec-verbatim — handled by pre-slice
    def handle_endtag(self, tag):
        if tag in {"script","style","nav","footer"} and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def extract_divs(html: str, cls: str) -> list[str]:
    parts=[]
    token=f'class="{cls}"'
    start=0
    while True:
        i=html.find(token, start)
        if i<0:
            break
        j=html.rfind("<div", 0, i)
        if j<0:
            break
        # move to end of opening tag
        k=html.find(">", i)
        if k<0:
            break
        k += 1
        depth=1
        p=k
        last=None
        while p < len(html) and depth:
            nxt=html.find("<div", p)
            nxtc=html.find("</div>", p)
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

def html_verbatim_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    chunks = extract_divs(raw, "lec-verbatim")
    out=[]
    for ch in chunks:
        parser=TextExtract()
        parser.feed(ch)
        out.append("".join(parser.parts))
    return "\n".join(out)


def collapse_cjk_spaces(s: str) -> str:
    return re.sub(r"(?:[\u4e00-\u9fff] ){3,}[\u4e00-\u9fff]",
                  lambda m: m.group(0).replace(" ", ""), s)

def norm(s: str, pdf_lines: bool=False) -> str:
    s = s.replace("\ufeff", "").replace("\u000c", "\n").replace("\uf0b7", "·")
    if pdf_lines:
        lines=[]
        for ln in s.splitlines():
            st=ln.strip()
            if not st:
                continue
            if re.fullmatch(r"\d{1,3}", st):
                continue
            # drop short running-header / footer lines only
            if len(st) <= 60 and HDR.search(st):
                continue
            lines.append(collapse_cjk_spaces(ln))
        s="".join(lines)
    else:
        s=collapse_cjk_spaces(s)
    s = re.sub(r"\s+", "", s)
    # running titles glued into the PDF stream; drop from both sides
    for h in (
        "中国改革宗圣经学院：海德堡要理问答讲座",
        "http://www.ccifellowship.org/BibleCollege/programs.php",
        "请在使用本课资料时，注明资料来源",
        "版权所有，未经许可不得翻印、更改",
        "20190730nw-重新裁剪统一上下",
        "大小，并且上下目录移动到首页",
        "多特信经的历史回顾",
        "第一项教义",
        "第二项教义",
        "第三、四项教义",
        "第五项教义",
        "《比利时信条》释义",
        "靠主夸口",
        "——《多特信经》学习",
        "讲座原文·逐字（仅整理断行与页眉页脚）",
        "版权所有。使用时请注明资料来源",
        "未经许可不得传播、翻印或更改",
        "使用时请注明资料来源",
        "为什么要学习《比利时信条》？",
        "为什么要学习《比利时信条》",
        "《比利时信条》的历史背景",
    ):
        s=s.replace(re.sub(r"\s+", "", h), "")
    s=re.sub(r"〔\d+〕", "", s)
    return s


def load_pdf_body(book: str, digest: str) -> str:
    outlines = json.loads((ROOT / "data/lec-outlines.json").read_text(encoding="utf-8"))
    pages_dir = LEC103 / f"{digest}-pages"
    spans = [(it["pdf_start"], it["pdf_end"]) for it in outlines[book]]
    buf=[]
    for a,b in spans:
        for i in range(a, b+1):
            fp = pages_dir / f"p{i:03d}.txt"
            if fp.exists():
                buf.append(fp.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(buf)

def coverage(src: str, dst: str, n: int = 20):
    """Non-overlapping n-gram coverage: what share of the PDF body
    appears in the page text (order of files does not matter)."""
    if not src:
        return 1.0, 0, 0, 0
    if len(src) < n:
        ok = src in dst
        return (1.0 if ok else 0.0), (len(src) if ok else 0), (0 if ok else len(src)), len(src)
    hit = miss = 0
    for i in range(0, len(src), n):
        frag = src[i:i+n]
        if not frag:
            continue
        if frag in dst:
            hit += len(frag)
        else:
            miss += len(frag)
    tot = hit + miss
    return (hit / tot if tot else 1.0), hit, miss, tot


def main():
    report={"books":{}}
    all_ok=True
    print(f"{'book':<6} {'src':>8} {'dst':>8} {'cov':>8} {'miss':>8}")
    for book, (digest, files) in PDFS.items():
        files=sorted(files)
        src=norm(load_pdf_body(book, digest), pdf_lines=True)
        dst=norm("".join(html_verbatim_text(f) for f in files), pdf_lines=False)
        cov, hit, miss, n = coverage(src, dst)
        report["books"][book]={
            "src_chars": n, "dst_chars": len(dst),
            "matched": hit, "missing": miss,
            "coverage_pct": round(cov*100, 2),
            "pages": [f.name for f in files],
        }
        mark="OK" if cov >= 0.97 else "LOW"
        if cov < 0.97:
            all_ok=False
        print(f"{book:<6} {n:8d} {len(dst):8d} {cov*100:7.2f}% {miss:8d}  {mark}  files={len(files)}")
    outp=Path("/workspace/qa90/t107-lec-coverage.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", outp)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
