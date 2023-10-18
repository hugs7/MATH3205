# Intersection of a collection of sets
def intersection(iter):
    """
    Determine the intersection of a collection of sets. The collection may be
    any iterable
    """
    ret = None # can't pick an identity because we don't know the universal set
    for s in iter:
        if ret is None:
            ret = s
        else:
            ret &= s
    return ret
