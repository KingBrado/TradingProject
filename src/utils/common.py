def chunk(lst: list, size: int):
    """
    Common chunking function
    """
    for i in range(0, len(lst), size):
        yield lst[i : i + size]
