# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops

from ij import IJ
from ij import ImagePlus
from ij import Prefs
from net.imglib2 import FinalInterval
from jarray import zeros
from jarray import array
from net.imglib2.type.numeric.real import FloatType
from net.imglib2.type.numeric.integer import UnsignedShortType
from net.imglib2.type.logic import BitType
from ij.plugin.frame import RoiManager;
from ij.gui import Roi

from net.imagej.ops.convert import ConvertPixCopy
from net.imglib2.meta import ImgPlus
from net.imglib2.img.display.imagej import ImageJFunctions
from ij.plugin.filter import BackgroundSubtracter
from fiji.plugin.trackmate.detection import DetectionUtils
from ij.plugin import Duplicator

import os
import sys

homedir=IJ.getDirectory('imagej')
jythondir=os.path.join(homedir,'macros/Evalulab/')
jythondir=os.path.abspath(jythondir)
sys.path.append(jythondir)

import Utility
reload(Utility)

import CountParticles
reload(CountParticles)
from CountParticles import countParticles

#dataset=data.open(inputDirectory+inputName)
#display.createDisplay(dataset.getName(), dataset)
inputImp=IJ.getImage()
inputDataset=Utility.getDatasetByName(data, inputImp.getTitle())

truecolor1=Duplicator().run(inputImp)
truecolor1.show()

# get the roi that will be processed
inputRoi=inputImp.getRoi().clone()

inputRec = inputRoi.getBounds()
x1=long(inputRec.getX())
y1=long(inputRec.getY())
x2=x1+long(inputRec.getWidth())-1
y2=y1+long(inputRec.getHeight())-1

print str(x1)+" "+str(y1)+" "+str(x2)+" "+str(y2)

# crop the roi
interval=FinalInterval( array([x1, y1 ,0], 'l'), array([x2, y2, 2], 'l') )
cropped=ops.crop(interval, None, inputDataset.getImgPlus() ) 
	
dataset=data.create(cropped)
display.createDisplay("cropped", dataset)
	
dimensions2D=array( [dataset.dimension(0), dataset.dimension(1)], 'l')
cropIntervalBlue=FinalInterval( array([0,0,2], 'l'), array([dataset.dimension(0)-1,dataset.dimension(1)-1,2],'l') )
blue=ops.crop(cropIntervalBlue, None, dataset.getImgPlus() ) 

display.createDisplay("blue", data.create(blue))

# wrap as ImagePlus
imp=IJ.getImage()
#imp=ImageJFunctions.wrap(blue, "wrapped")

# create and call background subtractor
bgs=BackgroundSubtracter()
bgs.rollingBallBackground(imp.getProcessor(), 20.0, False, True, True, True, True) 

imp.getProcessor().invert()
imp.show()

print imp

# wrap as Img and display
#iplus=ImagePlus("bgs", imp.getProcessor())
imgBgs=ImageJFunctions.wrapByte(imp)


kernel = DetectionUtils.createLoGKernel( 2.0, 2, array([1.0, 1.0], 'd' ) )

factory=cropped.getImg().factory()

bgs32=ImgPlus( ops.run("createimg", factory, FloatType(), dimensions2D) )
ops.convert(bgs32, imgBgs, ConvertPixCopy() )

#run("createimg", factory, FloatType(), dimensions2D)
log = ops.convolve(ops.run("createimg", factory, FloatType(), dimensions2D), bgs32, kernel)
display.createDisplay("log", data.create(ImgPlus(log)))

otsu=ops.otsu(imgBgs);
display.createDisplay("thresholded", data.create(ImgPlus(otsu)))
imp=IJ.getImage()

#Utility.clearOutsideRoi(imp, clone)
IJ.run(imp, "Auto Local Threshold", "method=MidGrey radius=15 parameter_1=0 parameter_2=0 white");
IJ.run(imp, "Fill Holes", "");
IJ.run(imp, "Close-", "");
IJ.run(imp, "Watershed", "");
IJ.run(imp, "Erode", "");
IJ.run(imp, "Dilate", "");

imp.updateAndDraw()

# create a hidden roi manager
roim = RoiManager(True)
	
# count the particles
countParticles(imp, roim, 10, 400, 0.3, 1.0)

[truecolor1.getProcessor().draw(roi) for roi in roim.getRoisAsArray()]
truecolor1.updateAndDraw()
	
#Prefs.blackBackground = False;
#IJ.run("Make Binary", "");

#IJ.run("LoG 3D");

#IJ.run("Duplicate...", "title="+"test")
#IJ.run("RGB Stack");
#IJ.run("Convert Stack to Images");