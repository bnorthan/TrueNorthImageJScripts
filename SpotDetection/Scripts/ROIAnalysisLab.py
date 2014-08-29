# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops
# @ImageDisplayService ids

from ij import IJ
from ij import Prefs
from ij import WindowManager
from ij.gui import Roi
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
from SpotDetectionFunction import SpotDetectionRedFromHue

import CountParticles
reload(CountParticles)
from CountParticles import countParticles

import ExportDataFunction
reload(ExportDataFunction)
from ExportDataFunction import exportToCsv

def drawRoi(processor, roi, color):
	processor.setColor(color)
	processor.draw(roi)

def clearOutsideRoi(imp, roi):
	imp.setRoi(roi)
	IJ.setBackgroundColor(0, 0, 0);
	IJ.run(impthresholded, "Clear Outside", "");

imagedir=homedir+'/ProprietaryImages/Evalulab/'
truecolor=imagedir+'002/002-R-SD.tif'

inputName='B013-D0-L-UV.jpg'
#roiName='RoiSet.zip'
roiName='roi.roi'
#dataset=data.open(imagedir+inputName)
#display.createDisplay(dataset.getName(), dataset)

inputImp=IJ.getImage()
inputDataset=ids.getActiveDataset()

# get the roi that will be processed
#manager=IJ.openImage(imagedir+roiName);
#rm.runCommand("Open", imagedir+roiName)
inputRoi=inputImp.getRoi()

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

# duplicate the roi
duplicator=Duplicator()
duplicate=duplicator.run(croppedPlus)
#duplicate.show()

# convert duplicate of roi to HSB

IJ.run(duplicate, "Color Transformer", "colour=Lab")
IJ.selectWindow('Lab')
labPlus=IJ.getImage()
substackMaker=SubstackMaker()

brightnessPlus=substackMaker.makeSubstack(labPlus, "1-1")
brightnessPlus.show()
brightnessPlus.setTitle('Lightness')

print type(brightnessPlus)

brightness=ImgPlus(ImageJFunctions.wrapByte(brightnessPlus))
'''brightnessPlus.setTitle("Brightness")
brightnessPlus.show()

huePlus=substackMaker.makeSubstack(duplicate, "2-2")
hue=ImgPlus(ImageJFunctions.wrapByte(huePlus))
huePlus.setTitle("Hue")
huePlus.show()

duplicate=duplicator.run(croppedPlus)
channels=ChannelSplitter().split(duplicate)
# convert roi to HSB
redPlus=channels[0]
red=ImgPlus(ImageJFunctions.wrapByte(redPlus))
redPlus.show()

# threshold the spots from the red channel
thresholdedred=SpotDetectionGray(red, data, display, ops, False)
display.createDisplay("thresholdedred", data.create(thresholdedred))
impthresholdedred = ImageJFunctions.wrap(thresholdedred, "wrapped")

# threshold the spots from the brightness channel
thresholded=SpotDetectionGray(brightness, data, display, ops, False)
display.createDisplay("thresholded", data.create(thresholded))
impthresholded=ImageJFunctions.wrap(thresholded, "wrapped")

# or the thresholding results from red and brightness channel
ic = ImageCalculator();
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

# filter particles using hue
newRoiList=CountParticles.filterParticles(huePlus, roim.getRoisAsArray(),  -10)

print "Total particles: "+str(len(roim.getRoisAsArray()))
print "Filtered particles: "+str(len(newRoiList))

# for each rio add the offset such that the roi is positioned in the correct location for the 
# original image
[roi.setLocation(roi.getXBase()+x1, roi.getYBase()+y1) for roi in newRoiList]

overlay=Overlay()

overlay.add(inputRoi)
[overlay.add(roi) for roi in newRoiList]

# draw overlay
inputImp.setOverlay(overlay)
inputImp.updateAndDraw()

exportToCsv(imagedir+'best.csv', newRoiList)'''





