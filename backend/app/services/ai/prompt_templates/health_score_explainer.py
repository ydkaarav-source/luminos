from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def build_prompt(scores: dict, memory_lines: list[str]) -> tuple[str, str]:
    system = f"""{SAFETY_GUARDRAILS}

You are explaining a Business Health Score breakdown. Respond ONLY with a
single JSON object, no preamble, matching exactly this shape:

{{
  "strengths": ["string", "string"],
  "weaknesses": ["string", "string"],
  "recommendations": ["string", "string", "string"]
}}

Keep each item to one clear sentence. Recommendations must be concrete
next actions, not generic advice."""

    user = f"""Score breakdown (0-100 each):
- Revenue: {scores['revenue_score']}
- Operations: {scores['operations_score']}
- Marketing: {scores['marketing_score']}
- Customer growth: {scores['customer_growth_score']}
- Financial management: {scores['financial_management_score']}
- Overall: {scores['overall_score']}

Known context about this founder and business:
{format_memory_context(memory_lines)}

Write the explanation JSON now."""

    return system, user
