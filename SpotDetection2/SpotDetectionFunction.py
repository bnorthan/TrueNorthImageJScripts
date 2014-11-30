
from ij import Prefs
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
from ij.plugin import Duplicator

# spot detection routine for gray scale data.  Detects light objects
def SpotDetectionGray(gray, data, display, ops, invert, thresholdmethod, showSteps=False):
	
	# get the dimensions
	dimensions2D=array( [gray.dimension(0), gray.dimension(1)], 'l')
	factory=gray.getImg().factory()

	# wrap as ImagePlus
	imp=ImageJFunctions.wrap(gray, "wrapped")

	# create and call background subtractor
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 
	
	if (invert==True):
		imp.getProcessor().invert()
	
	imgBgs=ImageJFunctions.wrapByte(imp)

	if (showSteps): display.createDisplay("back_sub", data.create(ImgPlus(imgBgs))) 

	# convert the background subtracted image to 32 bit
	temp=ops.run( "createimg", factory, FloatType(), dimensions2D )
	imgBgs32=ImgPlus( temp )
	ops.convert(imgBgs32, imgBgs, ConvertPixCopy() )
	#display.createDisplay("back_sub 32", data.create(ImgPlus(imgBgs32))) 

	# create the Laplacian of Gaussian filter
	kernel = DetectionUtils.createLoGKernel( 3.0, 2, array([1.0, 1.0], 'd' ) )

	# apply the log filter and display the result
	log=ImgPlus( ops.run("createimg", factory, FloatType(), dimensions2D) )
	ops.convolve(log, imgBgs32, kernel)
	if (showSteps): display.createDisplay("log", data.create(ImgPlus(log)))
	
	# apply the threshold operation
	thresholded = ops.run(thresholdmethod, log)
	
	return ImgPlus(thresholded)

def SpotDetection2(imp):
	imp=Duplicator().run(imp)
	# subtract background
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 
	IJ.run(imp, "Auto Threshold", "method=Triangle white");
	return imp

def SpotDetection3(imp, invert=False):
	# operate on a duplicate as not to change the original
	imp=Duplicator().run(imp)
	if (invert):
		IJ.run(imp, "Invert", "");
	
	# subtract background
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True)
	# run midGrey autothreshold
	IJ.run(imp, "Auto Local Threshold", "method=MidGrey radius=15 parameter_1=0 parameter_2=0 white");
	return imp

def SpotDetectionDark(imp):
	imp=Duplicator().run(imp)
	IJ.run(imp, "8-bit", "");
	IJ.run(imp, "Auto Local Threshold", "method=Niblack radius=50 parameter_1=0 parameter_2=0");
	Prefs.blackBackground = True;
	IJ.run(imp, "Erode", "");
	IJ.run(imp, "Fill Holes", "");
	IJ.run(imp, "Open", "");
	IJ.run(imp, "Close-", "");
	IJ.run(imp, "Watershed", "");
	return imp;