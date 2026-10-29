"""
STEP 6 — COMPUTATION AND VISUALISATION

Counts every item in Theme_JSON.py across N equal narrative segments of the
corpus and draws the figures used for interpretation (Step 7).

Counting rules (state these in your report):
  * case-insensitive, curly quotes normalised, whole-word matches only;
  * longest phrase wins: if "twenty dollars a week" matches, the shorter
    "twenty dollars" inside it is NOT counted again (no double counting);
  * an item listed under two themes is credited to both.

Run (locally or in Google Colab):
    pip install plotly pandas kaleido
    python visualise.py                 # 20 segments, like the original study
    python visualise.py --segments 10    # -> outputs_10_segments/

Outputs go to ./outputs/  (interactive .html for every figure, .png when kaleido works)
"""

import argparse
import importlib.util
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

HERE = Path(__file__).parent
CORPUS = HERE / "corpus_gift_of_the_magi.txt"
OUT = HERE / "outputs"

def load_themes(path: Path = HERE / "Theme_JSON.py") -> dict:
    """Load `themes` fresh from Theme_JSON.py (so edits are picked up without restarting)."""
    spec = importlib.util.spec_from_file_location("Theme_JSON", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.themes


themes = load_themes() if (HERE / "Theme_JSON.py").exists() else {}

# ---- edit these labels to match YOUR stages and dimensions -----------------
STAGE_NAMES = {"I": "Scarcity / Counting", "II": "Commodification / Sale", "III": "Revaluation / Gift"}
DIMENSION_NAMES = {"Money": "MONEY", "Commodity": "COMMODITY", "Treasure": "TREASURE", "Gift": "GIFT"}
# ---------------------------------------------------------------------------

# Validated categorical slots 1-3 (safe for colour-blind readers when used together)
STAGE_COLOURS = {"I": "#2a78d6", "II": "#eb6834", "III": "#1baf7a"}
INK, INK_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
HEAT_SCALE = [[0.0, "#f4f3f0"], [0.001, "#cde2fb"], [0.25, "#86b6ef"],
              [0.5, "#3987e5"], [0.75, "#1c5cab"], [1.0, "#0d366b"]]


# ---------- text handling ----------------------------------------------------
def normalise(s: str) -> str:
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s)


def story_sentences(path: Path) -> list[str]:
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    body = " ".join(l for l in lines if l not in ("The Gift of the Magi", "by O. Henry"))
    parts = re.split(r"(?:(?<=[.!?])|(?<=[.!?][”’\"]))\s+(?=[“\"A-Z0-9$])", body)
    merged = []
    for p in parts:
        if merged and re.search(r"\b(Mr|Mrs|Mme|Dr|St)\.$", merged[-1]):
            merged[-1] += " " + p
        else:
            merged.append(p)
    return merged


def segment(sentences: list[str], n: int) -> list[str]:
    size, rem = divmod(len(sentences), n)
    segs, start = [], 0
    for i in range(n):
        end = start + size + (1 if i < rem else 0)
        segs.append(" ".join(sentences[start:end]))
        start = end
    return segs


def theme_label(key: str) -> tuple[str, str, str]:
    """'Stage_II_Money' -> ('II', 'Money', 'MONEY: Commodification / Sale (II)')"""
    _, stage, dim = key.split("_", 2)
    return stage, dim, f"{DIMENSION_NAMES.get(dim, dim.upper())}: {STAGE_NAMES.get(stage, stage)} ({stage})"


