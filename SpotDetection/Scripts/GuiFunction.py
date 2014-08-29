from ij import WindowManager

def GetOpenImageList():
	wList=WindowManager.getIDList()
	if (wList==None): return None
	titles=[]
	[titles.append(WindowManager.getImage(id).getTitle()) for id in wList]
	return titles