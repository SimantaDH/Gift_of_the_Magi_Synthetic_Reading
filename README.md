# Synthetic Reading of O. Henry's "The Gift of the Magi"

A hermeneutic-computational reading of O. Henry's short story "The Gift of the Magi" (1905), following the **synthetic reading** method of Ghosh, Shanmugapriya T and Mandal (2026). In this method interpretation comes *before* computation: a partial reading produces an initial impression, the impression is turned into a prompt, an LLM extracts textual features, and the researcher computes, visualises and interprets them through literary and cultural theory.

**Researcher:** [Your name], [Programme, Department, Institute]
**Supervisor:** [Name]
**Date:** [Month Year]

## Research problem

> [One or two sentences. Example: *Does the story's vocabulary move from a market economy of counting and selling to a gift economy of sacrifice, and does the final "gift" depend on the very commodification it claims to transcend?*]

**Statement to test:** [Example: *Money and commodity vocabulary dominates the opening and middle segments; gift vocabulary dominates the close; the turn to the gift happens only after both treasures have been sold.*]

**Framework:** [Example: Mauss's theory of the gift; Derrida, *Given Time*; Kopytoff's "cultural biography of things"; Marx on the commodity form; Sara Ahmed's "affective economies".]

## Repository contents

| File | Step | What it is |
|---|---|---|
| `Synthetic_Reading_Gift_of_the_Magi.ipynb` | all | Google Colab notebook that runs every step |
| `source_gutenberg_pg7256.txt` | 3 | The untouched Project Gutenberg download |
| `prepare_corpus.py` | 3 | Removes the noise (Gutenberg header, footer, licence) and writes the corpus |
| `corpus_gift_of_the_magi.txt` | 3 | Full story, pre-processed (paragraphs joined onto single lines) |
| `partial_reading.py` | 1 | Divides the story into equal parts and selects 20% of the sentences from each |
| `partial_reading.txt` | 1 | The lines actually read before forming the initial impression |
| `initial_impression.md` | 2 | Initial impression, positionality / reflexivity statement, research problem, framework |
| `prompt.txt` | 4 | The exact prompt given to the LLM |
| `extract_with_local_llm.py` | 3–5 | Sends corpus + prompt to a local LLM (Ollama) and verifies the output against the text |
| `llm_raw_output.json` | 5 | The LLM's untouched JSON answer |
| `llm_verification.txt` | 5 | Which extracted items occur verbatim in the text |
| `item_positions.csv` | 5 | Where each verified item occurs across the 20 segments |
| `Theme_JSON.py` | 5 | Researcher-annotated themes: LLM items assigned to stages and dimensions |
| `visualise.py` | 6 | Counts every theme across narrative segments and draws the figures |
| `outputs/` | 6 | Figures (`.html`, `.png`), `theme_counts_by_segment.csv`, `segments.csv`, `items_not_found.txt` |
| `interpretation.md` | 7 | Interpretation of the figures through literary and cultural theory |

## Method in brief

1. **Partial reading.** The story was split into 153 sentences and divided into 3 equal parts. From the beginning part the first 20% was read, from the middle part a random 20% (seed 42), and from the end part the last 20%. That makes 30 of 153 sentences in total (`partial_reading.txt`).
2. **Initial impression.** This step records the researcher's impression, positionality and reflexivity (`initial_impression.md`).
3. **Text upload.** The full pre-processed corpus was given to the LLM.
4. **Query generation.** The prompt operationalises the impression into four dimensions (`prompt.txt`).
5. **Targeted extraction.** The LLM returned items in JSON. Each item was checked against the text, and the researcher then assigned it to a stage (`Theme_JSON.py`).
6. **Computation and visualisation.** Theme frequencies were counted across 20 equal segments (`visualise.py`).
7. **Interpretation.** The figures are read against the framework (`interpretation.md`).

### LLM run details

| Setting | Value |
|---|---|
| Model | [e.g. qwen2.5:7b via Ollama, on a Google Colab T4 GPU] |
| Temperature / seed | [0.0 / 42] |
| Date of run | [date] |
| Prompt | `prompt.txt` (SHA-256 recorded in `llm_run_log.json`) |

### Counting rules (`visualise.py`)

- Matching is case-insensitive, curly quotes are normalised, and only whole words are matched.
- The longest phrase wins. When "twenty dollars a week" matches, the "twenty dollars" inside it is not counted a second time.
- An item listed under two themes is credited to both.
- Segments are equal-sized blocks of sentences in story order.

## Reproduce

**Google Colab:** open `Synthetic_Reading_Gift_of_the_Magi.ipynb` in Colab, set **Runtime → Change runtime type → T4 GPU**, and run the cells from top to bottom.

**Locally:**

```bash
pip install -r requirements.txt
python prepare_corpus.py           # Step 3 pre-processing
python partial_reading.py          # Step 1
python extract_with_local_llm.py   # Steps 3–5 (needs Ollama running locally)
python visualise.py                # Step 6 -> outputs/
```

## Sources

- O. Henry, "The Gift of the Magi" (1905). Project Gutenberg eBook #7256, https://www.gutenberg.org/ebooks/7256. The text is in the public domain in the USA.
- S. Ghosh, Shanmugapriya T and S. Mandal, "Synthetic reading: Towards a hermeneutic-computational method for literary interpretation through Tagore's 'A Wife's Letter'", *International Journal of Humanities and Arts Computing* 20.2 (2026): 216–237. DOI: 10.3366/ijhac.2026.0378.
- Reference repository: https://github.com/SouravGhosh-digital-humanities/Wifes_Letter_JSON_themes
