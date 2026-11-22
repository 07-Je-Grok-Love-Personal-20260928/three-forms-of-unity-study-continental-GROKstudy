#!/usr/bin/env python3
"""Clean t114 source extracts: TULIP 160-slide deck + Five Solas RTV poster.

Radical rule: a CJK radical (U+2E80–2FDF) or compatibility ideograph,
possibly in a run, immediately followed by a CJK Unified ideograph is a
PDF-layer duplicate. Drop the radical(s), keep the unified character.
Do not NFKC the whole string (that would turn ⽂文 into 文文).
Tabs become spaces. cat -n prefixes and the page-78 tool artifact are dropped.
"""
from __future__ import annotations
import json, re, unicodedata
from pathlib import Path

RADICAL = re.compile(r"[\u2E80-\u2FDF\uF900-\uFAFF]")
UNIFIED = re.compile(r"[\u4E00-\u9FFF\u3400-\u4DBF]")
CATN = re.compile(r"^ *\d+\|")
ARTIFACT = re.compile(r"^\.* *\d+ lines not shown *\.?")
PAGE = re.compile(r"^-- +(\d+) +of +160 +-- *$")

SRC_DECK = Path("/workspace/uploads/t114/tulip-deck-160p.txt")
SRC_POSTER = Path("/workspace/uploads/t114/five-solas-rtv.txt")
OUT = Path(__file__).resolve().parents[1] / "data" / "t114"


def strip_radicals(s: str) -> str:
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if RADICAL.match(ch):
            j = i
            while j < n and RADICAL.match(s[j]):
                j += 1
            if j < n and UNIFIED.match(s[j]):
                i = j  # drop radical run, keep unified
                continue
            # unpaired radical: prefer NFKC if it yields a unified char
            nk = unicodedata.normalize("NFKC", ch)
            if nk and UNIFIED.match(nk[0]) and nk != ch:
                out.append(nk)
            else:
                out.append(ch)
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def clean_line(raw: str) -> str | None:
    s = CATN.sub("", raw).replace("\t", " ").rstrip("\n")
    if ARTIFACT.search(s) or s.strip().endswith("lines not shown ..."):
        return None
    if "lines not shown" in s:
        return None
    return strip_radicals(s)


def load_deck_lines() -> list[str]:
    lines = []
    for raw in SRC_DECK.read_text(encoding="utf-8").splitlines():
        s = clean_line(raw)
        if s is None:
            continue
        lines.append(s)
    return lines


def merge_slide(lines: list[str]) -> str:
    """Join slide-fragment lines into readable paragraphs. No char changes
    other than inserting a single space only when both sides are Latin / digits
    (CJK already runs together). Empty lines become paragraph breaks."""
    paras, buf = [], []

    def flush():
        if not buf:
            return
        acc = buf[0]
        for part in buf[1:]:
            if not part:
                continue
            if acc and (acc[-1].isascii() and acc[-1].isalnum()) and part[0].isascii() and part[0].isalnum():
                acc += " " + part
            else:
                acc += part
        paras.append(acc)
        buf.clear()

    for ln in lines:
        if not ln.strip():
            flush()
        else:
            buf.append(ln.strip())
    flush()
    return "\n\n".join(paras)


def parse_deck() -> dict:
    """Markers sit after the slide they number (PDF footer style).
    Content before `-- N of 160 --` belongs to page N."""
    lines = load_deck_lines()
    pages: list[dict] = []
    cur = []
    for ln in lines:
        m = PAGE.match(ln.strip())
        if m:
            n = int(m.group(1))
            pages.append({"n": n, "lines": cur, "text": merge_slide(cur)})
            cur = []
            continue
        cur.append(ln)
    # trailing non-marker lines should not exist (two blanks after 160 are ok)
    trailing = [x for x in cur if x.strip()]
    assert not trailing, trailing
    assert [p["n"] for p in pages] == list(range(1, 161)), ([p["n"] for p in pages][:8], len(pages))
    # leftover radicals
    blob = "\n".join(p["text"] for p in pages)
    left = sorted({c for c in blob if RADICAL.match(c)})
    return {"pages": pages, "leftover_radicals": left, "chars": len(blob)}


# --- poster: reassemble by unambiguous pairings, keep every Traditional char ---

POSTER_PAIR = [
    # (sola_title_line_hint, statement_line_range inclusive 1-based, quote_range, attribution)
]


def load_poster_raw() -> list[str]:
    # keep every character; only strip a possible cat -n if present (this file has none)
    lines = []
    for i, raw in enumerate(SRC_POSTER.read_text(encoding="utf-8").splitlines(), 1):
        s = raw.replace("\t", " ")
        if s.endswith("\n"):
            s = s[:-1]
        lines.append({"n": i, "text": s})
    return lines


