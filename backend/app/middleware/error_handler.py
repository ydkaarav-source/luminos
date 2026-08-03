"""
Placeholder module: exception handlers are registered directly via
`app.core.exceptions.register_exception_handlers` in main.py. Kept as
its own module in `middleware/` per the architecture doc in case
request-level error normalization (vs. exception-type handling) is
needed later - e.g. catching non-HTTPException crashes from
background tasks.
"""
