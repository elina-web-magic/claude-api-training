import json

with open("002_prompt_clear_direct.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source_str = "".join(cell["source"])
        if "def grade_output(self" in source_str:
            new_source = []
            for line in cell["source"]:
                if 'add_assistant_message(messages, "```json")' in line:
                    new_source.append('        add_assistant_message(messages, "```json\\n{")\n')
                elif 'eval_text = chat(' in line:
                    new_source.append('        raw_response = chat(\n')
                elif 'stop_sequences=["```"],' in line:
                    continue
                elif 'import ast, re' in line:
                    new_source.append('        eval_text = "{\\n" + raw_response.strip()\n')
                    new_source.append(line)
                else:
                    new_source.append(line)
            cell["source"] = new_source

with open("002_prompt_clear_direct.ipynb", "w") as f:
    json.dump(nb, f, indent=2)

print("Notebook evaluator fixed.")
