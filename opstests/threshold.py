# @DatasetService data
# @DisplayService display
# @IOService io
# @OpService ops
# @net.imagej.Dataset inputData

from net.imglib2.meta import ImgPlus

thresholded=ops.otsu(inputData.getImgPlus())
display.createDisplay("thresholded", data.create(ImgPlus(thresholded)))