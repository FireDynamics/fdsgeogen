import os

import numpy as np
import matplotlib.pyplot as plt

subdirs = []
tasks = {}

subdirs_file = open('fdsgeogen.subdirlist', 'r')
for line in subdirs_file:
	subdir = line.split(';')[0]
	subdirs.append(subdir)
subdirs_file.close()
	
for subdir in subdirs:
	print "analyse subdirectory " + subdir

	devc_file = open(subdir + '/simple_burner_devc.csv', 'r')
	units = devc_file.readline().rstrip().split(',')
	ids   = devc_file.readline().rstrip().split(',')
	devc_file.close()
	
	#strip "'s from device ids 
	for i in range(1,len(ids)):
		ids[i] = ids[i].strip("\"")
	
	print "found units: ", units
	print "found ids  : ", ids
	
	subdir_data = np.loadtxt(subdir + '/simple_burner_devc.csv', skiprows=2, delimiter=',')
	
	plot_file = open(subdir + '/fdsgeogen.plot', 'r')
	for line in plot_file:
		line_content = line.rstrip().split(';')
		devc_id   = line_content[0]
		devc_q    = line_content[1]
		plot_type = line_content[2]
		
		print "found task: ", devc_id, devc_q, plot_type
		
		index_in_csv = ids.index(devc_id)
		
		if devc_id in ids:
			print "found device id in output file at position ", index_in_csv
		else:
			print "WARNING: did not find corresponding device id !!"
		
		if plot_type == 'single':
			plt.plot(subdir_data[:,0], subdir_data[:,index_in_csv])
			plt.xlabel('time [s]')
			plt.ylabel('%s, '%devc_q + devc_id + ' [%s]'%units[index_in_csv])
			plt.savefig('plot_%s.pdf'%devc_id)
			plt.clf()
	