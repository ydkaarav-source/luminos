from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def build_prompt(idea_description: str, business_context: dict, memory_lines: list[str]) -> tuple[str, str]:
    system = f"""{SAFETY_GUARDRAILS}

You are generating a structured business plan. Respond ONLY with a single
JSON object, no preamble, no markdown fences, matching exactly this shape:

{{
  "title": "string",
  "overview": {{
    "target_customer": "string",
    "problem_solved": "string",
    "revenue_model": "string",
    "competition": "string",
    "risks": "string"
  }},
  "roadmap": [
    {{"month": 1, "focus": "string", "milestones": ["string"]}},
    {{"month": 2, "focus": "string", "milestones": ["string"]}},
    {{"month": 3, "focus": "string", "milestones": ["string"]}}
  ],
  "action_plan": {{
    "daily_tasks": ["string"],
    "weekly_goals": ["string"],
    "milestones": ["string"]
  }}
}}"""

    user = f"""Business idea: {idea_description}

Business context:
- Stage: {business_context.get('stage')}
- Type: {business_context.get('business_type')}
- Primary goal: {business_context.get('primary_goal')}
- Available time per week: {business_context.get('available_time_per_week')}
- Budget range: {business_context.get('budget_range')}

Known context about this founder and business so far:
{format_memory_context(memory_lines)}

Generate the business plan JSON now."""

    return system, user