def count_matrix(segments: list[str]) -> tuple[pd.DataFrame, dict]:
    item_to_themes: dict[str, list[str]] = {}
    for key, items in themes.items():
        for it in items:
            item_to_themes.setdefault(normalise(it).strip(), []).append(key)

    # one regex, longest alternatives first -> non-overlapping, longest-match counting
    alts = sorted(item_to_themes, key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(" + "|".join(re.escape(a) for a in alts) + r")(?!\w)")

    counts = pd.DataFrame(0, index=list(themes), columns=range(1, len(segments) + 1))
    hits = {a: 0 for a in alts}
    for s_no, seg in enumerate(segments, start=1):
        for m in pattern.finditer(normalise(seg)):
            hits[m.group(1)] += 1
            for key in item_to_themes[m.group(1)]:
                counts.loc[key, s_no] += 1
    return counts, hits


# ---------- figures ----------------------------------------------------------
def base_layout(fig, title, x_title, y_title, height):
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16, color=INK)),
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=12, color=INK_2),
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE, height=height, width=1100,
        margin=dict(l=20, r=20, t=70, b=60),
        hoverlabel=dict(bgcolor="white", font=dict(color=INK)),
    )
    fig.update_xaxes(title=x_title, gridcolor=GRID, linecolor="#c3c2b7", tickfont=dict(color=MUTED), dtick=1)
    fig.update_yaxes(title=y_title, gridcolor=GRID, linecolor="#c3c2b7", tickfont=dict(color=INK_2))
    return fig


PNG_WARNED = False


def save(fig, name, out: Path = OUT):
    global PNG_WARNED
    fig.write_html(out / f"{name}.html", include_plotlyjs="cdn")
    try:
        fig.write_image(out / f"{name}.png", scale=2)
    except Exception as e:  # kaleido missing or no Chrome available
        if not PNG_WARNED:
            print(f"  (PNG export unavailable: {type(e).__name__}. HTML saved; use the camera icon on a figure for PNG.)")
            PNG_WARNED = True


def heatmap(counts, labels):
    n = counts.shape[1]
    text = counts.where(counts > 0, "").astype(str)
    fig = go.Figure(go.Heatmap(
        z=counts.values, x=list(counts.columns), y=labels, colorscale=HEAT_SCALE,
        text=text.values, texttemplate="%{text}", textfont=dict(size=11),
        xgap=2, ygap=2, colorbar=dict(title="Count", outlinewidth=0),
        hovertemplate="%{y}<br>Segment %{x}: %{z} item(s)<extra></extra>",
    ))
    base_layout(fig, f"Fig. 1 — Frequency of each theme across {n} narrative segments",
                "Narrative segment (story order)", "", 120 + 38 * len(labels))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    return fig


def bubble(counts, keys, title):
    fig = go.Figure()
    for stage in STAGE_NAMES:
        rows = [k for k in keys if theme_label(k)[0] == stage]
        if not rows:
            continue
        xs, ys, ss = [], [], []
        for k in rows:
            for seg, v in counts.loc[k].items():
                if v > 0:
                    xs.append(seg); ys.append(theme_label(k)[2]); ss.append(v)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers", name=f"Stage {stage}: {STAGE_NAMES[stage]}",
            marker=dict(size=[8 + 7 * s for s in ss], color=STAGE_COLOURS[stage], opacity=0.85,
                        line=dict(color=SURFACE, width=2)),
            customdata=ss, hovertemplate="%{y}<br>Segment %{x}: %{customdata} item(s)<extra></extra>",
        ))
    order = [theme_label(k)[2] for k in keys]
    base_layout(fig, title, "Narrative segment (story order)", "", 140 + 40 * len(keys))
    fig.update_yaxes(categoryorder="array", categoryarray=order[::-1])
    fig.update_xaxes(range=[0.3, counts.shape[1] + 0.7])
    fig.update_layout(legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0))
    return fig


def stage_share(counts):
    by_stage = counts.groupby(lambda k: theme_label(k)[0]).sum()
    share = (by_stage / by_stage.sum().replace(0, 1) * 100).round(1)
    fig = go.Figure()
    for stage in STAGE_NAMES:
        if stage in share.index:
            fig.add_trace(go.Bar(
                x=list(share.columns), y=share.loc[stage], name=f"Stage {stage}: {STAGE_NAMES[stage]}",
                marker=dict(color=STAGE_COLOURS[stage], line=dict(color=SURFACE, width=2)),
                customdata=by_stage.loc[stage],
                hovertemplate=f"Stage {stage}<br>Segment %{{x}}: %{{y}}% (%{{customdata}} items)<extra></extra>",
            ))
    base_layout(fig, "Fig. 4 — Which stage's vocabulary dominates each segment? (share of matched items)",
                "Narrative segment (story order)", "Share of matched items (%)", 460)
    fig.update_layout(barmode="stack", bargap=0.15, legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0))
    fig.update_yaxes(range=[0, 100])
    return fig, by_stage


