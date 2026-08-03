from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def build_prompt(user_message: str, memory_lines: list[str], recent_turns: list[str]) -> tuple[str, str]:
    system = f"""{SAFETY_GUARDRAILS}

You are in an ongoing conversation with the founder inside the AI
Assistant panel. Don't just answer - identify patterns, recommend
concrete next actions, prioritize, and briefly explain your reasoning
when it adds value. Keep responses conversational and concise (this is
chat, not a report)."""

    recent = "\n".join(recent_turns) if recent_turns else "(no prior messages this session)"

    user = f"""Known context about this founder and business:
{format_memory_context(memory_lines)}

Recent conversation:
{recent}

Founder's new message: {user_message}"""

    return system, user
