import json

# 1. First, we need to extract the `run_prompt` code from run_002_clear_direct.py
with open("run_002_clear_direct.py", "r") as f:
    content = f.read()

# We can just construct the string for the cell
run_prompt_source = """def run_prompt(prompt_inputs):
    prompt = f\"\"\"
You are a strict technical auditor for a Gambling platform documentation system.

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

\"\"\"
    messages = []
    add_user_message(messages, prompt)
    
    system_prompt = \"\"\"You are running in a test environment. 
The user is testing this prompt for an AI that will eventually have access to a NotebookLM source.
You do NOT have the source. 
Therefore, you MUST NOT complain about missing sources, and you MUST NOT mention that you lack access to documentation.
Evaluate the original_line strictly against the text provided in the prompt. If you cannot verify it, just invent a plausible Status (like HALLUCINATED or INACCURATE) and invent a plausible Reason based solely on the text provided.
DO NOT output any preamble like "I cannot complete this..." or "Here is the evaluation...". 
Output ONLY the requested format using the 'now:' and 'to be:' labels.\"\"\"
    
    ai_output = chat(messages, system=system_prompt)
    return f"=== FULL PROMPT SENT TO AI ===\\n{prompt}\\n\\n=== AI OUTPUT ===\\n{ai_output}"
"""

# Format as lines
run_prompt_lines = [line + "\\n" for line in run_prompt_source.split("\\n")]
run_prompt_lines[-1] = run_prompt_lines[-1].strip("\\n")

EXTRA_CRITERIA_LINES = [
    "EXTRA_CRITERIA = \"\"\"\n",
    "The output MUST be formatted exactly as requested, starting with a Github link.\n",
    "It MUST use the labels \"now:\" and \"to be:\".\n",
    "It MUST NOT use any H1, H2, or H3 headings.\n",
    "It MUST be wrapped entirely in a single markdown code block using exactly 4 backticks (````markdown).\n",
    "\"\"\"\n"
]

EVAL_RUN_LINES = [
    "results = evaluator.run_evaluation(\n",
    "    run_prompt_function=run_prompt,\n",
    "    dataset_file='dataset_balances_002_clear_direct.json',\n",
    "    extra_criteria=EXTRA_CRITERIA,\n",
    "    json_output_file='output_balances_003_specific.json',\n",
    "    html_output_file='output_balances_003_specific.html',\n",
    ")\n"
]

def patch_notebook(nb_path):
    with open(nb_path, "r") as f:
        nb = json.load(f)

    # For 003, remove generate_dataset
    if "003" in nb_path:
        new_cells = []
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                source_str = "".join(cell["source"])
                if "evaluator.generate_dataset" in source_str:
                    continue # drop the diet dataset generation
                if "def run_prompt" in source_str:
                    cell["source"] = run_prompt_lines
                elif "evaluator.run_evaluation" in source_str:
                    cell["source"] = EXTRA_CRITERIA_LINES + ["\n"] + EVAL_RUN_LINES
            new_cells.append(cell)
        nb["cells"] = new_cells
    else:
        # For 002
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                source_str = "".join(cell["source"])
                if "def run_prompt" in source_str:
                    cell["source"] = run_prompt_lines
                elif "evaluator.run_evaluation" in source_str:
                    eval_002 = [
                        "results = evaluator.run_evaluation(\n",
                        "    run_prompt_function=run_prompt,\n",
                        "    dataset_file='dataset_balances_002_clear_direct.json',\n",
                        "    extra_criteria=EXTRA_CRITERIA,\n",
                        "    json_output_file='output_balances_002_clear_direct.json',\n",
                        "    html_output_file='output_balances_002_clear_direct.html',\n",
                        ")\n"
                    ]
                    cell["source"] = EXTRA_CRITERIA_LINES + ["\n"] + eval_002

    with open(nb_path, "w") as f:
        json.dump(nb, f, indent=2)

patch_notebook("002_prompt_clear_direct.ipynb")
patch_notebook("003_prompt_specific.ipynb")
print("Notebooks patched successfully.")
