import numpy as np

####### Flat normalizing function ##################
def FLAT_Normalizing(image, method):
	if method=='max':
		out=image/np.max(image)
	if method=='mean':
		out=image/np.mean(image)
	if method=='exptime':
		out=image/exptime
	return out
