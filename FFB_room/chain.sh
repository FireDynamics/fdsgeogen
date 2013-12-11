#!/bin/bash
# submit a chain of jobs with dependency

# number of jobs to submit
NO_OF_JOBS=6

# define jobscript
JOB_SCRIPT=fds.job

i=0
echo "msub $JOB_SCRIPT"
JOBID=$(msub $JOB_SCRIPT 2>&1 | grep -v -e '^$' | sed -e 's/\s*//')
while [ $i -le $NO_OF_JOBS ]; do
echo "msub -W depend=afterok:$JOBID $JOB_SCRIPT"
JOBID=$(msub -W depend=afterok:$JOBID $JOB_SCRIPT 2>&1 | grep -v -e '^$' | sed -e 's/\s*//')
let i=$i+1
done
