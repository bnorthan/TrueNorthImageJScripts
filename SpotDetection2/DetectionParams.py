from ij.measure import Calibration

class DetectionParams(object):
	def __init__(self, pixelWidth, pixelHeight, minSize, maxSize, minCircularity, maxCircularity, redPercentage):
		self.pixelWidth=pixelWidth
		self.pixelHeight=pixelHeight
		self.minSize = minSize
		self.maxSize = maxSize
		self.minCircularity = minCircularity
		self.maxCircularity = maxCircularity
		self.redPercentage = redPercentage
	
	def setCalibration(self, imp):
		calibration=Calibration()
		calibration.pixelWidth=self.pixelWidth
		calibration.pixelHeight=self.pixelHeight
		imp.setCalibration(calibration)