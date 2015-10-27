#!/usr/bin/env python

import subprocess as sp
import os.path

fn_subdirlist = 'fgg.subdirlist'

fds_exec = 'fds'

subdirs = []
inputs  = []
chids   = []

# read in all sub directories, FDS input files, and CHIDs
subdirs_file = open(fn_subdirlist, 'r')
for line in subdirs_file:
	if line[0] == '#': continue
	lc = line.rstrip().split(';')
	subdirs.append(lc[0])
	inputs.append(lc[1])
	chids.append(lc[2])
subdirs_file.close()

print "processing subdirectories: "

for cd_ind in range(len(subdirs)):
	subdir    = subdirs[cd_ind]
	chid      = chids[cd_ind]
	inputfile = inputs[cd_ind]

	print " -", subdir
	
	if os.path.isfile(subdir + "/" + chid + ".end"):
		print "   ... skipping, was already finished"
	else:
		stdoutf = open(subdir + '/fgg.stdout', 'w')
		sp.Popen([fds_exec, inputfile], stdout=stdoutf, stderr=sp.STDOUT, cwd=subdir).communicate()
		stdoutf.close()
		print "   ... finished"
	

