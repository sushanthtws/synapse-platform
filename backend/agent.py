# DEPRECATED MODULE
# Kept only for future experiments or fallback pipelines

def extract_skill(*args, **kwargs):
    """
    This function is deprecated.
    Use backend.refiner.refine_skill instead.
    """
    raise NotImplementedError(
        "extract_skill is deprecated. Use refine_skill() instead."
    )