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

# check for command line options
parser = argparse.ArgumentParser()
parser.add_argument("xmlfile", help="XML file to be parsed and have its output executed")
parser.add_argument("--fgg_create",
                    help="fgg_create location", default="fgg_create", action="store_true")
parser.add_argument("--fdsexec",
                    help="name of the FDS executable (default: fds)", default="fds", action="store_true")
cmdl_args = parser.parse_args()

fds_exec = cmdl_args.fdsexec
fgg_create = cmdl_args.fgg_create

stdoutf = open('fgg_create.stdout', 'w')
sp.Popen([fgg_create, xmlfile], stdout=stdoutf, stderr=sp.STDOUT, cwd=subdir).communicate()
stdoutf.close()

stdoutf = open('fgg.stdout', 'w')
sp.Popen([fds_exec, inputfile], stdout=stdoutf, stderr=sp.STDOUT, cwd=subdir).communicate()
stdoutf.close()
