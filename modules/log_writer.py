import numpy as np

def log(filename, number, header,scidata,name,flag):
	filename.write(str(header['FRAME'])+" #"+str(number)+"\t"+name+"\t"+ str(round(float(header['EXPTIME']), 4))+"\t"+str(np.min(scidata))+"\t"+ str(np.max(scidata))+"\t"+ str(round(np.mean(scidata),1))+"\t"+ str(round(np.median(scidata),1))+"\t"+ str(round(np.std(scidata),1))+ "\t" +flag +"\n")
