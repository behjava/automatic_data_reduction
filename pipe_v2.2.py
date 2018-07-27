import time
import sys
start_time = time.time()
import datetime
import numpy as np
import errno
import glob
import os
from astropy.io import fits
#my modules:
import master_maker as master
import normalizer as norm
import dimensions
import log_writer as log


master_method='mean'  # The method for producing master images. Can be 'sum', 'mean', or 'median'
flat_normalizing_method='max' # The method for normalizing flat frames. Can be 'max', 'mean', or 'exptime'
flat_min_count=10000
flat_max_count=50000
min_bias_limit= 900  # mean of bias is around 1050 and its std is around 30. These limits are mean +/- 5*std
max_bias_limit= 1200


####### Reading all the fits files in the folder ###################

path = '*.fits'
files = glob.glob(path)


################ First reading a sample fits file to obtain the dimensions of the images NAXIS2,NAXIS1 #########

[NAXIS1, NAXIS2]=dimensions.read(path,files)

########## Using the image dimensions (NAXIS2,NAXIS1) to make an empty slice for producing image cubes ############ 

flat_exptime=np.empty(1)
flat_cube=np.empty([NAXIS2,NAXIS1,1])
bias_cube=np.empty([NAXIS2,NAXIS1,1])
dark_cube=np.empty([NAXIS2,NAXIS1,1])


####### Making data cubes using flat, bias, and dark frames. The Light frames are only renamed for later use. ################


