from ij.measure import ResultsTable
from ij.measure import Measurements
from ij.plugin.frame import RoiManager
from ij.plugin.filter import ParticleAnalyzer

from java.lang import Double

def countParticles(imp, roim):
	# Create a table to store the results
	table = ResultsTable()
	
	# Create the particle analyzer
	pa = ParticleAnalyzer(ParticleAnalyzer.ADD_TO_MANAGER, Measurements.AREA|Measurements.MEAN, table, 0, Double.POSITIVE_INFINITY, 0.5, 1.0)
	pa.setRoiManager(roim)
	pa.setHideOutputImage(True)

	if pa.analyze(imp):
		print "All ok"
	else:
 		print "There was a problem in analyzing", blobs

 	areas = table.getColumn(0)
	intensities = table.getColumn(1)
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

def accumulateInROI(roi, func, imp):
	mask = roi.getMask()
	ip = imp.getProcessor() 
	r = roi.getBounds()
	summ =  0
	for y in range(r.height):
		for x in range(r.width):
			if mask.get(x,y)!=0: 
				total+=1
				summ+= ip.getf(r.x+x,r.y+y)
