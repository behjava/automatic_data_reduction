################ First reading a sample fits file to obtain the dimensions of the images NAXIS2,NAXIS1 #########
from astropy.io import fits
def read(path,files):
	dummy=0
	while dummy < 1:
	    try:
		for name in files:
	        		with fits.open(name) as img:
					header=img[0].header
					scidata=img[0].data
					NAXIS1=int(header['NAXIS1'])
					NAXIS2=int(header['NAXIS2'])
					dummy=dummy+1
	    except IOError as exc:
	        if exc.errno != errno.EISDIR:
	            raise


	return [NAXIS1, NAXIS2]
