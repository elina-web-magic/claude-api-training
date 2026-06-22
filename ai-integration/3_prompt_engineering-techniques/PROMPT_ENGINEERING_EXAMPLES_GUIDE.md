# Prompt Engineering Guide: Practical Lessons & Examples

This document summarizes the key techniques we learned and applied while building a complex Prompt Engineering pipeline for the Diet Planner.

---

## 1. Clear and Direct

### 1. Problem

People tend to write prompts as if they are talking to a human (using polite phrases, vague wording, or unnecessary context). This forces the model to spend "attention" on useless words instead of the core task.

### 1. Bad Prompt

```text
Hi! Could you please help me with something? I would like you to write some kind of menu, for about a day, for a single woman who wants to lose weight. Something that isn't too hard to cook.
```

### 1. Good Prompt

```text
Write a 1-day dynamic meal plan for a 37-year-old woman. Goal: lose weight from 61kg to 55kg.
```

### 1. Explanation

A good prompt starts with a clear action verb ("Write"). It leaves no room for ambiguity regarding the format, target audience, or scope of the task.

### 1. Use Cases

- Code generation (e.g., "Write a Python script that...")
- Text generation (e.g., "Summarize this article in 3 paragraphs")
- The very first line of any system prompt.

---

## 2. Being Specific (Using Guidelines)

### 2. Problem

If you leave details up to the model, it will choose the simplest, most average path. For example, it might invent recipes that take 2 hours to cook or include ingredients that cause bloating.

### 2. Bad Prompt

```text
Create a meal plan that is quick and good for the stomach.
```

### 2. Good Prompt

```text
Guidelines:
1. Prep Time: All meals MUST be prepared in under 20 minutes. Avoid slow-cooking methods like simmering soups or stews.
2. Medical Needs: Evening meals must be easily digestible and avoid triggers to prevent bloating.
```

### 2. Explanation

Clearly numbered rules (Guidelines) act as laws for the model. By stating "Avoid slow-cooking methods," we preemptively close the path for the model to create time-consuming soups.

### 2. Use Cases

- Setting strict boundaries (format, length, tone of voice).
- Enforcing business rules (e.g., "Never mention competitors X and Y").

---

## 3. Dynamic Variables vs. Overfitting

### 3. Problem

A prompt might work perfectly for one client (e.g., a woman allergic to garlic) but fail completely for another (a vegetarian). This happens when we hardcode specific products into the prompt itself.

### 3. Bad Prompt

```text
Guidelines:
Include salmon, chicken, and eggs.
Exclude: onion, garlic, beans.
```

> Note: This conflicts immediately if the client is vegetarian!

### 3. Good Prompt

```text
Guidelines:
Strictly exclude any ingredients forbidden by the user's dietary profile ({prompt_inputs['restrictions']}). Only use ingredients that are 100% safe.
```

### 3. Explanation

Extracting variables into `prompt_inputs` turns your prompt into a universal engine (Template). The model relies on the specific client's input data rather than hardcoded text rules, avoiding logical conflicts.

### 3. Use Cases

- Building APIs where the prompt processes requests from thousands of different users.
- Email templates, reports, or personalized content generation.

---

## 4. Process Steps (Chain of Thought)

### 4. Problem

Language models cannot "think silently." If you give them a complex math problem or ask them to consider 50 constraints at once, they will immediately start generating the final result and are guaranteed to make mistakes (like exceeding calorie limits).

### 4. Bad Prompt

```text
Immediately give me a 1530 kcal meal plan that accounts for all restrictions and cycle phases.
```

### 4. Good Prompt

```text
Follow these steps to generate the plan:
Step 1: Ingredient Filtering. Review the user's specific dietary restrictions and list a few safe ingredients to use.
Step 2: Medical Strategy. Briefly outline how you will adapt the meals to prevent evening bloating.
Step 3: Meal Generation. Only after completing steps 1 and 2, generate the full meal plan.
```

### 4. Explanation

By forcing the model to write out its "thoughts" (Steps 1 and 2) as text, you create a cheat sheet for it. When it reaches the actual menu generation (Step 3), it "reads" its own previous text and only uses the products it just deemed safe. This drastically reduces hallucinations.

### 4. Use Cases

- Mathematical calculations and logic puzzles.
- Analyzing large volumes of data before forming a conclusion.
- Writing code (e.g., "Step 1: Plan the architecture, Step 2: Write the code").

---

## 5. Giving Examples (One-Shot Prompting & Formatting)

### 5. Problem

Even if the model understands the task, it might add unnecessary "fluff" (e.g., "Here is your menu, I hope you enjoy it!") or use a format that your application cannot parse (missing meal times, chaotic macro output).

### 5. Bad Prompt

```text
Write down each meal in detail: calories, ingredients, time, and macros.
```

### 5. Good Prompt

```text
Generate the meal plan strictly following the Example Format below. Do not add any extra conversational text.

<example>
BREAKFAST: [Meal Name] (XXX kcal)
Time of Day: 08:00 AM
- [Ingredient 1 with exact amount]
Macros: P: XXg | C: XXg | F: XXg
Prep Time: [X] min
</example>
```

### 5. Explanation

Using an exact structural template (One-Shot Prompting) shows the model the ideal visual structure. This:

1. Prevents the generation of unnecessary text (saving tokens and preventing truncation).
2. Ensures no required field (like the time of day) is missed.
3. Helps enforce the mathematical logic you built into the template.

