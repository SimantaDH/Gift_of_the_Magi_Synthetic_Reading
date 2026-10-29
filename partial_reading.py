"""
STEP 1 — PARTIAL READING (Synthetic Reading method, Ghosh et al. 2026)

Divides the corpus into N equal parts (by sentence count) and selects 20% of
the sentences ("lines") from each part, so the researcher can form an initial
impression WITHOUT reading the whole story.

Selection strategy per part (configurable below):
    "first"  -> the first 20% of the part
    "middle" -> the central 20% of the part
    "last"   -> the last 20% of the part
    "random" -> a random 20% of the part (fixed seed, so it is reproducible)

Default: 3 equal parts -> Beginning (first 20%), Middle (random 20%), End (last 20%),
mirroring the beginning / random-middle / end design of the original study.

Usage:
    python partial_reading.py
    python partial_reading.py --parts 4 --strategies first random random last --seed 7
"""

import argparse
import random
import re
from pathlib import Path

CORPUS = Path(__file__).with_name("corpus_gift_of_the_magi.txt")
OUTPUT = Path(__file__).with_name("partial_reading.txt")
FRACTION = 0.20


def load_story_body(path: Path) -> str:
    """Return the story text without the title and byline lines."""
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    # drop title + "by O. Henry"
    body = [l for l in lines if l not in ("The Gift of the Magi", "by O. Henry")]
    return "\n".join(body)


def split_sentences(text: str) -> list[str]:
    """Simple rule-based sentence splitter that keeps closing quotes attached."""
    text = re.sub(r"\s+", " ", text)
    # split after . ! ? (optionally followed by a closing quote) when followed by space + capital/quote
    parts = re.split(r"(?:(?<=[.!?])|(?<=[.!?][”’\"]))\s+(?=[“\"A-Z0-9$])", text)
    # protect common abbreviations that the regex wrongly splits on
    merged = []
    for p in parts:
        if merged and re.search(r"\b(Mr|Mrs|Mme|Dr|St)\.$", merged[-1]):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return [s.strip() for s in merged if s.strip()]


def equal_parts(items: list, n: int) -> list[list]:
    size, rem = divmod(len(items), n)
    out, start = [], 0
    for i in range(n):
        end = start + size + (1 if i < rem else 0)
        out.append(items[start:end])
        start = end
    return out


def select(part: list, strategy: str, rng: random.Random) -> list[int]:
    k = max(1, round(len(part) * FRACTION))
    idx = list(range(len(part)))
    if strategy == "first":
        return idx[:k]
    if strategy == "last":
        return idx[-k:]
    if strategy == "middle":
        start = (len(part) - k) // 2
        return idx[start:start + k]
    if strategy == "random":
        return sorted(rng.sample(idx, k))
    raise ValueError(f"Unknown strategy: {strategy}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", type=int, default=3)
    ap.add_argument("--strategies", nargs="+", default=["first", "random", "last"])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if len(args.strategies) != args.parts:
        raise SystemExit("Give exactly one strategy per part.")

    rng = random.Random(args.seed)
    sentences = split_sentences(load_story_body(CORPUS))
    parts = equal_parts(sentences, args.parts)

    labels = {0: "Beginning", args.parts - 1: "End"}
    out = [
        "PARTIAL READING",
        "",
        "Text: “The Gift of the Magi” by O. Henry (1905), Project Gutenberg eBook #7256",
        f"Unit of reading: sentence (“line”). Total sentences: {len(sentences)}",
        f"Division: {args.parts} equal parts; 20% of the sentences read from each part",
        f"Selection strategy per part: {', '.join(args.strategies)} (random seed = {args.seed})",
        f"Sentences read: {sum(max(1, round(len(p) * FRACTION)) for p in parts)} of {len(sentences)}",
        "",
        "Researcher's note: mark (bold / highlight) the phrases in these lines that",
        "produced your initial impression before moving to Step 2.",
        "",
    ]

    global_no = 0
    for i, part in enumerate(parts):
        chosen = select(part, args.strategies[i], rng)
        name = labels.get(i, f"Middle {i}" if args.parts > 3 else "Middle")
        first_no, last_no = global_no + 1, global_no + len(part)
        out.append(f"{chr(65 + i)}. Part {i + 1} — {name} "
                   f"(sentences {first_no}–{last_no}; {len(chosen)} {args.strategies[i]} sentences read)")
        out.append("")
        for j in chosen:
            out.append(f"[{global_no + j + 1}] {part[j]}")
        out.append("")
        global_no += len(part)

    out.append("(O. Henry, “The Gift of the Magi”)")
    OUTPUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUTPUT.name}: {len(sentences)} sentences, {args.parts} parts")


if __name__ == "__main__":
    main()
