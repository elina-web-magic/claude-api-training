import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from pydantic import BaseModel, Field

# =====================================================================
# 📚 HOW TO AVOID "pip install" IN EVERY JUPYTER NOTEBOOK (.ipynb)
# =====================================================================
# 1. Create a virtual environment once for the whole project:
#    $ python3 -m venv .venv
#
# 2. Activate the virtual environment:
#    $ source .venv/bin/activate
#
# 3. Install all dependencies from requirements.txt:
#    $ pip install -r requirements.txt
#
# 4. Register this virtual environment as a Jupyter Kernel:
#    $ pip install ipykernel
#    $ python -m ipykernel install --user --name=claude-api-training --display-name "Python (Claude API Training)"
#
# 5. In your Jupyter Notebook (.ipynb), simply select the kernel:
#    "Python (Claude API Training)" from the top-right kernel selector.
#    Now all libraries (anthropic, pydantic, dotenv, etc.) are available
#    globally across all notebooks without any "!pip install ..." cells!
# =====================================================================

# Load environment variables from .env file
load_dotenv()

# Initialize the Anthropic client
# (It will automatically read the ANTHROPIC_API_KEY environment variable)
client = Anthropic()

# =====================================================================
# 💡 ANTHROPIC TOKEN SAVING TECHNIQUES & ARCHITECTURE
# =====================================================================
#
# 1. PROMPT CACHING (Saves up to 90% of input token costs!)
#    - Perfect for long system prompts, document uploads, or conversation history.
#    - Anthropic allows up to 4 cache breakpoints ("ephemeral" cache).
#    - The minimum cacheable prompt size is:
#      * 1,024 tokens for Claude 3.5 Sonnet / Haiku
#      * 8,192 tokens for Claude 3 Opus
#    - Cached prompts remain active for 5 minutes (re-refreshed on every cache hit).
#
# 2. STRUCTURED OUTPUTS WITH PYDANTIC (Saves output tokens!)
#    - By forcing Claude to return raw structured data (like JSON), we prevent
#      conversational preambles/postambles ("Sure, here is the information..."),
#      saving valuable output tokens and making parsing 100% reliable.
#
# 3. CONCISE SYSTEM PROMPTS
#    - Avoid fluff in system instructions.
#
# 4. FASTAPI & UVICORN (Are they needed?)
#    - They are NOT needed for running notebooks or python scripts.
#    - HOWEVER, they are extremely useful if you build a proxy gateway
#      web service to add custom caching (e.g. caching responses in Redis
#      for duplicate user requests to spend 0 tokens).
# =====================================================================


# Define a Pydantic model for structured outputs
class CourseChapterSummary(BaseModel):
    chapter_name: str = Field(description="The name of the course chapter")
    key_takeaway: str = Field(
        description="A concise 1-sentence summary of what this chapter teaches"
    )
    estimated_hours: float = Field(
        description="Estimated hours to complete this chapter"
    )


