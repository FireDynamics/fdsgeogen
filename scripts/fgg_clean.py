#!/usr/bin/env python

# This file is part of fdsgeogen.
# 
# fdsgeogen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fdsgeogen is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fdsgeogen. If not, see <http://www.gnu.org/licenses/>.

import shutil
import os

def printHead():
    rootdir = os.path.abspath(os.path.dirname(__file__)) 
    vf = open(rootdir + "/scripts/version", "r")
    version = vf.readline()
    vf.close()
    lf = open(rootdir + "/scripts/logo", "r")
    logo = lf.read()
    lf.close()

    print logo

    print "###"
    print "### fdsgeogen -- clean up tool"
    print "### version %s"%version
    print "###"
    print
	
printHead()

fn_subdirlist = 'fgg.subdirlist'

fds_exec = 'fds'

subdirs = []

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