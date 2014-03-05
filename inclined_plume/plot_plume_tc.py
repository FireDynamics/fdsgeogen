import sys
import numpy as np

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

devc_fn = sys.argv[1]

print "reading devc file: ", devc_fn

devc_file = open(devc_fn, 'r')
devc_file.readline()
devc_list = devc_file.readline().rstrip('\n').split(",")

tc_index_coord = []

tc_identifyer = "FIRE-TC-GRID"
tc_num = 20

for idx, devc in enumerate(devc_list):
    if (devc.find(tc_identifyer) > 0):
        line = devc.replace(tc_identifyer, "")[1:-1]
        coords = line.split(".")
        tc_index_coord.append([int(coords[0]), int(coords[1]), idx])

#print len(tc_index_coord), tc_num, tc_num**2
if len(tc_index_coord) != tc_num**2:
    print "wrong number of devices found!"
    sys.exit()

tc_plane = np.zeros([tc_num, tc_num])

#print tc_index_coord

devc_data = np.loadtxt(devc_fn, skiprows=2, delimiter=',')
#print devc_data

its = np.linspace(1, len(devc_data[:])-1, 25)
its = its.astype(int)
#print its

for it in its:
    print "plot time index: ", it
    for tc in tc_index_coord:
        i1 = tc[0]
        i2 = tc[1]
        di = tc[2]
        tc_plane[i1, i2] = devc_data[it, di]
    
    #print tc_plane
    
    cp = plt.contour(tc_plane)
    plt.clabel(cp)
    plt.title("temperature @ t=%f"%devc_data[it, 0])
    plt.savefig("tc_plane_%04d.pdf"%it)
    plt.clf()