def assemble_poster(raw: list[dict]) -> dict:
    """Reassemble each sola with statement + quote only where pairing is unambiguous.
    Line numbers are 1-based as in the extract. Every character is kept."""
    def L(*ns):
        return [{"n": n, "text": raw[n - 1]["text"]} for n in ns]

    # From the extract (63 lines). Pairings per brief + inspection:
    # 5-10 慈運理 quote, 22-24 唯獨基督 statement
    # 17-21 加爾文 quote, 25-27 唯獨上帝的榮耀 statement
    # 28-32 路德 quote, 33-35 唯獨恩典 statement
    # 39-44 墨藍頓 quote, 36-38 唯獨信心 statement
    # 48-55 貝撒 quote, 45-47 唯獨聖經 statement
    blocks = {
        "front": {
            "title": L(1),
            "banner": L(2),
            "lead": L(3, 4),
        },
        "solas": [
            {
                "id": "solus-christus",
                "name": "唯獨基督",
                "latin": "Solus Christus",
                "statement": L(22, 23, 24),
                "quote": L(5, 6, 7, 8, 9, 10),
            },
            {
                "id": "soli-deo-gloria",
                "name": "唯獨上帝的榮耀",
                "latin": "Soli Deo Gloria",
                "statement": L(25, 26, 27),
                "quote": L(17, 18, 19, 20, 21),
            },
            {
                "id": "sola-gratia",
                "name": "唯獨恩典",
                "latin": "Sola Gratia",
                "statement": L(33, 34, 35),
                "quote": L(28, 29, 30, 31, 32),
            },
            {
                "id": "sola-fide",
                "name": "唯獨信心",
                "latin": "Sola Fide",
                "statement": L(36, 37, 38),
                "quote": L(39, 40, 41, 42, 43, 44),
            },
            {
                "id": "sola-scriptura",
                "name": "唯獨聖經",
                "latin": "Sola Scriptura",
                "statement": L(45, 46, 47),
                "quote": L(48, 49, 50, 51, 52, 53, 54, 55),
            },
        ],
        "close": {
            "exhortation": L(11, 12, 13, 14, 15, 16),
            "credit": L(56, 57, 58, 59, 60, 61, 62, 63),
        },
    }
    # leftover lines (the banner words 唯獨聖經 etc. appear only on line 2;
    # lines 1-63 all accounted)
    used = set()
    for part in (blocks["front"]["title"], blocks["front"]["banner"], blocks["front"]["lead"],
                 blocks["close"]["exhortation"], blocks["close"]["credit"]):
        used.update(x["n"] for x in part)
    for s in blocks["solas"]:
        used.update(x["n"] for x in s["statement"] + s["quote"])
    missing = [i for i in range(1, len(raw) + 1) if i not in used]
    extra = sorted(used - set(range(1, len(raw) + 1)))
    blocks["_coverage"] = {"n_lines": len(raw), "missing": missing, "extra": extra}
    return blocks


SAMPLES = [
    ("加尔文", "加尔文"),
    ("加尔⽂文", "加尔文"),
    ("⼀一", "一"),
    ("⼈人", "人"),
    ("⽬目", "目"),
    ("⽬⽬目", "目"),
    ("⻅见", "见"),
    ("⿁鬼", "鬼"),
    ("⻓长", "长"),
    ("⻢马", "马"),
    ("⻬齐", "齐"),
    ("⻄西", "西"),
    ("⺫目", "目"),
    ("⻦鸟", "鸟"),
    ("⻜飞", "飞"),
    ("更为⼲⼴广泛", "更为广泛"),
    ("以很⼲⼴广泛", "以很广泛"),
]


def self_check():
    fails = []
    for raw, want in SAMPLES:
        got = strip_radicals(raw)
        if got != want:
            fails.append((raw, want, got))
    return fails


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    fails = self_check()
    if fails:
        raise SystemExit("sample cleanup failed: " + repr(fails))
    deck = parse_deck()
    poster_raw = load_poster_raw()
    poster = assemble_poster(poster_raw)

    # flatten cleaned deck as readable text with page markers (markers are ours)
    deck_txt_parts = []
    for p in deck["pages"]:
        deck_txt_parts.append(f"-- {p['n']} of 160 --")
        deck_txt_parts.append(p["text"])
        deck_txt_parts.append("")
    deck_txt = "\n".join(deck_txt_parts).rstrip() + "\n"

    (OUT / "tulip-deck-clean.txt").write_text(deck_txt, encoding="utf-8")
    # compact json: drop raw line arrays to keep file lean? keep them for
    # paragraph rebuild audit
    slim = {
        "source": "讲座幻灯片原文《加尔文主义五要点》，160 页",
        "pages": [{"n": p["n"], "text": p["text"]} for p in deck["pages"]],
        "leftover_radicals": deck["leftover_radicals"],
        "chars": deck["chars"],
    }
    (OUT / "tulip-deck.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "five-solas-rtv.json").write_text(
        json.dumps({"source": "《宗教改革的五個唯獨》RTV TAIWAN × STF 海报原文（繁体）", **poster},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    # also a linear poster text in assembled order, each line tagged
    plines = []
    def emit(label, items):
        plines.append(f"[{label}]")
        for it in items:
            plines.append(f"{it['n']}|{it['text']}")
    emit("title", poster["front"]["title"])
    emit("banner", poster["front"]["banner"])
    emit("lead", poster["front"]["lead"])
    for s in poster["solas"]:
        emit(s["id"] + ".statement", s["statement"])
        emit(s["id"] + ".quote", s["quote"])
    emit("exhortation", poster["close"]["exhortation"])
    emit("credit", poster["close"]["credit"])
    (OUT / "five-solas-rtv-assembled.txt").write_text("\n".join(plines) + "\n", encoding="utf-8")

    print("samples: ok")
    print("deck pages:", len(deck["pages"]), "chars:", deck["chars"], "leftover_radicals:", deck["leftover_radicals"])
    print("poster lines:", poster["_coverage"])
    # print a few cleaned samples from the real deck
    blob = "\n".join(p["text"] for p in deck["pages"])
    for needle in ("加尔文", "广阔", "广泛", "见解", "看见", "马", "齐", "西", "鸟", "飞", "人", "目"):
        i = blob.find(needle)
        print(f"  find {needle!r}:", "OK" if i >= 0 else "MISSING", repr(blob[max(0,i-8):i+16]) if i>=0 else "")
    # leftover any ⼲ ⼴
    for ch in "⼲⼴⽂⼀⼈⽬⻅⿁⻓⻢⻬⻄⺫⻦⻜":
        print(f"  leftover {ch} U+{ord(ch):04X}:", blob.count(ch))


if __name__ == "__main__":
    main()
