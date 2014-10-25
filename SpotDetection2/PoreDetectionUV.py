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

import Constants
reload(Constants)
from Constants import Constants

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

def runPoreDetection(inputImp, data, ops, display):
	
	name=inputImp.getTitle()	
	inputDataset=Utility.getDatasetByName(data, name)
	
	detectionParameters=DetectionParams(Constants.pixelWidth, Constants.pixelHeight, Constants.smallestObject, Constants.largestObject, 0.5, 1.0, 0.3)

	roi=inputImp.getRoi()

	if (roi is None):
		message=name+": "+Messages.NoRoi
		IJ.write(message)
		return

	roi=inputImp.getRoi().clone();

	roilist, statslist, statsdict, statsheader=poreDetectionUV(inputImp, inputDataset, roi, ops, data, display, detectionParameters)

	directory=inputImp.getOriginalFileInfo().directory
	name=os.path.splitext(inputImp.getTitle())[0];

	# name of file to save image with overlay	
	overlaydir=os.path.join(directory, 'overlay')
	print "overlaydir: "+overlaydir
	print "directory: "+directory
	
	if not os.path.exists(overlaydir):
		os.makedirs(overlaydir)
	overlayname=os.path.join(overlaydir, name+'_overlay.tif')
	
	# name of file to save roi 
	roidir=os.path.join(directory, 'roi')
	if not os.path.exists(roidir):
		os.makedirs(roidir)
	roiname=os.path.join(roidir, name+'.roi')
	print "roidir: "+roidir

	print "directory: "+directory
	# name of file to save summary stats 
	statsname=os.path.join(directory, 'stats.csv')
	
	# save the image with overlay
	IJ.save(inputImp, overlayname);
	
	# save the roi 
	IJ.saveAs(inputImp, "Selection", roiname);

	statsheader.insert(0,Messages.FileName)
	statslist.insert(0,name)

	#ExportDataFunction.exportUVStats(roistatsname, statsdict)
	ExportDataFunction.exportSummaryStats(statsname, statsheader, statslist)

	print statsname

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
	
	title =  inputImp.getTitle()
	title=title.replace('UV', 'SD')
	
	print title
	
	# calculate area of roi 
	stats=inputImp.getStatistics()
	inputRoiArea=stats.area
	
	print inputRoi
	
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
	#duplicate.show()
	
	# convert duplicate of roi to HSB and get brightness
	IJ.run(duplicate, "HSB Stack", "");
	brightnessPlus=substackMaker.makeSubstack(duplicate, "3-3")
	brightness=ImgPlus(ImageJFunctions.wrapByte(brightnessPlus))
	brightnessPlus.setTitle("Brightness")
	#brightnessPlus.show()
	
	# make another duplicate, split channels and get red
	duplicate=duplicator.run(croppedPlus)
	channels=ChannelSplitter().split(duplicate)
	redPlus=channels[0]
	red=ImgPlus(ImageJFunctions.wrapByte(redPlus))
	#redPlus.show()
	
	# convert to lab
	IJ.run(croppedPlus, "Color Transformer", "colour=Lab")
	IJ.selectWindow('Lab')
	labPlus=IJ.getImage()
	
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
	#redMask.show()
	
	labPlus.close()
	
	# threshold the spots from the red channel
	thresholdedred=SpotDetectionGray(red, data, display, ops, False, "triangle")
	#display.createDisplay("thresholdedred", data.create(thresholdedred))
	impthresholdedred = ImageJFunctions.wrap(thresholdedred, "wrapped")
	
	# threshold the spots from the brightness channel
	thresholded=SpotDetectionGray(brightness, data, display, ops, False, "triangle")
	#display.createDisplay("thresholded", data.create(thresholded))
	impthresholded=ImageJFunctions.wrap(thresholded, "wrapped")

	duplicate=duplicator.run(brightnessPlus);
	duplicate.show()
	thresholdedDark=SpotDetectionFunction.SpotDetectionDark(duplicate);
	
	# or the thresholding results from red and brightness channel
	impthresholded = ic.run("OR create", impthresholded, impthresholdedred);
	
	# convert to mask
	Prefs.blackBackground = True
	IJ.run(impthresholded, "Convert to Mask", "")
	
	# clear the region outside the roi
	clone=inputRoi.clone()
	clone.setLocation(0,0)
	Utility.clearOutsideRoi(impthresholded, clone)
	
	# create a hidden roi manager
	roim = RoiManager(True)
	detectionParameters.setCalibration(impthresholded)
	# count the particlesimp.getProcessor().setColor(Color.green)
	countParticles(impthresholded, roim, detectionParameters.minSize, detectionParameters.maxSize, detectionParameters.minCircularity, detectionParameters.maxCircularity)
	
	roim2 = RoiManager(True)
	detectionParameters.setCalibration(thresholdedDark)
	# count the particlesimp.getProcessor().setColor(Color.green)
	countParticles(thresholdedDark, roim2, 10, 100000, 0.2, 1.0)
	
	# define a function to determine the percentage of pixels that are foreground in a binary image
	# inputs:
	#    imp: binary image, 0=background, 1=foreground
	#    roi: an roi
	def isRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>detectionParameters.redPercentage): return True
		else: return False
	
	def notRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>detectionParameters.redPercentage): return False
		else: return True

	allList=[]
	darkList=[]

	for roi in roim.getRoisAsArray():
		allList.append(roi.clone())

	for roi in roim2.getRoisAsArray():
		darkList.append(roi.clone())
	

	
	# count particles that are red
	redList=CountParticles.filterParticlesWithFunction(redMask, allList, isRed)
	# count particles that are red
	blueList=CountParticles.filterParticlesWithFunction(redMask, allList, notRed)

	print "Total particles: "+str(len(allList))
	print "Filtered particles: "+str(len(redList))

	
	# for each roi add the offset such that the roi is positioned in the correct location for the 
	# original image
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in allList]
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in darkList]
	# create an overlay and add the rois
	overlay1=Overlay()
	inputRoi.setStrokeColor(Color.green)
	overlay1.add(inputRoi)
	[CountParticles.addParticleToOverlay(roi, overlay1, Color.red) for roi in redList]
	[CountParticles.addParticleToOverlay(roi, overlay1, Color.cyan) for roi in blueList]
	def drawAllRoisOnImage(imp, mainRoi, redList, blueList):
		imp.getProcessor().setColor(Color.green)
		IJ.run(imp, "Line Width...", "line=3");
		imp.getProcessor().draw(inputRoi)
		imp.updateAndDraw()
		IJ.run(imp, "Line Width...", "line=1");
		[CountParticles.drawParticleOnImage(imp, roi, Color.magenta) for roi in redList]
		[CountParticles.drawParticleOnImage(imp, roi, Color.green) for roi in blueList]
		imp.updateAndDraw()
	
	drawAllRoisOnImage(inputImp, inputRoi, redList, blueList)
	[CountParticles.drawParticleOnImage(inputImp, roi, Color.yellow) for roi in darkList]
	inputImp.updateAndDraw()
	#drawAllRoisOnImage(trueColorImp, inputRoi, redList, blueList)
	
	# draw overlay
	# inputImp.setOverlay(overlay1)
	# inputImp.updateAndDraw()
	
	#inputImp.setProperty("pixel_width", "0.5")
	#inputImp.setProperty("pixel_height", "0.5")
	#IJ.run(APlus, "Properties...", "channels=1 slices=1 frames=1 unit=inch pixel_width=0.25 pixel_height=0.25 voxel_depth=10");
	
	'''calibration=Calibration()
	calibration.pixelWidth=100.0
	calibration.pixelHeight=100.0
	APlus.setCalibration(calibration)'''

	detectionParameters.setCalibration(APlus)
	
	statsdict=CountParticles.calculateParticleStatsUV(APlus, BPlus, redMask, roim.getRoisAsArray())
	
	print inputRoiArea

	areas=statsdict['Areas']
	poreArea=0
	for area in areas:
		poreArea=poreArea+area
	poreArea=poreArea/len(areas)

	diameters=statsdict['Diameters']
	poreDiameter=0
	for diameter in diameters:
		poreDiameter=poreDiameter+diameter
	poreDiameter=poreDiameter/len(diameters)

	ATotal=0
	ALevels=statsdict['ALevel']
	for A in ALevels:
		ATotal=ATotal+A

	AAverage=ATotal/len(ALevels)

	BTotal=0
	BLevels=statsdict['BLevel']
	for B in BLevels:
		BTotal=BTotal+B

	BAverage=BTotal/len(BLevels)

	redTotal=0
	redPercentages=statsdict['redPercentage']
	for red in redPercentages:
		redTotal=redTotal+red

	redAverage=redTotal/len(redPercentages)
	pixwidth=inputImp.getCalibration().pixelWidth

	inputRoiArea=inputRoiArea/(pixwidth*pixwidth)

	statslist=[len(allList), len(redList), len(blueList), 100*poreArea/inputRoiArea, 100*redAverage, poreArea, poreDiameter];
	statsheader=[Messages.TotalDetectedPores, Messages.Porphyrins, Messages.NoPorphyrins, Messages.PoresFractionalArea, Messages.PercentageRedPixels, Messages.AveragePoresArea, Messages.AveragePoresDiameter]

	print str(len(allList))+" "+str(len(redList))+" "+str(len(blueList))+" "+str(100*poreArea/inputRoiArea)+" "+str(100*redAverage)

	# close images that represent intermediate steps
	APlus.changes=False
	APlus.close()
	BPlus.changes=False
	BPlus.close()
	croppedPlus.changes=False
	croppedPlus.close()

	return allList, statslist, statsdict, statsheader


	