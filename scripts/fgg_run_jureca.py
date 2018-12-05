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
parser.add_argument("--force",
                    help="submit FDS job even if job was already submitted", action="store_true")
parser.add_argument("--number_of_jobs",
                    help="maximal number of jobs in queue (default: 5)", default=5, type=int)
parser.add_argument("--status",
                    help="shows status of jobs (no action / submitted / running / finished)", action="store_true")
cmdl_args = parser.parse_args()

fn_subdirlist = 'fgg.subdirlist'

submit_cmd = 'sbatch'

subdirs = []
inputs  = []
chids   = []

# read in all sub directories, FDS input files, and CHIDs
if not os.path.isfile(fn_subdirlist):
    print(" -- file %s could not be opened -> EXIT"%fn_subdirlist)
    print()
    sys.exit(1)
subdirs_file = open(fn_subdirlist, 'r')
for line in subdirs_file:
    if line[0] == '#': continue
    lc = line.rstrip().split(';')
    subdirs.append(lc[0])
    inputs.append(lc[1])
    chids.append(lc[2])
subdirs_file.close()

print("processing subdirectories: ")

if cmdl_args.status:

    cnt_finished = 0
    cnt_running  = 0
    cnt_queued   = 0
    cnt_noaction = 0

    for cd_ind in range(len(subdirs)):
        subdir    = subdirs[cd_ind]
        chid      = chids[cd_ind]
        inputfile = inputs[cd_ind]

        if os.path.isfile(os.path.join(subdir, "fgg.jureca.finished")):
            print(subdir + ": simulation finished")
            cnt_finished +=1
            continue

        if os.path.isfile(os.path.join(subdir, "fgg.jureca.running")):
            print(subdir + ": simulation running")
            cnt_running += 1
            continue

        if os.path.isfile(os.path.join(subdir, "fgg.jureca.submitted")):
            print(subdir + ": simulation queued")
            cnt_queued += 1
            continue

        print(subdir + ": no action so far")
        cnt_noaction += 1

    print("SUMMARY")
    print("finished: ", cnt_finished)
    print("running : ", cnt_running)
    print("queued  : ", cnt_queued)
    print("noaction: ", cnt_noaction)


else:
    submitted_number = 0
    for cd_ind in range(len(subdirs)):
        subdir    = subdirs[cd_ind]
        chid      = chids[cd_ind]
        inputfile = inputs[cd_ind]

        print(" -", subdir)

        if os.path.isfile(os.path.join(subdir, "fgg.jureca.finished")):
            print("   ... skipping, is already finished")
            continue

        if os.path.isfile(os.path.join(subdir, "fgg.jureca.submitted")) and not cmdl_args.force:
            print("   ... was already submitted")
        else:
            stdoutf = open(os.path.join(subdir, 'fgg.jureca.stdout'), 'w')
            sp.Popen([submit_cmd, 'fgg.jureca.job'], stdout=stdoutf, stderr=sp.STDOUT, cwd=subdir).communicate()
            stdoutf.close()

            sf = open(os.path.join(subdir, 'fgg.jureca.submitted'), 'w')
            sf.close()

            print("   ... submitted to job queue")

        submitted_number += 1

        if submitted_number >= cmdl_args.number_of_jobs:
            print("  maximal number of submitted jobs reached, stopping ")
            break

