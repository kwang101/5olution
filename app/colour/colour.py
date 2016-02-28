import math

registered_colours = []
max_rgb_diff = 25

def get_difference(expected, actual):
    red = (expected.red - actual.red)**2
    green = (expected.green - actual.green)**2
    blue = (expected.blue - actual.blue)**2
    return math.sqrt(red + green + blue)

def equals(expected, actual):
    return get_difference(expected, actual) < max_rgb_diff

class Colour(object):
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue