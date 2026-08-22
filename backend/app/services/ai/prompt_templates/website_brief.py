from app.services.ai.prompt_templates.shared import SAFETY_GUARDRAILS, format_memory_context


def build_prompt(business_context: dict, plan_context: dict | None, memory_lines: list[str]) -> tuple[str, str]:
    system = f"""{SAFETY_GUARDRAILS}

You are generating a website brief for this business - a recommended
page structure and messaging direction the founder can hand to a
developer or use in a website builder tool. You are NOT writing
website code, and you are NOT building, hosting, or deploying
anything. Respond ONLY with a single JSON object, no preamble, no
markdown fences, matching exactly this shape:

{{
  "title": "string",
  "target_pages": [
    {{"name": "string", "purpose": "string"}}
  ],
  "copy_direction": "string",
  "design_direction": "string"
}}

Recommend page structure and messaging appropriate to this specific
business, not generic advice ("a homepage, an about page, a contact
page" applies to nothing in particular - ground every page and its
purpose in what this business actually sells and who it sells to).

Frame copy_direction as tone and messaging guidance grounded in this
business's real customers and goals - not a guarantee of what will
convert or perform.

Frame design_direction as visual style suggestions in the spirit of a
calm, intelligent, not-generic-AI aesthetic (quiet dark surfaces,
purposeful accent color, restrained motion, no hype-driven visual
noise) - describe it as a direction the founder can hand to a
developer or website builder tool, not a guarantee of outcomes."""

    plan_lines = "No business plan generated yet for this business."
    if plan_context:
        plan_lines = f"""Overview: {plan_context.get('overview')}
Roadmap: {plan_context.get('roadmap')}"""

    user = f"""Business context:
- Industry: {business_context.get('industry')}
- Description: {business_context.get('description')}
- Products/services: {business_context.get('products_services')}
- Target customers: {business_context.get('target_customers')}
- Company goals: {business_context.get('company_goals')}

Most recent business plan for this business:
{plan_lines}

Known context about this founder and business so far:
{format_memory_context(memory_lines)}

Generate the website brief JSON now."""

    return system, user
