# Turn an iterable object containing lists into a single list
def concat(iter):
    for lst in iter:
        for x in lst:
            yield x
