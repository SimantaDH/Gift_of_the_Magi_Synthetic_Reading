"""
STEP 3–5 — TEXT UPLOAD, QUERY, TARGETED EXTRACTION (local LLM via Ollama)

Sends the full corpus + your prompt to a LOCAL model running in Ollama and saves
the model's raw JSON answer. It then checks every extracted item against the
corpus, so hallucinated (non-verbatim) items are flagged before you use them.

Setup (once, on your own computer — Google Colab users: the notebook does this):
    1. Install Ollama: https://ollama.com/download
    2. Pull a model, e.g.:   ollama pull qwen2.5:7b      (or llama3.1:8b)
    3. Keep Ollama running (it serves http://localhost:11434)

Run:
    python extract_with_local_llm.py --model qwen2.5:7b
    python extract_with_local_llm.py --model qwen2.5:7b --chunks 3   # small models: more exhaustive

Outputs:
    llm_raw_output.json        the model's JSON answer, untouched (merged if --chunks > 1)
    llm_run_log.json           model, settings, date, prompt hash (for your README)
    llm_verification.txt       which items were / were not found verbatim in the text

Not using a local model? Paste prompt.txt + the corpus into any LLM, save its JSON
answer as llm_raw_output.json, then run:
    python extract_with_local_llm.py --verify-only
"""

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CORPUS = HERE / "corpus_gift_of_the_magi.txt"
PROMPT = HERE / "prompt.txt"
RAW_OUT = HERE / "llm_raw_output.json"
LOG_OUT = HERE / "llm_run_log.json"
VERIFY_OUT = HERE / "llm_verification.txt"
OLLAMA = "http://localhost:11434"


def normalise(s: str) -> str:
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def prompt_body(text: str) -> str:
    """Strip the heading lines and the [WORKED EXAMPLE ...] note from prompt.txt."""
    text = re.sub(r"\[WORKED EXAMPLE.*?\]\s*", "", text, flags=re.S)
    keep = [l for l in text.splitlines() if l.strip() != "PROMPT" and not l.startswith("B. Prompt")]
    return "\n".join(keep).strip()


def item_text(entry) -> str:
    if isinstance(entry, dict):
        return str(entry.get("item") or entry.get("text") or entry.get("phrase") or "")
    return str(entry)


def split_corpus(corpus: str, n: int) -> list[str]:
    paras = [p for p in corpus.split("\n\n") if p.strip()]
    size = -(-len(paras) // n)
    return ["\n\n".join(paras[i:i + size]) for i in range(0, len(paras), size)]


def call_ollama(model: str, prompt: str, text: str, temperature: float, ctx: int, num_predict: int) -> str:
    payload = {
        "model": model,
        "prompt": f"{prompt}\n\n=== TEXT START ===\n{text}\n=== TEXT END ===",
        "format": "json",
        "stream": False,
        "options": {"temperature": temperature, "num_ctx": ctx, "num_predict": num_predict, "seed": 42},
    }
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3600) as r:
        return json.loads(r.read().decode("utf-8"))["response"]


def merge(parts: list[dict]) -> dict:
    """Merge chunk answers: same keys, items de-duplicated by normalised text, order kept."""
    merged, seen = {}, {}
    for part in parts:
        for key, entries in part.items():
            if not isinstance(entries, list):
                continue
            merged.setdefault(key, []); seen.setdefault(key, set())
            for e in entries:
                k = normalise(item_text(e))
                if k and k not in seen[key]:
                    seen[key].add(k); merged[key].append(e)
    return merged


def verify(raw: dict, corpus: str) -> str:
    text = normalise(corpus)
    report, total, missing = [], 0, 0
    for category, entries in raw.items():
        if not isinstance(entries, list):
            continue
        found, not_found = [], []
        for e in entries:
            item = item_text(e)
            total += 1
            (found if item and normalise(item) in text else not_found).append(item)
        missing += len(not_found)
        report.append(f"## {category}: {len(found)} verbatim, {len(not_found)} NOT FOUND")
        report += [f"   x {i}" for i in not_found]
    pct = f" ({(total - missing) / total:.0%})" if total else ""
    head = [
        "LLM EXTRACTION — VERIFICATION AGAINST THE CORPUS",
        f"Items extracted: {total}   Found verbatim: {total - missing}{pct}   Not found: {missing}",
        "Items marked x are not in the text as written. Correct or remove them",
        "(or keep them deliberately as interpretive labels and say so in the README).",
        "",
    ]
    return "\n".join(head + report)


def run_extraction(model: str = "qwen2.5:7b", chunks: int = 1, temperature: float = 0.0,
                   ctx: int = 16384, num_predict: int = 8192) -> dict:
    corpus = CORPUS.read_text(encoding="utf-8")
    prompt = prompt_body(PROMPT.read_text(encoding="utf-8"))
    pieces = [corpus] if chunks <= 1 else split_corpus(corpus, chunks)
    answers = []
    for i, piece in enumerate(pieces, start=1):
        print(f"Asking {model} (part {i}/{len(pieces)}) ...", flush=True)
        answers.append(json.loads(call_ollama(model, prompt, piece, temperature, ctx, num_predict)))
    raw = answers[0] if len(answers) == 1 else merge(answers)
    RAW_OUT.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    LOG_OUT.write_text(json.dumps({
        "model": model, "chunks": len(pieces), "temperature": temperature, "num_ctx": ctx,
        "num_predict": num_predict, "seed": 42,
        "run_at": dt.datetime.now().isoformat(timespec="seconds"),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    }, indent=2), encoding="utf-8")
    print(f"Saved {RAW_OUT.name} and {LOG_OUT.name}")
    return raw


def run_verification() -> str:
    raw = json.loads(RAW_OUT.read_text(encoding="utf-8"))
    report = verify(raw, CORPUS.read_text(encoding="utf-8"))
    VERIFY_OUT.write_text(report, encoding="utf-8")
    print(f"Saved {VERIFY_OUT.name}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--chunks", type=int, default=1)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--ctx", type=int, default=16384)
    ap.add_argument("--num-predict", type=int, default=8192)
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()
    if not args.verify_only:
        run_extraction(args.model, args.chunks, args.temperature, args.ctx, args.num_predict)
    print(run_verification().splitlines()[1])


if __name__ == "__main__":
    main()
