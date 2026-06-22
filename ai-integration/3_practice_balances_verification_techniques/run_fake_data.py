import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

client = Anthropic()
model = "claude-haiku-4-5"

def run_fake_data_test():
    fake_data_path = Path("fake_game_aggregation_data.md")
    with open(fake_data_path, "r") as f:
        fake_data = f.read()
        
    prompt_path = Path("../../docs/BALANCES_VERIFICATION_PROMPT_2.md")
    with open(prompt_path, "r") as f:
        full_content = f.read()
        
    # Extract the prompt template from the ```text block
    try:
        prompt_template = full_content.split("```text")[1].split("```")[0].strip()
    except IndexError:
        print("Could not find ```text block in prompt file!")
        return

    # Replace the balances.md specific context with our fake data
    # We will just replace everything between '## Source Documentation Section' and 'Analyze whether the original line is:'
    
    parts = prompt_template.split("## Source Documentation Section")
    part1 = parts[0]
    part2 = parts[1].split("Analyze whether the original line is:")[1]
    
    # Also replace document names
    part1 = part1.replace("balances.md", "game_aggregation.md")
    part2 = part2.replace("balances.md", "game_aggregation.md")
    
    injected_context = f"""## Source Documentation Section

{fake_data}

technical_fact

Idempotency keys are optional on money endpoints because the aggregation layer resolves duplicate credits automatically.

Analyze whether the original line is:"""

    prompt = part1 + injected_context + part2

    print("Sending prompt to Anthropic API...")
    
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    
    result_text = response.content[0].text
    
    output_path = Path("fake_game_aggregation_output.md")
    with open(output_path, "w") as f:
        f.write(result_text)
        
    print(f"Result written to {output_path}")

if __name__ == "__main__":
    run_fake_data_test()
