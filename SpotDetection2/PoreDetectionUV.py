from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.gui import Roi
from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij.process import ImageProcessor
from ij.plugin.frame import RoiManager;
from ij.measure import Measurements
from ij.plugin.filter import Analyzer
from ij.gui import Overlay
from ij.plugin import ImageCalculator
from ij.plugin import Duplicator
from ij.plugin import ChannelSplitter
from ij.plugin import SubstackMaker

from net.imglib2 import FinalInterval
from jarray import array
import sys
from net.imglib2.meta import ImgPlus
from net.imglib2.img.display.imagej import ImageJFunctions
from net.imglib2.type.numeric.integer import UnsignedByteType
from java.awt import Color

import os
import copy

homedir=IJ.getDirectory('imagej')
jythondir=os.path.join(homedir,'macros/Evalulab/')
jythondir=os.path.abspath(jythondir)
sys.path.append(jythondir)

import SpotDetectionFunction
reload(SpotDetectionFunction)
from SpotDetectionFunction import SpotDetectionGray

import CountParticles
reload(CountParticles)
from CountParticles import countParticles

import ExportDataFunction
reload(ExportDataFunction)
from ExportDataFunction import exportToCsv

import Utility
reload(Utility)

import DetectionParams
reload(DetectionParams)
from DetectionParams import DetectionParams 

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

def runPoreDetection(inputImp, data, ops, display):

	# in this step get the image in the "imagej2" dataset format
	# this way we can take advantage of some of the new imagej2 functionality
	name=inputImp.getTitle()	
	inputDataset=Utility.getDatasetByName(data, name)

	# this structure keeps track of detection parameters
	detectionParameters=DetectionParams()

	roi=inputImp.getRoi()

	if (roi is None):
		message=name+": "+Messages.NoRoi
		IJ.write(message)
		return

	roi=inputImp.getRoi().clone();

	roilist, statslist, statsheader=poreDetectionUV(inputImp, inputDataset, roi, ops, data, display, detectionParameters)

	directory, overlayname, roiname=Utility.createImageNames(inputImp)
	
	# name of file to save summary stats 
	statsname=os.path.join(directory, 'stats.csv')
	
	# save the image with overlay
	IJ.save(inputImp, overlayname);
	
	# save the roi 
	IJ.saveAs(inputImp, "Selection", roiname);

	statsheader.insert(0,Messages.FileName)
	statslist.insert(0,name)

	ExportDataFunction.exportSummaryStats(statsname, statsheader, statslist)

	print statsname
	print statsheader
	print statslist

def drawRoi(processor, roi, color):
	processor.setColor(color)
	processor.draw(roi)

def threshold(imp, lower, upper):
	duplicate=Duplicator().run(imp)
	duplicate.getProcessor().resetMinAndMax()
	IJ.setAutoThreshold(duplicate, "Default dark");
	IJ.setThreshold(duplicate, lower, upper)
	IJ.run(duplicate, "Convert to Mask", "");
	return duplicate

