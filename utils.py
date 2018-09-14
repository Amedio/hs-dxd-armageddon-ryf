def is_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False