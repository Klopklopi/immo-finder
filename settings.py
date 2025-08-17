
# Load default config or env variables.
try:
    from config import core, filtering, seloger, pap, bienici
    # Make config modules available through settings namespace
    globals().update(locals())
except Exception:
    pass