def demonstrate_prompt_caching():
    """
    Demonstrates how to implement Prompt Caching to save tokens.
    """
    print("\n--- 1. Demonstrating Prompt Caching ---")

    # We will simulate a very long context (e.g. the entire syllabus)
    # to serve as our reusable prompt cache base.
    reusable_syllabus_context = """
    Course Syllabus: Building with the Claude API.
    Welcome to the course. Learn to build applications with Anthropic Claude API.
    Chapters include:
    - Chapter 1: Introduction (Welcome, Anthropic overview, Claude models)
    - Chapter 2: Accessing Claude with the API (Keys, multi-turn chat, system prompts, streaming, structured data)
    - Chapter 3: Prompt Evaluation (Evals, datasets, model-based grading)
    - Chapter 4: Prompt Engineering Techniques (XML tags, few-shot examples, prompt clarity)
    - Chapter 5: Tool Use (Function calling, tool schemas, multi-turn tool loops)
    - Chapter 6: RAG and Agentic Search (Retrieval-Augmented Generation, chunking, embeddings, BM25)
    - Chapter 7: Features of Claude (Extended thinking, image & PDF support, Citations, Prompt Caching)
    - Chapter 8: Model Context Protocol (MCP, clients, servers, inspector)
    - Chapter 9: Anthropic Apps (Claude Code setup, Computer Use)
    - Chapter 10: Agents and Workflows (Chaining, routing, parallelization workflows)
    - Chapter 11: Final assessment and Wrap Up.
    """

    # We add a cache breakpoint at the system prompt using cache_control={"type": "ephemeral"}
    # This caches the syllabus context. Subsequent calls referencing this system prompt
    # will read from cache, costing 90% less!

    start_time = time.time()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        temperature=0.0,
        system=[
            {
                "type": "text",
                "text": f"You are a helpful course assistant. Here is the course syllabus:\n{reusable_syllabus_context}",
                "cache_control": {
                    "type": "ephemeral"
                },  # ⚡ THIS ENABLES PROMPT CACHING!
            }
        ],
        messages=[
            {
                "role": "user",
                "content": "Explain briefly what I will learn in Chapter 5: Tool Use.",
            }
        ],
    )

    duration = time.time() - start_time
    print(f"Response: {response.content[0].text.strip()}")
    print(f"Time taken: {duration:.2f} seconds")

    # Check token usage and cache performance
    usage = response.usage
    print("Tokens Used:")
    print(f"  - Input Tokens (total): {usage.input_tokens}")
    # Note: On the very first request, it writes to cache (cache creation)
    # On subsequent requests within 5 minutes, we will see `cache_read_input_tokens` matching the cached size!
    if hasattr(usage, "cache_creation_input_tokens"):
        print(f"  - Cache Creation Input Tokens: {usage.cache_creation_input_tokens}")
    if hasattr(usage, "cache_read_input_tokens"):
        print(
            f"  - Cache Read Input Tokens (Saves Money!): {usage.cache_read_input_tokens}"
        )
    print(f"  - Output Tokens: {usage.output_tokens}")


def demonstrate_structured_output():
    """
    Demonstrates using structured system instructions + Pydantic schema
    to minimize output tokens by preventing conversational clutter.
    """
    print("\n--- 2. Demonstrating Structured Output & Output Token Saving ---")

    # We ask Claude to return a raw JSON structure matching our Pydantic model
    # and strictly instruct it to avoid conversational chat.
    pydantic_schema_str = CourseChapterSummary.model_json_schema()

    start_time = time.time()
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",  # Claude 3.5 Haiku is faster and cheaper!
        max_tokens=300,
        temperature=0.0,
        system="""You are a strict JSON generator. You must output ONLY a raw valid JSON object matching the provided Pydantic JSON Schema.
Do not include any intro, outro, preamble, postamble, or markdown formatting (do not wrap in ```json).
Your entire response must be a single parseable JSON object.""",
        messages=[
            {
                "role": "user",
                "content": f"Generate a summary for Chapter 6 (RAG and Agentic Search). Schema:\n{pydantic_schema_str}",
            }
        ],
    )

    duration = time.time() - start_time
    raw_response = response.content[0].text.strip()

    print(f"Raw Output (No conversational fluff = Saved Tokens!):\n{raw_response}")
    print(f"Time taken: {duration:.2f} seconds")
    print(
        f"Tokens Used: Input = {response.usage.input_tokens}, Output = {response.usage.output_tokens}"
    )


if __name__ == "__main__":
    print("🚀 Starting Anthropic Claude API Token Optimization Demo")

    # Verify API key is present
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ Warning: ANTHROPIC_API_KEY environment variable not found in .env!")
        print("Please copy .env.example to .env and fill in your actual API Key first.")
    else:
        try:
            # 1. Run prompt caching demo
            demonstrate_prompt_caching()

            # 2. Run structured outputs demo
            demonstrate_structured_output()

        except Exception as e:
            print(f"\n❌ Error calling API: {e}")
            print("Ensure your ANTHROPIC_API_KEY in .env is valid and active.")
