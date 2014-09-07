from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer

from java.lang import Double

def countParticles(imp, roim, minSize, maxSize, minCircularity, maxCircularity):
	# Create a table to store the results
	table = ResultsTable()
	
	# Create the particle analyzer
	pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA|Measurements.MEAN, table, minSize, maxSize, minCircularity, maxCircularity)
	#pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA|Measurements.MEAN, table, 10, Double.POSITIVE_INFINITY, 0.5, 1.0)
	#pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA|Measurements.MEAN, table, 5, 6, 0.5, 1.0)
	pa.setRoiManager(roim)
	pa.setHideOutputImage(True)

	if pa.analyze(imp):
		print "All ok"
	else:
 		print "There was a problem in analyzing", blobs

 	areas = table.getColumn(0)
	intensities = table.getColumn(1)

	if ( (areas!=None) and (intensities!=None)):
 		for area, intensity in zip(areas,intensities): print str(area)+": "+str(intensity)

def filterParticles(imp, roiArray, threshold) :
 	newRoiList=[]
 	for roi in roiArray:
 		imp.setRoi(roi)
		stats = imp.getStatistics(Measurements.MEAN)
		if stats.mean > threshold:
			newRoiList.append(roi)
	#	print str(stats.mean)+": "+str(stats.histogram[200])
	return newRoiList

def filterParticlesWithFunction(imp, roiArray, function):
	newRoiList=[]
	for roi in roiArray:
 		imp.setRoi(roi)
		
		if (function(imp, roi)==True):
			newRoiList.append(roi)
	return newRoiList
	
def filterParticlesOutsideRange(imp, roiArray, lowerthreshold, upperthreshold) :
 	newRoiList=[]
 	for roi in roiArray:
 		imp.setRoi(roi)
		stats = imp.getStatistics(Measurements.MEAN | Measurements.MIN_MAX)
		if (stats.min < lowerthreshold)  or  (stats.max > upperthreshold):
			newRoiList.append(roi)
	return newRoiList

def calculateParticleStats(A, B, redMask, roiArray):
	areas=[]
	ALevel=[]
	BLevel=[]
	redPercentage=[]

	for roi in roiArray:
		A.setRoi(roi)
		stats = A.getStatistics()
		areas.append(stats.area)
		ALevel.append(stats.mean)
		B.setRoi(roi)
		stats=B.getStatistics()
		BLevel.append(stats.mean)
		redMask.setRoi(roi)
		stats=redMask.getStatistics()
		redPercentage.append(stats.mean)
		
	statsdict={}
	statsdict['Areas']=areas
	statsdict['ALevel']=ALevel
	statsdict['BLevel']=BLevel
	statsdict['redPercentage']=redPercentage

	return statsdict

