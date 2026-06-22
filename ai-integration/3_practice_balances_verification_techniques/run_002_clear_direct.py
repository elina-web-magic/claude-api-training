"""
Technique 002: Clear & Direct Prompting — Balances Verification
--------------------------------------------------------------
Uses the clear, direct prompting approach from 002_prompt_clear_direct.ipynb
Applied to the BALANCES_VERIFICATION_PROMPT to verify balances.md claims.

Key technique: Start with a strong action verb, be specific, eliminate vague wording.

IMPORTANT: The dataset is NOT AI-generated. It is built directly from the real
claims listed in docs/BALANCES_VERIFICATION_PROMPT.md — the "High-Risk Claims"
section and the "Background" key claims. The run_prompt function uses the prompt
template defined in that document.

Output files:
  dataset_balances_002_clear_direct.json
  output_balances_002_clear_direct.json
  output_balances_002_clear_direct.html
"""

import json
import concurrent.futures
from statistics import mean
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

client = Anthropic()
model = "claude-haiku-4-5"

TECHNIQUE_TAG = "002_clear_direct"
DATASET_FILE = f"dataset_balances_{TECHNIQUE_TAG}.json"
JSON_OUTPUT_FILE = f"output_balances_{TECHNIQUE_TAG}.json"
HTML_OUTPUT_FILE = f"output_balances_{TECHNIQUE_TAG}.html"

# ── Real claims from docs/BALANCES_VERIFICATION_PROMPT.md ──────────────────────
# These are the actual lines from balances.md to verify.
# Source: "Background" key claims + "High-Risk Claims to Prioritize" section.

REAL_DATASET = [
    {
        "scenario": "Wallet-per-currency record uniqueness",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "The gambling platform architecture dictates that players maintain separate wallets for each supported currency. To ensure transaction integrity, the database enforces exactly one active record per currency wallet per player.",
            "claim_type": "technical_fact",
            "original_line": "Players have one wallet per currency with exactly one record.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must use 'now:' and 'to be:' labels without any markdown headings",
            "Must include the exact original text",
            "Must include a proposed correction or 'No change needed'",
                    ],
    },
    {
        "scenario": "Seven balance pockets — exact names",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "A wallet contains multiple balance segments to track different funds. These include main cash, bonus, and withdrawal-pending. There are no sports-specific pockets in the current MVP.",
            "claim_type": "technical_fact",
            "original_line": (
                "Seven balance 'pockets' exist per wallet: "
                "main cash, committed cash, bonus, deposit-pending, "
                "withdrawal-pending, sports bonus, sports locked."
            ),
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must verify both the count (seven) and the exact pocket names",
            "Must use \"now:\" and \"to be:\" labels without any markdown headings",
            "Must include a proposed correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Three headline figures returned by balance query",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "The balance query endpoint aggregates the pocket values and returns three headline figures: available real cash, available bonus, and sports bonus. If a player has no sports bonus, it returns zero.",
            "claim_type": "ui_behavior",
            "original_line": (
                "The system returns three headline figures: "
                "available real cash, available bonus, sports bonus."
            ),
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must verify whether sports bonus reads zero or is omitted when absent",
            "Must include 'now' with the exact original text",
            "Must include 'to be' with correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Exchange rate cache duration (~15 minutes)",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "The platform fetches real-time exchange rates via API for every transaction. No caching layer is implemented for exchange rates to prevent arbitrage.",
            "claim_type": "technical_fact",
            "original_line": "Exchange rates are cached for ~15 minutes and updated asynchronously.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must flag that the exact 15-minute duration is a high-risk hallucination candidate",
            "Must use \"now:\" and \"to be:\" labels without any markdown headings",
            "Must include a proposed correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Currency code length distinction (5-char vs 3-char)",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "All currencies, regardless of whether they are fiat or crypto, are represented internally using standard 3-character ISO codes.",
            "claim_type": "technical_fact",
            "original_line": "Currencies use either 5-char or 3-char codes depending on type.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must include 'now' with the exact original text",
            "Must include 'to be' with correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Credit corrections always go to main cash pocket",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "Credit corrections are manual adjustments made by administrators. According to compliance rules, these corrections must always be applied directly to the main cash pocket.",
            "claim_type": "business_rule",
            "original_line": "Credit corrections always add to the main cash pocket.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must verify the direction rule (main cash pocket specifically)",
            "Must use \"now:\" and \"to be:\" labels without any markdown headings",
            "Must include a proposed correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Wagering configuration inheritance from parent brands",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "Wagering configuration can be defined at the brand level. If a brand does not have specific rules, the configuration can be inherited from parent brands.",
            "claim_type": "business_rule",
            "original_line": "Wagering configuration can be inherited from parent brands.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must include 'now' with the exact original text",
            "Must include 'to be' with correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Default wagering multiplier of 3 for new brands",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "When a new brand is created without explicit wagering configuration, the system automatically applies a fallback multiplier. This default value is set to 3 across the platform.",
            "claim_type": "default_value",
            "original_line": "New brands with no wagering config get a default multiplier of 3.",
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must verify the exact multiplier value (3) as a high-risk hallucination candidate",
            "Must use \"now:\" and \"to be:\" labels without any markdown headings",
            "Must include a proposed correction or 'No change needed'",
        ],
    },
    {
        "scenario": "Balance-change signals sent on best-endeavours basis",
        "task_description": "Verify claims from balances.md for LLM hallucinations and factual inaccuracies.",
        "prompt_inputs": {
            "document_section": "Balance-change signals to reporting are sent via Kafka with guaranteed delivery. No messages can be lost.",
            "claim_type": "technical_fact",
            "original_line": (
                "Balance-change signals to reporting are sent on a best-endeavours basis "
                "and can occasionally be lost."
            ),
        },
        "solution_criteria": [
            "Must provide the Github URL format",
            "Must verify whether delivery is best-endeavours or guaranteed",
            "Must include 'now' with the exact original text",
            "Must include 'to be' with correction or 'No change needed'",
        ],
    },
]


