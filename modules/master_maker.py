import numpy as np

####### Master making function ############################
def MASTER(cube, method):
	if method=='sum':
		out=np.sum(cube, axis=2)
	if method=='mean':
		out=np.mean(cube, axis=2)
	if method=='median':
		out=np.median(cube, axis=2)
	return out
###########################################################
