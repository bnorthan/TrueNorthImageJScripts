# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops
# @ImageDisplayService ids

from ij import IJ
from ij import WindowManager
from ij.gui import GenericDialog
from ij.gui import NonBlockingGenericDialog
from ij.plugin.frame import RoiManager

import sys

#homedir='/home/bnorthan/Brian2012/Round2/ImageJScriptingProjects/'
homedir='/home/bnorthan/Brian2014/Projects/ImageJScriptingProjects/'
jythondir=homedir+'TrueNorthImageJScripts/SpotDetection/Scripts/'
roiname=homedir+'ProprietaryImages/Evalulab/Rois/Right.roi'
sys.path.append(jythondir)

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

import PoreDetectionUV
reload(PoreDetectionUV)
from PoreDetectionUV import poreDetectionUV
from PoreDetectionUV import DetectionParameters

import Utility
reload(Utility)

def runPoreDetection():
	'''roiManager=RoiManager(False)
	roiManager.runCommand("open", roiname)
	roiHash=roiManager.getROIs()
	roi=roiHash.get("Right")
	print roi'''
	
	imageList=Utility.GetOpenImageList()

	nbgd=NonBlockingGenericDialog(Messages.AddRoi)
	nbgd.addMessage(Messages.ChooseImage)
	                              
	if (imageList==None):
		IJ.showMessage(Messages.noOpenImages)
		return;
		
	nbgd.addChoice("Image1:", imageList, imageList[0]);
	nbgd.showDialog()

	name = nbgd.getNextChoice()

	inputImp = WindowManager.getImage(name)
	inputDataset=Utility.getDatasetByName(data, name)
	
	detectionParameters=DetectionParameters(10, 200, 0.5, 1.0, 0.3)

	#inputImp.setRoi(roi)

	nbgd2=NonBlockingGenericDialog(Messages.PositionRoi)
	nbgd2.addMessage(Messages.PositionRoiAndPressOK)
	nbgd2.showDialog()

	poreDetectionUV(inputImp, inputDataset, inputImp.getRoi().clone(), ops, data, display, detectionParameters)

if __name__ == '__main__':
	runPoreDetection()
	
	
	
	
