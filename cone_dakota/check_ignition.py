import sys
import numpy as np

data = np.loadtxt(sys.argv[1], delimiter=',', skiprows=2)

time = data[:,0]
hrr  = data[:,1]

hrr_thr = 1e-3
hrr_int = 20

time_ignition = 20.0

for i in range(len(time)-hrr_int):
    if np.all(hrr[i:i+hrr_int] > hrr_thr):
        #print "found ignition at %f"%time[i]
        print np.abs(time[i]-time_ignition)
        sys.exit()

#print np.abs(time[-1]-time_ignition)
print -1
