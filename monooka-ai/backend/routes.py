from prompts import run_diet_planner_prompt

# Registry mapping context identifiers to their specific logic
# type: dict[str, dict]

LESSON_ROUTES = {
    "1_making_a_request": {
        "system_prompt": "You are helping the user learn how to make basic HTTP requests to the Claude API. Provide clear explanations.",
    },
    "1_system_prompts": {
        "system_prompt": "You are helping the user learn about System Prompts. Emphasize how system prompts change AI behavior.",
    },
    "1_temperature": {
        "system_prompt": "You are helping the user understand the 'temperature' parameter in LLMs. Use analogies like creativity vs predictability.",
    },
    "1_response_streaming": {
        "system_prompt": "You are explaining streaming responses. Keep your answers focused on Server-Sent Events (SSE) and chunked generation.",
    },
    "1_structured_data": {
        "system_prompt": "You are teaching the user how to control JSON/XML output formats and stop sequences.",
    },
    "2_prompt_evaluation": {
        "system_prompt": "You are acting as an AI judge evaluating prompts based on strict criteria.",
    },
    "3_prompt_engineering": {
        "extractor_prompt": """
            Extract these parameters from the user's text: height (cm), weight (kg), goal, restrictions.
            Return ONLY valid JSON like: {{"height": "160", "weight": "60", "goal": "lose weight", "restrictions": "none"}}
            If a parameter is not mentioned, use "unknown".
            User text: {user_input}
        """,
        "generator_func": run_diet_planner_prompt,
        "max_tokens": 1000
    }
}