def dominant_timeline(by_stage):
    fig = go.Figure()
    totals = by_stage.sum()
    dom = by_stage.idxmax().where(totals > 0)
    for stage in STAGE_NAMES:
        segs = [s for s in by_stage.columns if dom[s] == stage]
        fig.add_trace(go.Scatter(
            x=segs, y=[f"Stage {stage}: {STAGE_NAMES[stage]}"] * len(segs), mode="markers",
            name=f"Stage {stage}", marker=dict(size=[10 + 3 * by_stage.loc[stage, s] for s in segs],
                                               color=STAGE_COLOURS[stage], line=dict(color=SURFACE, width=2)),
            customdata=[by_stage.loc[stage, s] for s in segs],
            hovertemplate="Segment %{x}: dominant = %{y} (%{customdata} items)<extra></extra>",
        ))
    base_layout(fig, "Fig. 5 — Dominant stage per segment (timeline)", "Narrative segment (story order)", "", 320)
    fig.update_yaxes(categoryorder="array",
                     categoryarray=[f"Stage {s}: {n}" for s, n in reversed(STAGE_NAMES.items())])
    fig.update_xaxes(range=[0.3, by_stage.shape[1] + 0.7])
    fig.update_layout(showlegend=False)
    return fig


def run(n_segments: int = 20, stage_names: dict | None = None, dimension_names: dict | None = None,
        out_dir: Path | None = None) -> dict:
    """Count, save CSVs and figures, and return the figures (for fig.show() in a notebook)."""
    global themes
    themes = load_themes()
    if stage_names:
        STAGE_NAMES.clear(); STAGE_NAMES.update(stage_names)
    if dimension_names:
        DIMENSION_NAMES.clear(); DIMENSION_NAMES.update(dimension_names)
    out = Path(out_dir) if out_dir else (OUT if n_segments == 20 else HERE / f"outputs_{n_segments}_segments")
    out.mkdir(exist_ok=True)

    sentences = story_sentences(CORPUS)
    segs = segment(sentences, n_segments)
    counts, hits = count_matrix(segs)
    keys = list(themes)
    labels = [theme_label(k)[2] for k in keys]

    # data files
    table = counts.copy(); table.index = labels
    table.to_csv(out / "theme_counts_by_segment.csv", index_label="theme")
    pd.DataFrame({"segment": range(1, len(segs) + 1),
                  "first_sentence": [s[:90] for s in segs]}).to_csv(out / "segments.csv", index=False)
    missing = [i for i, h in hits.items() if h == 0]
    (out / "items_not_found.txt").write_text(
        "Items in Theme_JSON.py that never occur verbatim in the corpus:\n"
        + ("\n".join(f"  - {m}" for m in missing) if missing else "  (none)"), encoding="utf-8")

    # figures
    figs = {"fig1_heatmap": heatmap(counts, labels),
            "fig2_bubble_all_themes": bubble(
                counts, keys, "Fig. 2 — Thematic distribution across the narrative (bubble size = frequency)")}
    for n, stage in enumerate(STAGE_NAMES):
        rows = [k for k in keys if theme_label(k)[0] == stage]
        if rows:
            figs[f"fig3{'abc'[n]}_bubble_stage_{stage}"] = bubble(
                counts, rows, f"Fig. 3{'abc'[n]} — Stage {stage}: {STAGE_NAMES[stage]}")
    share_fig, by_stage = stage_share(counts)
    figs["fig4_stage_share"] = share_fig
    figs["fig5_dominant_stage_timeline"] = dominant_timeline(by_stage)
    for name, fig in figs.items():
        save(fig, name, out)

    print(f"{len(sentences)} sentences -> {n_segments} segments; "
          f"{int(counts.values.sum())} theme hits; {len(missing)} item(s) not found")
    if missing:
        print("Not found in the text:", ", ".join(missing))
    print(f"Outputs written to {out}/")
    return {"figures": figs, "counts": table, "missing": missing}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--segments", type=int, default=20)
    args = ap.parse_args()
    run(args.segments)


if __name__ == "__main__":
    main()