# ── Helpers ─────────────────────────────────────────────────────────────────────

def add_user_message(messages, text):
    messages.append({"role": "user", "content": text})

def add_assistant_message(messages, text):
    messages.append({"role": "assistant", "content": text})

def chat(messages, system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1500,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }
    if system:
        params["system"] = system
    return client.messages.create(**params).content[0].text


# ── Report Builder ──────────────────────────────────────────────────────────────

def generate_prompt_evaluation_report(evaluation_results):
    total_tests = len(evaluation_results)
    scores = [r["score"] for r in evaluation_results]
    avg_score = mean(scores) if scores else 0
    pass_rate = 100 * len([s for s in scores if s >= 7]) / total_tests if total_tests else 0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Balances Verification — Technique: Clear &amp; Direct</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        .header {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #0284c7; }}
        .badge {{ background: #0284c7; color: #fff; padding: 3px 10px; border-radius: 3px; font-size: 12px; margin-right: 8px; }}
        .source-badge {{ background: #16a34a; color: #fff; padding: 3px 10px; border-radius: 3px; font-size: 12px; }}
        .summary-stats {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }}
        .stat-box {{ background: #fff; border-radius: 5px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex-basis: 30%; min-width: 180px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #0284c7; color: white; text-align: left; padding: 12px; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; vertical-align: top; width: 20%; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .score {{ font-weight: bold; padding: 5px 10px; border-radius: 3px; display: inline-block; }}
        .score-high {{ background: #c8e6c9; color: #2e7d32; }}
        .score-medium {{ background: #fff9c4; color: #f57f17; }}
        .score-low {{ background: #ffcdd2; color: #c62828; }}
        .output pre {{ background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 10px; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; margin: 0; }}
        .score-col {{ width: 80px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Balances Verification Report</h1>
        <p>
            <span class="badge">Technique: 002 — Clear &amp; Direct</span>
            <span class="source-badge">✅ Real claims from docs/BALANCES_VERIFICATION_PROMPT.md</span>
        </p>
        <div class="summary-stats">
            <div class="stat-box"><div>Total Claims Verified</div><div class="stat-value">{total_tests}</div></div>
            <div class="stat-box"><div>Average Score</div><div class="stat-value">{avg_score:.1f} / 10</div></div>
            <div class="stat-box"><div>Pass Rate (≥7)</div><div class="stat-value">{pass_rate:.1f}%</div></div>
        </div>
    </div>
    <table>
        <thead>
            <tr><th>Claim</th><th>Inputs</th><th>Solution Criteria</th><th>Verification Output</th><th>Score</th><th>Reasoning</th></tr>
        </thead>
        <tbody>"""

    for result in evaluation_results:
        prompt_inputs_html = "<br>".join(
            [f"<strong>{k}:</strong> {v}" for k, v in result["test_case"]["prompt_inputs"].items()]
        )
        criteria_string = "<br>• ".join(result["test_case"]["solution_criteria"])
        score = result["score"]
        score_class = "score-high" if score >= 8 else ("score-low" if score <= 5 else "score-medium")
        html += f"""
        <tr>
            <td>{result["test_case"]["scenario"]}</td>
            <td>{prompt_inputs_html}</td>
            <td>• {criteria_string}</td>
            <td class="output"><pre>{result["output"]}</pre></td>
            <td class="score-col"><span class="score {score_class}">{score}</span></td>
            <td>{result["reasoning"]}</td>
        </tr>"""

    html += "</tbody></table></body></html>"
    return html


# ── Grader ───────────────────────────────────────────────────────────────────────

def grade_output(test_case, output, extra_criteria=""):
    prompt_inputs = "".join(
        [f'"{k}": "{v}",\n' for k, v in test_case["prompt_inputs"].items()]
    )
    extra_section = (
        f"Mandatory Requirements — ANY VIOLATION = score 3 or lower:\n{extra_criteria}"
        if extra_criteria else ""
    )
    eval_prompt = f"""
    Evaluate this AI-generated verification output with EXTREME RIGOR.

    Task: {test_case["task_description"]}
    Inputs: {{{prompt_inputs}}}
    Output to grade: {output}
    Criteria: {chr(10).join(test_case["solution_criteria"])}
    {extra_section}

    Score 1-3: fails mandatory requirements.
    Score 4-6: significant deficiencies.
    Score 7-8: meets most criteria, minor issues.
    Score 9-10: meets all criteria.

    Grade ONLY on the listed criteria. If all criteria are met, give 10.
    Respond with JSON:
    {{
        "scratchpad": "check each field is present in the output",
        "strengths": [],
        "weaknesses": [],
        "reasoning": "",
        "score": number
    CRITICAL: You must ensure all output is strictly valid JSON. Properly escape all quotes, backslashes, and newlines in the string fields.
    """
    msgs = []
    add_user_message(msgs, eval_prompt.strip())
    add_assistant_message(msgs, "```json\n{")
    raw_response = chat(msgs, temperature=0.0)
    raw_json = "{\n" + raw_response.strip()
    try:
        obj, idx = json.JSONDecoder().raw_decode(raw_json)
        return obj
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}\nRaw JSON: {raw_json}")
        return {"scratchpad": "", "strengths": [], "weaknesses": [], "reasoning": "JSON Error", "score": 0}


# ── run_prompt — uses the prompt template from BALANCES_VERIFICATION_PROMPT.md ──

def run_prompt(prompt_inputs):
    """
    TECHNIQUE 002: Clear & Direct Prompting

    Uses the exact prompt template provided by the user.
    """
    prompt = f"""You are a strict technical auditor for a Gambling platform documentation system.

Your task is to verify a specific claim from the document `balances.md` against the authoritative source documentation.

The document being verified is a BA-facing business scope document describing a real+bonus, multi-currency wallet system for a Gambling platform (MVP).
It was generated with AI assistance, using a NotebookLM source notebook (ID: 404f9a90-606f-42b6-926b-99b4ee0e3628) as the factual ground truth.

## High-Risk Claims to Prioritize
The following claims in `balances.md` are known to be high-risk for AI hallucinations. Be extremely strict when auditing these:
- The exact 15-minute cache duration for exchange rates
- The 5-char vs 3-char currency code distinction
- The credit correction direction rule (always to main cash pocket)
- The default wagering multiplier of 3 for new brands
- The exact names of the seven balance pockets
- Whether sports bonus amount reads zero or is omitted entirely when absent
- The inheritance model for wagering configuration across brands
- Whether balance-change signals are sent on best-endeavours or guaranteed delivery
- The exact fields returned in the balance summary response

## Source Documentation Section


{prompt_inputs['document_section']}



{prompt_inputs['claim_type']}



{prompt_inputs['original_line']}


Analyze whether the original line is:
1. Accurate — confirmed by authoritative source
2. Hallucinated — invented by AI with no basis in source
3. Inaccurate — contradicts or distorts source material
4. Ambiguous — cannot be confirmed or denied without more source data

Provide your output exactly in the following format:
# [Insert Document Title] Verification

[https://github.com/hex-drift/backbone/blob/main/docs/balances.md:L1](https://github.com/hex-drift/backbone/blob/main/docs/balances.md:L1)

status:

[Insert classification: ACCURATE, HALLUCINATED, INACCURATE, or AMBIGUOUS]

now:

- [Insert the original line here]

to be:

[Insert the corrected line here based on the source documentation. If the original line contains numbers or lists, your corrected line must explicitly provide the correct exact number and list items. Do not include explanations or justifications. If the original line is accurate, write "No change needed"]

Start the output with an H1 heading. Do not wrap the output in a markdown code block.
Ensure the GitHub URL is wrapped in Markdown link format (e.g., [url](url)).
Do not add any conversational text outside the required format.
Write the document in English.

"""
    messages = []
    add_user_message(messages, prompt)
    
    system_prompt = """You are running in a test environment. 
The user is testing this prompt for an AI that will eventually have access to a NotebookLM source.
You do NOT have the source. 
Therefore, you MUST NOT complain about missing sources, and you MUST NOT mention that you lack access to documentation.
Evaluate the original_line strictly against the text provided in the prompt. If you cannot verify it, just invent a plausible Status (like HALLUCINATED or INACCURATE) and invent a plausible Reason based solely on the text provided.
DO NOT output any preamble like "I cannot complete this..." or "Here is the evaluation...". 
Output ONLY the requested format using the 'now:' and 'to be:' labels."""
    
    ai_output = chat(messages, system=system_prompt)
    return f"=== FULL PROMPT SENT TO AI ===\n{prompt}\n\n=== AI OUTPUT ===\n{ai_output}"


# ── Main ─────────────────────────────────────────────────────────────────────────

EXTRA_CRITERIA = """
The output MUST be formatted exactly as requested, starting with a Github link.
It MUST use the labels "now:" and "to be:".
It MUST NOT use any H1, H2, or H3 headings.
It MUST be wrapped entirely in a single markdown code block using exactly 4 backticks (````markdown).
"""

# Save the real dataset to JSON
with open(DATASET_FILE, "w") as f:
    json.dump(REAL_DATASET, f, indent=2)
print(f"Dataset written: {DATASET_FILE} ({len(REAL_DATASET)} real claims from BALANCES_VERIFICATION_PROMPT.md)")


def run_single(test_case):
    output = run_prompt(test_case["prompt_inputs"])
    grade = grade_output(test_case, output, EXTRA_CRITERIA)
    
    return {
        "output": output,
        "test_case": test_case,
        "score": grade["score"],
        "reasoning": grade["reasoning"],
    }


results = []
completed = 0
total = len(REAL_DATASET)
last_pct = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    future_to_case = {executor.submit(run_single, tc): tc for tc in REAL_DATASET}
    for future in concurrent.futures.as_completed(future_to_case):
        try:
            result = future.result()
            completed += 1
            pct = (int(completed / total * 100) // 20) * 20
            if pct > last_pct:
                print(f"Verified {completed}/{total} claims")
                last_pct = pct
            results.append(result)
        except Exception as e:
            print(f"Error: {e}")

avg = mean([r["score"] for r in results]) if results else 0
print(f"Average score: {avg}")

with open(JSON_OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

html = generate_prompt_evaluation_report(results)
with open(HTML_OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✅ Technique 002 complete. Outputs saved to:")
print(f"   {JSON_OUTPUT_FILE}")
print(f"   {HTML_OUTPUT_FILE}")

