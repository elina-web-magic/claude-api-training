# Balances Verification — Prompt Engineering Techniques

This folder is a copy of `3_prompt_engineering-techniques/`, adapted to test the **Balances Verification Prompt** from `docs/BALANCES_VERIFICATION_PROMPT.md` using all four prompt engineering approaches.

## What is being tested

The `BALANCES_VERIFICATION_PROMPT` asks Claude to verify claims from `balances.md` — a BA-facing business scope document for a Gambling platform's wallet and balance system. Claims are classified as:

- `ACCURATE` — confirmed by the source
- `HALLUCINATED` — invented with no source basis
- `INACCURATE` — contradicts the source
- `AMBIGUOUS` — cannot be confirmed without more data

---

## Technique Comparison

| Script | Technique | Output Files |
|:---|:---|:---|
| `run_001_basic.py` | Basic Prompting (naive baseline) | `output_balances_001_basic.*` |
| `run_002_clear_direct.py` | Clear & Direct (action verbs + numbered rules) | `output_balances_002_clear_direct.*` |
| `run_003_specific.py` | Specific + Chain of Thought + One-Shot Example | `output_balances_003_specific.*` |
| `run_004_xml.py` | XML Tag Structure | `output_balances_004_xml.*` |

---

## Output Files (per technique)

Each script produces **3 uniquely named output files**:

```text
dataset_balances_<technique>.json   — generated test cases
output_balances_<technique>.json    — evaluation results (scores, reasoning)
output_balances_<technique>.html    — visual HTML report
```

---

## How to Run

### Run a single technique:

```bash
cd ai-integration/4_balances_verification_techniques
python run_001_basic.py
```

### Run all techniques at once:

```bash
cd ai-integration/4_balances_verification_techniques
python run_all_techniques.py
```

---

## Folder Structure

```text
4_balances_verification_techniques/
├── README.md                         ← this file
├── run_001_basic.py                  ← Technique 001: Basic Prompting
├── run_002_clear_direct.py           ← Technique 002: Clear & Direct
├── run_003_specific.py               ← Technique 003: Specific + CoT + Example
├── run_004_xml.py                    ← Technique 004: XML Tags
├── run_all_techniques.py             ← Master runner (all 4 scripts)
│
├── 001_prompting.ipynb               ← Original notebook (reference)
├── 002_prompt_clear_direct.ipynb     ← Original notebook (reference)
├── 003_prompt_specific.ipynb         ← Original notebook (reference)
├── 004_prompt_xml.ipynb              ← Original notebook (reference)
│
├── PROMPT_ENGINEERING_EXAMPLES_GUIDE.md
├── PROMPT_ENGINEERING_FLOW.md
│
└── [output files generated on run]
    ├── dataset_balances_001_basic.json
    ├── output_balances_001_basic.json
    ├── output_balances_001_basic.html
    ├── dataset_balances_002_clear_direct.json
    ├── output_balances_002_clear_direct.json
    ├── output_balances_002_clear_direct.html
    ├── dataset_balances_003_specific.json
    ├── output_balances_003_specific.json
    ├── output_balances_003_specific.html
    ├── dataset_balances_004_xml.json
    ├── output_balances_004_xml.json
    └── output_balances_004_xml.html
```

---

## Key Design Decisions

- **Unique output names** — Every script writes files prefixed with `output_balances_<technique>` so running all four scripts never overwrites each other's results.
- **Same task, different techniques** — All four scripts test the same balances verification task using different prompt structures, making it easy to compare technique effectiveness.
- **Coloured HTML reports** — Each HTML report uses a distinct colour theme (grey, blue, purple, orange) to visually distinguish the technique.
- **dotenv root lookup** — Scripts use `Path(__file__).parent.parent.parent / ".env"` to find the root `.env` file (which contains `ANTHROPIC_API_KEY`).
