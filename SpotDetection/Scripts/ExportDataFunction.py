
import csv

def exportToCsv(name, roiList):
	myFile = open(name, 'w')
	writer = csv.writer(myFile, delimiter=',')
	[writer.writerow([roi.getXBase(), roi.getYBase()]) for roi in roiList]

	myFile.flush()
	myFile.close()
