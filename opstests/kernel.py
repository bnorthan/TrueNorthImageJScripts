# @DatasetService data
# @DisplayService display
# @IOService io
# @OpService ops
# @net.imagej.Dataset inputData

from net.imglib2.type.numeric.real import FloatType
from net.imglib2.meta import ImgPlus
from jarray import array

fact=inputData.getImgPlus().getImg().factory()

#ops.createImg(inputData.getImgPlus().getImg())
#ops.createImg(factory, FloatType(), array([100, 100],'i'))

blank=ops.run("createimg", fact, FloatType(), array([100, 100],'l'))

gauss=ops.run("gauss", fact, FloatType(), 3, 20.0)
display.createDisplay("gauss", data.create(ImgPlus(gauss)))

gauss3d=ops.run("gauss", fact, FloatType(), 3, 20.0, array([1, 1, 3],'f'))
display.createDisplay("gauss3d", data.create(ImgPlus(gauss3d)))

log=ops.run("log", fact, FloatType(), 3, 20.0, array([1, 1, 3],'f'))
display.createDisplay("log", data.create(ImgPlus(log)))


'''