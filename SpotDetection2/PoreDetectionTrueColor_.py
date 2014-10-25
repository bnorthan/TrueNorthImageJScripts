# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops
# @ImageDisplayService ids

from ij import IJ
from ij import WindowManager
from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij.plugin.frame import RoiManager

import os
import sys

homedir=IJ.getDirectory('imagej')
jythondir=os.path.join(homedir,'plugins/Evalulab/')
jythondir=os.path.abspath(jythondir)
sys.path.append(jythondir)

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

import PoreDetectionUV
reload(PoreDetectionUV)

from PoreDetectionUV import poreDetectionUV
from PoreDetectionUV import DetectionParams

import PoreDetectionTrueColor
reload(PoreDetectionTrueColor)
from PoreDetectionTrueColor import poreDetectionTrueColor

import CountParticles
reload(CountParticles)
from CountParticles import countParticles

import ExportDataFunction
reload(ExportDataFunction)
from ExportDataFunction import exportToCsv

import DetectionParams
reload(DetectionParams)
from DetectionParams import DetectionParams

import Utility
reload(Utility)

def runPoreDetection(inputImp, data, ops, display):

	name=inputImp.getTitle()	
	inputDataset=Utility.getDatasetByName(data, name)
	
	detectionParameters=DetectionParams(1,1,20, 8800, 0.0 , 1.0, 0.3)

	roi=inputImp.getRoi()

	if (roi is None):
		message=name+": "+Messages.NoRoi
		IJ.write(message)
		return

	roi=inputImp.getRoi().clone();

	statslist=poreDetectionTrueColor(inputImp, inputDataset, roi, ops, data, display, detectionParameters)

	directory=inputImp.getOriginalFileInfo().directory
	name=os.path.splitext(inputImp.getTitle())[0];
	filename=directory+name+'_count.tif'
	roiname=directory+name+'.roi'
	roistatsname=directory+name+'_roistats.csv'
	statsname=directory+name+'_stats.csv'
	
	print name
	IJ.save(inputImp, filename);
	#IJ.save(roi, roiname);
	IJ.saveAs(inputImp, "Selection", roiname);

	print statslist

	#ExportDataFunction.exportToCsv(roistatsname, roiList)
	#ExportDataFunction.exportList(statsname, statslist)
	
if __name__ == '__main__':
	inputImp = IJ.getImage()
	runPoreDetection(inputImp, data, ops, display)

	
	
