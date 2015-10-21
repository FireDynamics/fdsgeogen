import os

import numpy as np
import matplotlib.pyplot as plt

fn_subdirlist = 'fdsgeogen.subdirlist'
fn_plotlist = 'fdsgeogen.plot'

subdirs = []
chids = []
single_tasks = []
local_tasks = {}
global_tasks = {}

# read in all sub directories and CHIDs
subdirs_file = open(fn_subdirlist, 'r')
for line in subdirs_file:
	if line[0] == '#': continue
	lc = line.rstrip().split(';')
	subdirs.append(lc[0])
	chids.append(lc[2])
subdirs_file.close()

# read in all plot tasks
for ind in range(len(subdirs)):

	plot_file = open(subdirs[ind] + '/' + fn_plotlist, 'r')
	for line in plot_file:
		if line[0] == '#': continue
		line_content = line.rstrip().split(';')
		devc_id   = line_content[0]
		devc_q    = line_content[1]
		plot_type = line_content[2]
		
		if plot_type == 'single':
			single_tasks.append([subdirs[ind], chids[ind], devc_id, devc_q])
		elif len(plot_type.split(':')) == 2:
			lc = plot_type.split(':')
			place = lc[0]
			group = lc[1]
			if place == 'local':
				if not subdirs[ind] in local_tasks:
					local_tasks[subdirs[ind]] = {}
				if not group in local_tasks[subdirs[ind]]:
					local_tasks[subdirs[ind]][group] = []
				local_tasks[subdirs[ind]][group].append([chids[ind], devc_id, devc_q])
		else:
			print "WARNING: the plot task syntax is not known: ", plot_type
		
		

print "== single tasks"
for i in single_tasks:
	print i

print "== local tasks"
for i in local_tasks:
	print " =", i
	for j in local_tasks[i]:
		print "  -", j
	
print "== global tasks"
for i in global_tasks:
	print i



# for ind in range(len(subdirs)):
# 	print "analyse subdirectory " + subdirs[ind]
# 
# 	fn_devc = subdirs[ind] + '/' + chids[ind] + '_devc.csv'
# 
# 	devc_file = open(fn_devc, 'r')
# 	units = devc_file.readline().rstrip().split(',')
# 	ids   = devc_file.readline().rstrip().split(',')
# 	devc_file.close()
# 	
# 	#strip "'s from device ids 
# 	for i in range(1,len(ids)):
# 		ids[i] = ids[i].strip("\"")
# 	
# 	print "found units: ", units
# 	print "found ids  : ", ids
# 	
# 	subdir_data = np.loadtxt(fn_devc, skiprows=2, delimiter=',')
# 	
# 	plot_file = open(subdirs[ind] + '/' + fn_plotlist, 'r')
# 	for line in plot_file:
# 		if line[0] == '#': continue
# 		line_content = line.rstrip().split(';')
# 		devc_id   = line_content[0]
# 		devc_q    = line_content[1]
# 		plot_type = line_content[2]
# 		
# 		print "found task: ", devc_id, devc_q, plot_type
# 		
# 		index_in_csv = ids.index(devc_id)
# 		
# 		if devc_id in ids:
# 			print "found device id in output file at position ", index_in_csv
# 		else:
# 			print "WARNING: did not find corresponding device id !!"
# 		
# 		if plot_type == 'single':
# 			plt.plot(subdir_data[:,0], subdir_data[:,index_in_csv])
# 			plt.xlabel('time [s]')
# 			plt.ylabel('%s, '%devc_q + devc_id + ' [%s]'%units[index_in_csv])
# 			plt.savefig(subdir + '/plot_%s.pdf'%devc_id)
# 			plt.clf()
	