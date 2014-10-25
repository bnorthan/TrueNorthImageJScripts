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
from ij.plugin.filter import BackgroundSubtracter

import os
import copy

homedir=IJ.getDirectory('imagej')
jythondir=os.path.join(homedir,'macros/Evalulab/')
jythondir=os.path.abspath(jythondir)
sys.path.append(jythondir)

import SpotDetectionFunction
reload(SpotDetectionFunction)
from SpotDetectionFunction import SpotDetectionGray2

import CountParticles
reload(CountParticles)
from CountParticles import countParticles

import ExportDataFunction
reload(ExportDataFunction)
from ExportDataFunction import exportToCsv

import Utility
reload(Utility)

class DetectionParameters():
    def __init__(self, minSize, maxSize, minCircularity, maxCircularity, redPercentage):
        self.minSize = minSize
        self.maxSize = maxSize
        self.minCircularity = minCircularity
        self.maxCircularity = maxCircularity
        self.redPercentage = redPercentage

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

def poreDetectionTrueColor(inputImp, inputDataset, inputRoi, ops, data, display, detectionParameters):
	
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
	
	IJ.run(duplicate, "RGB Stack", "")
	bluePlus=substackMaker.makeSubstack(duplicate, "3-3")
	blue=ImgPlus(ImageJFunctions.wrapByte(bluePlus))
	bluePlus.setTitle("Blue")
	bluePlus.show()
	imp=IJ.getImage()

	bluePlus=duplicator.run(bluePlus)
	# threshold the spots from the blue channel
	#thresholded=SpotDetectionGray2(blue, data, display, ops, True, "percentile", True)
	#display.createDisplay("thresholded", data.create(thresholded))
	#impthresholded = ImageJFunctions.wrap(thresholded, "wrapped")

	# if looking for dark spots invert the image
	imp.getProcessor().invert()

	# subtract background
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 

	# operate on a duplicate
	imp=duplicator.run(imp)

	# run midGrey autothreshold
	IJ.run(imp, "Auto Local Threshold", "method=MidGrey radius=15 parameter_1=0 parameter_2=0 white");
	imp.updateAndDraw()
	IJ.run(imp, "Convert to Mask", "")

	impthresholded=imp
	
	# convert to mask
	Prefs.blackBackground = True
	IJ.run(imp, "Convert to Mask", "")
	
	# clear the region outside the roi
	clone=inputRoi.clone()
	clone.setLocation(0,0)
	Utility.clearOutsideRoi(imp, clone)
	
	# create a hidden roi manager
	roim = RoiManager(True)
	
	# count the particles
	countParticles(imp, roim, detectionParameters.minSize, detectionParameters.maxSize, detectionParameters.minCircularity, detectionParameters.maxCircularity)
	
	# create a list containing all particles
	allList=[]
	for roi in roim.getRoisAsArray():
		allList.append(roi.clone())
	
	# calculate the stats
	statsDict=CountParticles.calculateParticleStats(bluePlus, allList)

	areas=statsDict['Areas']
	poreArea=0
	for area in areas:
		poreArea=poreArea+area

	poreArea=poreArea/len(areas)
		
	intensity=0
	intensities=statsDict['Intensity']
	for intens in intensities:
		intensity=intensity+intens

	intensity=intensity/len(intensities)

	print "Total particles: "+str(len(allList))+ " area: "+str(poreArea)+" intensity: "+str(intensity)
	
	# for each roi add the offset such that the roi is positioned in the correct location for the 
	# original image
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in allList]
	
	# create an overlay and add the rois
	overlay1=Overlay()
		
	inputRoi.setStrokeColor(Color.green)
	overlay1.add(inputRoi)
	[CountParticles.addParticleToOverlay(roi, overlay1, Color.cyan) for roi in allList]
	
	def drawAllRoisOnImage(imp, mainRoi, allList):
		imp.getProcessor().setColor(Color.green)
		IJ.run(imp, "Line Width...", "line=3");
		imp.getProcessor().draw(inputRoi)
		imp.updateAndDraw()
		IJ.run(imp, "Line Width...", "line=1");
		[CountParticles.drawParticleOnImage(imp, roi, Color.magenta) for roi in allList]
		imp.updateAndDraw()
	
	drawAllRoisOnImage(inputImp, inputRoi, allList)
	
	'''