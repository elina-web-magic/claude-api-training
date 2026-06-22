import json

with open("002_prompt_clear_direct.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            if "return json.loads(eval_text)" in line:
                new_source.extend([
                    "        import ast, re\n",
                    "        try:\n",
                    "            return json.loads(eval_text)\n",
                    "        except json.JSONDecodeError:\n",
                    "            # Try to fix unescaped newlines within strings by falling back or just regex\n",
                    "            try:\n",
                    "                # Sometimes LLMs write valid python dicts but invalid JSON\n",
                    "                fixed_text = eval_text.replace('true', 'True').replace('false', 'False')\n",
                    "                return ast.literal_eval(fixed_text)\n",
                    "            except:\n",
                    "                return {\n",
                    "                    'strengths': [],\n",
                    "                    'weaknesses': [],\n",
                    "                    'reasoning': f'JSON Parse Error on evaluation:\\n{eval_text}',\n",
                    "                    'score': 5\n",
                    "                }\n"
                ])
            else:
                new_source.append(line)
        cell["source"] = new_source

with open("002_prompt_clear_direct.ipynb", "w") as f:
    json.dump(nb, f, indent=2)

print("Notebook patched with try/except for json.loads(eval_text)")
