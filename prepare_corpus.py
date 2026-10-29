"""
STEP 3 — PRE-PROCESSING (removing noise)

Downloads "The Gift of the Magi" from Project Gutenberg (or uses a local copy)
and writes the cleaned corpus:
  * keeps only the text between the *** START *** and *** END *** markers
    (drops the Gutenberg header, release metadata and the licence);
  * keeps the title, byline, every word, original punctuation, curly quotes, dashes;
  * joins each paragraph onto one line;
  * does NOT lower-case, remove stop words or stem (the LLM needs the text as written).

Usage:
    python prepare_corpus.py                      # download from Gutenberg
    python prepare_corpus.py --raw pg7256.txt     # use a file you downloaded yourself
"""

import argparse
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
URL = "https://www.gutenberg.org/cache/epub/7256/pg7256.txt"
RAW = HERE / "source_gutenberg_pg7256.txt"
CORPUS = HERE / "corpus_gift_of_the_magi.txt"


def clean(raw: str) -> str:
    raw = raw.replace("\r\n", "\n").lstrip("﻿")
    start = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw)
    end = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", raw)
    if not (start and end):
        raise ValueError("Gutenberg START/END markers not found — is this the right file?")
    body = raw[start.end():end.start()].strip()
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body)]
    paragraphs = [p for p in paragraphs if p]
    # title + byline on their own lines, blank line after byline, then one paragraph per line
    title, byline, rest = paragraphs[0], paragraphs[1], paragraphs[2:]
    return f"{title}\n\n{byline}\n\n\n" + "\n\n".join(rest) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, help="local Gutenberg .txt (skip the download)")
    args = ap.parse_args()

    if args.raw:
        raw = args.raw.read_text(encoding="utf-8-sig")
    else:
        with urllib.request.urlopen(URL, timeout=60) as r:
            raw = r.read().decode("utf-8-sig")
    RAW.write_text(raw, encoding="utf-8")

    corpus = clean(raw)
    CORPUS.write_text(corpus, encoding="utf-8")
    words = len(re.findall(r"\b[\w’'-]+\b", corpus))
    paras = len([l for l in corpus.splitlines() if l.strip()]) - 2
    print(f"Raw file: {len(raw.splitlines())} lines -> corpus: {paras} paragraphs, ~{words} words")
    print(f"Saved {RAW.name} (untouched source) and {CORPUS.name} (cleaned)")


if __name__ == "__main__":
    main()