def poreDetectionUV(inputImp, inputDataset, inputRoi, ops, data, display, detectionParameters):

	# set calibration
	detectionParameters.setCalibration(inputImp);
	
	# calculate area of roi 
	stats=inputImp.getStatistics()
	inputRoiArea=stats.area
	
	# get the bounding box of the active roi
	inputRec = inputRoi.getBounds()
	x1=long(inputRec.getX())
	y1=long(inputRec.getY())
	x2=x1+long(inputRec.getWidth())-1
	y2=y1+long(inputRec.getHeight())-1
	
	# crop the roi
	interval=FinalInterval( array([x1, y1 ,0], 'l'), array([x2, y2, 2], 'l') )
	cropped=ops.crop(interval, None, inputDataset.getImgPlus() ) 
	
	datacropped=data.create(cropped)
	display.createDisplay("cropped", datacropped)
	croppedPlus=IJ.getImage()
	
	duplicator=Duplicator()
	substackMaker=SubstackMaker()
	
	# duplicate the roi
	duplicate=duplicator.run(croppedPlus)
	
	# convert duplicate of roi to HSB and get brightness
	IJ.run(duplicate, "HSB Stack", "");
	brightnessPlus=substackMaker.makeSubstack(duplicate, "3-3")
	brightness=ImgPlus(ImageJFunctions.wrapByte(brightnessPlus))
	brightnessPlus.setTitle("Brightness")
	
	# make another duplicate, split channels and get red
	duplicate=duplicator.run(croppedPlus)
	channels=ChannelSplitter().split(duplicate)
	redPlus=channels[0]
	red=ImgPlus(ImageJFunctions.wrapByte(redPlus))
	
	# convert to lab
	IJ.run(croppedPlus, "Color Transformer", "colour=Lab")
	IJ.selectWindow('Lab')
	labPlus=IJ.getImage()

	# get the L channel
	#LPlus=substackMaker.makeSubstack(labPlus, "1-1")
	#l=ImgPlus(ImageJFunctions.wrapByte(lPlus))
		
	# get the A channel
	APlus=substackMaker.makeSubstack(labPlus, "2-2")
	APlus.setTitle('A')
	APlus.show()
	APlus.getProcessor().resetMinAndMax()
	APlus.updateAndDraw()
	AThresholded=threshold(APlus, -10, 50)
	
	# get the B channel
	BPlus=substackMaker.makeSubstack(labPlus, "3-3")
	BPlus.setTitle('B')
	BPlus.show()
	BPlus.getProcessor().resetMinAndMax()
	BPlus.updateAndDraw()
	BThresholded=threshold(BPlus, -10, 50)
	
	# AND the Athreshold and Bthreshold to get a map of the red pixels
	ic = ImageCalculator();
	redMask = ic.run("AND create", AThresholded, BThresholded);
	IJ.run(redMask, "Divide...", "value=255");
	
	labPlus.close()
	
	# threshold the spots from the red channel
	thresholdedred=SpotDetectionGray(red, data, display, ops, False, "triangle")
	#display.createDisplay("thresholdedred", data.create(thresholdedred))
	impthresholdedred = ImageJFunctions.wrap(thresholdedred, "wrapped")
	
	# threshold the spots from the brightness channel
	thresholded=SpotDetectionGray(brightness, data, display, ops, False, "triangle")
	impthresholded=ImageJFunctions.wrap(thresholded, "wrapped")
	# or the thresholding results from red and brightness channel
	impthresholded = ic.run("OR create", impthresholded, impthresholdedred);
	
	roim=RoiManager(True)
	
	# convert to mask
	Prefs.blackBackground = True
	IJ.run(impthresholded, "Convert to Mask", "")
	
	def isRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>detectionParameters.porphyrinRedPercentage): return True
		else: return False
	
	def notRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>detectionParameters.porphyrinRedPercentage): return False
		else: return True


	roiClone=inputRoi.clone()
	roiClone.setLocation(0,0)
	Utility.clearOutsideRoi(impthresholded, roiClone)
	
	countParticles(impthresholded, roim, detectionParameters.porphyrinMinSize, detectionParameters.porphyrinMaxSize, \
		detectionParameters.porphyrinMinCircularity, detectionParameters.porphyrinMaxCircularity)

	thresholdedDark=SpotDetectionFunction.SpotDetectionDark(brightnessPlus);

	# clear the region outside the roi
	Utility.clearOutsideRoi(thresholdedDark, roiClone)
 
	roimClosedPores = RoiManager(True)
	detectionParameters.setCalibration(thresholdedDark)
	countParticles(thresholdedDark, roimClosedPores, detectionParameters.closedPoresMinSize, detectionParameters.closedPoresMaxSize, \ 
		detectionParameters.closedPoresMinCircularity, detectionParameters.closedPoresMaxCircularity)
	
	roimOpenPores = RoiManager(True)
	detectionParameters.setCalibration(thresholdedDark)
	countParticles(thresholdedDark, roimOpenPores, detectionParameters.openPoresMinSize, detectionParameters.openPoresMaxSize, \ 
		detectionParameters.openPoresMinCircularity, detectionParameters.openPoresMaxCircularity)
	
	uvPoreList=[]
	openPoresList=[]
	closedPoresList=[]
	
	for roi in roim.getRoisAsArray():
		uvPoreList.append(roi.clone())
	for roi in roimClosedPores.getRoisAsArray():
		closedPoresList.append(roi.clone())
	for roi in roimOpenPores.getRoisAsArray():
		openPoresList.append(roi.clone())

	brightnessPlus.setRoi(roiClone)
	stats=brightnessPlus.getStatistics()
	roiMean=stats.mean
	

	def isDark(imp, roi):
		stats=imp.getStatistics()

		print ""
		print roiMean
		print stats.mean
		
		if (stats.mean<roiMean): return True
		else: return False


	
	openPoresList=CountParticles.filterParticlesWithFunction(brightnessPlus, openPoresList, isDark)
	closedPoresList=CountParticles.filterParticlesWithFunction(brightnessPlus, closedPoresList, isDark)
	print "roiMean"+str(roiMean)
	allList=uvPoreList+closedPoresList+openPoresList
	
	# count particles that are porphyrins (red)
	porphyrinList=CountParticles.filterParticlesWithFunction(redMask, uvPoreList, isRed)
	# count particles that are visible on uv but not porphyrins
	notPorphyrinList=CountParticles.filterParticlesWithFunction(redMask, uvPoreList, notRed)

	# for each roi add the offset such that the roi is positioned in the correct location for the 
	# original image
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in uvPoreList]
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in closedPoresList]
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in openPoresList]

	# draw the ROIs on to the image
	inputImp.getProcessor().setColor(Color.green)
	IJ.run(inputImp, "Line Width...", "line=3");
	inputImp.getProcessor().draw(inputRoi)
	IJ.run(inputImp, "Line Width...", "line=1");
	[CountParticles.drawParticleOnImage(inputImp, roi, Color.magenta) for roi in porphyrinList]
	[CountParticles.drawParticleOnImage(inputImp, roi, Color.green) for roi in notPorphyrinList]	
	[CountParticles.drawParticleOnImage(inputImp, roi, Color.yellow) for roi in closedPoresList]
	[CountParticles.drawParticleOnImage(inputImp, roi, Color.red) for roi in openPoresList]
	inputImp.updateAndDraw()

	# calculate stats for the UV visible particles
	detectionParameters.setCalibration(APlus)
	statsDictUV=CountParticles.calculateParticleStatsUV(APlus, BPlus, redMask, roim.getRoisAsArray())
	
	totalUVPoreArea=0
	for area in statsDictUV['Areas']:
		totalUVPoreArea=totalUVPoreArea+area
	averageUVPoreArea=totalUVPoreArea/len(statsDictUV['Areas'])

	poreDiameter=0
	for diameter in statsDictUV['Diameters']:
		poreDiameter=poreDiameter+diameter
	poreDiameter=poreDiameter/len(statsDictUV['Diameters'])

	redTotal=0
	for red in statsDictUV['redPercentage']:
		redTotal=redTotal+red
	redAverage=redTotal/len(statsDictUV['redPercentage'])
	
	statslist=[len(closedPoresList), len(openPoresList), len(porphyrinList), len(notPorphyrinList), 100*totalUVPoreArea/inputRoiArea, 100*redAverage, averageUVPoreArea, poreDiameter];
	statsheader=[Messages.ClosedPores, Messages.OpenPores, Messages.Porphyrins, Messages.Sebum, Messages.UVPoresFractionalArea, Messages.PercentageRedPixels, Messages.UVPoresAverageArea, Messages.UVPoresAverageDiameter]

	print("Roi Area: "+str(inputRoiArea))
	print("Total Pore Area: "+str(totalUVPoreArea))
	print("Average Pore Area: "+str(averageUVPoreArea))
	
	print str(len(uvPoreList))+" "+str(len(porphyrinList))+" "+str(len(notPorphyrinList))+" "+str(100*totalUVPoreArea/inputRoiArea)+" "+str(100*redAverage)

	print "cp min circularity"+str(detectionParameters.closedPoresMinCircularity)+":"+str(detectionParameters.closedPoresMinSize)
	
	# close images that represent intermediate steps
	APlus.changes=False
	APlus.close()
	BPlus.changes=False
	BPlus.close()
	croppedPlus.changes=False
	croppedPlus.close()
	thresholdedDark.changes=False
	thresholdedDark.close()

	return uvPoreList, statslist, statsheader
