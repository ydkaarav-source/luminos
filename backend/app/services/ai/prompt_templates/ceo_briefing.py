from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def build_prompt(
    business_name: str,
    tasks_completed_yesterday: int,
    open_priority_tasks: list[str],
    latest_health_score: int | None,
    memory_lines: list[str],
) -> tuple[str, str]:
    system = f"""{SAFETY_GUARDRAILS}

You are writing today's CEO Morning Briefing for {business_name}. Respond
ONLY with a single JSON object, no preamble, matching exactly this shape:

{{
  "title": "string, e.g. 'Your Monday Briefing'",
  "body": "string, 3-6 short sentences: acknowledge yesterday's progress,
           state the top priorities in order, and end with ONE clear key
           insight about the business's biggest current bottleneck or
           opportunity",
  "priority": "low" | "medium" | "high"
}}"""

    user = f"""Yesterday: {tasks_completed_yesterday} task(s) completed.
Open priority tasks: {', '.join(open_priority_tasks) if open_priority_tasks else 'none logged'}.
Latest Business Health Score: {latest_health_score if latest_health_score is not None else 'not yet calculated'}.

Known context about this founder and business:
{format_memory_context(memory_lines)}

Write today's briefing JSON now."""

    return system, user
