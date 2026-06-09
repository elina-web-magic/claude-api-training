def run_diet_planner_prompt(height: str, weight: str, goal: str, restrictions: str) -> str:
    """
    Build and return the prompt string using the diet dataset inputs.
    """
    return f"""Write a compact, concise 1 day meal plan for a single woman.

Height: {height} cm
Weight: {weight} kg
Goal: {goal}
Dietary restrictions: {restrictions}

Your response MUST include:
1. Daily caloric total (e.g. "Total: 1850 kcal")
2. Macronutrient breakdown: protein / carbs / fat in grams
3. Each meal with: exact foods, portion sizes, and time of day
4. Calorie count appropriate for the stated goal (not under 1500 kcal unless goal is weight loss)
"""
