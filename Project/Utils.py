# Turn an iterable object containing lists into a single list
def concat(xs):
    return sum((x for x in xs), [])
