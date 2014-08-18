# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops

from ij import IJ
from ij.plugin.frame import RoiManager;
from net.imglib2 import FinalInterval
from jarray import array
import sys
from net.imglib2.meta import ImgPlus
from net.imglib2.img.display.imagej import ImageJFunctions


jythondir='/home/bnorthan/Brian2012/Round2/RogueImageJPlugins/SpotDetection/Scripts/'
sys.path.append(jythondir)
import SpotDetectionFunction
reload(SpotDetectionFunction)
from SpotDetectionFunction import SpotDetection
from SpotDetectionFunction import SpotDetectionGray


inputDirectory='/home/bnorthan/Brian2012/Round2/RogueImageJPlugins/SpotDetection/Images/'
inputName='B013-D0-L-UV.jpg'
#roiName='RoiSet.zip'
roiName='roi.roi'

dataset=data.open(inputDirectory+inputName)
#display.createDisplay(dataset.getName(), dataset)
rm=RoiManager.getInstance()
if (rm==None):
    rm = RoiManager()
manager=IJ.openImage(inputDirectory+roiName);


for roi in rm.getRoisAsArray():
	rec = roi.getBounds()
	x1=long(rec.getX())
	y1=long(rec.getY())
	x2=x1+long(rec.getWidth())-1
	y2=y1+long(rec.getHeight())-1
	print str(x1)+": "+str(y1)+": "+str(x2)+": "+str(y2)

	#interval=FinalInterval( array([10, 10 ,0], 'l'), array([12, 12, 2], 'l') )
	
	interval=FinalInterval( array([x1, y1 ,0], 'l'), array([x2, y2, 2], 'l') )
	cropped=ops.crop(interval, None, dataset.getImgPlus() ) 
	datacropped=data.create(cropped)
	display.createDisplay("c", datacropped)
	#SpotDetection(datacropped, data, display, ops)
	IJ.run("HSB Stack", "");
	IJ.run("Stack to Images", "");
	
	IJ.selectWindow('Hue')
	iplus=IJ.getImage()
	print type(iplus)
	hue=ImageJFunctions.wrapByte(iplus)
	print type(hue)
	hue=data.create(ImgPlus(hue))
	SpotDetectionGray(hue, data, display, ops)
