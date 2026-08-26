from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def _format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def _format_pct(pct: float | None) -> str:
    if pct is None:
        return "not calculable (no revenue logged the prior week to compare against)"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct}%"


def _format_business_profile(profile: dict | None) -> str:
    if not profile:
        return "No business profile filled in yet."
    fields = (
        ("Industry", "industry"),
        ("Description", "description"),
        ("Target customers", "target_customers"),
        ("Company goals", "company_goals"),
    )
    return "\n".join(f"- {label}: {profile.get(key) or 'not provided'}" for label, key in fields)


def _format_calendar_events(events: list[dict] | None) -> str:
    # None = not connected (or a broken connection) - this is genuinely
    # absent context, not "zero events," so it's worded differently from
    # a connected calendar that's simply empty today.
    if events is None:
        return "No calendar connected - this founder hasn't connected Google Calendar."
    if not events:
        return "Google Calendar connected - no events scheduled today."
    lines = [f"Google Calendar connected - {len(events)} event(s) scheduled today:"]
    for e in events:
        start = (e["start"] or "")[11:16] or e["start"]
        lines.append(f"- {start}: {e['title']}")
    return "\n".join(lines)


def build_prompt(business_name: str, metrics: dict, memory_lines: list[str]) -> tuple[str, str]:
    """
    Builds today's CEO Briefing prompt. Every figure below is already
    computed in Python (same split as Health Score: code computes, AI
    explains) - the model reasons about numbers it's handed, it never
    estimates or invents one of its own.
    """
    system = f"""{SAFETY_GUARDRAILS}

You are writing today's CEO Morning Briefing for {business_name}, grounded
entirely in this business's own historical numbers, not projections or
promises about the future. Every claim you make must be traceable to a
specific number given to you below. Never estimate, round vaguely, or
invent a figure. If a number isn't available, say so explicitly rather
than working around it.

Respond ONLY with a single JSON object, no preamble, matching exactly this
shape:

{{
  "finding": "string",
  "why": ["string", "string"],
  "recommendation": "string",
  "confidence": "high" | "medium" | "low"
}}

"finding" is one sentence that references at least one specific real
number from the data below - not vague language like "revenue is trending
well".
"why" is 2-4 short factors (one sentence each), each grounded in a real
number from the data below - fewer than 4 is fine if there genuinely
isn't enough data, don't pad with vague filler to hit a count.
"recommendation" is one concrete, specific action the founder can take
TODAY in a single sitting - not a strategic direction like "improve
marketing".
Be honest about "confidence": use "low" when there's minimal real data to
work with (e.g. zero revenue entries this week, or no prior Health Score
to compare against) - never default to "high" just to seem more useful.

Today's calendar (if connected) is additional context, not a required
ingredient - only reference it in "finding", "why", or "recommendation"
when it's genuinely relevant to the most important thing happening in
this business today (e.g. a heavy meeting day competing with an overdue
task, or a clear day that's a good opportunity to catch up). Don't force
a calendar mention into every briefing just because the data is present."""

    user = f"""Revenue:
- This week (last 7 days): {_format_currency(metrics['revenue_this_week'])}
- Prior week (7 days before that): {_format_currency(metrics['revenue_last_week'])}
- Week-over-week change: {_format_pct(metrics['revenue_change_pct'])}

Tasks:
- Completed in the last 24 hours: {metrics['tasks_completed_yesterday']}
- Completed in the same 24-hour window one week ago: {metrics['tasks_completed_same_weekday_last_week']}
- Currently overdue (past due date, not done): {metrics['overdue_tasks_count']}
- Open priority tasks: {', '.join(metrics['open_priority_tasks']) if metrics['open_priority_tasks'] else 'none logged'}

Business Health Score:
- Latest: {metrics['latest_health_score'] if metrics['latest_health_score'] is not None else 'not yet calculated'}
- Change from the previous calculation: {metrics['health_score_delta'] if metrics['health_score_delta'] is not None else 'not enough history to compare yet'}

Business profile:
{_format_business_profile(metrics['business_profile'])}

Today's calendar:
{_format_calendar_events(metrics['todays_calendar_events'])}

Known context about this founder and business:
{format_memory_context(memory_lines)}

Write today's briefing JSON now."""

    return system, user
