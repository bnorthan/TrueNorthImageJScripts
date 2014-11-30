# @DatasetService data
# @DisplayService display
# @net.imagej.ops.OpService ops
# @ImageDisplayService ids

from ij import IJ

import os
import sys

homedir=IJ.getDirectory('imagej')
jythondir=os.path.join(homedir,'plugins/Evalulab/')
jythondir=os.path.abspath(jythondir)
sys.path.append(jythondir)

import PoreDetectionUV
reload(PoreDetectionUV)
from PoreDetectionUV import runPoreDetection

if __name__ == '__main__':
	inputImp = IJ.getImage()
	runPoreDetection(inputImp, data, ops, display)
	
	
