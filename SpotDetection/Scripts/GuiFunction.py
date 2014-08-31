from ij import WindowManager

def GetOpenImageList():
	wList=WindowManager.getIDList()
	if (wList==None): return None
	titles=[]
	[titles.append(WindowManager.getImage(id).getTitle()) for id in wList]
	return titles

def printDatasets(data):
	for dataset in data.getDatasets():
		print dataset.getName()

def getDatasetByName(data, name):
	for dataset in data.getDatasets():
		if dataset.getName()==name:
			return dataset
	return None
		