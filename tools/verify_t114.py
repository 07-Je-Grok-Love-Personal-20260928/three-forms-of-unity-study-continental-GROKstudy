#!/usr/bin/env python3
"""Verbatim coverage for the t114 lecture deck and five-solas poster."""
import json, re, sys, html as H
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DECK = json.loads((ROOT / "data/t114/tulip-deck.json").read_text(encoding="utf-8"))
POSTER = json.loads((ROOT / "data/t114/five-solas-rtv.json").read_text(encoding="utf-8"))

def pack(s):
    return re.sub(r"\s+", "", s)

def t2s(s):
    try:
        from opencc import OpenCC
        return OpenCC("t2s").convert(s)
    except Exception:
        return s

def text_of(html):
    html = re.sub(r"<script[\s\S]*?</script>", "", html)
    html = re.sub(r"<style[\s\S]*?</style>", "", html)
    html = re.sub(r"<[^>]+>", "", html)
    return H.unescape(html)

def coverage(name, source, html, label):
    src, dst = pack(source), pack(text_of(html))
    if src in dst:
        print(f"{label}: 100% ({len(src)} packed chars in {name})")
        return 0
    # longest prefix
    i = 0
    lim = min(len(src), len(dst))
    # find best window
    pos = dst.find(src[:20]) if len(src) >= 20 else -1
    if pos < 0:
        print(f"{label}: MISSING start {src[:40]!r} in {name}")
        return 1
    j = 0
    k = pos
    while j < len(src) and k < len(dst) and src[j] == dst[k]:
        j += 1; k += 1
    print(f"{label}: prefix {j}/{len(src)} ({j/len(src)*100:.2f}%) break at {src[j:j+24]!r} vs {dst[k:k+24]!r}")
    return 1

def main():
    deck_html = (ROOT / "sot-tulip.html").read_text(encoding="utf-8")
    sola_html = (ROOT / "sot-sola.html").read_text(encoding="utf-8")
    # drop the inserted slide labels before packing the whole deck
    src_deck = "".join(p["text"] for p in DECK["pages"])
    deck_html_for_pack = re.sub(r"幻灯片第\s*\d+\s*页", "", deck_html)
    poster_lines = []  # filled below, then converted t2s
    for part in (POSTER["front"]["title"], POSTER["front"]["banner"], POSTER["front"]["lead"],
                 POSTER["close"]["exhortation"], POSTER["close"]["credit"]):
        poster_lines.extend(x["text"] for x in part)
    for s in POSTER["solas"]:
        poster_lines.extend(x["text"] for x in s["statement"] + s["quote"])
    poster_lines = [t2s(ln).replace("\u0336", "——") for ln in poster_lines]
    # also check each line individually (order may follow assembled blocks, not extract order)
    bad = 0
    coverage("sot-tulip.html", src_deck, deck_html_for_pack, "tulip-deck (contiguous, section titles may split)")
    # per-page
    nmiss=0
    for p in DECK["pages"]:
        if pack(p["text"]) and pack(p["text"]) not in pack(text_of(deck_html_for_pack)):
            nmiss+=1
            if nmiss<=5: print(" missing page", p["n"], p["text"][:40])
    print(f"tulip-deck pages present: {160-nmiss}/160")
    if nmiss: bad += 1
    # per poster line
    dst = pack(text_of(sola_html))
    miss = [ln for ln in poster_lines if pack(ln) and pack(ln) not in dst]
    if miss:
        print(f"five-solas-poster: missing {len(miss)}/{len(poster_lines)} lines")
        for ln in miss[:8]:
            print("  ", ln[:60])
        bad += 1
    else:
        print(f"five-solas-poster: {len(poster_lines)}/{len(poster_lines)} lines present")
    # slide page chips must be gone; compare deck as reflowed packed text
    marks = [f"幻灯片第 {n} 页" for n in range(1, 161)]
    present = [m for m in marks if m in deck_html]
    print(f"slide markers removed: {160-len(present)}/160", ("leftover "+str(present[:5]) if present else "ok"))
    if present:
        bad += 1

    # children's catechism: 130/130 exact packed coverage of each Q+A line
    cq_path = ROOT / "data/t114/child-catechism-130-corrected.txt"
    cq_html = (ROOT / "childq.html").read_text(encoding="utf-8")
    cq_dst = pack(text_of(cq_html))
    book = r"(?:创|出|利|民|申|书|士|得|撒上|撒下|王上|王下|代上|代下|拉|尼|斯|伯|诗|箴|传|歌|赛|耶|哀|结|但|何|珥|摩|俄|拿|弥|鸿|哈|番|该|亚|玛|太|可|路|约|徒|罗|林前|林后|加|弗|腓|西|帖前|帖后|提前|提后|多|门|来|雅|彼前|彼后|约壹|约贰|约叁|犹|启)"
    ref1 = book + r"\d+：[0-9]+(?:-[0-9]+)?(?:、[0-9]+(?:-[0-9]+)?)*"
    refs = re.compile(r"(" + ref1 + r"(?:、" + ref1 + r")*)$")
    cq_lines = cq_path.read_text(encoding="utf-8").splitlines()
    cq_title = cq_lines[0]
    if pack(cq_title) not in cq_dst:
        print("child-catechism title missing:", cq_title)
        bad += 1
    qitems = []
    i = 1
    while i < len(cq_lines):
        ln = cq_lines[i]
        if ln.startswith("## "):
            if pack(ln[3:]) not in cq_dst:
                print("child-catechism section missing:", ln[3:])
                bad += 1
            i += 1
            continue
        if not re.match(r"^\d+", ln):
            print("child-catechism unparsed:", ln)
            bad += 1
            i += 1
            continue
        i += 1
        if i >= len(cq_lines) or not cq_lines[i].startswith("\t"):
            print("child-catechism missing answer after", ln)
            bad += 1
            continue
        body = cq_lines[i][1:]
        qitems.append((ln, body))
        i += 1
    nmiss = 0
    for q, a in qitems:
        if pack(q) not in cq_dst or pack(a) not in cq_dst:
            nmiss += 1
            if nmiss <= 8:
                print(" missing", q[:40], "|", a[:40])
    print(f"child-catechism questions: {len(qitems)-nmiss}/{len(qitems)}")
    if nmiss or len(qitems) != 130:
        if len(qitems) != 130:
            print(f"child-catechism expected 130 items, got {len(qitems)}")
        bad += 1

    return bad


if __name__ == "__main__":
    sys.exit(main())
