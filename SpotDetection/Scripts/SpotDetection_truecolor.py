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

from net.imagej.ops.convert import ConvertPixCopy
from net.imglib2.meta import ImgPlus
from net.imglib2.img.display.imagej import ImageJFunctions
from ij.plugin.filter import BackgroundSubtracter
from fiji.plugin.trackmate.detection import DetectionUtils
from net.imagej.ops.threshold import Otsu
from net.imagej.ops.threshold import Triangle
from net.imagej.ops.threshold import MaxEntropy

import sys

homedir='/home/bnorthan/Brian2012/Round2/ImageJScriptingProjects/'
#homedir='/home/bnorthan/Brian2014/Projects/ImageJScriptingProjects/'
jythondir=homedir+'TrueNorthImageJScripts/SpotDetection/Scripts/'
roiname=homedir+'ProprietaryImages/Evalulab/Rois/Right.roi'
sys.path.append(jythondir)

import GuiFunction
reload(GuiFunction)

inputDirectory='/home/bnorthan/Brian2012/Round2/RogueImageJPlugins/SpotDetection/Images/'
inputName='001-D0_cropped.tif'

#dataset=data.open(inputDirectory+inputName)
#display.createDisplay(dataset.getName(), dataset)
inputImp=IJ.getImage()
inputDataset=GuiFunction.getDatasetByName(data, inputImp.getTitle())

# get the roi that will be processed
inputRoi=inputImp.getRoi().clone()

inputRec = inputRoi.getBounds()
x1=long(inputRec.getX())
y1=long(inputRec.getY())
x2=x1+long(inputRec.getWidth())-1
y2=y1+long(inputRec.getHeight())-1

# crop the roi
interval=FinalInterval( array([x1, y1 ,0], 'l'), array([x2, y2, 2], 'l') )
cropped=ops.crop(interval, None, inputDataset.getImgPlus() ) 
	
dataset=data.create(cropped)
display.createDisplay("cropped", dataset)
	
dimensions2D=array( [dataset.dimension(0), dataset.dimension(1)], 'l')
cropIntervalBlue=FinalInterval( array([0,0,2], 'l'), array([dataset.dimension(0)-1,dataset.dimension(1)-1,2],'l') )
blue=ops.crop(cropIntervalBlue, None, dataset.getImgPlus() ) 

display.createDisplay("blue", data.create(blue))

blue32=ImgPlus( ops.create( dimensions2D, FloatType()) )
ops.convert(blue32, blue, ConvertPixCopy() )

# make a copy of the red + green image
copy=blue32.copy()
# wrap as ImagePlus
imp=ImageJFunctions.wrap(copy, "wrapped")
imp.getProcessor().invert()

# create and call background subtractor
bgs=BackgroundSubtracter()
bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 

print imp

# wrap as Img and display
iplus=ImagePlus("bgs", imp.getProcessor())
imgBgs=ImageJFunctions.wrapFloat(iplus)
print iplus
print imgBgs

display.createDisplay("back_sub", data.create(ImgPlus(imgBgs))) 

kernel = DetectionUtils.createLoGKernel( 2.0, 2, array([1.0, 1.0], 'd' ) )

print type(kernel)
print type(imgBgs)
print type(blue32.getImg())

log = ops.convolve(ops.create( dimensions2D, FloatType()), imgBgs, kernel)
display.createDisplay("log", data.create(ImgPlus(log)))

otsu=ops.run("threshold", ops.create( dimensions2D, BitType()), log, Triangle())

display.createDisplay("thresholded", data.create(ImgPlus(otsu)))

Prefs.blackBackground = False;
IJ.run("Make Binary", "");

#IJ.run("LoG 3D");

#IJ.run("Duplicate...", "title="+"test")
#IJ.run("RGB Stack");
#IJ.run("Convert Stack to Images");