################# opening log files ##############################
def assure_path_exists(path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
                os.makedirs(dir)

assure_path_exists('./log_files/')  #the directory for the log files
bias_log=open("./log_files/bias_log.txt","w+")
bias_log.write("#number	file_name		EXPTIME	min	max	mean	median	std"+"\n")
dark_log=open("./log_files/dark_log.txt","w+")
dark_log.write("#number	file_name		EXPTIME	min	max	mean	median	std"+"\n")
flat_log=open("./log_files/flat_log.txt","w+")
flat_log.write("#number		file_name		EXPTIME	min	max	mean	median	std"+"\n")
light_log=open("./log_files/light_log.txt","w+")
light_log.write("#number		file_name			EXPTIME	min	max	mean	median	std"+"\n")
###################################################################

frames_num=0
flat_num=0
bias_num=0
dark_num=0
light_num=0
flag=''
for name in files:
    try:
        with fits.open(name) as img:
		header=img[0].header
		scidata=img[0].data
		if header['FRAME']=='Flat Field':
			if np.min(scidata) > flat_min_count and np.max(scidata) < flat_max_count:
				flag='frame used'
				flat_cube=np.dstack((flat_cube,scidata))
				flat_exptime=np.append(flat_exptime,float(header['EXPTIME']))   ### Saving the exposure time of each flat frame for later use
			else:
				flag='frame not used'
			flat_num=flat_num+1
			log.log(flat_log, flat_num, header,scidata,name,flag)
		if header['FRAME']=='Bias':
			if min_bias_limit < np.mean(scidata) < max_bias_limit:
				flag='frame used'
				bias_cube=np.dstack((bias_cube,scidata))
			else:
				flag='frame not used'
			bias_num=bias_num+1
			log.log(bias_log, bias_num, header,scidata,name,flag)
		if header['FRAME']=='Dark':
			flag=''
			dark_cube=np.dstack((dark_cube,scidata))
			dark_num=dark_num+1
			log.log(dark_log, dark_num, header,scidata,name,flag)
		if header['FRAME']=='Light':
			flag=''
			if 'Light' not in name:
				os.rename(name, 'Light_'+name)
			light_num=light_num+1
			log.log(light_log, light_num, header,scidata,name,flag)
		frames_num=frames_num+1
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise


bias_log.close()
dark_log.close()
flat_log.close()
light_log.close()



##### Getting rid of the first slice of each cube which is empty ################################

flat_exptime=np.delete(flat_exptime, 0)
flat_cube=np.delete(flat_cube, (0), axis=2)
bias_cube=np.delete(bias_cube, (0), axis=2)
dark_cube=np.delete(dark_cube, (0), axis=2)

################ Printing the counts ############################################################
            
print "Total Number of Frames", frames_num
print "Number of Flat Field Frames=", flat_num
print "Number of used Flat Field Frames=", np.shape(flat_cube)[2]
print "Number of Bias Frames=", bias_num
print "Number of used Bias Field Frames=", np.shape(bias_cube)[2]
print "Number of Dark Frames=", dark_num
print "Number of used Dark Frames=", np.shape(dark_cube)[2]
print "Number of Light Frames=", light_num


######### Checking if the number of used is zero ##############

if np.shape(flat_cube)[2] ==0:
	print "\n"+"The script cannot continue since the number of good flat frames is zero"+"\n"
	sys.exit()

if np.shape(flat_cube)[2] ==1:
	print "\n"+"WARNING: Only 1 good flat frame was found"+"\n"


if np.shape(bias_cube)[2] ==0:
	print "\n"+"The script cannot continue since the number of good bias frames is zero"+"\n"
	sys.exit()

if np.shape(bias_cube)[2] ==1:
	print "\n"+"WARNING: Only 1 good bias frame was found"+"\n"



######################### Making masters ##########################################################
assure_path_exists('./products/')  #the directory for the products


master_bias=master.MASTER(bias_cube, method=master_method)
hdu=fits.PrimaryHDU(data=master_bias)#, header=header)
hdu.writeto('./products/master_bias.fits', overwrite=True)

master_dark=master.MASTER(dark_cube, method=master_method)
hdu=fits.PrimaryHDU(data=master_dark)#, header=header)
hdu.writeto('./products/master_dark.fits', overwrite=True)

master_dark_bias_subtracted=master_dark-master_bias
hdu=fits.PrimaryHDU(data=master_dark_bias_subtracted)#, header=header)
hdu.writeto('./products/master_dark_bias_subtracted.fits', overwrite=True)

for i in range(len(flat_exptime)):
	flat_cube[:,:,i]=flat_cube[:,:,i]-master_dark_bias_subtracted
	exptime=flat_exptime[i]
	flat_cube[:,:,i]=norm.FLAT_Normalizing(flat_cube[:,:,i], method=flat_normalizing_method)

master_flat=master.MASTER(flat_cube, method=master_method)
hdu=fits.PrimaryHDU(data=master_flat)#, header=header)
hdu.writeto('./products/master_flat.fits', overwrite=True)

################## test flat

test_flat_division=flat_cube[:,:,0]/master_flat
hdu=fits.PrimaryHDU(data=test_flat_division)#, header=header)
hdu.writeto('./products/test_flat_division.fits', overwrite=True)

####################### Applying the reductions to the Light frames and saving new fits files with the same header and a comment line #########


light_path = 'Light*'
light_files = glob.glob(light_path)

for name in light_files:
	with fits.open(name) as img:
		header=img[0].header
		scidata=img[0].data
		scidata_dark_subtracted=scidata-master_dark_bias_subtracted
		scidata_flat_divided=scidata_dark_subtracted/master_flat
		header['FRAME']='Light Reduced'
		header['comment'] = 'Reduced using the INOWFS Data Reduction Pipeline (B. Javanmardi) on ' + str(datetime.datetime.now())
		hdu=fits.PrimaryHDU(data=scidata_flat_divided, header=header)
		#filename=name.replace('raw_data/','')
		hdu.writeto('./products/reduced_'+name, overwrite=True)



pyc_path = '*.pyc'
pyc_files = glob.glob(pyc_path)
for pyc_name in pyc_files:
	os.remove(pyc_name)


elapsed_time = time.time() - start_time
print "Elapsed Time= ", elapsed_time, "sec"





















