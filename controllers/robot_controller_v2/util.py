from math import floor
def is_close(value, target, delta=0.1):
    return target-delta < value < target + delta

def normalize_degree(degree):
    width = 360
    return (degree - (floor(degree / width) * width))
