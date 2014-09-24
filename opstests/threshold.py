# @DatasetService data
# @DisplayService display
# @IOService io
# @OpService ops
# @net.imagej.Dataset inputData
# @OUTPUT net.imglib2.meta.ImgPlus thresholded

from net.imglib2.meta import ImgPlus
from net.imglib2.type.numeric.real import FloatType
from net.imglib2.img.display.imagej import ImageJFunctions

from ij import ImagePlus
from ij.plugin.filter import BackgroundSubtracter

from jarray import array

from fiji.plugin.trackmate.detection import DetectionUtils

from net.imagej.ops.convert import ConvertPixCopy

###############################################################
# Step 1:  Rolling ball background subtraction (still uses IJ1)
###############################################################

# wrap as ImagePlus
imp=ImageJFunctions.wrap(inputData, "wrapped")

# create and call background subtractor
bgs=BackgroundSubtracter()
bgs.rollingBallBackground(imp.getProcessor(), 50.0, False, False, True, True, True) 

# wrap the result of background subtraction as Img
iplus=ImagePlus("bgs", imp.getProcessor())
imgBgs=ImageJFunctions.wrapShort(iplus)


###############################################################
# Step 2:  Laplacian of Gaussian Filtering
###############################################################

# convert to 32 bit
imgBgs32=ops.run("createimg", imgBgs, FloatType())
ops.convert(imgBgs32, imgBgs, ConvertPixCopy() )

# create the Laplacian of Gaussian filter
kernel = DetectionUtils.createLoGKernel( 3.0, 2, array([1.0, 1.0], 'd' ) )

# create the output Img for convolution
log=ImgPlus( ops.run("createimg", inputData.getImgPlus(), FloatType() ) )

# apply the log filter
ops.convolve(log, imgBgs32, kernel)


###############################################################
# Step 3:  Threshold
###############################################################

# apply the threshold operation
thresholded = ops.run("triangle", log)
display.createDisplay("thresholded", data.create(ImgPlus(thresholded)))