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

inputDirectory='/home/bnorthan/Brian2012/Round2/RogueImageJPlugins/SpotDetection/Images/'
inputName='001-D0_cropped.tif'

dataset=data.open(inputDirectory+inputName)
display.createDisplay(dataset.getName(), dataset)

dimensions2D=array( [dataset.dimension(0), dataset.dimension(1)], 'l')
cropIntervalBlue=FinalInterval( array([0,0,2], 'l'), array([dataset.dimension(0)-1,dataset.dimension(1)-1,0],'l') )

blue=ops.crop(cropIntervalBlue, None, dataset.getImgPlus() ) 

display.createDisplay("blue", data.create(red))

blue32=ImgPlus( ops.create( dimensions2D, FloatType()) )
ops.convert(blue32, blue, ConvertPixCopy() )

# make a copy of the red + green image
copy=blue.copy()
# wrap as ImagePlus
imp=ImageJFunctions.wrap(copy, "wrapped")

# create and call background subtractor
bgs=BackgroundSubtracter()
bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 

# wrap as Img and display
iplus=ImagePlus("bgs", imp.getProcessor())
print type(imp)
imgBgs=ImageJFunctions.wrapFloat(iplus)
display.createDisplay("back_sub", data.create(ImgPlus(imgBgs))) 

kernel = DetectionUtils.createLoGKernel( 2.0, 2, array([1.0, 1.0], 'd' ) )

print type(kernel)
print type(imgBgs)
print type(red32.getImg())

log = ops.convolve(ops.create( dimensions2D, FloatType()), imgBgs, kernel)
display.createDisplay("log", data.create(ImgPlus(log)))

otsu=ops.run("threshold", ops.create( dimensions2D, BitType()), log, Otsu())

display.createDisplay("thresholded", data.create(ImgPlus(otsu)))

Prefs.blackBackground = False;
IJ.run("Make Binary", "");

#IJ.run("LoG 3D");

#IJ.run("Duplicate...", "title="+"test")
#IJ.run("RGB Stack");
#IJ.run("Convert Stack to Images");