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

homedir='/home/bnorthan/Brian2014/Projects/ImageJScriptingProjects/'
jythondir=homedir+'TrueNorthImageJScripts/SpotDetection/Scripts/'
roiname=homedir+'ProprietaryImages/Evalulab/Rois/Right.roi'
sys.path.append(jythondir)

import MessageStrings
reload(MessageStrings)
from MessageStrings import Messages

import ROIAnalysis
reload(ROIAnalysis)
from ROIAnalysis import roiAnalysis
from ROIAnalysis import DetectionParameters

import GuiFunction
reload(GuiFunction)

def runRoiAnalysis():
	roiManager=RoiManager(False)
	roiManager.runCommand("open", roiname)
	roiHash=roiManager.getROIs()
	roi=roiHash.get("Right")
	print roi
	
	imageList=GuiFunction.GetOpenImageList()

	nbgd=NonBlockingGenericDialog(Messages.AddRoi)
	nbgd.addMessage(Messages.ChooseImage)
	                              
	if (imageList==None):
		IJ.showMessage(Messages.noOpenImages)
		return;
		
	nbgd.addChoice("Image1:", imageList, imageList[0]);
	nbgd.showDialog()

	name = nbgd.getNextChoice()

	inputImp = WindowManager.getImage(name)
	inputDataset=GuiFunction.getDatasetByName(data, name)

	print inputImp
	print inputDataset
	
	detectionParameters=DetectionParameters(10, 200, 0.5, 1.0, 0.3)

	'''inputImp.setRoi(roi)

	nbgd2=NonBlockingGenericDialog(Messages.PositionRoiAndPressOK)
	nbgd2.showDialog()'''

	print inputDataset
	
	roiAnalysis(inputImp, inputDataset, ops, data, display, detectionParameters)

if __name__ == '__main__':
	runRoiAnalysis()
	
	
	
	
