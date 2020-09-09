# Uses the astropy ccdproc cosmic ray removing tool. It's based on van Dokkum (2001) as implemented by McCully (2014).
# Check http://ccdproc.readthedocs.io/en/latest/api/ccdproc.cosmicray_lacosmic.html for comments.

import glob
import numpy as np
from astropy.io import fits
import ccdproc


reduced_light_path = './products/reduced*'
reduced_light_files = glob.glob(reduced_light_path)


for name in reduced_light_files:
	with fits.open(name) as img:
		header=img[0].header
		scidata=img[0].data
		newdata, mask = ccdproc.cosmicray_lacosmic(scidata, sigclip=10, sigfrac=0.3, objlim=5.0, gain=1.0, readnoise=6.5, satlevel=65535.0, pssl=0.0, niter=4, sepmed=True, cleantype=u'meanmask', fsmode=u'median', psfmodel=u'gauss', psffwhm=3.5, psfsize=7, psfk=None, psfbeta=4.765, verbose=False)  


		mask=1*mask

		header['FRAME']='Light Reduced Cosmic Rays Removed'
		header['comment'] = 'Cosmic Rays Removed'
		hdu=fits.PrimaryHDU(data=newdata, header=header)
		filename=name.replace('./products/','')
		hdu.writeto('./products/cosmic_ray_removed_'+filename, overwrite=True)


		hdu=fits.PrimaryHDU(data=mask)
		hdu.writeto('./products/cosmic_ray_mask_of_'+filename, overwrite=True)







