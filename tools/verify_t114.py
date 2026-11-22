#!/usr/bin/env python3
"""Verbatim coverage for the t114 lecture deck and five-solas poster."""
import json, re, sys, html as H
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DECK = json.loads((ROOT / "data/t114/tulip-deck.json").read_text(encoding="utf-8"))
POSTER = json.loads((ROOT / "data/t114/five-solas-rtv.json").read_text(encoding="utf-8"))

def pack(s):
    return re.sub(r"\s+", "", s)

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
    poster_lines = []
    for part in (POSTER["front"]["title"], POSTER["front"]["banner"], POSTER["front"]["lead"],
                 POSTER["close"]["exhortation"], POSTER["close"]["credit"]):
        poster_lines.extend(x["text"] for x in part)
    for s in POSTER["solas"]:
        poster_lines.extend(x["text"] for x in s["statement"] + s["quote"])
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
    # all 160 slide markers
    marks = [f"幻灯片第 {n} 页" for n in range(1, 161)]
    absent = [m for m in marks if m not in deck_html]
    print(f"slide markers: {160-len(absent)}/160", ("missing "+str(absent[:5]) if absent else "ok"))
    if absent:
        bad += 1
    return bad

if __name__ == "__main__":
    sys.exit(main())