### 5. Use Cases

- Generating structured data (Markdown, tables, lists, JSON).
- Forcing the model to respond in a specific persona (e.g., a strict lawyer or concise programmer).
- Data Extraction without generating conversational fluff.

## 6. Structure with XML Tags

### 6. Problem

When building prompts that include a lot of content, Claude can sometimes struggle to understand which pieces of text belong together or what different sections represent. Without clear boundaries, the model might confuse instructions with the data it's supposed to analyze.

### 6. Solution & Best Practice

Use **XML tags** to provide a simple way to add structure and clarity to your prompts.

- Create custom, descriptive tag names (e.g., `<sales_records>` instead of `<data>`, or `<athlete_information>`).
- Wrap distinct parts of your prompt (context, data, examples, formatting) in these tags.
- This creates clear delimiters, making it explicitly clear to Claude how to parse your intent.

### 6. Use Cases

- Interpolating multiple dynamic variables into a prompt.
- Separating long context documents from the actual user query.
- Differentiating between code (`<my_code>`) and documentation (`<docs>`).

---

## 7. Providing Examples (One-Shot & Multi-Shot Prompting)

### 7. Problem

Even with clear instructions, the model might still misunderstand the desired format, fail to catch corner cases (like sarcasm in sentiment analysis), or ignore constraints because it defaults to its standard behavior.

### 7. Solution & Best Practice

Provide **Examples** within your prompt.

- Examples should *complement*, not replace, your core guidelines. If you remove strict rules and leave only an example, the model might lose the hard constraints (like a strict calorie limit).
- Wrap examples in XML tags like `<sample_input>` and `<ideal_output>`.
- Add context explaining *why* the example output is good. This helps the model generalize the rules.

### 7. Use Cases

- Handling tricky corner cases (e.g., classifying sarcastic text).
- Enforcing complex formatting that is hard to describe with words alone.
- Calibrating the tone of voice or style of the output.

---

## 8. LLM-as-a-Judge Hallucinations & Chain of Thought

### 8. Problem

When using an LLM to evaluate the output of another prompt (Prompt Evaluation), the judge might "hallucinate" math. For example, it might incorrectly claim that 1608 kcal exceeds a limit of 1500-1650 kcal, penalizing a perfectly valid output.

### 8. Solution & Best Practice (Chain of Thought)

LLMs cannot do math reliably in their heads. You must give the judge a "scratchpad" to think step-by-step before it outputs a final score.

- Add a `"scratchpad"` field as the very first item in your JSON output format.
- Instruct the judge to use the scratchpad to extract numbers and explicitly verify if they fall within the required boundaries.

---

## 9. Why LLM Judges Are Excessively Strict

### 9. Problem

LLMs (like Claude or GPT) are notoriously harsh graders on a 1-10 scale. They hesitate to give a perfect 10 because "nothing is perfect." Even if you instruct them to grade *only* based on the provided criteria, they will often invent new criteria (e.g., "formatting inconsistency", "lack of hydration advice") just to justify giving a 9 instead of a 10.

### 9. Solution & Best Practice

- Avoid using a subjective 1-10 scale. Instead, use a binary `Pass / Fail` or `1 / 0` system for each specific criterion.
- If you must use a scale, write highly aggressive instructions: *"If all criteria are met, you MUST score 10. DO NOT deduct points for anything not explicitly listed in the criteria."*
- Consider using **Code-based grading** (e.g., Python scripts checking boundaries) instead of LLMs for strict mathematical or presence checks.

### 10. Markdown with Mermaid

> Generates documentation with full markdown formatting and mermaid diagrams, ready to be pasted into a .md file.

**When to use:** editing documentation, schemas, architectural diagrams in a single block, ready to be saved.
**Problem it solves:** the internal ` ```mermaid ` breaks the outer ` ```markdown ` block — we use 4 backticks for the outer block.

```text
Wrap the entire output in a single markdown code block using 4 backticks (````markdown).
Do not add any text outside the code block.
Write the document in English.

## Document structure rules
- One H1 heading (#) at the top — the document title
- All other headings must be H2 (##) or H3 (###)
- Separate every section with a horizontal rule (---)
- Use plain bullet lists (-) for enumerations — no nested bullet walls
- Keep paragraphs short and direct

## Code blocks
- Use ```mermaid for diagrams (3 backticks inside the outer 4-backtick fence)
- Use ```text for plain text examples or rules
- Use the correct language tag for code: ```typescript, ```python, ```bash, etc.
- Never use an untagged code block

## Mermaid diagram rules
- Use flowchart TD or flowchart LR
- Style all nodes with classDef using fill, stroke, stroke-width, color
- Assign each logical group its own class
- After the diagram, add a ## Legend section with a markdown table:
  | Color | Meaning |
  | :--- | :--- |
  | 🔵 Blue | ... |
  | 🟣 Purple | ... |
  (use emoji + color name + layer meaning)

## Color palette for classDef (use consistently)
- Purple (#ede9fe / #7c3aed / #1e1b4b) — server / infrastructure
- Blue (#bae6fd / #0284c7 / #082f49) — client / UI layer
- Orange (#ffedd5 / #ea580c / #431407) — state / cache / data
- Green (#bbf7d0 / #16a34a / #052e16) — logic / services / actions
- Red (#fee2e2 / #dc2626 / #450a0a) — failure / rollback
```

---
