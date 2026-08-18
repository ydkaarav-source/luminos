from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context

ROLE_PROMPTS = {
    "cfo": {
        "title": "CFO",
        "focus": "financial health - revenue and financial management",
        "score_keys": ["revenue_score", "financial_management_score"],
    },
    "cmo": {
        "title": "CMO",
        "focus": "marketing performance",
        "score_keys": ["marketing_score"],
    },
    "coo": {
        "title": "COO",
        "focus": "operations - task execution and completion rate",
        "score_keys": ["operations_score"],
    },
    "cro": {
        "title": "CRO",
        "focus": "customer growth",
        "score_keys": ["customer_growth_score"],
    },
    "ceo": {
        "title": "CEO",
        "focus": "the whole business - synthesizing across every score",
        "score_keys": [
            "revenue_score",
            "operations_score",
            "marketing_score",
            "customer_growth_score",
            "financial_management_score",
        ],
    },
}


def build_role_prompt(role: str, scores: dict, memory_lines: list[str]) -> tuple[str, str]:
    """
    Builds a prompt scoped to ONE executive role instead of all categories
    at once. This is the core fix for generic output: a model asked to
    explain "marketing only" reasons more specifically than one asked to
    explain five unrelated categories in a single breath.

    "ceo" is the one exception - it deliberately sees ALL five scores,
    because its job is cross-category synthesis and prioritization (see
    the ceo branch below), not a narrow slice like the other four roles.
    """
    role_info = ROLE_PROMPTS[role]
    relevant_scores = {k: scores[k] for k in role_info["score_keys"]}
    scores_text = "\n".join(f"- {k.replace('_', ' ').title()}: {v}" for k, v in relevant_scores.items())

    if role == "ceo":
        # Unlike CFO/CMO/COO/CRO, the CEO isn't scoped to one slice - it
        # must read across all five categories and decide what matters
        # most right now. Explicitly forbid a five-item summary (that's
        # just restating what the other four roles already said) and
        # instead push for a single prioritized read, in the same
        # calm/strategic voice as ceo_briefing.py.
        system = f"""{SAFETY_GUARDRAILS}

You are the CEO, giving a strategic synthesis across this business's
entire health score breakdown - revenue, operations, marketing, customer
growth, and financial management. Respond ONLY with a single JSON object,
no preamble, matching exactly this shape:

{{
  "strengths": ["string", "string"],
  "weaknesses": ["string", "string"],
  "recommendations": ["string", "string", "string"]
}}

Do not simply list or summarize all five categories one by one - that is
what the CFO, CMO, COO, and CRO breakdowns already do individually. Your
job is prioritization: identify the SINGLE biggest priority across the
whole business right now, and let strengths/weaknesses/recommendations
flow from that judgment call. Keep each item to one clear sentence.
Recommendations must be concrete next actions, not generic advice."""
    else:
        system = f"""{SAFETY_GUARDRAILS}

You are the {role_info['title']}, giving a focused breakdown of this
business's {role_info['focus']}. Respond ONLY with a single JSON object,
no preamble, matching exactly this shape:

{{
  "strengths": ["string", "string"],
  "weaknesses": ["string", "string"],
  "recommendations": ["string", "string", "string"]
}}

Stay strictly within your role's focus area - do not comment on categories
outside {role_info['focus']}. Keep each item to one clear sentence.
Recommendations must be concrete next actions, not generic advice."""

    user = f"""Your relevant score(s) (0-100):
{scores_text}

Overall business health: {scores['overall_score']}

Known context about this founder and business:
{format_memory_context(memory_lines)}

Write your {role_info['title']} breakdown JSON now."""

    return system, user


def build_prompt(scores: dict, memory_lines: list[str]) -> tuple[str, str]:
    """
    Kept for backward compatibility - the original single combined
    explanation. No longer called by health_score_service, but left in
    place in case anything else references it.
    """
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