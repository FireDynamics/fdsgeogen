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

import sys
import subprocess as sp
import os.path
import argparse

def printHead():
    rootdir = os.path.abspath(os.path.dirname(__file__))
    if sys.platform == "win32": # WINDOWS
        vf = open(rootdir + "\\version", "r")
        lf = open(rootdir + "\\logo", "r")
    else:
        vf = open(rootdir + "/scripts/version", "r")
        lf = open(rootdir + "/scripts/logo", "r")
    version = vf.readline()
    logo = lf.read()
    vf.close()
    lf.close()

    print logo

    print "###"
    print "### fdsgeogen -- serial execution tool"
    print "### version %s"%version
    print "###"
    print

printHead()

# check for command line options
parser = argparse.ArgumentParser()
parser.add_argument("--force",
                    help="run FDS even if job was finished", action="store_true")
parser.add_argument("--fdsexec",
                    help="name of the FDS executable (default: fds)", default="fds", action="store_true")
cmdl_args = parser.parse_args()

fn_subdirlist = 'fgg.subdirlist'

fds_exec = cmdl_args.fdsexec

subdirs = []
inputs  = []
chids   = []

# read in all sub directories, FDS input files, and CHIDs
if not os.path.isfile(fn_subdirlist):
    print " -- file %s could not be opened -> EXIT"%fn_subdirlist
    print 
    sys.exit(1)
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
	
	if os.path.isfile(subdir + "/" + chid + ".end") and not cmdl_args.force:
		print "   ... skipping, was already finished"
	else:
		stdoutf = open(subdir + '/fgg.stdout', 'w')
		sp.Popen([fds_exec, inputfile], stdout=stdoutf, stderr=sp.STDOUT, cwd=subdir).communicate()
		stdoutf.close()
		print "   ... finished"