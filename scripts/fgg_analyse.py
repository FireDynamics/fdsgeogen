#!/usr/bin/env python

import os

import numpy as np
import matplotlib.pyplot as plt

fn_subdirlist = 'fdsgeogen.subdirlist'
fn_plotlist = 'fdsgeogen.plot'

############################ HELPER

def readDevcInfo(fn):
	devc_file = open(fn, 'r')
	units = devc_file.readline().rstrip().split(',')
	ids   = devc_file.readline().rstrip().split(',')
	devc_file.close()
	
	#strip "'s from device ids 
	for i in range(1,len(ids)):
		ids[i] = ids[i].strip("\"")
	
	return units, ids

#################

def saveDevcPlot(dir, t, ys, ids, qs, units, group, mode='all'):

	mode_init = False
	mode_finish = False
	if mode == 'all': 
		mode_init = True
		mode_finish = True
	if mode == 'init':
		mode_init = True
	if mode == 'finish':
		mode_finish = True

	allSame = True

	if mode_init:
		for i in range(len(ids)-1):
			if qs[i] != qs[i+1]: allSame = False
			if units[i] != units[i+1]: allSame = False
		
		for i in range(len(ys)):
			label = ids[i]
			if not allSame:
				label = ids[i] + " [" + units[i] + "]" 
			plt.plot(t, ys[i], marker='o', linestyle='--', label=label)
	
	if mode_finish:
		plt.xlabel('time [s]')
		
		ylabel = qs[0] + " [" + units[0] + "]" 
		if not allSame:
			ylabel = 'individual scale'
		plt.ylabel(ylabel)
		plt.legend()
		fn = "fgg_" + group + ".pdf"
		if len(ys) == 1:
			fn = "fgg_" + ids[0] + ".pdf"
		plt.savefig(dir + '/' + fn)
		plt.clf()

############################


subdirs = []
chids = []
single_tasks = {}
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
			if not subdirs[ind] in single_tasks:
				single_tasks[subdirs[ind]] = []
			single_tasks[subdirs[ind]].append([chids[ind], devc_id, devc_q])
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
	print " =", i
	for j in single_tasks[i]:
		print "  -", j

print "== local tasks"
for i in local_tasks:
	print " =", i
	for j in local_tasks[i]:
		print "  -", j
	
print "== global tasks"
for i in global_tasks:
	print i

# go to all directories and check for tasks
for ind in range(len(subdirs)):
	csd = subdirs[ind]
	ccid = chids[ind]
	fn_devc = csd + '/' + ccid + '_devc.csv'
	
	if not ((csd in single_tasks) or (csd in local_tasks)):
		print "INFO: skipping directory, as not single or local tasks exist", csd
		continue
	
	units, ids = readDevcInfo(fn_devc)
	
	data = np.loadtxt(fn_devc, skiprows=2, delimiter=',')
	
	for i in single_tasks[csd]:
	
		print "processing single task in directory: ", csd
	
		if not i[1] in ids:
			print "WARNINIG: did not find according device id: ", i[1]
			continue
		
		col = ids.index(i[1])
	
		saveDevcPlot(csd, data[:,0], (data[:,col],), (i[1], ), (i[2], ), (units[col],), '')

	for cg in local_tasks[csd]:
		
		print "processing local task in directory: ", csd, ", group: ", cg
		
		gc_cols  = []
		gc_ids   = []
		gc_qs    = []
		gc_units = []
		gc_data  = []
		
		for ct in local_tasks[csd][cg]:
			if not ct[1] in ids:
				print "WARNINIG: did not find according device id: ", i[1]
				continue
			col = ids.index(ct[1])
			gc_cols.append(col)
			gc_units.append(units[col])
			gc_ids.append(ct[1])
			gc_qs.append(ct[2])
			gc_data.append(data[:,col])
		
		saveDevcPlot(csd, data[:,0], gc_data, gc_ids, gc_qs, gc_units, cg)
		