# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops
# @ImageDisplayService ids

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

homedir='/home/bnorthan/Brian2014/Projects/ImageJScriptingProjects/'
jythondir=homedir+'TrueNorthImageJScripts/SpotDetection/Scripts/'
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

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

import GuiFunction
reload(GuiFunction)

def drawRoi(processor, roi, color):
	processor.setColor(color)
	processor.draw(roi)

def clearOutsideRoi(imp, roi):
	imp.setRoi(roi)
	IJ.setBackgroundColor(0, 0, 0);
	IJ.run(imp, "Clear Outside", "");

def threshold(imp, lower, upper):
	duplicator=Duplicator()
	duplicate=duplicator.run(imp)
	duplicate.getProcessor().resetMinAndMax()
	IJ.setAutoThreshold(duplicate, "Default dark");
	IJ.setThreshold(duplicate, lower, upper)
	IJ.run(duplicate, "Convert to Mask", "");
	return duplicate


def roiAnalysis():
	imageList=GuiFunction.GetOpenImageList()

	GuiFunction.printDatasets(data)

	print ""
	for s in imageList:
		print s

	nbgd=NonBlockingGenericDialog(Messages.AddRoi)
	nbgd.addMessage(Messages.PositionRoiAndPressOK)
	                              
	if (imageList==None):
		IJ.showMessage(Messages.noOpenImages)
		return;
		
	nbgd.addChoice("Image1:", imageList, imageList[0]);
	nbgd.showDialog()

	name = nbgd.getNextChoice()

	inputImp = WindowManager.getImage(name)
	inputDataset=GuiFunction.getDatasetByName(data, name)

	print "input is: "+inputDataset.getName()
	
	#inputImp=IJ.getImage()
	#inputDataset=ids.getActiveDataset()
	
	title =  inputImp.getTitle()
	title=title.replace('UV', 'SD')
	
	print title
	
	#trueColorImp= WindowManager.getImage(title)
	#print type( trueColorImp)
	
	# get the roi that will be processed
	inputRoi=inputImp.getRoi().clone()
	
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
	thresholdedred=SpotDetectionGray(red, data, display, ops, False)
	display.createDisplay("thresholdedred", data.create(thresholdedred))
	impthresholdedred = ImageJFunctions.wrap(thresholdedred, "wrapped")
	
	# threshold the spots from the brightness channel
	thresholded=SpotDetectionGray(brightness, data, display, ops, False)
	display.createDisplay("thresholded", data.create(thresholded))
	impthresholded=ImageJFunctions.wrap(thresholded, "wrapped")
	
	# or the thresholding results from red and brightness channel
	impthresholded = ic.run("OR create", impthresholded, impthresholdedred);
	
	# convert to mask
	Prefs.blackBackground = True
	IJ.run(impthresholded, "Convert to Mask", "")
	
	# clear the region outside the roi
	clone=inputRoi.clone()
	clone.setLocation(0,0)
	clearOutsideRoi(impthresholded, clone)
	
	# create a hidden roi manager
	roim = RoiManager(True)
	
	# count the particles
	countParticles(impthresholded, roim)
	
	allList=roim.getRoisAsArray()
	
	# define a function to determine the percentage of pixels that are foreground in a binary image
	# inputs:
	#    imp: binary image, 0=background, 1=foreground
	#    roi: an roi
	def isRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>0.2): return True
		else: return False
	
	def notRed(imp, roi):
		stats = imp.getStatistics()
	
		if (stats.mean>0.2): return False
		else: return True
	
	# count particles that are red
	redList=CountParticles.filterParticlesWithFunction(redMask, roim.getRoisAsArray(), isRed)
	# count particles that are red
	blueList=CountParticles.filterParticlesWithFunction(redMask, roim.getRoisAsArray(), notRed)
	
	print "Total particles: "+str(len(allList))
	print "Filtered particles: "+str(len(redList))
	
	# for each rio add the offset such that the roi is positioned in the correct location for the 
	# original image
	[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in allList]
	
	# create an overlay and add the rois
	overlay1=Overlay()
	
	def addParticleToOverlay(roi, overlay, color):
		roi.setStrokeColor(color)
		overlay.add(roi)
	
	def drawParticleOnImage(imp, roi, color):
		imp.getProcessor().setColor(color)
		imp.getProcessor().draw(roi)
	
	inputRoi.setStrokeColor(Color.green)
	overlay1.add(inputRoi)
	[addParticleToOverlay(roi, overlay1, Color.red) for roi in redList]
	[addParticleToOverlay(roi, overlay1, Color.cyan) for roi in blueList]
	
	def drawAllRoisOnImage(imp, mainRoi, redList, blueList):
		imp.getProcessor().setColor(Color.green)
		IJ.run(imp, "Line Width...", "line=3");
		imp.getProcessor().draw(inputRoi)
		imp.updateAndDraw()
		IJ.run(imp, "Line Width...", "line=1");
		[drawParticleOnImage(imp, roi, Color.magenta) for roi in redList]
		[drawParticleOnImage(imp, roi, Color.green) for roi in blueList]
		imp.updateAndDraw()
	
	drawAllRoisOnImage(inputImp, inputRoi, redList, blueList)
	#drawAllRoisOnImage(trueColorImp, inputRoi, redList, blueList)
	
	# draw overlay
	#inputImp.setOverlay(overlay1)
	#inputImp.updateAndDraw()
	
	#exportToCsv(imagedir+'best.csv', redList)


if __name__ == '__main__':
	roiAnalysis()
	
	
	
	
