import math

def get_difference(expected, actual):
	red = (expected.red - actual.red)**2
	green = (expected.green - actual.green)**2
	blue = (expected.blue - actual.blue)**2
	return math.sqrt(red + green + blue)

def equals(expected, actual, threshold):
	return get_difference(expected, actual) < threshold

class Colour(object):
	def __init__(self, red, green, blue):
		self.red = red
		self.green = green
		self.blue = blue