# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops

from ij import IJ
from ij import ImagePlus
from net.imglib2 import FinalInterval
from jarray import zeros
from jarray import array
from net.imglib2.type.numeric.real import FloatType
from net.imglib2.type.numeric.integer import UnsignedShortType
from net.imglib2.type.numeric.integer import UnsignedByteType

from net.imglib2.type.logic import BitType

from net.imagej.ops.convert import ConvertPixCopy
from net.imglib2.meta import ImgPlus
from net.imglib2.img.display.imagej import ImageJFunctions
from ij.plugin.filter import BackgroundSubtracter
from fiji.plugin.trackmate.detection import DetectionUtils
from net.imagej.ops.threshold import Otsu
from net.imagej.ops.threshold import MaxEntropy
from net.imagej.ops.threshold import Triangle
from net.imagej.ops.threshold import Manual

# gray - gray level dataset
def SpotDetectionGray(gray, data, display, ops, invert):
	
	# get the dimensions
	dimensions2D=array( [gray.dimension(0), gray.dimension(1)], 'l')

	# wrap as ImagePlus
	imp=ImageJFunctions.wrap(gray, "wrapped")

	# create and call background subtractor
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 
	
	# wrap the result of background subtraction as Img and display it
	iplus=ImagePlus("bgs", imp.getProcessor())

#	if (invert==True):
#		iplus.getProcessor().invert()
	
	imgBgs=ImageJFunctions.wrapByte(iplus)
	#display.createDisplay("back_sub", data.create(ImgPlus(imgBgs))) 

	# create the Laplacian of Gaussian filter
	kernel = DetectionUtils.createLoGKernel( 3.0, 2, array([1.0, 1.0], 'd' ) )

	# convert the background subtracted image to 32 bit
	imgBgs32=ImgPlus( ops.create( dimensions2D, FloatType()) )
	ops.convert(imgBgs32, imgBgs, ConvertPixCopy() )
	#display.createDisplay("back_sub 32", data.create(ImgPlus(imgBgs32))) 

	# apply the log filter and display the result
	log=ImgPlus( ops.create( dimensions2D, FloatType()) )
	ops.convolve(log, imgBgs32, kernel)
	#display.createDisplay("log", data.create(ImgPlus(log)))
	
	# apply the threshold operation
	thresholded=ops.run("threshold", ops.create( dimensions2D, BitType()), log, Triangle())

	return ImgPlus(thresholded)

def SpotDetectionRedFromHue(hue, data, ops, display):

	# get the dimensions
	dimensions2D=array( [hue.dimension(0), hue.dimension(1)], 'l')
	
	shift=UnsignedByteType()
	shift.setReal(-50)
	hue_shift=ops.add(hue, shift)
	display.createDisplay("shift", data.create(ImgPlus(hue_shift)))

	#test1=ops.op("otsu", hue_shift)
	manualthreshold=Manual()
	# apply the threshold operation
	thresholded=ops.run("threshold", ops.create( dimensions2D, BitType()), hue_shift, manualthreshold)
	#thresholded=ops.run("threshold", ops.create( dimensions2D, BitType()), hue_shift, Otsu())
	
	return thresholded