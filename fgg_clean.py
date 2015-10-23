#!/usr/bin/env python

import shutil
import os

fn_subdirlist = 'fdsgeogen.subdirlist'

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
subdirs_file.close()

ans = raw_input("removing all subdirectories? (yes / no): ")

if ans == 'yes':

	for d in subdirs:
		shutil.rmtree(d)
	
	os.remove(fn_subdirlist)

