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
from net.imagej.ops.threshold import MaxEntropy
from net.imagej.ops.threshold import Triangle

def SpotDetectionGray(gray, data, display, ops):
	
	# get the dimensions
	dimensions2D=array( [gray.dimension(0), gray.dimension(1)], 'l')

	# convert to 32 bit
	gray32=ImgPlus( ops.create( dimensions2D, FloatType()) )
	ops.convert(gray32, gray, ConvertPixCopy() )
	
	# wrap as ImagePlus
	imp=ImageJFunctions.wrap(gray.getImgPlus(), "wrapped")

	# create and call background subtractor
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 
	
	# wrap the result of background subtraction as Img and display it
	iplus=ImagePlus("bgs", imp.getProcessor())
	imgBgs=ImageJFunctions.wrapByte(iplus)
	display.createDisplay("back_sub", data.create(ImgPlus(imgBgs))) 

	# create the Laplacian of Gaussian filter
	kernel = DetectionUtils.createLoGKernel( 3.0, 2, array([1.0, 1.0], 'd' ) )

	# convert the background subtracted image to 32 bit
	img32=ImgPlus( ops.create( dimensions2D, FloatType()) )
	ops.convert(img32, imgBgs, ConvertPixCopy() )

	# apply the log filter and display the result
	log=ImgPlus( ops.create( dimensions2D, FloatType()) )
	ops.convolve(log, img32, kernel)
	display.createDisplay("log", data.create(ImgPlus(log)))
	
	# apply the threshold operation
	thresholded=ops.run("threshold", ops.create( dimensions2D, BitType()), log, Triangle())
	display.createDisplay("thresholded", data.create(ImgPlus(thresholded)))

	# convert to binary
	IJ.run("Duplicate...", "title=binary.tif");
	Prefs.blackBackground = False;
	IJ.run("Make Binary", "")